/* arraysubnext_noabs.c
 * Calcola la differenza CON SEGNO tra elementi consecutivi di un array.
 *
 * Uso in Pd: [arraysubnext_noabs input result]
 *   - input:  array sorgente
 *   - result: array di destinazione
 *   - bang:   esegue il calcolo
 *
 * Formula: result[k] = input[k] - input[k+1]  per k = 0 .. N-2
 * A differenza di arraysubnext, NON applica il valore assoluto.
 * Il risultato può quindi essere negativo (se input[k] < input[k+1]).
 *
 * Esempio:
 *   input  = [3, 5, 2, 8]
 *   result = [-2, 3, -6, ?]   ← l'ultimo bin non viene toccato
 *
 * Variante di arraysubnext per situazioni in cui il segno della
 * differenza è informativo (ad esempio per rilevare pendenze
 * crescenti o decrescenti dello spettro).
 */

#include "m_pd.h"

/* Puntatore globale alla classe */
static t_class *arraysubnext_noabs_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo. */
typedef struct _arraysubnext_noabs {
    t_object x_obj;
    t_symbol *nome_array1;
    t_symbol *nome_risultato;
} t_arraysubnext_noabs;

/* Funzione chiamata quando arriva un bang. */
void arraysubnext_noabs_bang(t_arraysubnext_noabs *x) {
    t_garray *a1, *aresult;

    a1      = (t_garray *)pd_findbyclass(x->nome_array1,    garray_class);
    aresult = (t_garray *)pd_findbyclass(x->nome_risultato, garray_class);

    if (!a1) {
        pd_error(x, "arraysubnext_noabs: array '%s' non trovato", x->nome_array1->s_name);
        return;
    }
    if (!aresult) {
        pd_error(x, "arraysubnext_noabs: array '%s' non trovato", x->nome_risultato->s_name);
        return;
    }

    t_word *vec1, *vecresult;
    int size1, sizeresult;
    garray_getfloatwords(a1,      &size1,      &vec1);
    garray_getfloatwords(aresult, &sizeresult, &vecresult);

    if (size1 <= 1 || sizeresult <= 0) {
        pd_error(x, "arraysubnext_noabs: array troppo piccolo o vuoto");
        return;
    }

    /* Usa la dimensione minima; il ciclo si ferma a minsize-1
     * perché legge input[k+1] */
    int minsize = size1 < sizeresult ? size1 : sizeresult;

    int i;
    for (i = 0; i < minsize - 1; i++) {
        /* Differenza con segno: non si usa fabs() */
        vecresult[i].w_float = vec1[i].w_float - vec1[i+1].w_float;
    }

    garray_redraw(aresult);
}

/* Costruttore */
void *arraysubnext_noabs_new(t_symbol *arr1, t_symbol *result) {
    t_arraysubnext_noabs *x = (t_arraysubnext_noabs *)pd_new(arraysubnext_noabs_class);
    x->nome_array1    = arr1;
    x->nome_risultato = result;
    return (void *)x;
}

/* Setup */
void arraysubnext_noabs_setup(void) {
    arraysubnext_noabs_class = class_new(
        gensym("arraysubnext_noabs"),
        (t_newmethod)arraysubnext_noabs_new,
        0,
        sizeof(t_arraysubnext_noabs),
        CLASS_DEFAULT,
        A_DEFSYMBOL,
        A_DEFSYMBOL,
        0);

    class_addbang(arraysubnext_noabs_class, arraysubnext_noabs_bang);
}
