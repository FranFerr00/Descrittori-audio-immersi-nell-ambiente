/* arraymax.c
 * Trova il valore massimo di un array ed emette un float dall'outlet.
 *
 * Uso in Pd: [arraymax array]
 *   - array:  nome dell'array da analizzare
 *   - bang:   esegue la ricerca
 *   - outlet: float, valore massimo trovato
 *
 * Esempio:
 *   array  = [0.1, 0.8, 0.3, 0.5]
 *   outlet = 0.8
 *
 * Pattern di RIDUZIONE (array → float): diverso dai soliti
 * external di questo toolkit che operano array → array.
 * Tecnicamente: invece di scrivere i risultati in un altro array
 * con garray_redraw, si emette un singolo float con outlet_float().
 *
 * Usato per costruire la soglia relativa del centroide (e di altri
 * descrittori): soglia = peak × 10^(-30/20). Il peak è quello che
 * calcola questo external; la moltiplicazione per il fattore dB
 * si fa con un comune [* 0.0316] nella patch.
 */

#include "m_pd.h"

/* Puntatore globale alla classe */
static t_class *arraymax_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo.
 * x_out è l'outlet float da cui viene emesso il massimo. */
typedef struct _arraymax {
    t_object  x_obj;
    t_symbol *nome_array;
    t_outlet *x_out;
} t_arraymax;

/* Funzione chiamata quando arriva un bang. */
void arraymax_bang(t_arraymax *x) {
    t_garray *a1;

    a1 = (t_garray *)pd_findbyclass(x->nome_array, garray_class);
    if (!a1) {
        pd_error(x, "arraymax: array '%s' non trovato", x->nome_array->s_name);
        return;
    }

    t_word *vec;
    int size;
    garray_getfloatwords(a1, &size, &vec);

    if (size <= 0) {
        pd_error(x, "arraymax: array vuoto");
        return;
    }

    /* Inizializza il massimo col primo elemento.
     * Non si usa 0 come valore iniziale perché un array di valori
     * tutti negativi darebbe erroneamente massimo = 0. */
    t_float massimo = vec[0].w_float;

    /* Scorre l'array a partire dal secondo elemento */
    int i;
    for (i = 1; i < size; i++) {
        if (vec[i].w_float > massimo) {
            massimo = vec[i].w_float;
        }
    }

    /* Emette il risultato dall'outlet come float */
    outlet_float(x->x_out, massimo);
}

/* Costruttore: riceve un solo argomento, il nome dell'array. */
void *arraymax_new(t_symbol *arr) {
    t_arraymax *x = (t_arraymax *)pd_new(arraymax_class);
    x->nome_array = arr;

    /* Crea l'outlet float. &s_float indica il tipo di messaggio
     * che l'outlet trasmette (qui: float). */
    x->x_out = outlet_new(&x->x_obj, &s_float);

    return (void *)x;
}

/* Setup */
void arraymax_setup(void) {
    arraymax_class = class_new(
        gensym("arraymax"),
        (t_newmethod)arraymax_new,
        0,
        sizeof(t_arraymax),
        CLASS_DEFAULT,
        A_DEFSYMBOL,    /* nome array */
        0);

    class_addbang(arraymax_class, arraymax_bang);
}
