/* zscore.c
 * Z-score incrementale via EMA (exponential moving average).
 *
 * Uso in Pd: [zscore tau]
 *   - tau:    costante di tempo in numero di campioni (frame), default 300
 *             (a 100 fps -> ~3 secondi di finestra).
 *   - float:  input x, aggiorna media/varianza e produce z = (x - mu) / sigma
 *   - bang:   ri-emette l'ultimo z senza aggiornare lo stato
 *   - (reset): azzera mu, var, conteggio
 *   - 2o inlet: aggiorna tau a runtime
 *
 * Formule (EMA):
 *   alpha = 1 / tau
 *   mu    <- (1 - alpha) * mu + alpha * x
 *   var   <- (1 - alpha) * var + alpha * (x - mu_old)^2
 *   sigma = sqrt(max(var, SIGMA_FLOOR^2))
 *   z     = (x - mu) / sigma
 *
 * Warmup: per i primi tau/4 frame mu/var non sono affidabili; in quel
 * periodo l'output e' 0. count viene incrementato fino al raggiungimento
 * della soglia di warmup, poi non si tocca piu'.
 *
 * SIGMA_FLOOR evita la divisione per zero quando il segnale e' costante.
 */

#include "m_pd.h"
#include <math.h>

#define SIGMA_FLOOR 1e-9

static t_class *zscore_class;

typedef struct _zscore {
    t_object x_obj;
    t_float  tau;
    double   mu;
    double   var;
    double   last_z;
    int      count;
    int      warmup;
    t_outlet *x_out;
} t_zscore;

static void zscore_float(t_zscore *x, t_floatarg f) {
    double xv = (double)f;

    double tau = (x->tau > 1.0) ? (double)x->tau : 1.0;
    double alpha = 1.0 / tau;

    double mu_old = x->mu;
    x->mu  = (1.0 - alpha) * x->mu + alpha * xv;
    double d = xv - mu_old;
    x->var = (1.0 - alpha) * x->var + alpha * d * d;

    if (x->count < x->warmup) {
        x->count++;
        x->last_z = 0.0;
    } else {
        double sigma = sqrt(x->var > (SIGMA_FLOOR * SIGMA_FLOOR)
                            ? x->var : (SIGMA_FLOOR * SIGMA_FLOOR));
        x->last_z = (xv - x->mu) / sigma;
    }

    outlet_float(x->x_out, (t_float)x->last_z);
}

static void zscore_bang(t_zscore *x) {
    outlet_float(x->x_out, (t_float)x->last_z);
}

static void zscore_reset(t_zscore *x) {
    x->mu = 0.0;
    x->var = 0.0;
    x->last_z = 0.0;
    x->count = 0;
}

static void *zscore_new(t_floatarg tau) {
    t_zscore *x = (t_zscore *)pd_new(zscore_class);
    x->tau = (tau > 1.0) ? tau : 300.0;
    x->mu = 0.0;
    x->var = 0.0;
    x->last_z = 0.0;
    x->count = 0;
    x->warmup = (int)(x->tau / 4.0);
    if (x->warmup < 4) x->warmup = 4;
    floatinlet_new(&x->x_obj, &x->tau);
    x->x_out = outlet_new(&x->x_obj, &s_float);
    return (void *)x;
}

void zscore_setup(void) {
    zscore_class = class_new(gensym("zscore"),
        (t_newmethod)zscore_new, 0,
        sizeof(t_zscore), CLASS_DEFAULT, A_DEFFLOAT, 0);
    class_addfloat(zscore_class, zscore_float);
    class_addbang(zscore_class, zscore_bang);
    class_addmethod(zscore_class, (t_method)zscore_reset,
                    gensym("reset"), 0);
}
