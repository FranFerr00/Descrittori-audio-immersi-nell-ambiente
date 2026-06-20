/* arraysubscalar.c
 * Sottrae un valore scalare a ogni elemento di un array.
 *
 * Uso in Pd: [arraysubscalar input result scalare]
 *   - input:   array sorgente
 *   - result:  array di destinazione
 *   - scalare: valore float da sottrarre (argomento opzionale, default 0)
 *   - bang:    esegue il calcolo
 *
 * Lo scalare può essere aggiornato in tempo reale tramite l'inlet
 * passivo (il secondo inlet dell'oggetto).
 *
 * Esempio con scalare = 2:
 *   input  = [5, 3, 8]
 *   result = [3, 1, 6]
 *
 * Usato ad esempio per centrare un array rispetto alla sua media
 * (sottraendo il centroide) nel calcolo dello spread spettrale.
 */

#include "m_pd.h"

/* Puntatore globale alla classe */
static t_class *arraysubscalar_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo. */
typedef struct _arraysubscalar {
    t_object x_obj;
    t_symbol *nome_array;
    t_symbol *nome_risultato;
    t_float   valore_scalare;
} t_arraysubscalar;

/* Funzione chiamata quando arriva un bang. */
void arraysubscalar_bang(t_arraysubscalar *x) {
    t_garray *a1, *aresult;

    a1      = (t_garray *)pd_findbyclass(x->nome_array,     garray_class);
    aresult = (t_garray *)pd_findbyclass(x->nome_risultato, garray_class);

    if (!a1) {
        pd_error(x, "arraysubscalar: array '%s' non trovato", x->nome_array->s_name);
        return;
    }
    if (!aresult) {
        pd_error(x, "arraysubscalar: array '%s' non trovato", x->nome_risultato->s_name);
        return;
    }

    t_word *vec1, *vecresult;
    int size1, sizeresult;
    garray_getfloatwords(a1,      &size1,      &vec1);
    garray_getfloatwords(aresult, &sizeresult, &vecresult);

    /* Usa la dimensione minima tra i due array */
    int minsize = size1 < sizeresult ? size1 : sizeresult;

    int i;
    for (i = 0; i < minsize; i++) {
        vecresult[i].w_float = vec1[i].w_float - x->valore_scalare;
    }

    garray_redraw(aresult);
}

/* Costruttore */
void *arraysubscalar_new(t_symbol *arr, t_symbol *result, t_floatarg f) {
    t_arraysubscalar *x = (t_arraysubscalar *)pd_new(arraysubscalar_class);
    x->nome_array     = arr;
    x->nome_risultato = result;
    x->valore_scalare = f;

    /* Inlet passivo: aggiorna x->valore_scalare direttamente */
    floatinlet_new(&x->x_obj, &x->valore_scalare);

    return (void *)x;
}

/* Setup */
void arraysubscalar_setup(void) {
    arraysubscalar_class = class_new(
        gensym("arraysubscalar"),
        (t_newmethod)arraysubscalar_new,
        0,
        sizeof(t_arraysubscalar),
        CLASS_DEFAULT,
        A_DEFSYMBOL,    /* array input */
        A_DEFSYMBOL,    /* array output */
        A_DEFFLOAT,     /* valore scalare (default 0) */
        0);

    class_addbang(arraysubscalar_class, arraysubscalar_bang);
}
