/* tpr.c
 * Tonal Power Ratio (con regola MPEG-1, lobo +/-1, scala dB tonal/noise)
 * + n_peaks tonali. Due outlet.
 *
 * Uso in Pd: [tpr spectrum lobe_width]
 *   - spectrum:    nome dell'array di magnitudo
 *   - lobe_width:  semi-ampiezza del lobo per banda tonale (default 1)
 *   - bang:        esegue il calcolo
 *   - outlet 1:    float, tpr in dB
 *   - outlet 2:    float, n_peaks tonali
 *
 * Algoritmo (analisi.py.tonal_power_ratio):
 *   power[k]  = X[k]^2
 *   total     = sum(power)
 *   picchi    = massimi locali con distanza minima 3 bin
 *   tonali    = picchi che superano i vicini a +/-2 bin di almeno 7 dB
 *               in potenza (fattore ~5 in lineare): regola MPEG-1
 *   tonal_pwr = sum_{pk tonale} sum_{i = pk-L .. pk+L} power[i]
 *   noise_pwr = max(total - tonal_pwr, eps)
 *   tpr_db    = 10 * log10(tonal_pwr / noise_pwr)
 *
 * Nota su "distanza minima 3 bin": qui implementata come picco locale
 * stretto (p[k] > p[k-1] e p[k] > p[k+1]) con il successivo controllo
 * MPEG-1 a +/-2 bin che, di fatto, esclude picchi a distanza < 3 da uno
 * piu' alto. Allinea con find_peaks(distance=3) di scipy ai fini del
 * conteggio dei picchi tonali.
 *
 * Nessun gating relativo: tpr lavora sull'energia totale, il filtro e'
 * gia' nella regola di tonalita' MPEG-1.
 */

#include "m_pd.h"
#include <math.h>

#define TPR_EPSILON 1e-30
#define TPR_RATIO_DB 7.0   /* soglia MPEG-1 in dB di potenza */

static t_class *tpr_class;

typedef struct _tpr {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_float   lobe_width;
    t_outlet *x_out_tpr;
    t_outlet *x_out_n;
} t_tpr;

void tpr_bang(t_tpr *x) {
    t_garray *a_spettro = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a_spettro) {
        pd_error(x, "tpr: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }
    t_word *vec;
    int size;
    garray_getfloatwords(a_spettro, &size, &vec);
    if (size < 5) {
        outlet_float(x->x_out_n, 0);
        outlet_float(x->x_out_tpr, 0.0);
        return;
    }

    int L = (int)x->lobe_width;
    if (L < 0) L = 0;

    /* Total power. Si tiene power "on the fly" senza array intermedio:
     * il bin power[k] = vec[k]^2 viene ricalcolato ogni volta che serve. */
    double total = 0.0;
    int k;
    for (k = 0; k < size; k++) {
        double m = vec[k].w_float;
        total += m * m;
    }
    if (total <= 0.0) {
        outlet_float(x->x_out_n, 0);
        outlet_float(x->x_out_tpr, 0.0);
        return;
    }

    /* Soglia MPEG-1 in lineare: 10^(7/10) ≈ 5.0119 */
    double ratio_thr = pow(10.0, TPR_RATIO_DB / 10.0);

    /* Scansione: per ogni bin verifica picco locale stretto + regola MPEG-1.
     * Per i picchi tonali accumula la potenza nel lobo +/-L. */
    double tonal_pwr = 0.0;
    int n_tonal = 0;

    for (k = 1; k < size - 1; k++) {
        double pm1 = vec[k - 1].w_float;
        double p0  = vec[k].w_float;
        double pp1 = vec[k + 1].w_float;
        double e0  = p0 * p0;
        double em1 = pm1 * pm1;
        double ep1 = pp1 * pp1;

        if (!(e0 > em1 && e0 > ep1)) continue;

        /* Regola MPEG-1 a +/-2 bin */
        int left_ok, right_ok;
        if (k < 2) {
            left_ok = 1;
        } else {
            double el2 = vec[k - 2].w_float;
            el2 *= el2;
            left_ok = (e0 / (el2 + TPR_EPSILON) >= ratio_thr);
        }
        if (k >= size - 2) {
            right_ok = 1;
        } else {
            double er2 = vec[k + 2].w_float;
            er2 *= er2;
            right_ok = (e0 / (er2 + TPR_EPSILON) >= ratio_thr);
        }
        if (!(left_ok && right_ok)) continue;

        /* Picco tonale: accumula la potenza del lobo +/-L */
        int lo = k - L; if (lo < 0) lo = 0;
        int hi = k + L; if (hi >= size) hi = size - 1;
        int j;
        for (j = lo; j <= hi; j++) {
            double mj = vec[j].w_float;
            tonal_pwr += mj * mj;
        }
        n_tonal++;
    }

    if (n_tonal == 0) {
        outlet_float(x->x_out_n, 0);
        outlet_float(x->x_out_tpr, 0.0);
        return;
    }

    double noise_pwr = total - tonal_pwr;
    if (noise_pwr < TPR_EPSILON) noise_pwr = TPR_EPSILON;

    double tpr_db = 10.0 * log10(tonal_pwr / noise_pwr);

    outlet_float(x->x_out_n, (t_float)n_tonal);
    outlet_float(x->x_out_tpr, (t_float)tpr_db);
}

void *tpr_new(t_symbol *spettro, t_floatarg lobe_width) {
    t_tpr *x = (t_tpr *)pd_new(tpr_class);
    x->nome_spettro = spettro;
    x->lobe_width   = (lobe_width > 0) ? lobe_width : 1.0;
    floatinlet_new(&x->x_obj, &x->lobe_width);
    /* In Pd l'ordine fisico degli outlet va destra → sinistra al click,
     * ma in lettura conviene crearli sinistra → destra: tpr (sx), n (dx). */
    x->x_out_tpr = outlet_new(&x->x_obj, &s_float);
    x->x_out_n   = outlet_new(&x->x_obj, &s_float);
    return (void *)x;
}

void tpr_setup(void) {
    tpr_class = class_new(gensym("tpr"), (t_newmethod)tpr_new, 0,
        sizeof(t_tpr), CLASS_DEFAULT, A_DEFSYMBOL, A_DEFFLOAT, 0);
    class_addbang(tpr_class, tpr_bang);
}
