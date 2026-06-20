#!/usr/bin/env python3
"""Verifica dell'allineamento dei gain: RMS per microfono sul grappolo iniziale.

Sul file del grappolo (8 mic accostati a ~1 m, NOISE_1mt) calcola l'RMS per canale e
lo scarto dalla media in dB: il dato numerico su quanto bene sono stati allineati a
mano i gain dei microfoni. Salva un CSV e un grafico a barre dello scarto per canale.

Uso:
    python esperimento_distanza/calibrazione_rms.py \\
        esperimento_distanza/2026-06-13-FRAFER-TEST-DISTANZA-GIUSTO/divisi/NOISE_1mt.wav
"""
import argparse
import csv
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from livelli import rms_per_canale


def scarti_db(dbfs):
    dbfs = np.asarray(dbfs, dtype=float)
    return dbfs - dbfs.mean()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('wav', help='wav del grappolo (NOISE_1mt.wav)')
    p.add_argument('-o', '--out-dir', default='analisi/distanza')
    args = p.parse_args(argv)

    lin, dbfs = rms_per_canale(args.wav)
    scarto = scarti_db(dbfs)
    ch = np.arange(1, len(dbfs) + 1)
    os.makedirs(args.out_dir, exist_ok=True)

    csv_path = os.path.join(args.out_dir, 'calibrazione_rms.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['canale', 'rms_dbfs', 'scarto_db'])
        for c, d, s in zip(ch, dbfs, scarto):
            w.writerow([int(c), round(float(d), 3), round(float(s), 3)])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(ch, scarto, color='C0')
    for c, s in zip(ch, scarto):
        ax.text(c, s, f'{s:+.2f}', ha='center',
                va='bottom' if s >= 0 else 'top', fontsize=8)
    ax.axhline(0, color='gray', lw=0.8)
    ax.set_xlabel('microfono (canale)')
    ax.set_ylabel('scarto dalla media (dB)')
    ax.set_title('Allineamento dei gain sul grappolo a 1 m\n'
                 f'dev.std fra microfoni = {scarto.std():.2f} dB, '
                 f'max-min = {scarto.max() - scarto.min():.2f} dB')
    ax.set_xticks(ch)
    ax.grid(True, alpha=0.3, axis='y')
    fig.tight_layout()
    figdir = os.path.join(args.out_dir, 'livelli')
    os.makedirs(figdir, exist_ok=True)
    fig.savefig(os.path.join(figdir, 'calibrazione_rms.png'), dpi=140)
    plt.close(fig)

    print(f'dev.std {scarto.std():.2f} dB, max-min '
          f'{scarto.max() - scarto.min():.2f} dB -> {csv_path}')


if __name__ == '__main__':
    main()
