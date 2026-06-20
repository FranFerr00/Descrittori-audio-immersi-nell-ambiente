/* flatness.c
 * Calcola la spectral flatness (Spectral Flatness Measure, SFM) in un
 * singolo external monolitico.
 *
 * Uso in Pd: [flatness spectrum threshold_db]
 *   - spectrum:     nome dell'array contenente lo spettro di magnitudo
 *   - threshold_db: soglia relativa in dB dal picco (default -30)
 *   - bang:         esegue il calcolo
 *   - outlet:       float, flatness in [0, 1] (adimensionale)
 *
 * Formula:
 *   peak    = max(X[k])
 *   soglia  = peak * 10^(threshold_db / 20)
 *   attive  = { X[k] : X[k] > soglia }
 *   geom    = exp( mean( log(attive + epsilon) ) )
 *   arith   = mean(attive)
 *   SFM     = geom / arith
 *
 * Identita' usata per il geom_mean: exp(mean(log(x))) = (prod(x))^(1/N).
 * Si calcola come somma dei log e divisione per N per evitare overflow
 * del prodotto su molti bin.
 *
 * Range: 0 (tutta l'energia in un picco) ... 1 (spettro perfettamente
 * piatto, rumore bianco). Non dipende da sr/fftsize: e' un rapporto
 * fra medie sui bin attivi.
 */

#include "m_pd.h"
#include <math.h>

#define FLATNESS_EPSILON 1e-19

static t_class *flatness_class;

typedef struct _flatness {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_float   threshold_db;
    t_outlet *x_out;
} t_flatness;

void flatness_bang(t_flatness *x) {
    t_garray *a_spettro;

    a_spettro = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a_spettro) {
        pd_error(x, "flatness: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }

    t_word *vec;
    int size;
    garray_getfloatwords(a_spettro, &size, &vec);

    if (size <= 0) {
        pd_error(x, "flatness: array vuoto");
        return;
    }

    /* PRIMA PASSATA: picco */
    double peak = 0.0;
    int k;
    for (k = 0; k < size; k++) {
        double mag = vec[k].w_float;
        if (mag > peak) peak = mag;
    }

    if (peak <= 0.0) {
        outlet_float(x->x_out, 0.0);
        return;
    }

    double soglia = peak * pow(10.0, (double)x->threshold_db / 20.0);

    /* SECONDA PASSATA: somma log e somma lineare sui bin attivi */
    double sum_log  = 0.0;
    double sum_lin  = 0.0;
    int    n_active = 0;
    for (k = 0; k < size; k++) {
        double mag = vec[k].w_float;
        if (mag > soglia) {
            sum_log += log(mag + FLATNESS_EPSILON);
            sum_lin += mag;
            n_active++;
        }
    }

    if (n_active == 0 || sum_lin <= 0.0) {
        outlet_float(x->x_out, 0.0);
        return;
    }

    double geom_mean  = exp(sum_log / (double)n_active);
    double arith_mean = sum_lin / (double)n_active;

    if (arith_mean <= 0.0) {
        outlet_float(x->x_out, 0.0);
        return;
    }

    double sfm = geom_mean / arith_mean;
    outlet_float(x->x_out, (t_float)sfm);
}

void *flatness_new(t_symbol *spettro, t_floatarg threshold_db) {
    t_flatness *x = (t_flatness *)pd_new(flatness_class);
    x->nome_spettro = spettro;
    x->threshold_db = (threshold_db < 0) ? threshold_db : -30.0;

    floatinlet_new(&x->x_obj, &x->threshold_db);

    x->x_out = outlet_new(&x->x_obj, &s_float);

    return (void *)x;
}

void flatness_setup(void) {
    flatness_class = class_new(
        gensym("flatness"),
        (t_newmethod)flatness_new,
        0,
        sizeof(t_flatness),
        CLASS_DEFAULT,
        A_DEFSYMBOL,    /* nome dello spettro */
        A_DEFFLOAT,     /* threshold_db (default -30) */
        0);

    class_addbang(flatness_class, flatness_bang);
}
