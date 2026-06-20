/* arraymolscalar.c
 * Moltiplica ogni elemento di un array per un valore scalare.
 *
 * Uso in Pd: [arraymolscalar input result scalare]
 *   - input:   array sorgente
 *   - result:  array di destinazione
 *   - scalare: valore float (argomento opzionale, default 0)
 *   - bang:    esegue il calcolo
 *
 * Lo scalare può essere aggiornato in tempo reale tramite l'inlet
 * passivo (il secondo inlet dell'oggetto).
 *
 * Esempio con scalare = 0.85:
 *   input  = [10, 20, 30]
 *   result = [8.5, 17, 25.5]
 *
 * Usato ad esempio per scalare l'energia totale dello spettro
 * dell'85% nel calcolo del rolloff spettrale.
 */

#include "m_pd.h"

/* Puntatore globale alla classe */
static t_class *arraymolscalar_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo.
 * valore_scalare è un t_float per poter essere collegato
 * direttamente a floatinlet_new(). */
typedef struct _arraymolscalar {
    t_object x_obj;
    t_symbol *nome_array;
    t_symbol *nome_risultato;
    t_float   valore_scalare;
} t_arraymolscalar;

/* Funzione chiamata quando arriva un bang. */
void arraymolscalar_bang(t_arraymolscalar *x) {
    t_garray *a1, *aresult;

    a1      = (t_garray *)pd_findbyclass(x->nome_array,     garray_class);
    aresult = (t_garray *)pd_findbyclass(x->nome_risultato, garray_class);

    if (!a1) {
        pd_error(x, "arraymolscalar: array '%s' non trovato", x->nome_array->s_name);
        return;
    }
    if (!aresult) {
        pd_error(x, "arraymolscalar: array '%s' non trovato", x->nome_risultato->s_name);
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
        vecresult[i].w_float = vec1[i].w_float * x->valore_scalare;
    }

    garray_redraw(aresult);
}

/* Costruttore: i primi due argomenti sono nomi di array (simboli),
 * il terzo è il valore scalare iniziale (float). */
void *arraymolscalar_new(t_symbol *arr, t_symbol *result, t_floatarg f) {
    t_arraymolscalar *x = (t_arraymolscalar *)pd_new(arraymolscalar_class);
    x->nome_array     = arr;
    x->nome_risultato = result;
    x->valore_scalare = f;

    /* Inlet passivo: un float mandato al secondo inlet aggiorna
     * direttamente x->valore_scalare senza bisogno di una funzione dedicata */
    floatinlet_new(&x->x_obj, &x->valore_scalare);

    return (void *)x;
}

/* Setup */
void arraymolscalar_setup(void) {
    arraymolscalar_class = class_new(
        gensym("arraymolscalar"),
        (t_newmethod)arraymolscalar_new,
        0,
        sizeof(t_arraymolscalar),
        CLASS_DEFAULT,
        A_DEFSYMBOL,    /* array input */
        A_DEFSYMBOL,    /* array output */
        A_DEFFLOAT,     /* valore scalare (default 0) */
        0);

    class_addbang(arraymolscalar_class, arraymolscalar_bang);
}
