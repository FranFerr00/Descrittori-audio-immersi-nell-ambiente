#!/usr/bin/env python3
"""
Matrice di correlazione fra i descrittori sul corpus.

Raccoglie tutti i CSV `*_analisi.csv` sotto una o piu' cartelle radice,
concatena i frame (scartando i frame gated), calcola la matrice di
correlazione di Pearson fra le colonne dei descrittori, e produce:

    <out>/correlazione_globale.csv     matrice numerica
    <out>/correlazione_globale.png     heatmap
    <out>/correlazione_per_catalogo/<nome>.{csv,png}   una per ogni catalogo

L'analisi per catalogo serve a verificare la stabilita' del segno fra
strumenti diversi: se due descrittori sono correlati positivamente sul
clarinetto e negativamente sul timpano, non sono raggruppabili in famiglia.

Uso:
    python correlazione_descrittori.py analisi/ --out cataloghi/correlazione
    python correlazione_descrittori.py segnali/francesco/ --out /tmp/corr
"""

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Colonne dei CSV che NON sono descrittori da correlare
NON_DESC = {'frame', 'time', 'gated', 'n_peaks'}


def find_csvs(root: Path):
    return sorted(root.rglob('*_analisi.csv'))


def load_concat(csvs, drop_gated=True):
    frames = []
    for p in csvs:
        try:
            df = pd.read_csv(p)
        except Exception as e:
            print(f'  skip {p}: {e}', file=sys.stderr)
            continue
        if drop_gated and 'gated' in df.columns:
            df = df[df['gated'] == 0]
        if len(df) == 0:
            continue
        frames.append(df)
    if not frames:
        return None
    return pd.concat(frames, ignore_index=True)


def descriptor_cols(df):
    cols = [c for c in df.columns if c not in NON_DESC]
    # Tieni solo colonne numeriche e con varianza non nulla
    keep = []
    for c in cols:
        if not np.issubdtype(df[c].dtype, np.number):
            continue
        if df[c].std(skipna=True) == 0 or df[c].isna().all():
            continue
        keep.append(c)
    return keep


def plot_corr(corr: pd.DataFrame, title: str, out_png: Path):
    n = len(corr.columns)
    fig, ax = plt.subplots(figsize=(max(6, 0.55 * n + 2),
                                    max(5, 0.55 * n + 1.5)))
    im = ax.imshow(corr.values, vmin=-1, vmax=1, cmap='RdBu_r', aspect='equal')
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(corr.columns, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(corr.columns, fontsize=8)
    for i in range(n):
        for j in range(n):
            v = corr.values[i, j]
            if np.isnan(v):
                continue
            ax.text(j, i, f'{v:+.2f}',
                    ha='center', va='center', fontsize=6,
                    color='white' if abs(v) > 0.55 else 'black')
    ax.set_title(title, fontsize=10)
    fig.colorbar(im, ax=ax, shrink=0.8, label='Pearson r')
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)


def compute_and_save(df, label, out_dir: Path):
    cols = descriptor_cols(df)
    if len(cols) < 2:
        print(f'  [{label}] meno di 2 descrittori utilizzabili, salto')
        return None
    corr = df[cols].corr(method='pearson')
    out_dir.mkdir(parents=True, exist_ok=True)
    corr.to_csv(out_dir / f'{label}.csv', float_format='%.4f')
    plot_corr(corr, f'Correlazione descrittori — {label} (n_frame={len(df)})',
              out_dir / f'{label}.png')
    print(f'  [{label}] {len(cols)} descrittori, {len(df)} frame -> '
          f'{out_dir / (label + ".csv")}')
    return corr


