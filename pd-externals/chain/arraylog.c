/* arraylog.c
 * Calcola il logaritmo naturale di ogni elemento di un array.
 *
 * Uso in Pd: [arraylog input result]
 *   - input:  array sorgente
 *   - result: array di destinazione
 *   - bang:   esegue il calcolo
 *
 * Gestione valori non positivi: se input[k] <= 0, si usa log(1e-7) ≈ -16.1
 * invece di -inf o NaN. Questa soglia corrisponde a un segnale circa 140 dB
 * sotto il massimo, sufficiente per qualsiasi uso pratico con audio.
 *
 * Usato ad esempio per calcolare la flatness spettrale (rapporto
 * media geometrica / media aritmetica, dove la media geometrica si
 * calcola come exp(mean(log(X)))).
 */

#include "m_pd.h"
#include <math.h>

/* Puntatore globale alla classe */
static t_class *arraylog_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo. */
typedef struct _arraylog {
    t_object x_obj;
    t_symbol *nome_array1;
    t_symbol *nome_risultato;
} t_arraylog;

/* Funzione chiamata quando arriva un bang. */
void arraylog_bang(t_arraylog *x) {
    t_garray *a1, *aresult;

    a1      = (t_garray *)pd_findbyclass(x->nome_array1,    garray_class);
    aresult = (t_garray *)pd_findbyclass(x->nome_risultato, garray_class);

    if (!a1) {
        pd_error(x, "arraylog: array '%s' non trovato", x->nome_array1->s_name);
        return;
    }
    if (!aresult) {
        pd_error(x, "arraylog: array '%s' non trovato", x->nome_risultato->s_name);
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
        if (vec1[i].w_float <= 0.0) {
            /* Valore non positivo: log non è definito.
             * Si usa un valore molto piccolo (≈ -140 dB) come pavimento. */
            vecresult[i].w_float = log(1e-7);
        } else {
            vecresult[i].w_float = log(vec1[i].w_float);
        }
    }

    garray_redraw(aresult);
}

/* Costruttore */
void *arraylog_new(t_symbol *arr1, t_symbol *result) {
    t_arraylog *x = (t_arraylog *)pd_new(arraylog_class);
    x->nome_array1    = arr1;
    x->nome_risultato = result;
    return (void *)x;
}

/* Setup */
void arraylog_setup(void) {
    arraylog_class = class_new(
        gensym("arraylog"),
        (t_newmethod)arraylog_new,
        0,
        sizeof(t_arraylog),
        CLASS_DEFAULT,
        A_DEFSYMBOL,
        A_DEFSYMBOL,
        0);

    class_addbang(arraylog_class, arraylog_bang);
}
