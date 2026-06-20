/* entropy.c
 * Spectral entropy: entropia di Shannon di p(k) = |X(k)|^2 / sum|X|^2,
 * normalizzata dividendo per log2(N_totale). Shen 1998, Misra 2004.
 *
 * Uso in Pd: [entropy spectrum]
 *   - spectrum: nome dell'array di magnitudo
 *   - bang:     esegue il calcolo
 *   - outlet:   float, entropy in [0, 1]
 *
 * Formula:
 *   power[k] = X[k]^2
 *   total    = sum(power)
 *   p[k]     = power[k] / total                (per power[k] > 0)
 *   H        = - sum( p[k] * log2(p[k]) )
 *   entropy  = H / log2(N_totale)
 *
 * NESSUN gating relativo: l'entropy guarda la distribuzione su tutti i
 * bin del power spectrum (un gate eliminerebbe la coda di rumore che
 * proprio l'entropy serve a misurare).
 *
 * Range: 0 (tutta l'energia in un bin) ... 1 (uniforme su tutti i bin,
 * rumore bianco). Adimensionale: non dipende da sr/fftsize.
 */

#include "m_pd.h"
#include <math.h>

#define LOG2_INV 1.4426950408889634   /* 1 / log(2) */

static t_class *entropy_class;

typedef struct _entropy {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_outlet *x_out;
} t_entropy;

void entropy_bang(t_entropy *x) {
    t_garray *a_spettro = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a_spettro) {
        pd_error(x, "entropy: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }
    t_word *vec;
    int size;
    garray_getfloatwords(a_spettro, &size, &vec);
    if (size < 2) { outlet_float(x->x_out, 0.0); return; }

    double total = 0.0;
    int k;
    for (k = 0; k < size; k++) {
        double m = vec[k].w_float;
        total += m * m;
    }
    if (total <= 0.0) { outlet_float(x->x_out, 0.0); return; }

    /* H = - sum p log2 p; usiamo log naturale e moltiplichiamo per 1/ln(2) */
    double H = 0.0;
    double inv_total = 1.0 / total;
    for (k = 0; k < size; k++) {
        double m = vec[k].w_float;
        double pwr = m * m;
        if (pwr > 0.0) {
            double p = pwr * inv_total;
            H -= p * log(p);
        }
    }
    H *= LOG2_INV;

    double norm = log((double)size) * LOG2_INV;   /* log2(N) */
    if (norm <= 0.0) { outlet_float(x->x_out, 0.0); return; }

    outlet_float(x->x_out, (t_float)(H / norm));
}

void *entropy_new(t_symbol *spettro) {
    t_entropy *x = (t_entropy *)pd_new(entropy_class);
    x->nome_spettro = spettro;
    x->x_out = outlet_new(&x->x_obj, &s_float);
    return (void *)x;
}

void entropy_setup(void) {
    entropy_class = class_new(gensym("entropy"), (t_newmethod)entropy_new, 0,
        sizeof(t_entropy), CLASS_DEFAULT, A_DEFSYMBOL, 0);
    class_addbang(entropy_class, entropy_bang);
}
