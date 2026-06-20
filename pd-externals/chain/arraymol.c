/* arraymol.c
 * Moltiplica due array elemento per elemento: result[k] = arr1[k] * arr2[k]
 *
 * Uso in Pd: [arraymol arr1 arr2 result]
 *   - arr1, arr2: array da moltiplicare
 *   - result:     array di destinazione
 *   - bang:       esegue il calcolo
 *
 * Esempio:
 *   arr1   = [2, 3, 4]
 *   arr2   = [2, 3, 4]
 *   result = [4, 9, 16]   ← quadrati
 *
 * Usato tipicamente per calcolare X[k]^2 (energia per bin spettrale),
 * passando lo stesso array spettrale come arr1 e arr2.
 */

#include "m_pd.h"

/* Puntatore globale alla classe */
static t_class *arraymol_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo. */
typedef struct _arraymol {
    t_object x_obj;
    t_symbol *nome_array1;
    t_symbol *nome_array2;
    t_symbol *nome_risultato;
} t_arraymol;

/* Funzione chiamata quando arriva un bang. */
void arraymol_bang(t_arraymol *x) {
    t_garray *a1, *a2, *aresult;

    a1      = (t_garray *)pd_findbyclass(x->nome_array1,    garray_class);
    a2      = (t_garray *)pd_findbyclass(x->nome_array2,    garray_class);
    aresult = (t_garray *)pd_findbyclass(x->nome_risultato, garray_class);

    if (!a1) {
        pd_error(x, "arraymol: array '%s' non trovato", x->nome_array1->s_name);
        return;
    }
    if (!a2) {
        pd_error(x, "arraymol: array '%s' non trovato", x->nome_array2->s_name);
        return;
    }
    if (!aresult) {
        pd_error(x, "arraymol: array '%s' non trovato", x->nome_risultato->s_name);
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
        vecresult[i].w_float = vec1[i].w_float * vec2[i].w_float;
    }

    garray_redraw(aresult);
}

/* Costruttore */
void *arraymol_new(t_symbol *arr1, t_symbol *arr2, t_symbol *result) {
    t_arraymol *x = (t_arraymol *)pd_new(arraymol_class);
    x->nome_array1    = arr1;
    x->nome_array2    = arr2;
    x->nome_risultato = result;
    return (void *)x;
}

/* Setup */
void arraymol_setup(void) {
    arraymol_class = class_new(
        gensym("arraymol"),
        (t_newmethod)arraymol_new,
        0,
        sizeof(t_arraymol),
        CLASS_DEFAULT,
        A_DEFSYMBOL,
        A_DEFSYMBOL,
        A_DEFSYMBOL,
        0);

    class_addbang(arraymol_class, arraymol_bang);
}
