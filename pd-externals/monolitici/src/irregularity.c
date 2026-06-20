/* irregularity.c
 * Calcola la spectral irregularity (variante log) in un singolo external.
 *
 * Uso in Pd: [irregularity spectrum threshold_db]
 *   - spectrum:     nome dell'array contenente lo spettro di magnitudo
 *   - threshold_db: soglia relativa in dB dal picco (default -30)
 *   - bang:         esegue il calcolo
 *   - outlet:       float, irregularity adimensionale
 *
 * Formula (variante log, come in analisi.py):
 *   peak       = max(X[k])
 *   soglia     = peak * 10^(threshold_db / 20)
 *   X_th[k]    = X[k] se X[k] > soglia, altrimenti log_epsilon
 *   irreg      = sum_k | log(X_th[k]) - log(X_th[k+1]) |
 *
 * I bin sotto soglia non vengono "buttati": vengono sostituiti con
 * log_epsilon (un floor numerico) per non interrompere la sequenza
 * dei vicini. Senza questo, eliminare bin spostarebbe i vicini e
 * inventerebbe transizioni grandi fra bin originariamente lontani.
 *
 * Range: [0, +inf), adimensionale.
 *  ~0 = spettro liscio (bin adiacenti simili in scala log)
 *  alto = spettro frastagliato (alternanze marcate fra bin vicini)
 *
 * Non dipende da sr/fftsize: e' una somma di differenze adimensionali.
 */

#include "m_pd.h"
#include <math.h>

/* log_epsilon = log(1e-19): floor per i bin sotto soglia, coerente
 * con analisi.py (LOG_EPSILON = log(EPSILON)). */
#define IRREG_LOG_EPSILON (-43.749115)

static t_class *irregularity_class;

typedef struct _irregularity {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_float   threshold_db;
    t_outlet *x_out;
} t_irregularity;

void irregularity_bang(t_irregularity *x) {
    t_garray *a_spettro;

    a_spettro = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a_spettro) {
        pd_error(x, "irregularity: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }

    t_word *vec;
    int size;
    garray_getfloatwords(a_spettro, &size, &vec);

    if (size <= 1) {
        pd_error(x, "irregularity: array troppo corto");
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

    /* SECONDA PASSATA: log con sostituzione + somma differenze in valore
     * assoluto fra bin adiacenti. Si tiene log(X[k-1]) di passata in
     * passata per evitare di ricalcolarlo. */
    double mag0 = vec[0].w_float;
    double log_prev = (mag0 > soglia) ? log(mag0) : IRREG_LOG_EPSILON;

    double sum = 0.0;
    for (k = 1; k < size; k++) {
        double mag = vec[k].w_float;
        double log_curr = (mag > soglia) ? log(mag) : IRREG_LOG_EPSILON;
        double d = log_curr - log_prev;
        if (d < 0) d = -d;
        sum += d;
        log_prev = log_curr;
    }

    outlet_float(x->x_out, (t_float)sum);
}

void *irregularity_new(t_symbol *spettro, t_floatarg threshold_db) {
    t_irregularity *x = (t_irregularity *)pd_new(irregularity_class);
    x->nome_spettro = spettro;
    x->threshold_db = (threshold_db < 0) ? threshold_db : -30.0;

    floatinlet_new(&x->x_obj, &x->threshold_db);

    x->x_out = outlet_new(&x->x_obj, &s_float);

    return (void *)x;
}

void irregularity_setup(void) {
    irregularity_class = class_new(
        gensym("irregularity"),
        (t_newmethod)irregularity_new,
        0,
        sizeof(t_irregularity),
        CLASS_DEFAULT,
        A_DEFSYMBOL,
        A_DEFFLOAT,
        0);

    class_addbang(irregularity_class, irregularity_bang);
}
