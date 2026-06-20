#!/usr/bin/env python3
"""
Aggrega i CSV di analisi dei singoli segmenti in grafici unici per categoria.

Legge le cartelle NN_*/ dentro la directory indicata, concatena i frame dei
CSV in ordine di numero e genera 4 PNG (forma, distribuzione, tonalita',
dinamica) con linee verticali ai confini dei segmenti ed etichette in alto.

Uso:
    python aggrega_grafici.py segnali
    python aggrega_grafici.py segnali/test_segnali_-30db
    python aggrega_grafici.py segnali/recs-002
"""

import os
import sys
import csv
import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt

CATEGORIES = {
    'forma': [
        ('centroid', 'Centroid (Hz)'),
        ('spread', 'Spread (Hz)'),
        ('rolloff', 'Rolloff (Hz)'),
        ('slope', 'Slope'),
        ('obsir_std', 'OBSIR-std'),
    ],
    'distribuzione': [
        ('flatness', 'Flatness'),
        ('crest', 'Crest Factor'),
        ('skewness', 'Skewness'),
        ('kurtosis', 'Kurtosis'),
        ('entropy', 'Entropy'),
    ],
    'tonalita': [
        ('tpr', 'TPR'),
        ('n_peaks', 'N. Picchi'),
        ('tonality', 'Tonality'),
    ],
    'dinamica': [
        ('flux', 'Flux'),
        ('irregularity', 'Irregularity'),
        ('zcr', 'ZCR'),
    ],
}


def read_csv(path):
    data = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            for k, v in row.items():
                data.setdefault(k, []).append(float(v))
    return {k: np.array(v) for k, v in data.items()}


def collect_segments(base_dir, only=None):
    """Ritorna [(nome, csv_path), ...] ordinato per NN.

    Se `only` e' una lista di stringhe, include solo le sottocartelle il cui
    nome inizia con uno dei prefissi indicati (per i cataloghi strumentali
    passare la lista degli id "ufficiali").
    """
    segs = []
    for sub in sorted(os.listdir(base_dir)):
        full = os.path.join(base_dir, sub)
        if not os.path.isdir(full) or not sub[:2].isdigit():
            continue
        if only is not None and not any(sub == o or sub.startswith(o + '_') for o in only):
            continue
        csvs = glob.glob(os.path.join(full, '*_analisi.csv'))
        if csvs:
            segs.append((sub, sorted(csvs)[0]))
    return segs


def aggregate(segments):
    """Concatena i frame di tutti i segmenti.

    Ritorna: dict {descrittore: array concatenato}, lista dei confini in
    numero di frame, lista dei nomi dei segmenti.
    """
    all_data = {}
    boundaries = [0]
    names = []
    for name, path in segments:
        d = read_csv(path)
        n = len(next(iter(d.values())))
        names.append(name)
        boundaries.append(boundaries[-1] + n)
        for k, v in d.items():
            all_data.setdefault(k, []).append(v)
    return ({k: np.concatenate(v) for k, v in all_data.items()},
            boundaries, names)


def plot_category(cat_name, descriptors, data, boundaries, names, out_path, title):
    n = len(descriptors)
    fig, axes = plt.subplots(n, 1, figsize=(16, 2.2 * n + 1), sharex=True)
    if n == 1:
        axes = [axes]
    x = np.arange(len(next(iter(data.values()))))

    for ax, (key, label) in zip(axes, descriptors):
        if key not in data:
            ax.set_ylabel(label)
            ax.text(0.5, 0.5, f'descrittore "{key}" assente',
                    transform=ax.transAxes, ha='center', va='center')
            continue
        ax.plot(x, data[key], linewidth=0.7, color='steelblue')
        ax.set_ylabel(label)
        ax.grid(True, alpha=0.3)
        # linee verticali ai confini
        for b in boundaries[1:-1]:
            ax.axvline(b, color='gray', linewidth=0.4, alpha=0.6)

    # etichette segmenti in alto
    ax_top = axes[0]
    ymin, ymax = ax_top.get_ylim()
    for i, name in enumerate(names):
        mid = (boundaries[i] + boundaries[i + 1]) / 2
        short = name.split('_', 1)[-1] if '_' in name else name
        ax_top.text(mid, ymax, short, rotation=90, va='bottom', ha='center',
                    fontsize=6, color='dimgray')

    axes[-1].set_xlabel('frame (tutti i segmenti concatenati)')
    fig.suptitle(title, y=1.0)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches='tight')
    plt.close(fig)
    print(f'  {out_path}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dir', help='Cartella contenente le sottocartelle NN_*/')
    parser.add_argument('--prefix', default=None,
                        help='Prefisso dei PNG di output (default: nome della cartella)')
    parser.add_argument('--only', default=None,
                        help='Lista di id (separati da virgola) da includere. '
                             'Utile per cataloghi in cui solo alcuni campioni '
                             'sono considerati ufficiali.')
    args = parser.parse_args()

    base_dir = os.path.abspath(args.dir)
    if not os.path.isdir(base_dir):
        print(f'Errore: {base_dir} non e\' una cartella', file=sys.stderr)
        sys.exit(1)

    only_ids = [s.strip() for s in args.only.split(',')] if args.only else None
    segments = collect_segments(base_dir, only=only_ids)
    if not segments:
        msg = f'Errore: nessun segmento NN_* trovato in {base_dir}'
        if only_ids:
            msg += f' (filtro --only={only_ids})'
        print(msg, file=sys.stderr)
        sys.exit(1)

    print(f'Trovati {len(segments)} segmenti in {base_dir}')
    data, boundaries, names = aggregate(segments)
    print(f'Totale frame concatenati: {boundaries[-1]}')

    prefix = args.prefix or os.path.basename(base_dir.rstrip('/'))
    print(f'\n=== Grafici aggregati ({prefix}) ===')
    for cat_name, descriptors in CATEGORIES.items():
        out_path = os.path.join(base_dir, f'{prefix}_aggregato_{cat_name}.png')
        title = f'{prefix} — {cat_name} (aggregato)'
        plot_category(cat_name, descriptors, data, boundaries, names,
                      out_path, title)


if __name__ == '__main__':
    main()
