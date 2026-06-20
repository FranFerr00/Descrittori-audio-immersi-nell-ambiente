/* arraysubnext2.c
 * Alias di arraysubnext: differenza assoluta tra elementi consecutivi.
 *
 * Uso in Pd: [arraysubnext2 input result]
 *   - input:  array sorgente
 *   - result: array di destinazione
 *   - bang:   esegue il calcolo
 *
 * Formula: result[k] = |input[k] - input[k+1]|  per k = 0 .. N-2
 *
 * Questo external è identico a arraysubnext.
 * Esiste come copia separata per compatibilità con patch che lo usano
 * già per nome. Da valutare se unificare i due in futuro.
 *
 * Vedi arraysubnext.c per una descrizione completa del comportamento.
 */

#include "m_pd.h"
#include <math.h>

/* Puntatore globale alla classe */
static t_class *arraysubnext2_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo. */
typedef struct _arraysubnext2 {
    t_object x_obj;
    t_symbol *nome_array1;
    t_symbol *nome_risultato;
} t_arraysubnext2;

/* Funzione chiamata quando arriva un bang. */
void arraysubnext2_bang(t_arraysubnext2 *x) {
    t_garray *a1, *aresult;

    a1      = (t_garray *)pd_findbyclass(x->nome_array1,    garray_class);
    aresult = (t_garray *)pd_findbyclass(x->nome_risultato, garray_class);

    if (!a1) {
        pd_error(x, "arraysubnext2: array '%s' non trovato", x->nome_array1->s_name);
        return;
    }
    if (!aresult) {
        pd_error(x, "arraysubnext2: array '%s' non trovato", x->nome_risultato->s_name);
        return;
    }

    t_word *vec1, *vecresult;
    int size1, sizeresult;
    garray_getfloatwords(a1,      &size1,      &vec1);
    garray_getfloatwords(aresult, &sizeresult, &vecresult);

    /* Usa la dimensione minima; il ciclo si ferma a minsize-1
     * perché legge input[k+1] */
    int minsize = size1 < sizeresult ? size1 : sizeresult;

    int i;
    for (i = 0; i < minsize - 1; i++) {
        vecresult[i].w_float = fabs(vec1[i].w_float - vec1[i+1].w_float);
    }

    garray_redraw(aresult);
}

/* Costruttore */
void *arraysubnext2_new(t_symbol *arr1, t_symbol *result) {
    t_arraysubnext2 *x = (t_arraysubnext2 *)pd_new(arraysubnext2_class);
    x->nome_array1    = arr1;
    x->nome_risultato = result;
    return (void *)x;
}

/* Setup */
void arraysubnext2_setup(void) {
    arraysubnext2_class = class_new(
        gensym("arraysubnext2"),
        (t_newmethod)arraysubnext2_new,
        0,
        sizeof(t_arraysubnext2),
        CLASS_DEFAULT,
        A_DEFSYMBOL,
        A_DEFSYMBOL,
        0);

    class_addbang(arraysubnext2_class, arraysubnext2_bang);
}
