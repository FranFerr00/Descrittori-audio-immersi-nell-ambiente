/* spread.c
 * Calcola lo spread spettrale (deviazione standard della distribuzione
 * di magnitudo rispetto al centroide) in un singolo external.
 *
 * Uso in Pd: [spread spectrum sr fftsize threshold_db]
 *   - spectrum:     nome dell'array contenente lo spettro di magnitudo
 *   - sr:           sample rate (default = sys_getsr())
 *   - fftsize:      dimensione della FFT (default 8192)
 *   - threshold_db: soglia relativa in dB dal picco (default -30)
 *   - bang:         esegue il calcolo
 *   - outlet:       float, spread in Hz
 *
 * I tre parametri numerici sono aggiornabili via inlet float passivi.
 *
 * Formula (identità della varianza):
 *   peak       = max(X[k])
 *   soglia     = peak * 10^(threshold_db / 20)
 *   X_th[k]    = X[k] se X[k] > soglia, altrimenti 0
 *   S0 = sum(X_th[k])
 *   S1 = sum(k * X_th[k])
 *   S2 = sum(k^2 * X_th[k])
 *   centroide_bin = S1 / S0
 *   varianza_bin  = S2/S0 - centroide_bin^2
 *   spread_hz     = sqrt(varianza_bin) * sr / fftsize
 *
 * Si usa l'identità Var(X) = E[X^2] - E[X]^2 per evitare una terza
 * passata: in UNA scansione dello spettro sopra soglia si accumulano
 * S0, S1, S2 e da lì si ricavano sia centroide sia spread.
 *
 * Attenzione: con numeri vicini l'identità E[X^2] - E[X]^2 può dare
 * varianze leggermente negative per cancellazione numerica; si clippa
 * a zero prima della radice. Con double e bin in scala 0..N/2 questo
 * è raro, ma la protezione è gratuita.
 *
 * Descrittore autonomo: ricalcola internamente il picco e il centroide,
 * senza dipendere da un [centroid] esterno. Stesso principio monolitico
 * di [centroid]: due passate, array caldo in cache, output diretto.
 */

#include "m_pd.h"
#include <math.h>

/* Puntatore globale alla classe */
static t_class *spread_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo. */
typedef struct _spread {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_float   sr;
    t_float   fftsize;
    t_float   threshold_db;
    t_outlet *x_out;
} t_spread;

/* Funzione chiamata quando arriva un bang. */
void spread_bang(t_spread *x) {
    t_garray *a_spettro;

    a_spettro = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a_spettro) {
        pd_error(x, "spread: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }

    t_word *vec;
    int size;
    garray_getfloatwords(a_spettro, &size, &vec);

    if (size <= 0) {
        pd_error(x, "spread: array vuoto");
        return;
    }

    if (x->fftsize <= 0) {
        pd_error(x, "spread: fftsize deve essere > 0");
        return;
    }

    /* PRIMA PASSATA: trova il picco dello spettro (double per coerenza) */
    double peak = 0.0;
    int k;
    for (k = 0; k < size; k++) {
        double mag = vec[k].w_float;
        if (mag > peak) peak = mag;
    }

    /* Silenzio: spread non definito, emetto 0 */
    if (peak <= 0.0) {
        outlet_float(x->x_out, 0.0);
        return;
    }

    /* Soglia assoluta a partire da quella relativa in dB */
    double soglia = peak * pow(10.0, (double)x->threshold_db / 20.0);

    /* SECONDA PASSATA: accumula i tre momenti S0, S1, S2 sui bin sopra soglia.
     * Con questi tre valori calcoliamo sia il centroide (S1/S0) sia lo
     * spread (sqrt(S2/S0 - centroide^2)) in una sola scansione. */
    double S0 = 0.0;
    double S1 = 0.0;
    double S2 = 0.0;
    for (k = 0; k < size; k++) {
        double mag = vec[k].w_float;
        if (mag > soglia) {
            double kd = (double)k;
            S0 += mag;
            S1 += kd * mag;
            S2 += kd * kd * mag;
        }
    }

    if (S0 <= 0.0) {
        outlet_float(x->x_out, 0.0);
        return;
    }

    double centroide_bin = S1 / S0;
    double varianza_bin  = S2 / S0 - centroide_bin * centroide_bin;

    /* Clipping a zero per sicurezza numerica: l'identità Var = E[X^2] - E[X]^2
     * può produrre valori leggermente negativi per cancellazione. */
    if (varianza_bin < 0.0) varianza_bin = 0.0;

    double spread_bin = sqrt(varianza_bin);
    double spread_hz  = spread_bin * (double)x->sr / (double)x->fftsize;

    outlet_float(x->x_out, (t_float)spread_hz);
}

/* Costruttore */
void *spread_new(t_symbol *spettro, t_floatarg sr, t_floatarg fftsize,
                 t_floatarg threshold_db) {
    t_spread *x = (t_spread *)pd_new(spread_class);
    x->nome_spettro = spettro;
    x->sr           = (sr      > 0) ? sr      : sys_getsr();
    x->fftsize      = (fftsize > 0) ? fftsize : 8192;
    x->threshold_db = (threshold_db < 0) ? threshold_db : -30.0;

    floatinlet_new(&x->x_obj, &x->sr);
    floatinlet_new(&x->x_obj, &x->fftsize);
    floatinlet_new(&x->x_obj, &x->threshold_db);

    x->x_out = outlet_new(&x->x_obj, &s_float);

    return (void *)x;
}

/* Setup */
void spread_setup(void) {
    spread_class = class_new(
        gensym("spread"),
        (t_newmethod)spread_new,
        0,
        sizeof(t_spread),
        CLASS_DEFAULT,
        A_DEFSYMBOL,    /* nome dello spettro */
        A_DEFFLOAT,     /* sample rate */
        A_DEFFLOAT,     /* fftsize */
        A_DEFFLOAT,     /* threshold_db (default -30) */
        0);

    class_addbang(spread_class, spread_bang);
}
