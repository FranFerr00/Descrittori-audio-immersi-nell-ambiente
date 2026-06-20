/* ema.c
 * Media mobile esponenziale (EMA) di un frame di 16 descrittori, per Pd.
 * Involucro attorno al nucleo ema_core.h. Misura il dt fra i frame dall'orologio
 * di Pd e applica una costante di tempo in secondi.
 *
 * Creazione: [ema <tau>]
 *   - tau: costante di tempo in secondi (default 1). Piccola = scorda in fretta,
 *     grande = media lunga.
 *
 * Inlet caldo: una LISTA di 16 descrittori (il frame corrente). Aggiorna la media
 *   ed emette in uscita la media corrente (lista di 16). E' uno smussatore:
 *   16 dentro -> 16 fuori (la media recente).
 *
 * Messaggi:
 *   tau <secondi>   cambia la costante di tempo
 *   reset           azzera la memoria (riparte dal prossimo frame)
 */
#include "m_pd.h"
#include "ema_core.h"

static t_class *ema_class;

typedef struct _ema {
    t_object  x_obj;
    ema_core  c;
    double    last_t;      /* tempo logico del frame precedente */
    int       have_t;
    t_outlet *out;
} t_ema;

static void ema_list(t_ema *x, t_symbol *s, int argc, t_atom *argv) {
    double frame[EMA_ND], out[EMA_ND];
    t_atom o[EMA_ND];
    int i;
    double dt;
    (void)s;
    if (argc < x->c.nd) {
        pd_error(x, "ema: servono %d valori, arrivati %d", x->c.nd, argc);
        return;
    }
    for (i = 0; i < x->c.nd; i++) frame[i] = (double)atom_getfloat(argv + i);
    dt = x->have_t ? clock_gettimesince(x->last_t) / 1000.0 : 0.0;
    x->last_t = clock_getlogicaltime();
    x->have_t = 1;
    ema_push(&x->c, frame, dt);
    ema_get(&x->c, out);
    for (i = 0; i < x->c.nd; i++) SETFLOAT(o + i, (t_float)out[i]);
    outlet_list(x->out, &s_list, x->c.nd, o);
}

static void ema_tau(t_ema *x, t_floatarg f) {
    ema_set_tau(&x->c, (double)f);
}

static void ema_reset(t_ema *x) {
    x->c.started = 0;
    x->have_t = 0;
}

static void *ema_new(t_floatarg tau) {
    t_ema *x = (t_ema *)pd_new(ema_class);
    ema_init(&x->c, EMA_ND);
    if (tau > 0.0) ema_set_tau(&x->c, (double)tau);
    x->have_t = 0;
    x->out = outlet_new(&x->x_obj, &s_list);
    return (void *)x;
}

void ema_setup(void) {
    ema_class = class_new(gensym("ema"),
                          (t_newmethod)ema_new, 0,
                          sizeof(t_ema), CLASS_DEFAULT, A_DEFFLOAT, 0);
    class_addlist(ema_class, ema_list);
    class_addmethod(ema_class, (t_method)ema_tau, gensym("tau"), A_DEFFLOAT, 0);
    class_addmethod(ema_class, (t_method)ema_reset, gensym("reset"), 0);
}
