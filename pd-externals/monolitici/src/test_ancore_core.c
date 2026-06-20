/* test_ancore_core.c
 * Test standalone del nucleo (ancore_core.h), senza Pd. Riproduce il calcolo
 * di prova_ancore.py: legge una matrice di suoni (una riga per suono, ND float
 * grezzi in ordine DESCS), ricava la taratura congelata (media/dev sui suoni),
 * fissa la coppia di ancore su due righe e stampa v per ogni suono.
 *
 * Uso: ./test_ancore_core <matrice.txt> <idx_piu> <idx_meno>
 *   matrice.txt: una riga per suono, ANC_ND (=16) float separati da spazi.
 *   idx_piu, idx_meno: indici di riga (0-based) delle due ancore.
 *
 * Confronto con prova_ancore.py fatto a valle (vedi script di verifica).
 */
#include <stdio.h>
#include <stdlib.h>
#include "ancore_core.h"

#define MAXROWS 1024

int main(int argc, char **argv) {
    if (argc < 4) {
        fprintf(stderr, "uso: %s matrice.txt idx_piu idx_meno\n", argv[0]);
        return 1;
    }
    const char *path = argv[1];
    int ip = atoi(argv[2]);
    int im = atoi(argv[3]);

    static double X[MAXROWS][ANC_ND];
    int nrow = 0;

    FILE *f = fopen(path, "r");
    if (!f) { perror("fopen"); return 1; }
    while (nrow < MAXROWS) {
        int j, ok = 1;
        for (j = 0; j < ANC_ND; j++)
            if (fscanf(f, "%lf", &X[nrow][j]) != 1) { ok = 0; break; }
        if (!ok) break;
        nrow++;
    }
    fclose(f);
    if (nrow < 2 || ip < 0 || im < 0 || ip >= nrow || im >= nrow) {
        fprintf(stderr, "dati insufficienti o indici fuori range\n");
        return 1;
    }

    /* taratura congelata: media e dev di popolazione su tutti i suoni */
    double media[ANC_ND], dev[ANC_ND];
    for (int j = 0; j < ANC_ND; j++) {
        double s = 0.0;
        for (int i = 0; i < nrow; i++) s += X[i][j];
        double m = s / nrow, var = 0.0;
        for (int i = 0; i < nrow; i++) { double d = X[i][j] - m; var += d * d; }
        media[j] = m;
        dev[j] = sqrt(var / nrow);
    }

    anc_core c;
    anc_init(&c, 1);
    anc_set_calibrazione(&c, media, dev);
    anc_set_ancora_grezza(&c, 0, X[ip], X[im]);

    for (int i = 0; i < nrow; i++) {
        double v;
        anc_v(&c, X[i], &v);
        printf("%.12g\n", v);
    }
    return 0;
}
