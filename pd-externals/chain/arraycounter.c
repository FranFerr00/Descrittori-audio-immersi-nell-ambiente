/* arraycounter.c
 * Riempie un array con un contatore intero: [0, 1, 2, 3, ..., N-1]
 *
 * Uso in Pd: [arraycounter result]
 *   - result: array da riempire
 *   - bang:   esegue il riempimento
 *
 * Esempio con array di 5 elementi:
 *   result = [0, 1, 2, 3, 4]
 *
 * Usato per costruire l'array degli indici di frequenza k,
 * necessario per calcolare il centroide spettrale e lo spread:
 *   centroid = sum(k * X[k]) / sum(X[k])
 * dove k è l'indice del bin (0, 1, 2, ... N/2).
 * Per ottenere la frequenza in Hz: f = k * sr / fftsize
 */

#include "m_pd.h"

/* Puntatore globale alla classe */
static t_class *arraycounter_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo. */
typedef struct _arraycounter {
    t_object x_obj;
    t_symbol *nome_risultato;
} t_arraycounter;

/* Funzione chiamata quando arriva un bang. */
void arraycounter_bang(t_arraycounter *x) {
    t_garray *aresult;

    aresult = (t_garray *)pd_findbyclass(x->nome_risultato, garray_class);

    if (!aresult) {
        pd_error(x, "arraycounter: array '%s' non trovato", x->nome_risultato->s_name);
        return;
    }

    t_word *vecresult;
    int sizeresult;
    garray_getfloatwords(aresult, &sizeresult, &vecresult);

    if (sizeresult <= 0) {
        pd_error(x, "arraycounter: array vuoto");
        return;
    }

    /* Riempie con i[k] = k: ogni cella riceve il suo indice */
    int i;
    for (i = 0; i < sizeresult; i++) {
        vecresult[i].w_float = (float)i;
    }

    garray_redraw(aresult);
}

/* Costruttore: riceve un solo argomento, il nome dell'array da riempire. */
void *arraycounter_new(t_symbol *result) {
    t_arraycounter *x = (t_arraycounter *)pd_new(arraycounter_class);
    x->nome_risultato = result;
    return (void *)x;
}

/* Setup */
void arraycounter_setup(void) {
    arraycounter_class = class_new(
        gensym("arraycounter"),
        (t_newmethod)arraycounter_new,
        0,
        sizeof(t_arraycounter),
        CLASS_DEFAULT,
        A_DEFSYMBOL,    /* nome array da riempire */
        0);

    class_addbang(arraycounter_class, arraycounter_bang);
}
