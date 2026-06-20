/* kurtosis.c
 * Spectral kurtosis (excess): quarto momento standardizzato della
 * distribuzione di magnitudo, meno 3 (Fisher convention, distribuzione
 * normale → 0).
 *
 * Uso in Pd: [kurtosis spectrum threshold_db]
 *   - spectrum:     nome dell'array di magnitudo
 *   - threshold_db: soglia relativa in dB dal picco (default -30)
 *   - bang:         esegue il calcolo
 *   - outlet:       float, kurtosis (excess) adimensionale
 *
 * Formula: stessa struttura di skewness ma con z^4 e sottrazione di 3.
 *
 * Adimensionale e scale-invariante: calcolo in bin = calcolo in Hz.
 */

#include "m_pd.h"
#include <math.h>

static t_class *kurtosis_class;

typedef struct _kurtosis {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_float   threshold_db;
    t_outlet *x_out;
} t_kurtosis;

void kurtosis_bang(t_kurtosis *x) {
    t_garray *a_spettro = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a_spettro) {
        pd_error(x, "kurtosis: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }
    t_word *vec;
    int size;
    garray_getfloatwords(a_spettro, &size, &vec);
    if (size <= 0) { pd_error(x, "kurtosis: array vuoto"); return; }

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

    double S4 = 0.0;
    for (k = 0; k < size; k++) {
        double m = vec[k].w_float;
        if (m > soglia) {
            double z = ((double)k - c) / s;
            double z2 = z * z;
            S4 += z2 * z2 * m;
        }
    }

    outlet_float(x->x_out, (t_float)(S4 / S0 - 3.0));
}

void *kurtosis_new(t_symbol *spettro, t_floatarg threshold_db) {
    t_kurtosis *x = (t_kurtosis *)pd_new(kurtosis_class);
    x->nome_spettro = spettro;
    x->threshold_db = (threshold_db < 0) ? threshold_db : -30.0;
    floatinlet_new(&x->x_obj, &x->threshold_db);
    x->x_out = outlet_new(&x->x_obj, &s_float);
    return (void *)x;
}

void kurtosis_setup(void) {
    kurtosis_class = class_new(gensym("kurtosis"), (t_newmethod)kurtosis_new, 0,
        sizeof(t_kurtosis), CLASS_DEFAULT, A_DEFSYMBOL, A_DEFFLOAT, 0);
    class_addbang(kurtosis_class, kurtosis_bang);
}
