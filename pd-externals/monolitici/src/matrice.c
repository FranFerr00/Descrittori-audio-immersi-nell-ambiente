/* matrice.c
 * Matrice di correlazione rolling generica: K serie temporali in ingresso,
 * scalari di sintesi configurabili in uscita (uno per outlet).
 *
 * Oggetto study-agnostico, da mettere in copia (una per famiglia di
 * descrittori, o per qualunque gruppo di serie da correlare). La matematica
 * vive in matrice_core.h, condivisa col test standalone test_matrice_core.c.
 *
 * Creazione: [matrice K (N) (D) (scalari...)]
 *   - K: numero di serie in ingresso (>= 2), obbligatorio. Crea K inlet:
 *        il sinistro (caldo) fa scattare il calcolo del frame, gli altri
 *        memorizzano l'ultimo valore ricevuto. Si collega un descrittore
 *        per inlet e si manda per ultimo quello dell'inlet caldo.
 *   - N, D: floats opzionali nell'ordine. N = finestra rolling
 *           (default max(16, 4*K)); D = lag per e1/e2 (default N/2).
 *   - scalari: parole che scelgono le uscite, nell'ordine dato. Se nessuna,
 *           default "c1" (una sola uscita). Disponibili:
 *             c1    coerenza media segnata    mean(r_ij)            [-1,+1]
 *             c2    concentrazione assiale    2|lam1|/sum|lam|-1    [-1,+1] (K>=3)
 *             c3    asimmetria di segno       (n+ - n-)/tot         [-1,+1]
 *             sigma dispersione               std(r_ij)            >= 0
 *             kurt  curtosi (Fisher) di r_ij                       reale
 *             polar polarizzazione            |C1|/mean|r|         [0,1]
 *             weak  frazione celle deboli     frac(|r| < 0.2)      [0,1]
 *             e1    velocita' di evoluzione   ||M(t)-M(t-D)||_F /  >= 0
 *                                               sqrt(K*(K-1))
 *             e2    coseno dei primi autov.   cos(v1(t),v1(t-D))   [-1,+1]
 *   Esempi:
 *     [matrice 4]                 -> 4 inlet, 1 uscita (c1), N=16, D=8
 *     [matrice 5 c1 e1]           -> 5 inlet, 2 uscite, N=20, D=10
 *     [matrice 3 32 16 c1 c2 c3]  -> 3 inlet, 3 uscite, N=32, D=16
 *
 * Ingressi:
 *   - inlet caldo (sinistro): un float = valore della 1a serie nel frame
 *     corrente; fa scattare il calcolo usando i valori memorizzati negli
 *     altri inlet. Accetta anche una lista di K float = frame completo
 *     (scorciatoia, ignora gli inlet freddi).
 *   - inlet freddi (1..K-1): memorizzano l'ultimo valore della rispettiva
 *     serie senza calcolare.
 *   [reset( (sull'inlet caldo): svuota finestra e storia.
 *   [N f( / [D f(: cambiano N o D a runtime (riallocano e azzerano la storia).
 *
 * Finche' la finestra non e' piena non si emette nulla; e1/e2 escono 0 finche'
 * non esiste una matrice di D frame fa. Uno scalare NaN non viene emesso.
 */

#include "m_pd.h"
#include <stdlib.h>
#include <string.h>
#include "matrice_core.h"

static t_class *matrice_class;

typedef struct _matrice {
    t_object  x_obj;
    int       K, N, D;

    double   *ring;         /* N*K ring buffer dei frame */
    int       head;
    long      count;

    double   *Mhist;        /* (D+1)*K*K */
    double   *Vhist;        /* (D+1)*K   */
    char     *Mvalid;       /* (D+1)     */
    int       hist_len;

    /* ingressi: in[0] = inlet caldo, in[1..K-1] = inlet freddi (memorizzati) */
    t_float  *in;

    /* buffer di lavoro per il core */
    double   *M, *v1, *colmean, *colstd, *A, *V, *w;
    char     *colok;
    double    sc[SC_NTYPES];

    int       n_out;
    int      *out_kind;
    t_outlet **outs;
} t_matrice;


/* Spinge il frame corrente (gia' in x->in[0..K-1]) nella finestra rolling,
 * calcola ed emette gli scalari scelti. */
