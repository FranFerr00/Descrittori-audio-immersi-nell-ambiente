/* zcr.c
 * Zero Crossing Rate: frazione di campioni adiacenti con segno opposto
 * in un frame di forma d'onda (time-domain, non spettrale).
 *
 * Uso in Pd: [zcr frame]
 *   - frame:  nome dell'array della forma d'onda (NON dello spettro)
 *   - bang:   esegue il calcolo
 *   - outlet: float, ZCR in [0, 1]
 *
 * Formula:
 *   crossings = numero di k tali che sign(x[k]) != sign(x[k+1])
 *   zcr       = crossings / (N - 1)
 *
 * Differenza dagli altri descrittori del toolkit: opera nel dominio del
 * tempo. L'array passato e' la finestra audio (es. dump di [tabwrite~]),
 * non lo spettro.
 *
 * Convenzione su sign(0): np.sign restituisce 0, e una transizione
 * 0 → x > 0 NON conta come crossing (|sign(0) - sign(x)| = 1, non > 0
 * solo se confrontato con > 0). Qui implementiamo la stessa regola di
 * analisi.py: contiamo solo |s_k - s_{k+1}| > 0 dopo aver mappato il
 * segno in {-1, 0, 1}. Questo coincide col counting Python su frame
 * lunghi (i campioni esattamente nulli sono rari).
 */

#include "m_pd.h"

static t_class *zcr_class;

typedef struct _zcr {
    t_object  x_obj;
    t_symbol *nome_frame;
    t_outlet *x_out;
} t_zcr;

static inline int sgn(double v) {
    return (v > 0) - (v < 0);
}

void zcr_bang(t_zcr *x) {
    t_garray *a_frame = (t_garray *)pd_findbyclass(x->nome_frame, garray_class);
    if (!a_frame) {
        pd_error(x, "zcr: array '%s' non trovato", x->nome_frame->s_name);
        return;
    }
    t_word *vec;
    int size;
    garray_getfloatwords(a_frame, &size, &vec);
    if (size < 2) { outlet_float(x->x_out, 0.0); return; }

    int s_prev = sgn(vec[0].w_float);
    int crossings = 0;
    int k;
    for (k = 1; k < size; k++) {
        int s_curr = sgn(vec[k].w_float);
        if (s_curr != s_prev) crossings++;
        s_prev = s_curr;
    }

    outlet_float(x->x_out, (t_float)((double)crossings / (double)(size - 1)));
}

void *zcr_new(t_symbol *frame) {
    t_zcr *x = (t_zcr *)pd_new(zcr_class);
    x->nome_frame = frame;
    x->x_out = outlet_new(&x->x_obj, &s_float);
    return (void *)x;
}

void zcr_setup(void) {
    zcr_class = class_new(gensym("zcr"), (t_newmethod)zcr_new, 0,
        sizeof(t_zcr), CLASS_DEFAULT, A_DEFSYMBOL, 0);
    class_addbang(zcr_class, zcr_bang);
}
