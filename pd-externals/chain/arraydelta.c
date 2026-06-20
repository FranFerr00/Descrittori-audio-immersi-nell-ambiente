/* arraydelta.c
 * Calcola la differenza assoluta tra lo spettro attuale e quello del frame precedente.
 *
 * Uso in Pd: [arraydelta input previous result]
 *   - input:    array con i valori del frame corrente
 *   - previous: array di appoggio dove vengono copiati i valori del frame precedente
 *               (utile per visualizzarli nella patch)
 *   - result:   array con le differenze |corrente - precedente|
 *   - bang:     esegue il calcolo e aggiorna la memoria interna
 *
 * Comportamento al primo bang:
 *   - alloca internamente un buffer della stessa dimensione di input
 *   - copia input in previous e nel buffer
 *   - scrive tutti zeri in result (nessun frame precedente da confrontare)
 *
 * Comportamento ai bang successivi:
 *   - confronta input con i valori salvati nel buffer interno
 *   - scrive i valori vecchi in previous
 *   - scrive |input[k] - vecchio[k]| in result
 *   - aggiorna il buffer con i valori correnti per il prossimo bang
 *
 * Questo external ha STATO INTERNO (il buffer dei valori precedenti).
 * È l'unico del toolkit a usare malloc/free, e per questo ha un
 * destructor registrato come secondo argomento di class_new().
 * Il destructor viene chiamato automaticamente da Pd quando l'oggetto
 * viene eliminato dalla patch, per liberare la memoria allocata.
 *
 * Usato per il flux spettrale: misura quanto lo spettro cambia
 * da un frame FFT al successivo. Un suono stazionario ha flux basso;
 * un attacco o un cambio timbrico improvviso produce flux alto.
 */

#include "m_pd.h"
#include <stdlib.h>
#include <math.h>

/* Puntatore globale alla classe */
static t_class *arraydelta_class;

/* Struttura dati dell'oggetto.
 * t_object deve essere SEMPRE il primo campo.
 * valori_precedenti è allocato dinamicamente con malloc al primo bang. */
typedef struct _arraydelta {
    t_object  x_obj;
    t_symbol *nome_array;           /* array di input (frame corrente) */
    t_symbol *nome_precedente;      /* array di output: valori del frame precedente */
    t_symbol *nome_risultato;       /* array di output: differenze */
    t_float  *valori_precedenti;    /* buffer interno: copia del frame precedente */
    int       dimensione;           /* numero di elementi nel buffer */
} t_arraydelta;

/* Costruttore: chiamato quando l'oggetto viene creato nella patch.
 * Inizializza il buffer a NULL: verrà allocato al primo bang,
 * quando si conosce la dimensione effettiva dell'array di input. */
void *arraydelta_new(t_symbol *arr, t_symbol *prev, t_symbol *result) {
    t_arraydelta *x = (t_arraydelta *)pd_new(arraydelta_class);
    x->nome_array        = arr;
    x->nome_precedente   = prev;
    x->nome_risultato    = result;
    x->valori_precedenti = NULL;    /* buffer non ancora allocato */
    x->dimensione        = 0;

    /* Azzera l'array "previous" alla creazione dell'oggetto,
     * così la patch non mostra dati casuali prima del primo bang */
    t_garray *a_prev = (t_garray *)pd_findbyclass(prev, garray_class);
    if (a_prev) {
        t_word *vec_prev;
        int size_prev;
        if (garray_getfloatwords(a_prev, &size_prev, &vec_prev)) {
            int i;
            for (i = 0; i < size_prev; i++) {
                vec_prev[i].w_float = 0.0;
            }
            garray_redraw(a_prev);
        }
    }

    return (void *)x;
}

/* Destructor: chiamato da Pd quando l'oggetto viene eliminato.
 * Libera il buffer allocato con malloc per evitare memory leak. */
void arraydelta_free(t_arraydelta *x) {
    if (x->valori_precedenti != NULL) {
        free(x->valori_precedenti);
        x->valori_precedenti = NULL;
    }
}