static void matrice_process(t_matrice *x) {
    const int K = x->K;
    int i;

    for (i = 0; i < K; i++)
        x->ring[x->head * K + i] = (double)x->in[i];
    x->head = (x->head + 1) % x->N;
    x->count++;

    if (x->count < x->N) return;

    mat_scalars(x->ring, x->N, K, x->M, x->v1, x->sc,
                x->colmean, x->colstd, x->colok, x->A, x->V, x->w);

    int slot = (int)(x->count % x->hist_len);
    memcpy(x->Mhist + (size_t)slot * K * K, x->M, sizeof(double) * K * K);
    memcpy(x->Vhist + (size_t)slot * K, x->v1, sizeof(double) * K);
    x->Mvalid[slot] = 1;

    if (x->count - x->D >= x->N) {
        int pslot = (int)((x->count - x->D) % x->hist_len);
        if (x->Mvalid[pslot]) {
            x->sc[SC_E1] = mat_e1(x->M, x->Mhist + (size_t)pslot * K * K, K);
            x->sc[SC_E2] = mat_e2(x->v1, x->Vhist + (size_t)pslot * K, K);
        }
    } else {
        x->sc[SC_E1] = 0.0;
        x->sc[SC_E2] = 0.0;
    }

    /* emetti da destra a sinistra; salta i NaN */
    for (i = x->n_out - 1; i >= 0; i--) {
        double v = x->sc[x->out_kind[i]];
        if (!isnan(v)) outlet_float(x->outs[i], (t_float)v);
    }
}


/* float sull'inlet caldo: valore della 1a serie, fa scattare il frame. */
static void matrice_float(t_matrice *x, t_floatarg f) {
    x->in[0] = f;
    matrice_process(x);
}

/* lista sull'inlet caldo: frame completo (scorciatoia, ignora i freddi). */
static void matrice_list(t_matrice *x, t_symbol *s, int argc, t_atom *argv) {
    (void)s;
    int i;
    if (argc != x->K) {
        pd_error(x, "matrice: attesi %d valori, ricevuti %d", x->K, argc);
        return;
    }
    for (i = 0; i < x->K; i++)
        x->in[i] = atom_getfloat(argv + i);
    matrice_process(x);
}


static void matrice_reset(t_matrice *x) {
    x->head = 0;
    x->count = 0;
    memset(x->ring, 0, sizeof(double) * x->N * x->K);
    memset(x->Mvalid, 0, sizeof(char) * x->hist_len);
}

/* Rialloca i buffer che dipendono da N e D (ring e storia) e azzera lo stato.
 * Usata da matrice_setN / matrice_setD per il cambio a runtime. */
static void matrice_realloc(t_matrice *x) {
    const int K = x->K;
    free(x->ring);   free(x->Mhist);   free(x->Vhist);   free(x->Mvalid);
    x->ring   = (double *)calloc((size_t)x->N * K, sizeof(double));
    x->Mhist  = (double *)calloc((size_t)x->hist_len * K * K, sizeof(double));
    x->Vhist  = (double *)calloc((size_t)x->hist_len * K, sizeof(double));
    x->Mvalid = (char   *)calloc((size_t)x->hist_len, sizeof(char));
    if (!x->ring || !x->Mhist || !x->Vhist || !x->Mvalid)
        pd_error(x, "matrice: malloc fallita nel resize");
    x->head = 0;
    x->count = 0;
}

/* [N f(: cambia la finestra rolling a runtime (rialloca + reset). */
static void matrice_setN(t_matrice *x, t_floatarg f) {
    int N = (int)f;
    if (N < 2) { pd_error(x, "matrice: N deve essere >= 2"); return; }
    x->N = N;
    matrice_realloc(x);
    post("matrice: N=%d D=%d (storia azzerata)", x->N, x->D);
}

/* [D f(: cambia il lag di e1/e2 a runtime (rialloca + reset). */
static void matrice_setD(t_matrice *x, t_floatarg f) {
    int D = (int)f;
    if (D < 1) { pd_error(x, "matrice: D deve essere >= 1"); return; }
    x->D = D;
    x->hist_len = D + 1;
    matrice_realloc(x);
    post("matrice: N=%d D=%d (storia azzerata)", x->N, x->D);
}


static int sc_da_nome(const char *nome) {
    int i;
    for (i = 0; i < SC_NTYPES; i++)
        if (strcmp(nome, SC_NOMI[i]) == 0) return i;
    return -1;
}


