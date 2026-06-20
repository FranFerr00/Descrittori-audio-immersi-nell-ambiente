/* ancore.c
 * Controllo bipolare a ancore e distanza, per Pd. Involucro attorno al nucleo
 * numerico ancore_core.h (la stessa matematica testata in test_ancore_core.c,
 * che riproduce prova_ancore.py).
 *
 * Creazione: [ancore N]
 *   - N: numero di parametri (coppie di ancore), default 1, max ANC_NPMAX.
 *
 * Inlet caldo (sinistro): una LISTA di 16 descrittori grezzi = il frame
 *   corrente. Fa scattare il calcolo ed emette una lista di N valori v.
 *   Il frame viene anche memorizzato come "ultimo", per i messaggi "impara".
 *
 * Messaggi (sull'inlet caldo):
 *   media <16 float>        taratura congelata: medie del corpus
 *   dev   <16 float>        taratura congelata: deviazioni del corpus
 *   piu  <k> <16 float>     ancora +1 del parametro k, da valori GREZZI
 *   meno <k> <16 float>     ancora -1 del parametro k, da valori GREZZI
 *   imparapiu  <k>          fotografa l'ultimo frame come ancora +1 di k
 *   imparameno <k>          fotografa l'ultimo frame come ancora -1 di k
 *   stampa                  stampa lo stato corrente in console
 *
 * L'ordine conta: prima "media" e "dev" (la conversione in z usa la taratura),
 * poi "piu"/"meno" o "impara*". L'uscita e' una lista di N float.
 */
#include "m_pd.h"
#include "ancore_core.h"

static t_class *ancore_class;

typedef struct _ancore {
    t_object  x_obj;
    anc_core  c;
    double    last[ANC_ND];   /* ultimo frame ricevuto (per "impara") */
    int       has_last;
    t_outlet *out;
} t_ancore;

/* copia n float da una lista di atomi (con offset) in dst; 0 se mancano */
static int leggi_n(int argc, t_atom *argv, int off, int n, double *dst) {
    int i;
    if (argc - off < n) return 0;
    for (i = 0; i < n; i++) dst[i] = (double)atom_getfloat(argv + off + i);
    return 1;
}

/* inlet caldo: lista di 16 descrittori -> calcola ed emette N valori v */
static void ancore_list(t_ancore *x, t_symbol *s, int argc, t_atom *argv) {
    double frame[ANC_ND], v[ANC_NPMAX];
    t_atom out[ANC_NPMAX];
    int i;
    (void)s;
    if (argc < ANC_ND) {
        pd_error(x, "ancore: servono %d descrittori, arrivati %d", ANC_ND, argc);
        return;
    }
    for (i = 0; i < ANC_ND; i++) frame[i] = (double)atom_getfloat(argv + i);
    for (i = 0; i < ANC_ND; i++) x->last[i] = frame[i];
    x->has_last = 1;
    anc_v(&x->c, frame, v);
    for (i = 0; i < x->c.np; i++) SETFLOAT(out + i, (t_float)v[i]);
    outlet_list(x->out, &s_list, x->c.np, out);
}

static void ancore_media(t_ancore *x, t_symbol *s, int argc, t_atom *argv) {
    double m[ANC_ND];
    int i;
    (void)s;
    if (!leggi_n(argc, argv, 0, ANC_ND, m)) {
        pd_error(x, "ancore: media vuole %d valori", ANC_ND);
        return;
    }
    for (i = 0; i < ANC_ND; i++) x->c.media[i] = m[i];
}

static void ancore_dev(t_ancore *x, t_symbol *s, int argc, t_atom *argv) {
    double d[ANC_ND];
    int i;
    (void)s;
    if (!leggi_n(argc, argv, 0, ANC_ND, d)) {
        pd_error(x, "ancore: dev vuole %d valori", ANC_ND);
        return;
    }
    for (i = 0; i < ANC_ND; i++) x->c.dev[i] = (d[i] > ANC_EPS) ? d[i] : 1.0;
}

