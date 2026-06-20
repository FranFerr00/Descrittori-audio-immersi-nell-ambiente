/* selettore.c
 * Selettore argmax con isteresi e tempo di permanenza, generico su N ingressi.
 *
 * Pensato per la mappatura al bicomb: riceve N grandezze (es. i C1 delle
 * famiglie di descrittori) e emette l'INDICE 0..N-1 di quella attualmente
 * dominante. L'indice puo' pilotare un selettore a N stati (es. la forma del
 * filtro). Study-agnostico: cosa rappresentino gli ingressi e l'uscita lo
 * decide il cablaggio.
 *
 * Creazione: [selettore N (margine) (dwell_ms) (finestra)]
 *   - N: numero di ingressi (>= 2, obbligatorio). Crea N inlet: il sinistro
 *        (caldo) fa scattare la valutazione, gli altri memorizzano.
 *   - margine: isteresi sul valore (default 0). Per cambiare vincente, il
 *        candidato deve superare il vincente attuale di almeno `margine`.
 *        Evita lo sfarfallio quando due ingressi sono quasi pari.
 *   - dwell_ms: tempo minimo di permanenza dopo un cambio (default 200 ms).
 *        Entro questo tempo l'uscita non cambia, anche se l'argmax cambia.
 *   - finestra: numero di frame su cui mediare ogni ingresso prima
 *        dell'argmax (default 1 = nessuna media). Liscia la decisione alla
 *        sorgente: l'argmax lavora sulla media mobile, non sull'ultimo frame.
 *
 * Ingressi:
 *   - inlet caldo (sinistro): un float = valore del 1o ingresso; fa scattare
 *     la valutazione usando i valori memorizzati negli altri inlet. Accetta
 *     anche una lista di N float = tutti gli ingressi insieme.
 *   - inlet freddi (1..N-1): memorizzano l'ultimo valore.
 *   [margine f( / [dwell f( / [finestra f(: cambiano i parametri a runtime.
 *   [reset(: torna allo stato "nessun vincente" (il prossimo frame sceglie
 *     liberamente, senza vincolo di dwell).
 *
 * Uscita: float, l'indice del vincente. Emesso solo quando l'indice CAMBIA
 *   (incluso il primo). Per riemetterlo a comando usare [bang(.
 */

#include "m_pd.h"
#include <stdlib.h>
#include <string.h>

static t_class *selettore_class;

typedef struct _selettore {
    t_object  x_obj;
    int       N;
    t_float   margine;
    t_float   dwell_ms;

    t_float  *in;        /* N: valori correnti (ultimo frame) degli ingressi */
    int       cur;       /* indice vincente attuale (-1 = nessuno) */
    double    t_switch;  /* tempo logico dell'ultimo cambio */

    int       W;         /* lunghezza finestra di media (>= 1) */
    t_float  *ring;      /* N*W: anelli di storia, uno per ingresso */
    int       pos;       /* posizione di scrittura nell'anello (0..W-1) */
    int       filled;    /* quanti frame validi finora (0..W) */

    t_outlet *out;
} t_selettore;


/* media corrente dell'ingresso i sui frame validi nell'anello */
static t_float selettore_media(t_selettore *x, int i) {
    int w, n = x->filled;
    double s = 0;
    if (n <= 0) return x->in[i];
    for (w = 0; w < n; w++) s += x->ring[i * x->W + w];
    return (t_float)(s / n);
}


static void selettore_eval(t_selettore *x) {
    const int N = x->N, W = x->W;
    int i, cand = 0;

    /* scrive il frame corrente nell'anello e calcola le medie mobili */
    for (i = 0; i < N; i++) x->ring[i * W + x->pos] = x->in[i];
    x->pos = (x->pos + 1) % W;
    if (x->filled < W) x->filled++;

    t_float v[N];
    for (i = 0; i < N; i++) v[i] = selettore_media(x, i);

    for (i = 1; i < N; i++)
        if (v[i] > v[cand]) cand = i;

    /* primo frame: nessun vincente ancora, scegli senza vincoli */
    if (x->cur < 0) {
        x->cur = cand;
        x->t_switch = clock_getlogicaltime();
        outlet_float(x->out, (t_float)x->cur);
        return;
    }

    if (cand == x->cur) return;   /* il vincente non cambia */

    /* isteresi: il candidato deve battere il vincente di almeno `margine` */
    if (v[cand] < v[x->cur] + x->margine) return;

    /* dwell: rispetta il tempo minimo di permanenza */
    if (clock_gettimesince(x->t_switch) < x->dwell_ms) return;

    x->cur = cand;
    x->t_switch = clock_getlogicaltime();
    outlet_float(x->out, (t_float)x->cur);
}


