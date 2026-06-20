/* arrayabs.c
 * Calcola il valore assoluto di ogni elemento di un array.
 *
 * Uso in Pd: [arrayabs input result]
 *   - input:  array sorgente (può contenere valori negativi)
 *   - result: array di destinazione
 *   - bang:   esegue il calcolo
 *
 * Esempio:
 *   input  = [-3, 1, -2, 4]
 *   result = [ 3, 1,  2, 4]
 *
 * Usa fabs() dalla libreria math.h, che opera su double e restituisce
 * il risultato corretto anche per -0.0 e valori denormalizzati.
 */

#include "m_pd.h"
#include <math.h>

/* Puntatore globale alla classe */
static t_class *arrayabs_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo. */
typedef struct _arrayabs {
    t_object x_obj;
    t_symbol *nome_array;
    t_symbol *nome_risultato;
} t_arrayabs;

/* Funzione chiamata quando arriva un bang. */
void arrayabs_bang(t_arrayabs *x) {
    t_garray *a1, *aresult;

    a1      = (t_garray *)pd_findbyclass(x->nome_array,     garray_class);
    aresult = (t_garray *)pd_findbyclass(x->nome_risultato, garray_class);

    if (!a1) {
        pd_error(x, "arrayabs: array '%s' non trovato", x->nome_array->s_name);
        return;
    }
    if (!aresult) {
        pd_error(x, "arrayabs: array '%s' non trovato", x->nome_risultato->s_name);
        return;
    }

    t_word *vec1, *vecresult;
    int size1, sizeresult;
    garray_getfloatwords(a1,      &size1,      &vec1);
    garray_getfloatwords(aresult, &sizeresult, &vecresult);

    if (size1 <= 0 || sizeresult <= 0) {
        pd_error(x, "arrayabs: array vuoto o non valido");
        return;
    }

    /* Usa la dimensione minima tra i due array */
    int minsize = size1 < sizeresult ? size1 : sizeresult;

    int i;
    for (i = 0; i < minsize; i++) {
        vecresult[i].w_float = fabs(vec1[i].w_float);
    }

    garray_redraw(aresult);
}

/* Costruttore */
void *arrayabs_new(t_symbol *arr, t_symbol *result) {
    t_arrayabs *x = (t_arrayabs *)pd_new(arrayabs_class);
    x->nome_array     = arr;
    x->nome_risultato = result;
    return (void *)x;
}

/* Setup */
void arrayabs_setup(void) {
    arrayabs_class = class_new(
        gensym("arrayabs"),
        (t_newmethod)arrayabs_new,
        0,
        sizeof(t_arrayabs),
        CLASS_DEFAULT,
        A_DEFSYMBOL,
        A_DEFSYMBOL,
        0);

    class_addbang(arrayabs_class, arrayabs_bang);
}
