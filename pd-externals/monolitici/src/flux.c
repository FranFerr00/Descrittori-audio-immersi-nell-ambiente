/* flux.c
 * Calcola lo spectral flux (somma delle differenze in valore assoluto fra
 * spettro corrente e spettro del frame precedente) in un singolo external.
 *
 * Uso in Pd: [flux spectrum threshold_db]
 *   - spectrum:     nome dell'array contenente lo spettro di magnitudo
 *   - threshold_db: soglia relativa in dB dal picco (default -30)
 *   - bang:         esegue il calcolo
 *   - outlet:       float, flux (adimensionale, somma di magnitudo)
 *
 * Formula:
 *   per ogni frame:
 *     peak    = max(X[k])
 *     soglia  = peak * 10^(threshold_db / 20)
 *     X_th[k] = X[k] se X[k] > soglia, altrimenti 0
 *   flux = sum_k | X_th[k] - X_th_prev[k] |
 *
 * Stato interno: buffer del frame precedente (X_th_prev). Allocato al
 * primo bang con la dimensione dello spettro corrente; ri-allocato se
 * la dimensione cambia. Il primo bang dopo la creazione (o dopo un
 * cambio di size) restituisce il flux contro un buffer di zeri, quindi
 * coincide con la somma del frame corrente sopra soglia. Per evitarlo,
 * inviare un [reset( prima del primo bang utile per azzerare il buffer
 * e scartare il primo valore.
 *
 * Pattern simile a arraydelta: malloc + destructor registrato in setup.
 */

#include "m_pd.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

static t_class *flux_class;

typedef struct _flux {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_float   threshold_db;
    double   *prev;        /* buffer del frame precedente (gia' gated) */
    int       prev_size;   /* dimensione corrente del buffer */
    t_outlet *x_out;
} t_flux;

void flux_bang(t_flux *x) {
    t_garray *a_spettro;

    a_spettro = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a_spettro) {
        pd_error(x, "flux: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }

    t_word *vec;
    int size;
    garray_getfloatwords(a_spettro, &size, &vec);

    if (size <= 0) {
        pd_error(x, "flux: array vuoto");
        return;
    }

    /* (Ri)alloca il buffer prev se serve. Inizializza a zero. */
    if (x->prev == NULL || x->prev_size != size) {
        free(x->prev);
        x->prev = (double *)calloc((size_t)size, sizeof(double));
        if (x->prev == NULL) {
            pd_error(x, "flux: malloc fallita");
            x->prev_size = 0;
            return;
        }
        x->prev_size = size;
    }

    /* PRIMA PASSATA: picco del frame corrente */
    double peak = 0.0;
    int k;
    for (k = 0; k < size; k++) {
        double mag = vec[k].w_float;
        if (mag > peak) peak = mag;
    }

    double soglia = (peak > 0.0)
        ? peak * pow(10.0, (double)x->threshold_db / 20.0)
        : 0.0;

    /* SECONDA PASSATA: gating del corrente, somma |curr - prev|, aggiornamento prev */
    double sum = 0.0;
    for (k = 0; k < size; k++) {
        double mag = vec[k].w_float;
        double curr = (mag > soglia) ? mag : 0.0;
        double d = curr - x->prev[k];
        if (d < 0) d = -d;
        sum += d;
        x->prev[k] = curr;
    }

    outlet_float(x->x_out, (t_float)sum);
}

/* Azzera il buffer del frame precedente. Utile dopo un cambio di sorgente
 * o per scartare il primo bang dopo la creazione. */
void flux_reset(t_flux *x) {
    if (x->prev != NULL && x->prev_size > 0) {
        memset(x->prev, 0, sizeof(double) * (size_t)x->prev_size);
    }
}

void *flux_new(t_symbol *spettro, t_floatarg threshold_db) {
    t_flux *x = (t_flux *)pd_new(flux_class);
    x->nome_spettro = spettro;
    x->threshold_db = (threshold_db < 0) ? threshold_db : -30.0;
    x->prev      = NULL;
    x->prev_size = 0;

    floatinlet_new(&x->x_obj, &x->threshold_db);

    x->x_out = outlet_new(&x->x_obj, &s_float);

    return (void *)x;
}

void flux_free(t_flux *x) {
    free(x->prev);
    x->prev = NULL;
    x->prev_size = 0;
}

void flux_setup(void) {
    flux_class = class_new(
        gensym("flux"),
        (t_newmethod)flux_new,
        (t_method)flux_free,
        sizeof(t_flux),
        CLASS_DEFAULT,
        A_DEFSYMBOL,
        A_DEFFLOAT,
        0);

    class_addbang(flux_class, flux_bang);
    class_addmethod(flux_class, (t_method)flux_reset, gensym("reset"), 0);
}
