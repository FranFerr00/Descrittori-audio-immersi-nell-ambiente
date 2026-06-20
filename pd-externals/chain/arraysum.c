/* arraysum.c
 * Somma due array elemento per elemento.
 *
 * Uso in Pd: [arraysum arr1 arr2 result]
 *   - arr1, arr2: array da sommare
 *   - result:     array di destinazione
 *   - bang:       esegue il calcolo
 *
 * Esempio:
 *   arr1   = [1, 2, 3]
 *   arr2   = [4, 5, 6]
 *   result = [5, 7, 9]
 *
 * Usato ad esempio per combinare contributi spettrali di due sorgenti.
 */

#include "m_pd.h"

/* Puntatore globale alla classe — richiesto da Pd per registrare l'oggetto */
static t_class *arraysum_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo. */
typedef struct _arraysum {
    t_object x_obj;
    t_symbol *nome_array1;
    t_symbol *nome_array2;
    t_symbol *nome_risultato;
} t_arraysum;

/* Funzione chiamata quando arriva un bang. */
void arraysum_bang(t_arraysum *x) {
    t_garray *a1, *a2, *aresult;

    /* Cerca gli array per nome nel namespace globale di Pd */
    a1      = (t_garray *)pd_findbyclass(x->nome_array1,    garray_class);
    a2      = (t_garray *)pd_findbyclass(x->nome_array2,    garray_class);
    aresult = (t_garray *)pd_findbyclass(x->nome_risultato, garray_class);

    if (!a1) {
        pd_error(x, "arraysum: array '%s' non trovato", x->nome_array1->s_name);
        return;
    }
    if (!a2) {
        pd_error(x, "arraysum: array '%s' non trovato", x->nome_array2->s_name);
        return;
    }
    if (!aresult) {
        pd_error(x, "arraysum: array '%s' non trovato", x->nome_risultato->s_name);
        return;
    }

    /* Ottieni puntatori ai dati e dimensioni.
     * t_word è il tipo base; il valore float si legge con .w_float */
    t_word *vec1, *vec2, *vecresult;
    int size1, size2, sizeresult;
    garray_getfloatwords(a1,      &size1,      &vec1);
    garray_getfloatwords(a2,      &size2,      &vec2);
    garray_getfloatwords(aresult, &sizeresult, &vecresult);

    /* Usa la dimensione minima tra i tre array per non sforare i bordi */
    int minsize = size1;
    if (size2      < minsize) minsize = size2;
    if (sizeresult < minsize) minsize = sizeresult;

    int i;
    for (i = 0; i < minsize; i++) {
        vecresult[i].w_float = vec1[i].w_float + vec2[i].w_float;
    }

    /* Ridisegna solo l'array di output */
    garray_redraw(aresult);
}

/* Costruttore: riceve i tre nomi di array come argomenti simbolici. */
void *arraysum_new(t_symbol *arr1, t_symbol *arr2, t_symbol *result) {
    t_arraysum *x = (t_arraysum *)pd_new(arraysum_class);
    x->nome_array1    = arr1;
    x->nome_array2    = arr2;
    x->nome_risultato = result;
    return (void *)x;
}

/* Setup: registra la classe in Pd. Chiamato una sola volta al caricamento. */
void arraysum_setup(void) {
    arraysum_class = class_new(
        gensym("arraysum"),
        (t_newmethod)arraysum_new,
        0,                      /* nessun destructor: niente malloc */
        sizeof(t_arraysum),
        CLASS_DEFAULT,
        A_DEFSYMBOL,            /* primo array */
        A_DEFSYMBOL,            /* secondo array */
        A_DEFSYMBOL,            /* array risultato */
        0);

    class_addbang(arraysum_class, arraysum_bang);
}