static void selettore_float(t_selettore *x, t_floatarg f) {
    x->in[0] = f;
    selettore_eval(x);
}

static void selettore_list(t_selettore *x, t_symbol *s, int argc, t_atom *argv) {
    (void)s;
    int i;
    if (argc != x->N) {
        pd_error(x, "selettore: attesi %d valori, ricevuti %d", x->N, argc);
        return;
    }
    for (i = 0; i < x->N; i++)
        x->in[i] = atom_getfloat(argv + i);
    selettore_eval(x);
}

/* riemette l'indice corrente senza rivalutare */
static void selettore_bang(t_selettore *x) {
    if (x->cur >= 0) outlet_float(x->out, (t_float)x->cur);
}

static void selettore_setmargine(t_selettore *x, t_floatarg f) {
    x->margine = (f < 0) ? 0 : f;
}

static void selettore_setdwell(t_selettore *x, t_floatarg f) {
    x->dwell_ms = (f < 0) ? 0 : f;
}

static void selettore_setfinestra(t_selettore *x, t_floatarg f) {
    int W = (int)f;
    if (W < 1) W = 1;
    if (W == x->W) return;
    t_float *r = (t_float *)calloc((size_t)(x->N * W), sizeof(t_float));
    if (!r) { pd_error(x, "selettore: realloc anello fallita"); return; }
    free(x->ring);
    x->ring = r;
    x->W = W;
    x->pos = 0;
    x->filled = 0;   /* riparte a riempire la nuova finestra */
}

static void selettore_reset(t_selettore *x) {
    x->cur = -1;
    x->pos = 0;
    x->filled = 0;
}


static void *selettore_new(t_symbol *s, int argc, t_atom *argv) {
    (void)s;
    int N = (argc > 0) ? (int)atom_getfloat(argv + 0) : 0;
    if (N < 2) { post("selettore: serve N >= 2 come primo argomento"); return NULL; }
    t_float margine = (argc > 1) ? atom_getfloat(argv + 1) : 0;
    t_float dwell   = (argc > 2) ? atom_getfloat(argv + 2) : 200;
    int     W       = (argc > 3) ? (int)atom_getfloat(argv + 3) : 1;
    if (margine < 0) margine = 0;
    if (dwell < 0) dwell = 0;
    if (W < 1) W = 1;

    t_selettore *x = (t_selettore *)pd_new(selettore_class);
    x->N = N;
    x->margine = margine;
    x->dwell_ms = dwell;
    x->cur = -1;
    x->t_switch = clock_getlogicaltime();
    x->W = W;
    x->pos = 0;
    x->filled = 0;
    x->in = (t_float *)calloc((size_t)N, sizeof(t_float));
    x->ring = (t_float *)calloc((size_t)(N * W), sizeof(t_float));
    if (!x->in || !x->ring) pd_error(x, "selettore: malloc fallita");

    int i;
    for (i = 1; i < N; i++)
        floatinlet_new(&x->x_obj, &x->in[i]);
    x->out = outlet_new(&x->x_obj, &s_float);

    post("selettore: N=%d margine=%g dwell=%g ms finestra=%d", N, margine, dwell, W);
    return (void *)x;
}

static void selettore_free(t_selettore *x) {
    free(x->in);
    free(x->ring);
}


void selettore_setup(void) {
    selettore_class = class_new(
        gensym("selettore"),
        (t_newmethod)selettore_new,
        (t_method)selettore_free,
        sizeof(t_selettore),
        CLASS_DEFAULT,
        A_GIMME, 0);

    class_addfloat(selettore_class, selettore_float);
    class_addlist(selettore_class, selettore_list);
    class_addbang(selettore_class, selettore_bang);
    class_addmethod(selettore_class, (t_method)selettore_setmargine, gensym("margine"), A_FLOAT, 0);
    class_addmethod(selettore_class, (t_method)selettore_setdwell, gensym("dwell"), A_FLOAT, 0);
    class_addmethod(selettore_class, (t_method)selettore_setfinestra, gensym("finestra"), A_FLOAT, 0);
    class_addmethod(selettore_class, (t_method)selettore_reset, gensym("reset"), 0);
}
