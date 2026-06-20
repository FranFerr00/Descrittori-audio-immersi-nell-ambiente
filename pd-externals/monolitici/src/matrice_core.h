/* matrice_core.h
 * Nucleo numerico della matrice di correlazione rolling, in C puro (niente
 * dipendenze da Pd). Incluso sia da matrice.c (l'esterno) sia dal test
 * standalone test_matrice_core.c, cosi' la matematica testata e' la stessa
 * che gira in Pd.
 */
#ifndef MATRICE_CORE_H
#define MATRICE_CORE_H

#include <math.h>

#define MF_EPS 1e-12

/* scalari disponibili */
enum {
    SC_C1, SC_C2, SC_C3, SC_SIGMA, SC_KURT, SC_POLAR, SC_WEAK, SC_E1, SC_E2,
    SC_NTYPES
};

static const char *SC_NOMI[SC_NTYPES] = {
    "c1", "c2", "c3", "sigma", "kurt", "polar", "weak", "e1", "e2"
};

/* Jacobi ciclico per matrice simmetrica K x K (K piccolo). A distrutta.
 * w[K] autovalori, V[K*K] autovettori per colonna (V[i*K+j] = i-esima
 * componente del j-esimo autovettore). */
static void jacobi_sym(double *A, int K, double *w, double *V) {
    int i, j, p, q, sweep;
    for (i = 0; i < K; i++)
        for (j = 0; j < K; j++)
            V[i * K + j] = (i == j) ? 1.0 : 0.0;
    for (sweep = 0; sweep < 100; sweep++) {
        double off = 0.0;
        for (p = 0; p < K; p++)
            for (q = p + 1; q < K; q++)
                off += A[p * K + q] * A[p * K + q];
        if (off < 1e-30) break;
        for (p = 0; p < K; p++) {
            for (q = p + 1; q < K; q++) {
                double apq = A[p * K + q];
                if (fabs(apq) < 1e-300) continue;
                double phi = 0.5 * (A[q * K + q] - A[p * K + p]) / apq;
                double t = (phi >= 0.0 ? 1.0 : -1.0)
                           / (fabs(phi) + sqrt(phi * phi + 1.0));
                double c = 1.0 / sqrt(t * t + 1.0);
                double s = t * c;
                for (i = 0; i < K; i++) {
                    double aip = A[i * K + p], aiq = A[i * K + q];
                    A[i * K + p] = c * aip - s * aiq;
                    A[i * K + q] = s * aip + c * aiq;
                }
                for (i = 0; i < K; i++) {
                    double api = A[p * K + i], aqi = A[q * K + i];
                    A[p * K + i] = c * api - s * aqi;
                    A[q * K + i] = s * api + c * aqi;
                }
                for (i = 0; i < K; i++) {
                    double vip = V[i * K + p], viq = V[i * K + q];
                    V[i * K + p] = c * vip - s * viq;
                    V[i * K + q] = s * vip + c * viq;
                }
            }
        }
    }
    for (i = 0; i < K; i++) w[i] = A[i * K + i];
}

/* Calcola la matrice di correlazione sulla finestra `ring` (N frame x K serie,
 * row-major; l'ordine dei frame e' irrilevante) e tutti gli scalari
 * istantanei (tutto tranne e1/e2). Riempie M[K*K] (NaN dove non definito),
 * v1[K] (NaN se indefinito) e sc[SC_NTYPES] (NaN per e1/e2 e per gli scalari
 * non definiti). I buffer di scratch (colmean,colstd,colok,A,V,w) sono forniti
 * dal chiamante, dimensionati su K (A,V su K*K). */
