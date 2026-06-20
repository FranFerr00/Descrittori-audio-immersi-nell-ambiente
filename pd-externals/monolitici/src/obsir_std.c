/* obsir_std.c
 * OBSIR-std: deviazione standard delle differenze di log-energia tra
 * bande ottavali consecutive (Essid, Richard, David 2006).
 *
 * Uso in Pd: [obsir_std spectrum sr fftsize]
 *   - spectrum: array di magnitudo (magnitudine PIENA, non gated)
 *   - sr:       sample rate (default = sys_getsr())
 *   - fftsize:  dim FFT (default 8192)
 *   - bang:     esegue il calcolo
 *   - outlet:   float, std delle differenze ottavali in log10
 *
 * Bande fisse (Hz): 200-400-800-1600-3200-6400-10000 → 6 bande, 5 diff.
 *
 * Formula (identica a analisi.py.spectral_obsir_std):
 *   power[k]   = X[k]^2
 *   log_E[i]   = log10(sum_k power[k] + EPSILON)   per k nella banda i
 *   obsir[j]   = log_E[j+1] - log_E[j]
 *   obsir_std  = std(obsir)  (popolazione, ddof=0, come numpy default)
 *
 * IMPORTANTE: NON applica la soglia relativa -30 dB. L'obiettivo del
 * descrittore e' la forma del decadimento per ottave, e con la soglia
 * intere bande si azzererebbero producendo log10(0)=-inf (discusso in
 * analisi.py). Quindi niente argomento threshold_db qui.
 *
 * Misura l'irregolarita' della pendenza spettrale per banda, ortogonale
 * allo slope globale (slope = pendenza media, obsir_std = quanto la
 * pendenza varia da ottava a ottava).
 */

#include "m_pd.h"
#include <math.h>

#define OBSIR_EPSILON 1e-19
#define OBSIR_NEDGES 7
#define OBSIR_NBANDS (OBSIR_NEDGES - 1)
#define OBSIR_NDIFFS (OBSIR_NBANDS - 1)

static const double OBSIR_EDGES[OBSIR_NEDGES] = {
    200.0, 400.0, 800.0, 1600.0, 3200.0, 6400.0, 10000.0
};

static t_class *obsir_std_class;

typedef struct _obsir_std {
    t_object  x_obj;
    t_symbol *nome_spettro;
    t_float   sr;
    t_float   fftsize;
    t_outlet *x_out;
} t_obsir_std;

void obsir_std_bang(t_obsir_std *x) {
    t_garray *a;
    a = (t_garray *)pd_findbyclass(x->nome_spettro, garray_class);
    if (!a) {
        pd_error(x, "obsir_std: array '%s' non trovato", x->nome_spettro->s_name);
        return;
    }

    t_word *vec;
    int size;
    garray_getfloatwords(a, &size, &vec);

    if (size <= 0) { pd_error(x, "obsir_std: array vuoto"); return; }
    if (x->fftsize <= 0) { pd_error(x, "obsir_std: fftsize deve essere > 0"); return; }

    double df = (double)x->sr / (double)x->fftsize;

    /* Accumula la potenza per banda. power[k] = mag[k]^2, sommata sui
     * bin con freq in [edges[i], edges[i+1]). */
    double band_power[OBSIR_NBANDS];
    int i;
    for (i = 0; i < OBSIR_NBANDS; i++) band_power[i] = 0.0;

    int k;
    for (k = 0; k < size; k++) {
        double freq = (double)k * df;
        if (freq < OBSIR_EDGES[0]) continue;
        if (freq >= OBSIR_EDGES[OBSIR_NEDGES - 1]) break;
        /* Trova la banda. Con solo 6 bande la ricerca lineare e' ok. */
        for (i = 0; i < OBSIR_NBANDS; i++) {
            if (freq < OBSIR_EDGES[i + 1]) {
                double mag = vec[k].w_float;
                band_power[i] += mag * mag;
                break;
            }
        }
    }

    /* log10 delle energie di banda (+ epsilon per evitare log(0)) */
    double log_E[OBSIR_NBANDS];
    for (i = 0; i < OBSIR_NBANDS; i++) {
        log_E[i] = log10(band_power[i] + OBSIR_EPSILON);
    }

    /* obsir[j] = log_E[j+1] - log_E[j], poi std popolazione (ddof=0) */
    double obsir[OBSIR_NDIFFS];
    double sum = 0.0;
    int j;
    for (j = 0; j < OBSIR_NDIFFS; j++) {
        obsir[j] = log_E[j + 1] - log_E[j];
        sum += obsir[j];
    }
    double mean = sum / (double)OBSIR_NDIFFS;

    double var = 0.0;
    for (j = 0; j < OBSIR_NDIFFS; j++) {
        double d = obsir[j] - mean;
        var += d * d;
    }
    var /= (double)OBSIR_NDIFFS;  /* std di popolazione, come np.std default */

    outlet_float(x->x_out, (t_float)sqrt(var));
}

void *obsir_std_new(t_symbol *spettro, t_floatarg sr, t_floatarg fftsize) {
    t_obsir_std *x = (t_obsir_std *)pd_new(obsir_std_class);
    x->nome_spettro = spettro;
    x->sr           = (sr      > 0) ? sr      : sys_getsr();
    x->fftsize      = (fftsize > 0) ? fftsize : 8192;

    floatinlet_new(&x->x_obj, &x->sr);
    floatinlet_new(&x->x_obj, &x->fftsize);

    x->x_out = outlet_new(&x->x_obj, &s_float);
    return (void *)x;
}

void obsir_std_setup(void) {
    obsir_std_class = class_new(
        gensym("obsir_std"),
        (t_newmethod)obsir_std_new,
        0,
        sizeof(t_obsir_std),
        CLASS_DEFAULT,
        A_DEFSYMBOL, A_DEFFLOAT, A_DEFFLOAT,
        0);
    class_addbang(obsir_std_class, obsir_std_bang);
}