/* Funzione chiamata quando arriva un bang. */
void arraydelta_bang(t_arraydelta *x) {
    t_garray *a_input, *a_previous, *a_result;

    a_input    = (t_garray *)pd_findbyclass(x->nome_array,       garray_class);
    a_previous = (t_garray *)pd_findbyclass(x->nome_precedente,  garray_class);
    a_result   = (t_garray *)pd_findbyclass(x->nome_risultato,   garray_class);

    if (!a_input) {
        pd_error(x, "arraydelta: array '%s' non trovato", x->nome_array->s_name);
        return;
    }
    if (!a_previous) {
        pd_error(x, "arraydelta: array '%s' non trovato", x->nome_precedente->s_name);
        return;
    }
    if (!a_result) {
        pd_error(x, "arraydelta: array '%s' non trovato", x->nome_risultato->s_name);
        return;
    }

    t_word *vec_input, *vec_previous, *vec_result;
    int size_input, size_previous, size_result;
    garray_getfloatwords(a_input,    &size_input,    &vec_input);
    garray_getfloatwords(a_previous, &size_previous, &vec_previous);
    garray_getfloatwords(a_result,   &size_result,   &vec_result);

    if (size_input <= 0 || size_previous <= 0 || size_result <= 0) {
        pd_error(x, "arraydelta: array vuoto o non valido");
        return;
    }

    /* PRIMO BANG: buffer non ancora allocato */
    if (x->valori_precedenti == NULL) {

        /* Alloca il buffer interno con la dimensione dell'array di input */
        x->valori_precedenti = (t_float *)malloc(size_input * sizeof(t_float));
        if (x->valori_precedenti == NULL) {
            pd_error(x, "arraydelta: errore allocazione memoria");
            return;
        }
        x->dimensione = size_input;

        /* Salva i valori correnti nel buffer interno */
        int i;
        for (i = 0; i < size_input; i++) {
            x->valori_precedenti[i] = vec_input[i].w_float;
        }

        /* Copia gli stessi valori in "previous" per visualizzazione */
        int minsize_prev = size_input < size_previous ? size_input : size_previous;
        for (i = 0; i < minsize_prev; i++) {
            vec_previous[i].w_float = x->valori_precedenti[i];
        }
        garray_redraw(a_previous);

        /* Result = zero: nessun frame precedente con cui confrontare */
        int minsize_res = size_input < size_result ? size_input : size_result;
        for (i = 0; i < minsize_res; i++) {
            vec_result[i].w_float = 0.0;
        }
        garray_redraw(a_result);

        return;
    }

    /* BANG SUCCESSIVI: buffer già allocato, confronta con il frame precedente */

    /* Controlla che la dimensione dell'array non sia cambiata */
    if (size_input != x->dimensione) {
        pd_error(x, "arraydelta: dimensione array cambiata da %d a %d",
                 x->dimensione, size_input);
        return;
    }

    int i;

    /* Scrivi i valori VECCHI in "previous" (il frame che stiamo per sostituire) */
    int minsize_prev = x->dimensione < size_previous ? x->dimensione : size_previous;
    for (i = 0; i < minsize_prev; i++) {
        vec_previous[i].w_float = x->valori_precedenti[i];
    }
    garray_redraw(a_previous);

    /* Calcola le differenze assolute tra frame corrente e precedente */
    int minsize_res = x->dimensione < size_result ? x->dimensione : size_result;
    for (i = 0; i < minsize_res; i++) {
        vec_result[i].w_float = fabs(vec_input[i].w_float - x->valori_precedenti[i]);
    }
    garray_redraw(a_result);

    /* Aggiorna il buffer con i valori correnti per il prossimo bang */
    for (i = 0; i < x->dimensione; i++) {
        x->valori_precedenti[i] = vec_input[i].w_float;
    }
}

/* Setup: registra la classe con il destructor come secondo argomento.
 * Senza il destructor, ogni eliminazione dell'oggetto causerebbe un memory leak. */
void arraydelta_setup(void) {
    arraydelta_class = class_new(
        gensym("arraydelta"),
        (t_newmethod)arraydelta_new,
        (t_method)arraydelta_free,  /* destructor: obbligatorio perché usiamo malloc */
        sizeof(t_arraydelta),
        CLASS_DEFAULT,
        A_DEFSYMBOL,                /* array input */
        A_DEFSYMBOL,                /* array previous */
        A_DEFSYMBOL,                /* array result */
        0);

    class_addbang(arraydelta_class, arraydelta_bang);
}
