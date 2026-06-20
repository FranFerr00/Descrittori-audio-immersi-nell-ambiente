/* rolloff.c
 * Calcola il rolloff spettrale (frequenza sotto la quale cade una
 * frazione "percentile" dell'energia spettrale cumulata).
 *
 * Uso in Pd: [rolloff spectrum sr fftsize threshold_db percentile]
 *   - spectrum:     nome dell'array di magnitudo
 *   - sr:           sample rate (default = sys_getsr())
 *   - fftsize:      dimensione FFT (default 8192)
 *   - threshold_db: soglia relativa dB dal picco (default -30)
 *   - percentile:   frazione cumulata, es. 0.85 (default 0.85)
 *   - bang:         esegue il calcolo
 *   - outlet:       float, frequenza di rolloff in Hz
 *
 * Quattro inlet passivi: sr, fftsize, threshold_db, percentile.
 *
 * Formula (identica a analisi.py.spectral_rolloff):
 *   peak     = max(X[k])
 *   soglia   = peak * 10^(threshold_db/20)
 *   X_th[k]  = X[k] se X[k] > soglia, altrimenti 0
 *   total    = sum(X_th)
 *   target   = percentile * total
 *   cumsum crescente su X_th; primo indice k dove cumsum[k] >= target
 *   rolloff_hz = k * sr / fftsize
 *
 * Due passate sullo spettro: picco, poi accumulazione + ricerca
 * dell'indice di rolloff nello stesso loop (uscita anticipata appena
 * cumsum supera target, quindi spesso si ferma ben prima di size).
 */

#include "m_pd.h"
#include <math.h>

static t_class *rolloff_class;

typedef struct _rolloff {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_float   sr;
    t_float   fftsize;
    t_float   threshold_db;
    t_float   percentile;
    t_outlet *x_out;
} t_rolloff;

void rolloff_bang(t_rolloff *x) {
    t_garray *a;
    a = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a) {
        pd_error(x, "rolloff: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }

    t_word *vec;
    int size;
    garray_getfloatwords(a, &size, &vec);

    if (size <= 0) { pd_error(x, "rolloff: array vuoto"); return; }
    if (x->fftsize <= 0) { pd_error(x, "rolloff: fftsize deve essere > 0"); return; }

    /* PRIMA PASSATA: picco + totale sopra soglia */
    double peak = 0.0;
    int k;
    for (k = 0; k < size; k++) {
        double mag = vec[k].w_float;
        if (mag > peak) peak = mag;
    }
    if (peak <= 0.0) { outlet_float(x->x_out, 0.0); return; }

    double soglia = peak * pow(10.0, (double)x->threshold_db / 20.0);

    /* Total = somma dei bin sopra soglia (serve per calcolare il target) */
    double total = 0.0;
    for (k = 0; k < size; k++) {
        double mag = vec[k].w_float;
        if (mag > soglia) total += mag;
    }
    if (total <= 0.0) { outlet_float(x->x_out, 0.0); return; }

    double target = (double)x->percentile * total;

    /* SECONDA PASSATA: cumsum + prima volta che supera target.
     * Uscita anticipata per non scorrere inutilmente il resto. */
    double cum = 0.0;
    int k_rolloff = size - 1;  /* fallback: ultimo bin se non si raggiunge mai */
    for (k = 0; k < size; k++) {
        double mag = vec[k].w_float;
        if (mag > soglia) {
            cum += mag;
            if (cum >= target) { k_rolloff = k; break; }
        }
    }

    double freq_hz = (double)k_rolloff * (double)x->sr / (double)x->fftsize;
    outlet_float(x->x_out, (t_float)freq_hz);
}

void *rolloff_new(t_symbol *spettro, t_floatarg sr, t_floatarg fftsize,
                  t_floatarg threshold_db, t_floatarg percentile) {
    t_rolloff *x = (t_rolloff *)pd_new(rolloff_class);
    x->nome_spettro = spettro;
    x->sr           = (sr      > 0) ? sr      : sys_getsr();
    x->fftsize      = (fftsize > 0) ? fftsize : 8192;
    x->threshold_db = (threshold_db < 0) ? threshold_db : -30.0;
    /* percentile deve stare in (0, 1]: se non passato o fuori range, default 0.85 */
    x->percentile   = (percentile > 0 && percentile <= 1) ? percentile : 0.85;

    floatinlet_new(&x->x_obj, &x->sr);
    floatinlet_new(&x->x_obj, &x->fftsize);
    floatinlet_new(&x->x_obj, &x->threshold_db);
    floatinlet_new(&x->x_obj, &x->percentile);

    x->x_out = outlet_new(&x->x_obj, &s_float);
    return (void *)x;
}

void rolloff_setup(void) {
    rolloff_class = class_new(
        gensym("rolloff"),
        (t_newmethod)rolloff_new,
        0,
        sizeof(t_rolloff),
        CLASS_DEFAULT,
        A_DEFSYMBOL, A_DEFFLOAT, A_DEFFLOAT, A_DEFFLOAT, A_DEFFLOAT,
        0);
    class_addbang(rolloff_class, rolloff_bang);
}
