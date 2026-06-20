/* slope.c
 * Calcola lo slope spettrale come pendenza della regressione lineare
 * di 20*log10(X[k]) su log2(frequenza in Hz).
 *
 * Uso in Pd: [slope spectrum sr fftsize threshold_db]
 *   - spectrum:     array di magnitudo
 *   - sr:           sample rate (default = sys_getsr())
 *   - fftsize:      dim FFT (default 8192)
 *   - threshold_db: soglia relativa dB dal picco (default -30)
 *   - bang:         esegue il calcolo
 *   - outlet:       float, slope in dB/ottava (tipicamente -20..+5)
 *
 * Formula (identica a analisi.py.spectral_slope):
 *   - x_k  = log2(freq[k])  (solo bin con freq>0 e mag_th>0)
 *   - y_k  = 20 * log10(mag_th[k] + EPSILON)
 *   - slope = sum((x - x_mean)*(y - y_mean)) / sum((x - x_mean)^2)
 *
 * Il bin k=0 (DC) viene escluso (freq=0 non ha log2).
 *
 * Scala log2/dB invece che Hz/ampiezza lineare per motivi noti:
 * i valori lineari danno slope ~1e-8 perche' il denominatore Hz^2 e'
 * signal-independent. In dB/ottava lo slope vive nel range udibile
 * (fonte: openSMILE/GeMAPS, Kazazis et al. 2022, vedi analisi.py).
 *
 * Due passate sullo spettro:
 *   1) picco
 *   2) accumulo somme per la regressione (x, y, x^2, x*y, conteggio)
 *      solo sui bin sopra soglia. log2 e log10 calcolati on-the-fly.
 *      Per performance estreme si potrebbe cachare log2(freq[k]), ma
 *      la cache andrebbe invalidata a ogni cambio di sr/fftsize: per
 *      ora si paga un log2/log10 per bin attivo (tipicamente << size).
 */

#include "m_pd.h"
#include <math.h>

#define SLOPE_EPSILON 1e-19

static t_class *slope_class;

typedef struct _slope {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_float   sr;
    t_float   fftsize;
    t_float   threshold_db;
    t_outlet *x_out;
} t_slope;

void slope_bang(t_slope *x) {
    t_garray *a;
    a = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a) {
        pd_error(x, "slope: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }

    t_word *vec;
    int size;
    garray_getfloatwords(a, &size, &vec);

    if (size <= 0) { pd_error(x, "slope: array vuoto"); return; }
    if (x->fftsize <= 0) { pd_error(x, "slope: fftsize deve essere > 0"); return; }

    /* PRIMA PASSATA: picco */
    double peak = 0.0;
    int k;
    for (k = 0; k < size; k++) {
        double mag = vec[k].w_float;
        if (mag > peak) peak = mag;
    }
    if (peak <= 0.0) { outlet_float(x->x_out, 0.0); return; }

    double soglia = peak * pow(10.0, (double)x->threshold_db / 20.0);
    double inv_log2 = 1.0 / log(2.0);  /* log2(z) = log(z) * inv_log2 */
    double df = (double)x->sr / (double)x->fftsize;

    /* SECONDA PASSATA: accumula somme per la regressione.
     * Si fa in due scan: prima le somme di x e y (per i mean), poi
     * gli scarti. Oppure, formulazione numericamente equivalente,
     * si accumulano Sx, Sy, Sxx, Sxy, N e si ricavano mean/covarianza
     * con le identita' algebriche. Qui uso la seconda. */
    double Sx = 0.0, Sy = 0.0, Sxx = 0.0, Sxy = 0.0;
    int N = 0;

    for (k = 1; k < size; k++) {  /* k=0 escluso: freq=0, log2 non definito */
        double mag = vec[k].w_float;
        if (mag > soglia) {
            double freq = (double)k * df;
            double xk = log(freq) * inv_log2;               /* log2(freq) */
            double yk = 20.0 * log10(mag + SLOPE_EPSILON);  /* dB */
            Sx  += xk;
            Sy  += yk;
            Sxx += xk * xk;
            Sxy += xk * yk;
            N++;
        }
    }

    if (N < 2) { outlet_float(x->x_out, 0.0); return; }

    /* slope = (N*Sxy - Sx*Sy) / (N*Sxx - Sx^2) */
    double den = (double)N * Sxx - Sx * Sx;
    if (den == 0.0) { outlet_float(x->x_out, 0.0); return; }
    double num = (double)N * Sxy - Sx * Sy;
    double slope_val = num / den;

    outlet_float(x->x_out, (t_float)slope_val);
}

void *slope_new(t_symbol *spettro, t_floatarg sr, t_floatarg fftsize,
                t_floatarg threshold_db) {
    t_slope *x = (t_slope *)pd_new(slope_class);
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

void slope_setup(void) {
    slope_class = class_new(
        gensym("slope"),
        (t_newmethod)slope_new,
        0,
        sizeof(t_slope),
        CLASS_DEFAULT,
        A_DEFSYMBOL, A_DEFFLOAT, A_DEFFLOAT, A_DEFFLOAT,
        0);
    class_addbang(slope_class, slope_bang);
}
