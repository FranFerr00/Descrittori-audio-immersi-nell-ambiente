#!/usr/bin/env python3
"""Confronto del centroide del rumore vs distanza fra due bande di analisi.

Legge centroidi_medie.csv da due cartelle (es. 10 kHz e banda piena) e disegna, per il
rumore orizzontale e verticale, il centroide medio (finestra 2 s) in funzione della
distanza, sovrapponendo le due bande. Mostra che il tetto a 10 kHz nasconde l'assorbimento
dell'aria sugli acuti, visibile solo a banda piena.

Uso:
    python esperimento_distanza/confronto_banda.py analisi/distanza analisi/distanza-banda-piena
"""
import argparse
import collections
import csv
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def carica(root):
    d = collections.defaultdict(dict)
    with open(os.path.join(root, 'centroidi_medie.csv')) as fh:
        for r in csv.DictReader(fh):
            if r['media_intero']:
                d[r['file']][int(r['canale'])] = float(r['media_intero'])
    return d


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('root_a', help='cartella con la banda di riferimento (es. 10 kHz)')
    p.add_argument('root_b', help='cartella con l\'altra banda (es. banda piena)')
    p.add_argument('--label-a', default='10 kHz')
    p.add_argument('--label-b', default='banda piena (48 kHz)')
    p.add_argument('-o', '--out', default=None)
    args = p.parse_args(argv)

    A, B = carica(args.root_a), carica(args.root_b)
    x = np.arange(1, 9)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    for ax, (f, tit) in zip(axes, [('NOISE_oriz_1-9mt', 'orizzontale'),
                                   ('NOISE_vert_1-9mt', 'verticale')]):
        yb = [B[f].get(c, np.nan) for c in x]
        ya = [A[f].get(c, np.nan) for c in x]
        ax.plot(x, yb, marker='o', lw=2, color='C3', label=args.label_b)
        ax.plot(x, ya, marker='o', lw=2, ls='--', color='C0', label=args.label_a)
        ax.set_title(f'rumore {tit}')
        ax.set_xlabel('distanza (m)')
        ax.set_xticks(x)
        ax.grid(True, alpha=0.3)
        ax.legend()
    axes[0].set_ylabel('centroide spettrale (Hz)')
    fig.suptitle('Centroide del rumore vs distanza: il tetto a 10 kHz nasconde la caduta '
                 'che si vede a banda piena')
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out = args.out or os.path.join(args.root_a, 'centroide', 'centroide_rumore_banda.png')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print('scritto', out)


if __name__ == '__main__':
    main()
