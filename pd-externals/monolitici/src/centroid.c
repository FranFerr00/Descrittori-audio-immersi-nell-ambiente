/* centroid.c
 * Calcola il centroide spettrale in un singolo external.
 *
 * Uso in Pd: [centroid spectrum sr fftsize threshold_db]
 *   - spectrum:     nome dell'array contenente lo spettro di magnitudo
 *                   (tipicamente l'output di [rfft~] dopo il modulo)
 *   - sr:           sample rate (argomento float, es. 96000)
 *   - fftsize:      dimensione della FFT (argomento float, es. 8192)
 *   - threshold_db: soglia relativa in dB dal picco (default -30)
 *   - bang:         esegue il calcolo
 *   - outlet:       float, centroide in Hz
 *
 * I tre parametri numerici possono essere aggiornati in tempo reale
 * tramite gli inlet passivi (secondo, terzo, quarto inlet).
 *
 * Formula:
 *   peak         = max(X[k])
 *   soglia       = peak * 10^(threshold_db / 20)
 *   X_th[k]      = X[k] se X[k] > soglia, altrimenti 0
 *   centroide_hz = sum(f[k] * X_th[k]) / sum(X_th[k])
 *
 * dove f[k] = k * sr / fftsize è la frequenza in Hz del bin k.
 *
 * La soglia relativa serve a escludere il rumore di fondo: senza,
 * anche bin molto piccoli (ma numerosi) sposterebbero il centroide.
 * Il valore -30 dB è lo stesso usato in analisi.py, così i risultati
 * coincidono tra analisi offline e calcolo real-time in Pd.
 *
 * Versione MONOLITICA: due passate sull'array (una per il picco,
 * una per l'accumulazione), senza array intermedi.
 *
 * Vantaggi rispetto alla catena di external:
 *   - 1 solo pd_findbyclass invece di 3-5
 *   - nessun array intermedio da allocare/ridisegnare
 *   - lo spettro resta caldo in cache per entrambe le passate
 *   - output diretto dall'outlet, niente garray_redraw
 */

#include "m_pd.h"
#include <math.h>

/* Puntatore globale alla classe */
static t_class *centroid_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo. */
typedef struct _centroid {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_float   sr;             /* sample rate, aggiornabile via inlet */
    t_float   fftsize;        /* dimensione FFT, aggiornabile via inlet */
    t_float   threshold_db;   /* soglia relativa in dB (negativa) */
    t_outlet *x_out;          /* outlet float per il risultato */
} t_centroid;

/* Funzione chiamata quando arriva un bang. */
void centroid_bang(t_centroid *x) {
    t_garray *a_spettro;

    a_spettro = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a_spettro) {
        pd_error(x, "centroid: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }

    t_word *vec;
    int size;
    garray_getfloatwords(a_spettro, &size, &vec);

    if (size <= 0) {
        pd_error(x, "centroid: array vuoto");
        return;
    }

    if (x->fftsize <= 0) {
        pd_error(x, "centroid: fftsize deve essere > 0");
        return;
    }

    /* PRIMA PASSATA: trova il picco dello spettro.
     * Si usa double per coerenza con la seconda passata. */
    double peak = 0.0;
    int k;
    for (k = 0; k < size; k++) {
        double mag = vec[k].w_float;
        if (mag > peak) peak = mag;
    }

    /* Se lo spettro è tutto zero (silenzio), centroide non definito: emetti 0 */
    if (peak <= 0.0) {
        outlet_float(x->x_out, 0.0);
        return;
    }

    /* Calcolo della soglia assoluta a partire da quella relativa in dB.
     * threshold_db è negativa (es. -30): 10^(-30/20) ≈ 0.0316
     * quindi soglia ≈ peak / 31.6 */
    double soglia = peak * pow(10.0, (double)x->threshold_db / 20.0);

    /* SECONDA PASSATA: accumula numeratore e denominatore solo sui bin
     * sopra soglia. Si usa double per evitare perdita di precisione
     * con FFT size grandi (8192 bin in float32 accumulano errori). */
    double num = 0.0;
    double den = 0.0;
    for (k = 0; k < size; k++) {
        double mag = vec[k].w_float;
        if (mag > soglia) {
            num += (double)k * mag;
            den += mag;
        }
    }

    /* Se dopo la soglia non resta nulla, emetti 0 */
    if (den <= 0.0) {
        outlet_float(x->x_out, 0.0);
        return;
    }

    /* Centroide in bin, poi conversione in Hz tramite f[k] = k * sr / fftsize */
    double centroide_bin = num / den;
    double centroide_hz  = centroide_bin * (double)x->sr / (double)x->fftsize;

    outlet_float(x->x_out, (t_float)centroide_hz);
}

/* Costruttore: riceve nome spettro, sample rate, fftsize e soglia in dB. */
void *centroid_new(t_symbol *spettro, t_floatarg sr, t_floatarg fftsize,
                   t_floatarg threshold_db) {
    t_centroid *x = (t_centroid *)pd_new(centroid_class);
    x->nome_spettro = spettro;
    x->sr           = (sr      > 0) ? sr      : sys_getsr();
    x->fftsize      = (fftsize > 0) ? fftsize : 8192;
    /* Se threshold_db è 0 (argomento non passato) uso il default -30.
     * Una soglia a 0 dB azzererebbe tutto tranne il picco, inutile. */
    x->threshold_db = (threshold_db < 0) ? threshold_db : -30.0;

    /* Tre inlet passivi per aggiornare i parametri in tempo reale.
     * Ordine di creazione = ordine degli inlet nell'oggetto. */
    floatinlet_new(&x->x_obj, &x->sr);
    floatinlet_new(&x->x_obj, &x->fftsize);
    floatinlet_new(&x->x_obj, &x->threshold_db);

    /* Outlet float per emettere il centroide calcolato */
    x->x_out = outlet_new(&x->x_obj, &s_float);

    return (void *)x;
}

/* Setup */
void centroid_setup(void) {
    centroid_class = class_new(
        gensym("centroid"),
        (t_newmethod)centroid_new,
        0,
        sizeof(t_centroid),
        CLASS_DEFAULT,
        A_DEFSYMBOL,    /* nome dello spettro */
        A_DEFFLOAT,     /* sample rate */
        A_DEFFLOAT,     /* fftsize */
        A_DEFFLOAT,     /* threshold_db (default -30) */
        0);

    class_addbang(centroid_class, centroid_bang);
}
