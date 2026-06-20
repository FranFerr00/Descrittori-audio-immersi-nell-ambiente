#!/usr/bin/env python3
"""Attenuazione del rumore sulla distanza vs legge dell'inverso della distanza.

Per i file del noise a distanza (orizzontale e verticale), 8 canali = 8 distanze
(ch_n = n m), calcola l'RMS per canale, lo riporta in dB relativo al microfono a 1 m
e lo confronta con il riferimento di campo libero (pressione ~ 1/r, cioe' -6 dB per
raddoppio = -20 log10(d)). Evidenzia i microfoni a 1, 2, 4, 8 m e stampa il rapporto
misurato per ciascun raddoppio. Salva un CSV e un grafico in scala log sulla distanza.

NB sul riferimento: il prompt parla di "1/sqrt(2) al raddoppio" (-3 dB, dipendenza
1/sqrt(r)), diverso dalla legge di campo libero (-6 dB, 1/r). Lo script resta neutro:
disegna il misurato e il riferimento -6 dB, e riporta i delta misurati per raddoppio,
cosi' la retta "ufficiale" del report si sceglie guardando i numeri.

Uso:
    python esperimento_distanza/attenuazione_distanza.py \\
        esperimento_distanza/2026-06-13-FRAFER-TEST-DISTANZA-GIUSTO/divisi/NOISE_oriz_1-9mt.wav \\
        esperimento_distanza/2026-06-13-FRAFER-TEST-DISTANZA-GIUSTO/divisi/NOISE_vert_1-9mt.wav
"""
import argparse
import csv
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from livelli import rms_per_canale


def teorico_campolibero(distanze):
    """dB relativi al riferimento (prima distanza) per pressione ~ 1/r."""
    d = np.asarray(distanze, dtype=float)
    return -20.0 * np.log10(d / d[0])


def raddoppi(distanze, rel_db, coppie=((1, 2), (2, 4), (4, 8))):
    """[(d_da, d_a, delta_dB_misurato)] per i raddoppi richiesti, se presenti."""
    dist = list(int(x) for x in distanze)
    out = []
    for a, b in coppie:
        if a in dist and b in dist:
            out.append((a, b, float(rel_db[dist.index(b)] - rel_db[dist.index(a)])))
    return out


# Misura indipendente col fonometro in sala (curva A): 96 dBA a 1 m, poi -3 dB a ogni
# raddoppio. Conferma che la legge della stanza e' 1/sqrt(2) (-3 dB), non il campo libero.
FONOMETRO_DBA = {1: 96.0, 2: 93.0, 4: 90.0, 8: 87.0}


def teorico_per_raddoppio(distanze, db_raddoppio):
    """dB relativi al riferimento per una legge di db_raddoppio dB a ogni raddoppio."""
    d = np.asarray(distanze, dtype=float)
    return db_raddoppio * np.log2(d / d[0])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('wav', nargs='+', help='uno o piu wav noise a distanza (oriz, vert)')
    p.add_argument('-o', '--out-dir', default='analisi/distanza')
    args = p.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    rows = []
    n_max = 0
    for path in args.wav:
        base = os.path.splitext(os.path.basename(path))[0]
        modo = 'vert' if 'vert' in base.lower() else 'oriz'
        lin, dbfs = rms_per_canale(path)
        distanze = np.arange(1, len(dbfs) + 1)
        n_max = max(n_max, len(dbfs))
        rel = dbfs - dbfs[0]
        ax.plot(distanze, rel, marker='o', label=f'misurato {modo}')
        for d, r, ab in zip(distanze, rel, dbfs):
            rows.append([modo, int(d), round(float(r), 3), round(float(ab), 3)])
            if d in (1, 2, 4, 8):
                ax.annotate(f'{r:.1f}', (d, r), textcoords='offset points',
                            xytext=(0, 8), ha='center', fontsize=8)
        rad = raddoppi(distanze, rel)
        print(modo, 'raddoppi (dB):',
              ', '.join(f'{a}->{b}m {dlt:.2f}' for a, b, dlt in rad))

    distanze = np.arange(1, n_max + 1)
    ax.plot(distanze, teorico_campolibero(distanze), 'k--',
            label='campo libero ($-6$ dB/raddoppio)')
    ax.plot(distanze, teorico_per_raddoppio(distanze, -3.0), color='0.45', ls=':', lw=1.8,
            label='$1/\\sqrt{2}$ ($-3$ dB/raddoppio)')
    fx = sorted(FONOMETRO_DBA)
    f0 = FONOMETRO_DBA[fx[0]]
    ax.plot(fx, [FONOMETRO_DBA[k] - f0 for k in fx], marker='s', ms=9, lw=0,
            color='C2', label='fonometro in sala (dBA)')
    for d in (1, 2, 4, 8):
        if d <= n_max:
            ax.axvline(d, color='gray', ls=':', lw=0.6)
    ax.set_xscale('log', base=2)
    ax.set_xticks(distanze)
    ax.set_xticklabels(distanze)
    ax.set_xlabel('distanza (m)')
    ax.set_ylabel('livello relativo al microfono a 1 m (dB)')
    ax.set_title('Attenuazione del rumore sulla distanza: misura, fonometro e riferimenti')
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')
    fig.tight_layout()
    figdir = os.path.join(args.out_dir, 'livelli')
    os.makedirs(figdir, exist_ok=True)
    fig.savefig(os.path.join(figdir, 'attenuazione_distanza.png'), dpi=140)
    plt.close(fig)

    csv_path = os.path.join(args.out_dir, 'attenuazione_distanza.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['modo', 'distanza_m', 'rel_db', 'rms_dbfs'])
        w.writerows(rows)
    print('scritto', csv_path)


if __name__ == '__main__':
    main()