static void ancore_piu(t_ancore *x, t_symbol *s, int argc, t_atom *argv) {
    double raw[ANC_ND];
    int k;
    (void)s;
    if (argc < 1) { pd_error(x, "ancore: piu vuole k + %d valori", ANC_ND); return; }
    k = (int)atom_getfloat(argv);
    if (!leggi_n(argc, argv, 1, ANC_ND, raw)) {
        pd_error(x, "ancore: piu vuole k + %d valori", ANC_ND);
        return;
    }
    if (k < 0 || k >= x->c.np) { pd_error(x, "ancore: parametro %d fuori range", k); return; }
    anc_set_piu_grezza(&x->c, k, raw);
}

static void ancore_meno(t_ancore *x, t_symbol *s, int argc, t_atom *argv) {
    double raw[ANC_ND];
    int k;
    (void)s;
    if (argc < 1) { pd_error(x, "ancore: meno vuole k + %d valori", ANC_ND); return; }
    k = (int)atom_getfloat(argv);
    if (!leggi_n(argc, argv, 1, ANC_ND, raw)) {
        pd_error(x, "ancore: meno vuole k + %d valori", ANC_ND);
        return;
    }
    if (k < 0 || k >= x->c.np) { pd_error(x, "ancore: parametro %d fuori range", k); return; }
    anc_set_meno_grezza(&x->c, k, raw);
}

static void ancore_imparapiu(t_ancore *x, t_floatarg fk) {
    int k = (int)fk;
    if (!x->has_last) { pd_error(x, "ancore: nessun frame da imparare"); return; }
    if (k < 0 || k >= x->c.np) { pd_error(x, "ancore: parametro %d fuori range", k); return; }
    anc_set_piu_grezza(&x->c, k, x->last);
}

static void ancore_imparameno(t_ancore *x, t_floatarg fk) {
    int k = (int)fk;
    if (!x->has_last) { pd_error(x, "ancore: nessun frame da imparare"); return; }
    if (k < 0 || k >= x->c.np) { pd_error(x, "ancore: parametro %d fuori range", k); return; }
    anc_set_meno_grezza(&x->c, k, x->last);
}

static void ancore_stampa(t_ancore *x) {
    int i, k;
    post("ancore: %d parametri, %d descrittori", x->c.np, x->c.nd);
    startpost("  media:");
    for (i = 0; i < x->c.nd; i++) startpost(" %.3g", x->c.media[i]);
    endpost();
    startpost("  dev:  ");
    for (i = 0; i < x->c.nd; i++) startpost(" %.3g", x->c.dev[i]);
    endpost();
    for (k = 0; k < x->c.np; k++) {
        startpost("  P+[%d] (z):", k);
        for (i = 0; i < x->c.nd; i++) startpost(" %.2f", x->c.pp[k][i]);
        endpost();
        startpost("  P-[%d] (z):", k);
        for (i = 0; i < x->c.nd; i++) startpost(" %.2f", x->c.pm[k][i]);
        endpost();
    }
}

static void *ancore_new(t_floatarg np) {
    t_ancore *x = (t_ancore *)pd_new(ancore_class);
    int n = (int)np;
    anc_init(&x->c, n);
    x->has_last = 0;
    x->out = outlet_new(&x->x_obj, &s_list);
    return (void *)x;
}

void ancore_setup(void) {
    ancore_class = class_new(gensym("ancore"),
                             (t_newmethod)ancore_new, 0,
                             sizeof(t_ancore), CLASS_DEFAULT, A_DEFFLOAT, 0);
    class_addlist(ancore_class, ancore_list);
    class_addmethod(ancore_class, (t_method)ancore_media, gensym("media"), A_GIMME, 0);
    class_addmethod(ancore_class, (t_method)ancore_dev, gensym("dev"), A_GIMME, 0);
    class_addmethod(ancore_class, (t_method)ancore_piu, gensym("piu"), A_GIMME, 0);
    class_addmethod(ancore_class, (t_method)ancore_meno, gensym("meno"), A_GIMME, 0);
    class_addmethod(ancore_class, (t_method)ancore_imparapiu, gensym("imparapiu"), A_DEFFLOAT, 0);
    class_addmethod(ancore_class, (t_method)ancore_imparameno, gensym("imparameno"), A_DEFFLOAT, 0);
    class_addmethod(ancore_class, (t_method)ancore_stampa, gensym("stampa"), 0);
}
