/* test_matrice_core.c
 * Test standalone del nucleo numerico (matrice_core.h), senza Pd.
 * Rispecchia lo streaming di matrice.c (ring + storia delle matrici) e
 * stampa per ogni frame: idx c1 c2 e1 e2. Confronto con matrice_controlli.py
 * fatto a valle (vedi script di verifica).
 *
 * Uso: ./test_matrice_core <frames.txt> K [N] [D]
 *   frames.txt: una riga per frame, K float separati da spazi (';' ignorato).
 */
#include <stdio.h>
#include <stdlib.h>
#include "matrice_core.h"

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "uso: %s frames.txt K [N] [D]\n", argv[0]); return 1; }
    const char *path = argv[1];
    int K = atoi(argv[2]);
    int N = (argc > 3) ? atoi(argv[3]) : ((16 > 4 * K) ? 16 : 4 * K);
    int D = (argc > 4) ? atoi(argv[4]) : N / 2;
    int hist_len = D + 1;

    double *ring = calloc((size_t)N * K, sizeof(double));
    double *Mhist = calloc((size_t)hist_len * K * K, sizeof(double));
    double *Vhist = calloc((size_t)hist_len * K, sizeof(double));
    char   *Mvalid = calloc((size_t)hist_len, sizeof(char));
    double *M = calloc((size_t)K * K, sizeof(double));
    double *v1 = calloc((size_t)K, sizeof(double));
    double *colmean = calloc((size_t)K, sizeof(double));
    double *colstd = calloc((size_t)K, sizeof(double));
    char   *colok = calloc((size_t)K, sizeof(char));
    double *A = calloc((size_t)K * K, sizeof(double));
    double *V = calloc((size_t)K * K, sizeof(double));
    double *w = calloc((size_t)K, sizeof(double));
    double sc[SC_NTYPES];

    FILE *f = fopen(path, "r");
    if (!f) { perror("fopen"); return 1; }

    int head = 0;
    long count = 0;
    int idx = 0;
    double val;
    /* lettura token per token (i ';' diventano separatori non numerici) */
    char tok[64];
    int filled = 0;
    while (fscanf(f, "%63s", tok) == 1) {
        /* prova a convertire; salta token non numerici (es. ';') */
        char *end;
        val = strtod(tok, &end);
        if (end == tok) continue;
        ring[head * K + filled] = val;
        filled++;
        if (filled < K) continue;
        filled = 0;
        head = (head + 1) % N;
        count++;
        idx++;

        if (count < N) continue;
        mat_scalars(ring, N, K, M, v1, sc, colmean, colstd, colok, A, V, w);

        int slot = (int)(count % hist_len);
        for (int t = 0; t < K * K; t++) Mhist[(size_t)slot * K * K + t] = M[t];
        for (int t = 0; t < K; t++) Vhist[(size_t)slot * K + t] = v1[t];
        Mvalid[slot] = 1;

        double e1 = 0.0, e2 = 0.0;
        if (count - D >= N) {
            int pslot = (int)((count - D) % hist_len);
            if (Mvalid[pslot]) {
                e1 = mat_e1(M, Mhist + (size_t)pslot * K * K, K);
                e2 = mat_e2(v1, Vhist + (size_t)pslot * K, K);
            }
        }
        printf("%d %.6f %.6f %.6f %.6f\n", idx - 1,
               sc[SC_C1], sc[SC_C2], e1, e2);
    }
    fclose(f);
    return 0;
}
