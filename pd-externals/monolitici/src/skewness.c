/* skewness.c
 * Spectral skewness: terzo momento standardizzato della distribuzione di
 * magnitudo rispetto a centroide e spread.
 *
 * Uso in Pd: [skewness spectrum threshold_db]
 *   - spectrum:     nome dell'array di magnitudo
 *   - threshold_db: soglia relativa in dB dal picco (default -30)
 *   - bang:         esegue il calcolo
 *   - outlet:       float, skewness adimensionale
 *
 * Formula:
 *   peak = max(X[k]); soglia = peak * 10^(threshold_db/20)
 *   X_th[k] = X[k] se > soglia, 0 altrimenti
 *   centroide_bin = sum(k * X_th) / sum(X_th)
 *   spread_bin    = sqrt(sum(k^2 * X_th)/sum(X_th) - centroide_bin^2)
 *   skewness = sum( ((k - centroide_bin)/spread_bin)^3 * X_th ) / sum(X_th)
 *
 * Nota: skewness e kurtosis sono adimensionali e scale-invarianti, quindi
 * il calcolo in bin coincide con quello in Hz (il fattore sr/fftsize si
 * cancella). Niente sr/fftsize negli argomenti.
 *
 * Una sola passata in piu' rispetto a centroide+spread per il momento
 * terzo: prima si accumulano S0/S1/S2 (per centroide e spread), poi una
 * seconda passata sui bin sopra soglia per S3 standardizzato.
 */

#include "m_pd.h"
#include <math.h>

static t_class *skewness_class;

typedef struct _skewness {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_float   threshold_db;
    t_outlet *x_out;
} t_skewness;

void skewness_bang(t_skewness *x) {
    t_garray *a_spettro = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a_spettro) {
        pd_error(x, "skewness: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }
    t_word *vec;
    int size;
    garray_getfloatwords(a_spettro, &size, &vec);
    if (size <= 0) { pd_error(x, "skewness: array vuoto"); return; }

    double peak = 0.0;
    int k;
    for (k = 0; k < size; k++) {
        double m = vec[k].w_float;
        if (m > peak) peak = m;
    }
    if (peak <= 0.0) { outlet_float(x->x_out, 0.0); return; }

    double soglia = peak * pow(10.0, (double)x->threshold_db / 20.0);

    double S0 = 0.0, S1 = 0.0, S2 = 0.0;
    for (k = 0; k < size; k++) {
        double m = vec[k].w_float;
        if (m > soglia) {
            double kd = (double)k;
            S0 += m;
            S1 += kd * m;
            S2 += kd * kd * m;
        }
    }
    if (S0 <= 0.0) { outlet_float(x->x_out, 0.0); return; }

    double c = S1 / S0;
    double v = S2 / S0 - c * c;
    if (v <= 0.0) { outlet_float(x->x_out, 0.0); return; }
    double s = sqrt(v);

    double S3 = 0.0;
    for (k = 0; k < size; k++) {
        double m = vec[k].w_float;
        if (m > soglia) {
            double z = ((double)k - c) / s;
            S3 += z * z * z * m;
        }
    }

    outlet_float(x->x_out, (t_float)(S3 / S0));
}

void *skewness_new(t_symbol *spettro, t_floatarg threshold_db) {
    t_skewness *x = (t_skewness *)pd_new(skewness_class);
    x->nome_spettro = spettro;
    x->threshold_db = (threshold_db < 0) ? threshold_db : -30.0;
    floatinlet_new(&x->x_obj, &x->threshold_db);
    x->x_out = outlet_new(&x->x_obj, &s_float);
    return (void *)x;
}

void skewness_setup(void) {
    skewness_class = class_new(gensym("skewness"), (t_newmethod)skewness_new, 0,
        sizeof(t_skewness), CLASS_DEFAULT, A_DEFSYMBOL, A_DEFFLOAT, 0);
    class_addbang(skewness_class, skewness_bang);
}
