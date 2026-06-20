/* arraysubnext.c
 * Calcola la differenza assoluta tra elementi consecutivi di un array.
 *
 * Uso in Pd: [arraysubnext input result]
 *   - input:  array sorgente
 *   - result: array di destinazione (deve avere almeno N-1 elementi)
 *   - bang:   esegue il calcolo
 *
 * Formula: result[k] = |input[k] - input[k+1]|  per k = 0 .. N-2
 * L'ultimo elemento di result non viene scritto (il confronto si fa
 * sempre tra coppie adiacenti, quindi si producono N-1 valori).
 *
 * Esempio:
 *   input  = [3, 1, 4, 1, 5]
 *   result = [2, 3, 3, 4, ?]   ← l'ultimo bin non viene toccato
 *
 * Usato per l'irregolarità spettrale: misura quanto lo spettro
 * varia da un bin al successivo. Un suono sinusoidale ha pochi bin
 * attivi e grandi salti, quindi alta irregolarità; un rumore bianco
 * ha una distribuzione uniforme e bassa irregolarità.
 */

#include "m_pd.h"
#include <math.h>

/* Puntatore globale alla classe */
static t_class *arraysubnext_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo. */
typedef struct _arraysubnext {
    t_object x_obj;
    t_symbol *nome_array1;
    t_symbol *nome_risultato;
} t_arraysubnext;

/* Funzione chiamata quando arriva un bang. */
void arraysubnext_bang(t_arraysubnext *x) {
    t_garray *a1, *aresult;

    a1      = (t_garray *)pd_findbyclass(x->nome_array1,    garray_class);
    aresult = (t_garray *)pd_findbyclass(x->nome_risultato, garray_class);

    if (!a1) {
        pd_error(x, "arraysubnext: array '%s' non trovato", x->nome_array1->s_name);
        return;
    }
    if (!aresult) {
        pd_error(x, "arraysubnext: array '%s' non trovato", x->nome_risultato->s_name);
        return;
    }

    t_word *vec1, *vecresult;
    int size1, sizeresult;
    garray_getfloatwords(a1,      &size1,      &vec1);
    garray_getfloatwords(aresult, &sizeresult, &vecresult);

    /* Usa la dimensione minima tra i due array.
     * Il ciclo arriva solo fino a minsize-1 perché legge input[k+1]. */
    int minsize = size1 < sizeresult ? size1 : sizeresult;

    int i;
    for (i = 0; i < minsize - 1; i++) {
        vecresult[i].w_float = fabs(vec1[i].w_float - vec1[i+1].w_float);
    }

    garray_redraw(aresult);
}

/* Costruttore */
void *arraysubnext_new(t_symbol *arr1, t_symbol *result) {
    t_arraysubnext *x = (t_arraysubnext *)pd_new(arraysubnext_class);
    x->nome_array1    = arr1;
    x->nome_risultato = result;
    return (void *)x;
}

/* Setup */
void arraysubnext_setup(void) {
    arraysubnext_class = class_new(
        gensym("arraysubnext"),
        (t_newmethod)arraysubnext_new,
        0,
        sizeof(t_arraysubnext),
        CLASS_DEFAULT,
        A_DEFSYMBOL,
        A_DEFSYMBOL,
        0);

    class_addbang(arraysubnext_class, arraysubnext_bang);
}
