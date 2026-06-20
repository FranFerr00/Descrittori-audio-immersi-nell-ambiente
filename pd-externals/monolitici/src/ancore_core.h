/* ancore_core.h
 * Nucleo numerico del controllo bipolare a ancore e distanza, in C puro
 * (niente dipendenze da Pd). Incluso sia dall'esterno ancore.c sia dal test
 * standalone test_ancore_core.c, cosi' la matematica testata e' la stessa che
 * gira in Pd. Riproduce prova_ancore.py.
 *
 *   z   = (grezzo - media) / dev          (taratura CONGELATA dal corpus)
 *   d+  = distanza euclidea in z da P+    (sugli assi attivi)
 *   d-  = distanza euclidea in z da P-
 *   v   = (d- - d+) / (d- + d+)           identico a P+ -> +1, a P- -> -1
 *
 * Ogni parametro ha la sua coppia di ancore (P+, P-): np parametri in
 * parallelo dallo stesso ingresso di nd descrittori.
 */
#ifndef ANCORE_CORE_H
#define ANCORE_CORE_H

#include <math.h>

#define ANC_ND    16     /* numero di descrittori */
#define ANC_NPMAX 8      /* coppie (parametri) massime */
#define ANC_EPS   1e-12

typedef struct _anc_core {
    int    nd;                        /* descrittori attivi (default ANC_ND) */
    int    np;                        /* coppie attive */
    double media[ANC_ND];             /* taratura congelata: media per descrittore */
    double dev[ANC_ND];               /* taratura congelata: deviazione */
    double pp[ANC_NPMAX][ANC_ND];     /* ancora +1, in z */
    double pm[ANC_NPMAX][ANC_ND];     /* ancora -1, in z */
    char   usa[ANC_ND];               /* maschera assi: 1 = conta nella distanza */
} anc_core;

/* azzera: taratura neutra (z = grezzo), tutti gli assi attivi, ancore a 0 */
static void anc_init(anc_core *c, int np) {
    int i, k;
    c->nd = ANC_ND;
    c->np = (np < 1) ? 1 : (np > ANC_NPMAX ? ANC_NPMAX : np);
    for (i = 0; i < ANC_ND; i++) { c->media[i] = 0.0; c->dev[i] = 1.0; c->usa[i] = 1; }
    for (k = 0; k < ANC_NPMAX; k++)
        for (i = 0; i < ANC_ND; i++) { c->pp[k][i] = 0.0; c->pm[k][i] = 0.0; }
}

/* fissa la taratura congelata (media e dev del corpus). dev <= 0 -> 1 (neutro) */
static void anc_set_calibrazione(anc_core *c, const double *media, const double *dev) {
    int i;
    for (i = 0; i < c->nd; i++) {
        c->media[i] = media[i];
        c->dev[i]   = (dev[i] > ANC_EPS) ? dev[i] : 1.0;
    }
}

static double anc_z(const anc_core *c, int i, double x) {
    return (x - c->media[i]) / c->dev[i];
}

/* imposta il solo polo +1 della coppia k da valori GREZZI (li converte in z) */
static void anc_set_piu_grezza(anc_core *c, int k, const double *raw) {
    int i;
    if (k < 0 || k >= c->np) return;
    for (i = 0; i < c->nd; i++) c->pp[k][i] = anc_z(c, i, raw[i]);
}

/* imposta il solo polo -1 della coppia k da valori GREZZI (li converte in z) */
static void anc_set_meno_grezza(anc_core *c, int k, const double *raw) {
    int i;
    if (k < 0 || k >= c->np) return;
    for (i = 0; i < c->nd; i++) c->pm[k][i] = anc_z(c, i, raw[i]);
}

/* imposta la coppia k da vettori GREZZI di nd descrittori (li converte in z) */
static void anc_set_ancora_grezza(anc_core *c, int k,
                                  const double *plus_raw, const double *minus_raw) {
    anc_set_piu_grezza(c, k, plus_raw);
    anc_set_meno_grezza(c, k, minus_raw);
}

/* imposta la coppia k direttamente in z (per ancore gia' calcolate) */
static void anc_set_ancora_z(anc_core *c, int k,
                             const double *plus_z, const double *minus_z) {
    int i;
    if (k < 0 || k >= c->np) return;
    for (i = 0; i < c->nd; i++) { c->pp[k][i] = plus_z[i]; c->pm[k][i] = minus_z[i]; }
}

/* distanza euclidea in z fra il vettore z[] e l'ancora a[], sugli assi attivi */
static double anc_dist(const anc_core *c, const double *z, const double *a) {
    int i; double s = 0.0;
    for (i = 0; i < c->nd; i++)
        if (c->usa[i]) { double d = z[i] - a[i]; s += d * d; }
    return sqrt(s);
}

/* calcola i np valori v da un ingresso GREZZO di nd descrittori.
 * out_v deve avere almeno np elementi. */
static void anc_v(const anc_core *c, const double *x_raw, double *out_v) {
    int i, k;
    double z[ANC_ND];
    for (i = 0; i < c->nd; i++) z[i] = anc_z(c, i, x_raw[i]);
    for (k = 0; k < c->np; k++) {
        double dp = anc_dist(c, z, c->pp[k]);
        double dm = anc_dist(c, z, c->pm[k]);
        out_v[k] = (dm + dp > ANC_EPS) ? (dm - dp) / (dm + dp) : 0.0;
    }
}

#endif
