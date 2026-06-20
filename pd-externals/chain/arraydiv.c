/* arraydiv.c
 * Divide due array elemento per elemento: result[k] = arr1[k] / arr2[k]
 *
 * Uso in Pd: [arraydiv arr1 arr2 result]
 *   - arr1:   dividendo
 *   - arr2:   divisore
 *   - result: array di destinazione
 *   - bang:   esegue il calcolo
 *
 * Gestione divisione per zero: se arr2[k] == 0, result[k] = 0.
 * Questa scelta è conservativa: non produce NaN o infinito che
 * potrebbero propagarsi nei calcoli successivi nella patch.
 *
 * Usato ad esempio per normalizzare uno spettro rispetto a un riferimento.
 */

#include "m_pd.h"

/* Puntatore globale alla classe */
static t_class *arraydiv_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo. */
typedef struct _arraydiv {
    t_object x_obj;
    t_symbol *nome_array1;
    t_symbol *nome_array2;
    t_symbol *nome_risultato;
} t_arraydiv;

/* Funzione chiamata quando arriva un bang. */
void arraydiv_bang(t_arraydiv *x) {
    t_garray *a1, *a2, *aresult;

    a1      = (t_garray *)pd_findbyclass(x->nome_array1,    garray_class);
    a2      = (t_garray *)pd_findbyclass(x->nome_array2,    garray_class);
    aresult = (t_garray *)pd_findbyclass(x->nome_risultato, garray_class);

    if (!a1) {
        pd_error(x, "arraydiv: array '%s' non trovato", x->nome_array1->s_name);
        return;
    }
    if (!a2) {
        pd_error(x, "arraydiv: array '%s' non trovato", x->nome_array2->s_name);
        return;
    }
    if (!aresult) {
        pd_error(x, "arraydiv: array '%s' non trovato", x->nome_risultato->s_name);
        return;
    }

    t_word *vec1, *vec2, *vecresult;
    int size1, size2, sizeresult;
    garray_getfloatwords(a1,      &size1,      &vec1);
    garray_getfloatwords(a2,      &size2,      &vec2);
    garray_getfloatwords(aresult, &sizeresult, &vecresult);

    /* Usa la dimensione minima tra i tre array */
    int minsize = size1;
    if (size2      < minsize) minsize = size2;
    if (sizeresult < minsize) minsize = sizeresult;

    int i;
    for (i = 0; i < minsize; i++) {
        if (vec2[i].w_float == 0.0) {
            /* Divisione per zero: il risultato è 0 per convenzione */
            vecresult[i].w_float = 0.0;
        } else {
            vecresult[i].w_float = vec1[i].w_float / vec2[i].w_float;
        }
    }

    garray_redraw(aresult);
}

/* Costruttore */
void *arraydiv_new(t_symbol *arr1, t_symbol *arr2, t_symbol *result) {
    t_arraydiv *x = (t_arraydiv *)pd_new(arraydiv_class);
    x->nome_array1    = arr1;
    x->nome_array2    = arr2;
    x->nome_risultato = result;
    return (void *)x;
}

/* Setup */
void arraydiv_setup(void) {
    arraydiv_class = class_new(
        gensym("arraydiv"),
        (t_newmethod)arraydiv_new,
        0,
        sizeof(t_arraydiv),
        CLASS_DEFAULT,
        A_DEFSYMBOL,
        A_DEFSYMBOL,
        A_DEFSYMBOL,
        0);

    class_addbang(arraydiv_class, arraydiv_bang);
}
