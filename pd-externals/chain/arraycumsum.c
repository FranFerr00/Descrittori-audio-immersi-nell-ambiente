/* arraycumsum.c
 * Calcola la somma cumulativa di un array elemento per elemento.
 *
 * Uso in Pd: [arraycumsum input result]
 *   - input:  nome dell'array sorgente
 *   - result: nome dell'array di destinazione
 *   - bang:   esegue il calcolo
 *
 * Esempio:
 *   input  = [2, 3, 1, 4]
 *   result = [2, 5, 6, 10]
 *
 * Usato per il rolloff spettrale: dopo aver calcolato X[k]^2 per ogni bin,
 * arraycumsum costruisce l'energia cumulativa dello spettro. Si cerca poi
 * il primo bin che supera l'85% dell'energia totale (con arrayfirstover).
 */

#include "m_pd.h"

/* Puntatore globale alla classe — richiesto da Pd per registrare l'oggetto */
static t_class *arraycumsum_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo: Pd lo usa internamente
 * per gestire inlet, outlet e il collegamento nella patch. */
typedef struct _arraycumsum {
    t_object x_obj;
    t_symbol *nome_array1;      /* nome dell'array di input */
    t_symbol *nome_risultato;   /* nome dell'array di output */
} t_arraycumsum;

/* Funzione chiamata quando arriva un bang.
 * Qui avviene tutto il calcolo. */
void arraycumsum_bang(t_arraycumsum *x) {
    t_garray *a1, *aresult;

    /* Cerca gli array per nome nel namespace globale di Pd.
     * pd_findbyclass restituisce NULL se l'array non esiste. */
    a1      = (t_garray *)pd_findbyclass(x->nome_array1,    garray_class);
    aresult = (t_garray *)pd_findbyclass(x->nome_risultato, garray_class);

    /* Controlla che entrambi gli array esistano prima di procedere */
    if (!a1) {
        pd_error(x, "arraycumsum: array '%s' non trovato", x->nome_array1->s_name);
        return;
    }
    if (!aresult) {
        pd_error(x, "arraycumsum: array '%s' non trovato", x->nome_risultato->s_name);
        return;
    }

    /* Ottieni i puntatori ai dati e le dimensioni.
     * t_word è il tipo base di Pd per i campioni; si accede al float con .w_float */
    t_word *vec1, *vecresult;
    int size1, sizeresult;
    garray_getfloatwords(a1,      &size1,      &vec1);
    garray_getfloatwords(aresult, &sizeresult, &vecresult);

    /* Usa la dimensione minima per non sforare i bordi di nessun array */
    int minsize = size1 < sizeresult ? size1 : sizeresult;

    /* Calcolo della somma cumulativa.
     * acc accumula la somma: al passo i contiene la somma di vec1[0..i]. */
    float acc = 0.0;
    int i;
    for (i = 0; i < minsize; i++) {
        acc += vec1[i].w_float;
        vecresult[i].w_float = acc;
    }

    /* Segnala a Pd che l'array di output è cambiato, così lo ridisegna.
     * Si chiama solo sull'array di output, mai su quello di input. */
    garray_redraw(aresult);
}

/* Costruttore: chiamato quando l'oggetto viene creato nella patch.
 * Riceve i due nomi di array come argomenti simbolici. */
void *arraycumsum_new(t_symbol *arr1, t_symbol *result) {
    /* Alloca la memoria per la struttura dell'oggetto */
    t_arraycumsum *x = (t_arraycumsum *)pd_new(arraycumsum_class);

    /* Salva i nomi degli array nella struttura */
    x->nome_array1    = arr1;
    x->nome_risultato = result;

    return (void *)x;
}

/* Setup: chiamato una sola volta quando Pd carica l'external.
 * Registra la classe e definisce come risponde ai messaggi. */
void arraycumsum_setup(void) {
    arraycumsum_class = class_new(
        gensym("arraycumsum"),       /* nome dell'oggetto in Pd */
        (t_newmethod)arraycumsum_new, /* costruttore */
        0,                            /* destructor (non serve: niente malloc) */
        sizeof(t_arraycumsum),        /* dimensione della struttura */
        CLASS_DEFAULT,                /* tipo di oggetto standard */
        A_DEFSYMBOL,                  /* primo argomento: nome array input */
        A_DEFSYMBOL,                  /* secondo argomento: nome array result */
        0);                           /* fine lista argomenti */

    /* Associa il bang alla funzione di calcolo */
    class_addbang(arraycumsum_class, arraycumsum_bang);
}
