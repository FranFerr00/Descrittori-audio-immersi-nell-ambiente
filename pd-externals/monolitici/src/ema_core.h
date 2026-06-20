/* ema_core.h
 * Nucleo numerico della media mobile esponenziale (EMA) su un vettore di nd
 * descrittori, in C puro (niente dipendenze da Pd). Incluso sia dall'esterno
 * ema.c sia da un eventuale test standalone.
 *
 * A ogni frame:  m += a * (x - m)   con  a = 1 - exp(-dt / tau)
 *   - tau = costante di tempo in secondi (quanto "memoria": piccolo = scorda in
 *     fretta, grande = media lunga). tau <= 0 -> nessuna media (passa il frame).
 *   - dt  = tempo trascorso dal frame precedente (s), misurato dall'involucro.
 * Il primo frame inizializza la media (niente transitorio da zero).
 */
#ifndef EMA_CORE_H
#define EMA_CORE_H

#include <math.h>

#define EMA_ND 16

typedef struct _ema_core {
    int    nd;
    double tau;            /* costante di tempo (s) */
    double m[EMA_ND];      /* media corrente */
    int    started;        /* 0 finche' non arriva il primo frame */
} ema_core;

static void ema_init(ema_core *c, int nd) {
    int i;
    c->nd = (nd < 1 || nd > EMA_ND) ? EMA_ND : nd;
    c->tau = 1.0;
    c->started = 0;
    for (i = 0; i < EMA_ND; i++) c->m[i] = 0.0;
}

static void ema_set_tau(ema_core *c, double tau) {
    c->tau = (tau < 0.0) ? 0.0 : tau;
}

/* aggiorna la media col nuovo frame x e il dt (s) trascorso */
static void ema_push(ema_core *c, const double *x, double dt) {
    int i; double a;
    if (!c->started) {
        for (i = 0; i < c->nd; i++) c->m[i] = x[i];
        c->started = 1;
        return;
    }
    if (c->tau <= 0.0 || dt <= 0.0) {
        for (i = 0; i < c->nd; i++) c->m[i] = x[i];
        return;
    }
    a = 1.0 - exp(-dt / c->tau);
    if (a > 1.0) a = 1.0;
    for (i = 0; i < c->nd; i++) c->m[i] += a * (x[i] - c->m[i]);
}

static void ema_get(const ema_core *c, double *out) {
    int i;
    for (i = 0; i < c->nd; i++) out[i] = c->m[i];
}

#endif
