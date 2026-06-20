/* scatto.c
 * Scatto ad attraversamento di soglia con tempo refrattario, generico.
 *
 * Riceve un flusso di float (un descrittore, es. E1 o E2 di una famiglia) e
 * emette un bang quando il segnale ATTRAVERSA la soglia nel verso scelto,
 * confrontando due frame adiacenti. Dopo uno scatto resta "sordo" per un
 * tempo refrattario, per non riscattare a raffica sullo stesso evento.
 *
 * Creazione: [scatto soglia (refrattario_ms) (verso)]
 *   - soglia: valore di soglia (default 0.6).
 *   - refrattario_ms: tempo minimo fra due scatti (default 200 ms).
 *   - verso: +1 = salita (scatta quando prec <= soglia e corr > soglia),
 *            -1 = discesa (scatta quando prec >= soglia e corr < soglia).
 *            Default +1. Per E2 (|cos|, riposo ~1, evento = calo) usare -1.
 *
 * Ingresso: float = valore del frame corrente. Un NaN viene ignorato (non
 *   scatta e non aggiorna il frame precedente): cosi' i buchi del segnale
 *   gated/indefinito non producono falsi attraversamenti.
 *
 * Messaggi: [soglia f( [refrattario f( [verso f( cambiano i parametri;
 *   [reset( dimentica il frame precedente e azzera il refrattario.
 *
 * Uscita: bang a ogni attraversamento valido.
 */

#include "m_pd.h"
#include <math.h>

static t_class *scatto_class;

typedef struct _scatto {
    t_object  x_obj;
    t_float   soglia;
    t_float   refr_ms;
    t_float   verso;       /* +1 salita, -1 discesa */

    t_float   prev;        /* ultimo frame valido */
    int       has_prev;    /* 0 finche' non e' arrivato un frame valido */
    double    t_last;      /* tempo logico dell'ultimo scatto */

    t_outlet *out;
} t_scatto;


static void scatto_float(t_scatto *x, t_floatarg f) {
    /* NaN/inf: buco del segnale, ignora senza toccare lo stato */
    if (!(f == f) || isinf(f)) return;

    if (!x->has_prev) {           /* primo frame valido: solo memorizza */
        x->prev = f;
        x->has_prev = 1;
        return;
    }

    int crossed;
    if (x->verso >= 0)            /* salita */
        crossed = (x->prev <= x->soglia) && (f > x->soglia);
    else                          /* discesa */
        crossed = (x->prev >= x->soglia) && (f < x->soglia);

    x->prev = f;

    if (!crossed) return;
    if (clock_gettimesince(x->t_last) < x->refr_ms) return;   /* refrattario */

    x->t_last = clock_getlogicaltime();
    outlet_bang(x->out);
}

static void scatto_setsoglia(t_scatto *x, t_floatarg f)  { x->soglia = f; }
static void scatto_setrefr(t_scatto *x, t_floatarg f)    { x->refr_ms = (f < 0) ? 0 : f; }
static void scatto_setverso(t_scatto *x, t_floatarg f)   { x->verso = (f < 0) ? -1 : 1; }

static void scatto_reset(t_scatto *x) {
    x->has_prev = 0;
    x->t_last = clock_getlogicaltime() - 1e9;   /* refrattario gia' scaduto */
}


static void *scatto_new(t_symbol *s, int argc, t_atom *argv) {
    (void)s;
    t_scatto *x = (t_scatto *)pd_new(scatto_class);
    x->soglia  = (argc > 0) ? atom_getfloat(argv + 0) : 0.6;
    x->refr_ms = (argc > 1) ? atom_getfloat(argv + 1) : 200;
    x->verso   = (argc > 2 && atom_getfloat(argv + 2) < 0) ? -1 : 1;
    if (x->refr_ms < 0) x->refr_ms = 0;
    x->has_prev = 0;
    x->t_last = clock_getlogicaltime() - 1e9;

    x->out = outlet_new(&x->x_obj, &s_bang);
    post("scatto: soglia=%g refrattario=%g ms verso=%g", x->soglia, x->refr_ms, x->verso);
    return (void *)x;
}


void scatto_setup(void) {
    scatto_class = class_new(
        gensym("scatto"),
        (t_newmethod)scatto_new,
        0,
        sizeof(t_scatto),
        CLASS_DEFAULT,
        A_GIMME, 0);

    class_addfloat(scatto_class, scatto_float);
    class_addmethod(scatto_class, (t_method)scatto_setsoglia, gensym("soglia"), A_FLOAT, 0);
    class_addmethod(scatto_class, (t_method)scatto_setrefr, gensym("refrattario"), A_FLOAT, 0);
    class_addmethod(scatto_class, (t_method)scatto_setverso, gensym("verso"), A_FLOAT, 0);
    class_addmethod(scatto_class, (t_method)scatto_reset, gensym("reset"), 0);
}