static void *matrice_new(t_symbol *s, int argc, t_atom *argv) {
    (void)s;
    int K = -1, N = 0, D = 0, n_float = 0;
    int kinds[64], n_out = 0;
    int i;

    for (i = 0; i < argc; i++) {
        if (argv[i].a_type == A_FLOAT) {
            int v = (int)atom_getfloat(argv + i);
            if (n_float == 0) K = v;
            else if (n_float == 1) N = v;
            else if (n_float == 2) D = v;
            n_float++;
        } else if (argv[i].a_type == A_SYMBOL) {
            const char *nome = atom_getsymbol(argv + i)->s_name;
            int k = sc_da_nome(nome);
            if (k < 0) { post("matrice: scalare sconosciuto '%s' (ignorato)", nome); continue; }
            if (n_out < 64) kinds[n_out++] = k;
        }
    }

    if (K < 2) { post("matrice: serve K >= 2 come primo argomento"); return NULL; }
    if (N <= 0) N = (16 > 4 * K) ? 16 : 4 * K;
    if (N < 2) N = 2;
    if (D <= 0) D = N / 2;
    if (D < 1) D = 1;

    if (n_out == 0) { kinds[0] = SC_C1; n_out = 1; }  /* default: c1 */

    t_matrice *x = (t_matrice *)pd_new(matrice_class);
    x->K = K; x->N = N; x->D = D;
    x->head = 0; x->count = 0; x->hist_len = D + 1;
    x->n_out = n_out;

    x->ring    = (double *)calloc((size_t)N * K, sizeof(double));
    x->Mhist   = (double *)calloc((size_t)x->hist_len * K * K, sizeof(double));
    x->Vhist   = (double *)calloc((size_t)x->hist_len * K, sizeof(double));
    x->Mvalid  = (char   *)calloc((size_t)x->hist_len, sizeof(char));
    x->M       = (double *)calloc((size_t)K * K, sizeof(double));
    x->v1      = (double *)calloc((size_t)K, sizeof(double));
    x->colmean = (double *)calloc((size_t)K, sizeof(double));
    x->colstd  = (double *)calloc((size_t)K, sizeof(double));
    x->colok   = (char   *)calloc((size_t)K, sizeof(char));
    x->A       = (double *)calloc((size_t)K * K, sizeof(double));
    x->V       = (double *)calloc((size_t)K * K, sizeof(double));
    x->w       = (double *)calloc((size_t)K, sizeof(double));
    x->in      = (t_float *)calloc((size_t)K, sizeof(t_float));
    x->out_kind = (int *)calloc((size_t)n_out, sizeof(int));
    x->outs     = (t_outlet **)calloc((size_t)n_out, sizeof(t_outlet *));

    /* inlet freddi 1..K-1: memorizzano l'ultimo valore in x->in[j] */
    for (i = 1; i < K; i++)
        floatinlet_new(&x->x_obj, &x->in[i]);

    for (i = 0; i < n_out; i++) {
        x->out_kind[i] = kinds[i];
        x->outs[i] = outlet_new(&x->x_obj, &s_float);
    }

    post("matrice: K=%d N=%d D=%d, %d uscite", K, N, D, n_out);
    return (void *)x;
}


static void matrice_free(t_matrice *x) {
    free(x->ring);    free(x->Mhist);  free(x->Vhist);  free(x->Mvalid);
    free(x->M);       free(x->v1);     free(x->colmean); free(x->colstd);
    free(x->colok);   free(x->A);      free(x->V);      free(x->w);
    free(x->in);      free(x->out_kind); free(x->outs);
}


void matrice_setup(void) {
    matrice_class = class_new(
        gensym("matrice"),
        (t_newmethod)matrice_new,
        (t_method)matrice_free,
        sizeof(t_matrice),
        CLASS_DEFAULT,
        A_GIMME, 0);

    class_addfloat(matrice_class, matrice_float);
    class_addlist(matrice_class, matrice_list);
    class_addmethod(matrice_class, (t_method)matrice_reset, gensym("reset"), 0);
    class_addmethod(matrice_class, (t_method)matrice_setN, gensym("N"), A_FLOAT, 0);
    class_addmethod(matrice_class, (t_method)matrice_setD, gensym("D"), A_FLOAT, 0);
}