static void mat_scalars(const double *ring, int N, int K,
                        double *M, double *v1, double *sc,
                        double *colmean, double *colstd, char *colok,
                        double *A, double *V, double *w) {
    int i, j, t, nvalid = 0;
    for (i = 0; i < SC_NTYPES; i++) sc[i] = NAN;

    for (j = 0; j < K; j++) {
        double sum = 0.0;
        for (t = 0; t < N; t++) sum += ring[t * K + j];
        double mean = sum / N, var = 0.0;
        for (t = 0; t < N; t++) {
            double d = ring[t * K + j] - mean;
            var += d * d;
        }
        var /= N;
        colmean[j] = mean;
        colstd[j] = sqrt(var);
        colok[j] = (colstd[j] > MF_EPS) ? 1 : 0;
        if (colok[j]) nvalid++;
    }

    for (i = 0; i < K; i++) {
        for (j = i; j < K; j++) {
            if (!colok[i] || !colok[j]) {
                M[i * K + j] = M[j * K + i] = NAN;
            } else if (i == j) {
                M[i * K + j] = 1.0;
            } else {
                double cov = 0.0;
                for (t = 0; t < N; t++)
                    cov += (ring[t * K + i] - colmean[i])
                         * (ring[t * K + j] - colmean[j]);
                cov /= N;
                double r = cov / (colstd[i] * colstd[j]);
                if (r > 1.0) r = 1.0;
                if (r < -1.0) r = -1.0;
                M[i * K + j] = M[j * K + i] = r;
            }
        }
    }

    double s = 0.0, s2 = 0.0, sabs = 0.0;
    int n = 0, n_pos = 0, n_neg = 0, n_weak = 0;
    for (i = 0; i < K; i++)
        for (j = i + 1; j < K; j++) {
            if (!colok[i] || !colok[j]) continue;
            double r = M[i * K + j];
            s += r; s2 += r * r; sabs += fabs(r);
            if (r > 0) n_pos++; else if (r < 0) n_neg++;
            if (fabs(r) < 0.2) n_weak++;
            n++;
        }
    if (n > 0) {
        double c1 = s / n;
        double var = s2 / n - c1 * c1;
        if (var < 0) var = 0;
        sc[SC_C1] = c1;
        sc[SC_SIGMA] = sqrt(var);
        double abs_mean = sabs / n;
        if (abs_mean > MF_EPS) sc[SC_POLAR] = fabs(c1) / abs_mean;
        sc[SC_WEAK] = (double)n_weak / n;
        int tot = n_pos + n_neg;
        if (tot > 0) sc[SC_C3] = (double)(n_pos - n_neg) / tot;
        if (var > MF_EPS) {
            double m4 = 0.0;
            for (i = 0; i < K; i++)
                for (j = i + 1; j < K; j++) {
                    if (!colok[i] || !colok[j]) continue;
                    double d = M[i * K + j] - c1;
                    m4 += d * d * d * d;
                }
            m4 /= n;
            sc[SC_KURT] = m4 / (var * var) - 3.0;
        }
    }

    for (i = 0; i < K; i++) v1[i] = NAN;
    if (K >= 3 && nvalid >= 2) {
        for (i = 0; i < K; i++)
            for (j = 0; j < K; j++) {
                double v = M[i * K + j];
                A[i * K + j] = (isnan(v) ? 0.0 : v);
            }
        for (i = 0; i < K; i++)
            for (j = i + 1; j < K; j++) {
                double avg = 0.5 * (A[i * K + j] + A[j * K + i]);
                A[i * K + j] = A[j * K + i] = avg;
            }
        jacobi_sym(A, K, w, V);
        int imax = 0;
        double lam_sum = 0.0;
        for (i = 0; i < K; i++) {
            lam_sum += fabs(w[i]);
            if (fabs(w[i]) > fabs(w[imax])) imax = i;
        }
        if (lam_sum > MF_EPS) {
            sc[SC_C2] = 2.0 * fabs(w[imax]) / lam_sum - 1.0;
            for (i = 0; i < K; i++) v1[i] = V[i * K + imax];
            for (i = 0; i < K; i++) {
                if (fabs(v1[i]) > MF_EPS) {
                    if (v1[i] < 0.0)
                        for (j = 0; j < K; j++) v1[j] = -v1[j];
                    break;
                }
            }
        }
    }
}

/* E1: Frobenius normalizzata fra M corrente e M di D frame fa (NaN -> 0). */
static double mat_e1(const double *M, const double *Mp, int K) {
    int i, j;
    double ss = 0.0;
    for (i = 0; i < K; i++)
        for (j = 0; j < K; j++) {
            double a = M[i * K + j], b = Mp[i * K + j];
            double d = (isnan(a) ? 0.0 : a) - (isnan(b) ? 0.0 : b);
            ss += d * d;
        }
    double norm = sqrt((double)K * (K - 1));
    return (norm > MF_EPS) ? sqrt(ss) / norm : 0.0;
}

/* E2: |coseno| fra v1 corrente e v1 di D frame fa. NaN se indefinito.
 * Si usa il valore assoluto perche' un autovettore e' definito a meno del
 * segno (v1 e -v1 sono lo stesso asse): il coseno con segno salterebbe fra
 * +1 e -1 sui ribaltamenti arbitrari di Jacobi pur senza riorientamento reale.
 * Esce in [0,1]: 1 = stesso asse, 0 = asse ruotato di 90 gradi. */
static double mat_e2(const double *v1, const double *v1p, int K) {
    int i;
    double dot = 0.0, na = 0.0, nb = 0.0;
    for (i = 0; i < K; i++) {
        if (isnan(v1[i]) || isnan(v1p[i])) return NAN;
        dot += v1[i] * v1p[i];
        na += v1[i] * v1[i];
        nb += v1p[i] * v1p[i];
    }
    if (na > MF_EPS && nb > MF_EPS) return fabs(dot) / sqrt(na * nb);
    return NAN;
}

#endif /* MATRICE_CORE_H */
