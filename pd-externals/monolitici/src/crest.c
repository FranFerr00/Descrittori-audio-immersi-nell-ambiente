/* crest.c
 * Spectral crest factor: max / mean sui bin sopra soglia relativa.
 *
 * Uso in Pd: [crest spectrum threshold_db]
 *   - spectrum:     nome dell'array di magnitudo
 *   - threshold_db: soglia relativa in dB dal picco (default -30)
 *   - bang:         esegue il calcolo
 *   - outlet:       float, crest adimensionale
 *
 * Formula:
 *   peak    = max(X[k])
 *   soglia  = peak * 10^(threshold_db/20)
 *   attivi  = { X[k] : X[k] > soglia }
 *   crest   = max(attivi) / mean(attivi)
 *
 * Nota: max(attivi) coincide con peak (peak supera sempre la soglia).
 * Si tiene comunque il calcolo esplicito per chiarezza.
 *
 * Range: [1, +inf). 1 = spettro perfettamente piatto sopra soglia,
 * grande = un singolo bin domina rispetto agli altri attivi.
 */

#include "m_pd.h"
#include <math.h>

static t_class *crest_class;

typedef struct _crest {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_float   threshold_db;
    t_outlet *x_out;
} t_crest;

void crest_bang(t_crest *x) {
    t_garray *a_spettro = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a_spettro) {
        pd_error(x, "crest: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }
    t_word *vec;
    int size;
    garray_getfloatwords(a_spettro, &size, &vec);
    if (size <= 0) { pd_error(x, "crest: array vuoto"); return; }

    double peak = 0.0;
    int k;
    for (k = 0; k < size; k++) {
        double m = vec[k].w_float;
        if (m > peak) peak = m;
    }
    if (peak <= 0.0) { outlet_float(x->x_out, 0.0); return; }

    double soglia = peak * pow(10.0, (double)x->threshold_db / 20.0);

    double sum = 0.0, mx = 0.0;
    int n = 0;
    for (k = 0; k < size; k++) {
        double m = vec[k].w_float;
        if (m > soglia) {
            sum += m;
            if (m > mx) mx = m;
            n++;
        }
    }
    if (n == 0 || sum <= 0.0) { outlet_float(x->x_out, 0.0); return; }

    double mean = sum / (double)n;
    outlet_float(x->x_out, (t_float)(mx / mean));
}

void *crest_new(t_symbol *spettro, t_floatarg threshold_db) {
    t_crest *x = (t_crest *)pd_new(crest_class);
    x->nome_spettro = spettro;
    x->threshold_db = (threshold_db < 0) ? threshold_db : -30.0;
    floatinlet_new(&x->x_obj, &x->threshold_db);
    x->x_out = outlet_new(&x->x_obj, &s_float);
    return (void *)x;
}

void crest_setup(void) {
    crest_class = class_new(gensym("crest"), (t_newmethod)crest_new, 0,
        sizeof(t_crest), CLASS_DEFAULT, A_DEFSYMBOL, A_DEFFLOAT, 0);
    class_addbang(crest_class, crest_bang);
}
