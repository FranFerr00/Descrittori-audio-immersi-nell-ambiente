/* tonality.c
 * Tonality coefficient (Peeters 9.1): SFM in dB, mappato in [0, 1].
 * Calcola la SFM internamente e poi applica la mappatura.
 *
 * Uso in Pd: [tonality spectrum threshold_db]
 *   - spectrum:     nome dell'array di magnitudo
 *   - threshold_db: soglia relativa in dB dal picco (default -30)
 *   - bang:         esegue il calcolo
 *   - outlet:       float, tonality in [0, 1]
 *
 * Formula (analisi.py.tonality_coefficient):
 *   sfm     = flatness(X)
 *   sfm_db  = 10 * log10(sfm + 1e-19)
 *   tonality = min(sfm_db / -60, 1)
 *
 * Convenzione: 1 = perfettamente tonale (sfm <= 0), 0 = perfettamente
 * rumoroso (sfm = 1, sfm_db = 0). Il taglio a -60 dB e' la soglia
 * pratica oltre cui un suono e' giudicato tonale.
 */

#include "m_pd.h"
#include <math.h>

#define TONALITY_EPSILON 1e-19

static t_class *tonality_class;

typedef struct _tonality {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_float   threshold_db;
    t_outlet *x_out;
} t_tonality;

void tonality_bang(t_tonality *x) {
    t_garray *a_spettro = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a_spettro) {
        pd_error(x, "tonality: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }
    t_word *vec;
    int size;
    garray_getfloatwords(a_spettro, &size, &vec);
    if (size <= 0) { pd_error(x, "tonality: array vuoto"); return; }

    double peak = 0.0;
    int k;
    for (k = 0; k < size; k++) {
        double m = vec[k].w_float;
        if (m > peak) peak = m;
    }
    if (peak <= 0.0) { outlet_float(x->x_out, 1.0); return; }

    double soglia = peak * pow(10.0, (double)x->threshold_db / 20.0);

    double sum_log = 0.0, sum_lin = 0.0;
    int n = 0;
    for (k = 0; k < size; k++) {
        double m = vec[k].w_float;
        if (m > soglia) {
            sum_log += log(m + TONALITY_EPSILON);
            sum_lin += m;
            n++;
        }
    }
    if (n == 0 || sum_lin <= 0.0) { outlet_float(x->x_out, 1.0); return; }

    double geom = exp(sum_log / (double)n);
    double arith = sum_lin / (double)n;
    double sfm = (arith > 0.0) ? geom / arith : 0.0;

    if (sfm <= 0.0) { outlet_float(x->x_out, 1.0); return; }

    double sfm_db = 10.0 * log10(sfm + TONALITY_EPSILON);
    double t = sfm_db / -60.0;
    if (t > 1.0) t = 1.0;
    if (t < 0.0) t = 0.0;

    outlet_float(x->x_out, (t_float)t);
}

void *tonality_new(t_symbol *spettro, t_floatarg threshold_db) {
    t_tonality *x = (t_tonality *)pd_new(tonality_class);
    x->nome_spettro = spettro;
    x->threshold_db = (threshold_db < 0) ? threshold_db : -30.0;
    floatinlet_new(&x->x_obj, &x->threshold_db);
    x->x_out = outlet_new(&x->x_obj, &s_float);
    return (void *)x;
}

void tonality_setup(void) {
    tonality_class = class_new(gensym("tonality"), (t_newmethod)tonality_new, 0,
        sizeof(t_tonality), CLASS_DEFAULT, A_DEFSYMBOL, A_DEFFLOAT, 0);
    class_addbang(tonality_class, tonality_bang);
}