def split_per_catalogo(csvs, root: Path):
    """Raggruppa i CSV per primo segmento di path relativo a root.

    Es. root=segnali/francesco/, csv=segnali/francesco/timpano/analisi/008/...
    -> catalogo='timpano'.
    """
    groups = {}
    for p in csvs:
        try:
            rel = p.relative_to(root)
        except ValueError:
            rel = p
        parts = rel.parts
        if len(parts) < 2:
            continue
        # Trova il primo segmento prima di "analisi"
        key = parts[0]
        for i, seg in enumerate(parts):
            if seg == 'analisi' and i > 0:
                key = parts[i - 1]
                break
        groups.setdefault(key, []).append(p)
    return groups


def per_sample_summary(csvs, out_dir: Path, root: Path, min_frames=30, drop_gated=True):
    """Per ogni CSV calcola la matrice di correlazione locale (intra-gesto)
    e poi aggrega la distribuzione di ogni coppia attraverso i gesti.

    Salva:
        per_sample_media.csv     media di r attraverso i gesti
        per_sample_std.csv       deviazione standard di r
        per_sample_frac_pos.csv  frazione di gesti con r > 0
        per_sample_stabili.csv   coppie ordinate per stabilita' (media e std)
        per_sample_media.png     heatmap della media
        per_sample_std.png       heatmap della std (instabilita')
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    # Determina le colonne descrittore dal primo CSV utile
    all_cols = None
    per_gesto = []  # list of (label, corr DataFrame)
    skipped = 0
    for p in csvs:
        try:
            df = pd.read_csv(p)
        except Exception:
            skipped += 1
            continue
        if drop_gated and 'gated' in df.columns:
            df = df[df['gated'] == 0]
        if len(df) < min_frames:
            skipped += 1
            continue
        cols = descriptor_cols(df)
        if len(cols) < 2:
            skipped += 1
            continue
        if all_cols is None:
            all_cols = cols
        # Usa l'intersezione con la prima colonna trovata per coerenza
        cols = [c for c in all_cols if c in cols]
        corr = df[cols].corr(method='pearson')
        stem = p.stem.replace('_hann_ov50_10000hz_analisi', '')
        # Catalogo di provenienza: primo segmento del path relativo a root,
        # oppure il segmento prima di "analisi" se compare piu' in profondita'
        try:
            rel = p.relative_to(root)
        except ValueError:
            rel = p
        parts = rel.parts
        cat = parts[0] if parts else ''
        for i, seg in enumerate(parts):
            if seg == 'analisi' and i > 0:
                cat = parts[i - 1]
                break
        label = f'{cat}__{stem}' if cat else stem
        per_gesto.append((label, corr))

    if not per_gesto:
        print('  nessun gesto utilizzabile')
        return
    print(f'  {len(per_gesto)} gesti analizzati ({skipped} scartati: <{min_frames} frame)')

    # Salva la matrice singola di ciascun gesto, organizzata per catalogo
    singoli_dir = out_dir / 'singoli'
    for label, corr in per_gesto:
        cat, _, stem = label.partition('__')
        if not stem:
            cat, stem = '_misc', cat
        sub = singoli_dir / cat
        sub.mkdir(parents=True, exist_ok=True)
        corr.to_csv(sub / f'{stem}.csv', float_format='%.4f')
        plot_corr(corr, f'{cat}/{stem}', sub / f'{stem}.png')

    cols = list(per_gesto[0][1].columns)
    n = len(cols)
    stack = np.stack([c.reindex(index=cols, columns=cols).values
                      for _, c in per_gesto], axis=0)  # (gesti, n, n)

    mean_mat = np.nanmean(stack, axis=0)
    std_mat = np.nanstd(stack, axis=0)
    frac_pos = np.nanmean(stack > 0, axis=0)

    pd.DataFrame(mean_mat, index=cols, columns=cols).to_csv(
        out_dir / 'per_sample_media.csv', float_format='%.4f')
    pd.DataFrame(std_mat, index=cols, columns=cols).to_csv(
        out_dir / 'per_sample_std.csv', float_format='%.4f')
    pd.DataFrame(frac_pos, index=cols, columns=cols).to_csv(
        out_dir / 'per_sample_frac_pos.csv', float_format='%.4f')

    plot_corr(pd.DataFrame(mean_mat, index=cols, columns=cols),
              f'Correlazione intra-gesto — media ({len(per_gesto)} gesti)',
              out_dir / 'per_sample_media.png')
    # Per la std uso una scala 0..1 con colormap diversa
    fig, ax = plt.subplots(figsize=(max(6, 0.55*n+2), max(5, 0.55*n+1.5)))
    im = ax.imshow(std_mat, vmin=0, vmax=0.6, cmap='magma_r', aspect='equal')
    ax.set_xticks(range(n)); ax.set_yticks(range(n))
    ax.set_xticklabels(cols, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(cols, fontsize=8)
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f'{std_mat[i,j]:.2f}', ha='center', va='center',
                    fontsize=6, color='white' if std_mat[i,j] > 0.35 else 'black')
    ax.set_title(f'Deviazione standard di r fra i gesti (alto = instabile)')
    fig.colorbar(im, ax=ax, shrink=0.8, label='std(r)')
    fig.tight_layout()
    fig.savefig(out_dir / 'per_sample_std.png', dpi=150)
    plt.close(fig)

    # Tabella ordinata: coppie piu' stabili (|media| alto, std bassa) e piu' instabili
    rows = []
    for i in range(n):
        for j in range(i+1, n):
            rows.append({
                'A': cols[i], 'B': cols[j],
                'media_r': mean_mat[i, j],
                'std_r': std_mat[i, j],
                'frac_positivi': frac_pos[i, j],
                'frac_negativi': 1 - frac_pos[i, j],
            })
    summary = pd.DataFrame(rows)
    summary['stabilita'] = summary['media_r'].abs() - summary['std_r']
    summary = summary.sort_values('stabilita', ascending=False)
    summary.to_csv(out_dir / 'per_sample_stabili.csv',
                   index=False, float_format='%.4f')
    print(f'  salvato {out_dir / "per_sample_stabili.csv"}')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('root', help='Cartella radice da cui cercare *_analisi.csv')
    ap.add_argument('--out', default='cataloghi/correlazione',
                    help='Cartella di output (default: cataloghi/correlazione)')
    ap.add_argument('--no-per-catalogo', action='store_true',
                    help='Salta le matrici per singolo catalogo')
    ap.add_argument('--per-sample', action='store_true',
                    help='Calcola la correlazione dentro ogni gesto e ne aggrega la distribuzione')
    ap.add_argument('--min-frames', type=int, default=30,
                    help='Frame minimi per includere un gesto nella per-sample analysis')
    ap.add_argument('--include-gated', action='store_true',
                    help='Non scartare i frame con gated=1')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out).resolve()

    csvs = find_csvs(root)
    if not csvs:
        print(f'Nessun *_analisi.csv trovato sotto {root}', file=sys.stderr)
        sys.exit(1)
    print(f'Trovati {len(csvs)} CSV sotto {root}')

    print('Matrice globale:')
    df_all = load_concat(csvs, drop_gated=not args.include_gated)
    if df_all is None:
        print('Nessun frame utilizzabile.', file=sys.stderr)
        sys.exit(1)
    compute_and_save(df_all, 'correlazione_globale', out_dir)

    if args.per_sample:
        print('\nCorrelazione intra-gesto:')
        per_sample_summary(csvs, out_dir / 'per_sample', root,
                           min_frames=args.min_frames,
                           drop_gated=not args.include_gated)

    if not args.no_per_catalogo:
        groups = split_per_catalogo(csvs, root)
        if len(groups) > 1:
            print(f'\nMatrici per catalogo ({len(groups)} cataloghi):')
            per_dir = out_dir / 'correlazione_per_catalogo'
            for name, paths in sorted(groups.items()):
                df = load_concat(paths, drop_gated=not args.include_gated)
                if df is None:
                    continue
                compute_and_save(df, name, per_dir)


if __name__ == '__main__':
    main()
