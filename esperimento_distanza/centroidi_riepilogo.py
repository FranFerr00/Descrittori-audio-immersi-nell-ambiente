#!/usr/bin/env python3
"""Riepilogo e grafici delle centroidi per canale (dai CSV di analizza_divisi.py).

Per ogni cartella <out>/<nome>/ con gli 8 CSV per canale:
  - calcola una finestra di 2 s centrata sulla parte attiva (frame non-gated); i
    file il cui nome finisce per `_DO` (ora contengono solo la nota) usano invece
    tutta la parte attiva (file intero);
  - scrive centroidi_medie.csv (media/std 2 s e intero, per file x canale);
  - rigenera per ogni file 3 plot: intero (media mobile), grezzo, finestra 2 s;
  - rigenera i grafici d'insieme (CCB+CS e NOISE separati, 2 s e intero) con
    pastiglia=canale e valore in Hz sopra ogni dot;
  - rigenera la heatmap (deviazione per riga, finestra 2 s).

Uso:
    python esperimento_distanza/centroidi_riepilogo.py analisi/distanza
"""
import argparse
import csv
import glob
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HALF = 1.0          # mezza finestra centrata (s)
W_SMOOTH = 12       # media mobile (frame) per il plot intero lisciato
CMAP = plt.get_cmap('tab10')


def smooth(y, w):
    if len(y) < w or w < 2:
        return y
    return np.convolve(y, np.ones(w) / w, mode='same')


def famiglia(f):
    p = f.split('_')
    if f.startswith('CCB'):
        return f'CCB {p[1]} {p[2]}'
    if f.startswith('CS'):
        return f'CS {p[1]}'
    return 'NOISE'


def leggi_canali(d, base):
    """{ch: [(time, centroid) non-gated]} per la cartella d."""
    perch = {}
    for ch in range(1, 9):
        cs = glob.glob(os.path.join(d, f'{base}_ch{ch}_*_analisi.csv'))
        if not cs:
            continue
        perch[ch] = [(float(r['time']), float(r['centroid']))
                     for r in csv.DictReader(open(cs[0])) if r['gated'] == '0']
    return perch


def finestra(base, tutti_t):
    centro = (min(tutti_t) + max(tutti_t)) / 2
    if base.endswith('_DO'):
        # il DO ora contiene solo la nota: si usa tutta la parte attiva (file intero)
        return min(tutti_t), max(tutti_t), centro
    return centro - HALF, centro + HALF, centro


# ---------- plot per singolo file ----------

def plot_per_file(d, base, perch, lo, hi, centro):
    # intero lisciato
    for suff, grezzo in [('', False), ('_grezzo', True)]:
        fig, ax = plt.subplots(figsize=(14, 6))
        for ch in sorted(perch):
            if not perch[ch]:
                continue
            t = [x for x, _ in perch[ch]]
            c = np.array([y for _, y in perch[ch]])
            y = c if grezzo else smooth(c, W_SMOOTH)
            lw = 0.6 if grezzo else 1.2
            ax.plot(t, y, lw=lw, alpha=0.8 if grezzo else 1.0,
                    label=f'ch{ch} ({c.mean():.0f} Hz)')
        tip = 'grezzo (ogni frame)' if grezzo else f'media mobile {W_SMOOTH} frame'
        ax.set_xlabel('tempo (s)'); ax.set_ylabel('centroide spettrale (Hz)')
        ax.set_title(f'{base} — centroide per canale, intero ({tip})')
        ax.legend(ncol=2, fontsize=8); ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(d, f'{base}_centroid_canali{suff}.png'), dpi=130)
        plt.close(fig)

    # finestra 2 s
    fig, ax = plt.subplots(figsize=(10, 5))
    for ch in sorted(perch):
        tw = [(t, c) for t, c in perch[ch] if lo <= t <= hi]
        if not tw:
            continue
        t = [x for x, _ in tw]; c = np.array([y for _, y in tw])
        ax.plot(t, c, lw=1.0, marker='.', ms=3, label=f'ch{ch} ({c.mean():.0f} Hz)')
    tag = 'campione (intero)' if base.endswith('_DO') else f'centro {centro:.1f}s'
    ax.set_xlabel('tempo (s)'); ax.set_ylabel('centroide spettrale (Hz)')
    ax.set_title(f'{base} — finestra 2s ({lo:.1f}-{hi:.1f}s, {tag})')
    ax.legend(ncol=2, fontsize=8); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(d, f'{base}_centroid_canali_centro2s.png'), dpi=130)
    plt.close(fig)


# ---------- grafici d'insieme ----------

def carica_csv(path, col):
    dati = {}
    for r in csv.DictReader(open(path)):
        if r[col] == '':
            continue
        dati.setdefault(r['file'], {})[int(r['canale'])] = float(r[col])
    return dati


def overview(path, col, files, titolo, out_png, figw=20, figh=9):
    dati = carica_csv(path, col); x = np.arange(len(files))
    fig, ax = plt.subplots(figsize=(figw, figh))
    for ci, ch in enumerate(range(1, 9)):
        y = [dati[f].get(ch, np.nan) for f in files]
        col_ch = CMAP(ci)
        ax.plot(x, y, lw=1.0, color=col_ch, alpha=0.6, zorder=1)
        for xi, yi in zip(x, y):
            if np.isnan(yi):
                continue
            ax.text(xi, yi, str(ch), ha='center', va='center', fontsize=6,
                    fontweight='bold', color='white', zorder=3,
                    bbox=dict(boxstyle='circle,pad=0.16', fc=col_ch, ec='none'))
            ax.annotate(f'{yi:.0f}', (xi, yi), textcoords='offset points',
                        xytext=(0, 7), ha='center', va='bottom', fontsize=4.5,
                        color=col_ch, zorder=2)
    fams = [famiglia(f) for f in files]
    for i in range(1, len(files)):
        if fams[i] != fams[i - 1]:
            ax.axvline(i - 0.5, color='gray', ls=':', lw=0.8)
    seen = {}
    for i, fm in enumerate(fams):
        seen.setdefault(fm, []).append(i)
    ymax = ax.get_ylim()[1]
    for fm, idx in seen.items():
        ax.text(np.mean(idx), ymax, fm, ha='center', va='bottom', fontsize=8, color='dimgray')
    ax.margins(y=0.08)
    ax.set_xticks(x); ax.set_xticklabels(files, rotation=90, fontsize=7)
    ax.set_ylabel(titolo)
    ax.set_title('Centroidi medie per canale (pastiglia = canale, sopra = Hz)')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout(); plt.savefig(out_png, dpi=150); plt.close(fig)


def heatmap(path, col, files, out_png):
    dati = carica_csv(path, col)
    M = np.array([[dati[f].get(ch, np.nan) for ch in range(1, 9)] for f in files])
    dev = M - np.nanmean(M, axis=1, keepdims=True)
    vmax = np.nanmax(np.abs(dev))
    fig, ax = plt.subplots(figsize=(9, 11))
    im = ax.imshow(dev, aspect='auto', cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    ax.set_xticks(range(8)); ax.set_xticklabels([f'ch{c}' for c in range(1, 9)])
    ax.set_yticks(range(len(files))); ax.set_yticklabels(files, fontsize=7)
    for i in range(len(files)):
        for j in range(8):
            v = dev[i, j]
            if np.isnan(v):
                continue
            ax.text(j, i, f'{v:+.0f}', ha='center', va='center', fontsize=6,
                    color='black' if abs(v) < vmax * 0.6 else 'white')
    ax.set_title('Profilo per canale: deviazione dalla media del file (Hz)\n'
                 'centroide, media sul file intero')
    cb = fig.colorbar(im, ax=ax, shrink=0.6); cb.set_label('Hz rispetto alla media del file')
    plt.tight_layout(); plt.savefig(out_png, dpi=130); plt.close(fig)


def profilo_onda(path, col, out_png):
    """Profilo per canale: deviazione media dalla media del file, per gruppo.

    Mostra l'onda dei CCB (cresta ch3, avvallamento ch6) confrontata con i CS.
    """
    dati = carica_csv(path, col)

    def prof(files):
        M = np.array([[dati[f][ch] for ch in range(1, 9)] for f in files])
        dev = M - M.mean(axis=1, keepdims=True)
        return dev.mean(axis=0), dev.std(axis=0)

    gruppi = [
        ('CCB oriz', lambda f: f.startswith('CCB') and '_oriz_' in f, 'C0'),
        ('CCB vert', lambda f: f.startswith('CCB') and '_vert_' in f, 'C1'),
        ('CS',       lambda f: f.startswith('CS'), 'C2'),
    ]
    x = np.arange(1, 9)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for nome, sel, c in gruppi:
        files = [f for f in dati if sel(f)]
        if not files:
            continue
        m, s = prof(files)
        ax.errorbar(x, m, yerr=s, marker='o', ms=6, lw=2, capsize=3,
                    label=f'{nome} (n={len(files)})', color=c)
    ax.axhline(0, color='gray', lw=0.8)
    ax.set_xlabel('canale')
    ax.set_ylabel('deviazione media dalla media del file (Hz)')
    ax.set_title("Profilo per canale della centroide: l'onda dei CCB "
                 "(picco ch3, avvallamento ch6)")
    ax.set_xticks(x); ax.set_xticklabels([f'ch{i}' for i in x])
    ax.legend(); ax.grid(True, alpha=0.3)
    plt.tight_layout(); plt.savefig(out_png, dpi=130); plt.close(fig)


def profilo_onda_separati(path, col, out_png):
    """Tre pannelli separati del profilo per canale (deviazione dalla media del file):
    contrabbasso orizzontale, contrabbasso verticale e soprano. Asse y condiviso."""
    dati = carica_csv(path, col)

    def prof(sel):
        files = [f for f in dati if sel(f)]
        if not files:
            return None, None, 0
        M = np.array([[dati[f][ch] for ch in range(1, 9)] for f in files])
        dev = M - M.mean(axis=1, keepdims=True)
        return dev.mean(axis=0), dev.std(axis=0), len(files)

    pannelli = [
        ('Contrabbasso orizzontale', lambda f: f.startswith('CCB') and '_oriz_' in f and 'CLUSTER' in f, 'C0'),
        ('Contrabbasso verticale',   lambda f: f.startswith('CCB') and '_vert_' in f and 'CLUSTER' in f, 'C1'),
        ('Soprano',                  lambda f: f.startswith('CS') and 'CLUSTER' in f,                    'C2'),
    ]
    x = np.arange(1, 9)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    for ax, (titolo, sel, c) in zip(axes, pannelli):
        m, s, n = prof(sel)
        if m is not None:
            ax.errorbar(x, m, yerr=s, marker='o', ms=6, lw=2, capsize=3,
                        color=c, label=f'n={n}')
        ax.axhline(0, color='gray', lw=0.8)
        ax.set_title(titolo)
        ax.set_xlabel('canale (= distanza in m)')
        ax.set_xticks(x); ax.set_xticklabels([f'ch{k}' for k in x])
        ax.legend(loc='upper right', fontsize=8); ax.grid(True, alpha=0.3)
    axes[0].set_ylabel('deviazione dalla media del file (Hz)')
    fig.suptitle('Profilo per canale del centroide (soli cluster): '
                 'orizzontale, verticale e soprano separati')
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(out_png, dpi=130); plt.close(fig)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('root', help='cartella di output di analizza_divisi.py')
    p.add_argument('--no-per-file', action='store_true',
                   help='salta i 3 plot per ogni file (solo CSV + insiemi)')
    args = p.parse_args(argv)

    prese = sorted(d for d in glob.glob(os.path.join(args.root, 'centroide', '*'))
                   if os.path.isdir(d))
    rows = []
    for d in prese:
        base = os.path.basename(d)
        perch = leggi_canali(d, base)
        tutti_t = [t for ch in perch for t, _ in perch[ch]]
        if not tutti_t:
            for ch in sorted(perch):
                rows.append([base, ch, '', '', 0, '', '', 0, ''])
            continue
        lo, hi, centro = finestra(base, tutti_t)
        if not args.no_per_file:
            plot_per_file(d, base, perch, lo, hi, centro)
        for ch in sorted(perch):
            intero = np.array([y for _, y in perch[ch]])
            win = np.array([y for t, y in perch[ch] if lo <= t <= hi])
            if win.size == 0:
                rows.append([base, ch, '', '', 0,
                             round(intero.mean(), 2), round(intero.std(), 2),
                             intero.size, round(centro, 2)])
                continue
            rows.append([base, ch, round(win.mean(), 2), round(win.std(), 2), win.size,
                         round(intero.mean(), 2), round(intero.std(), 2), intero.size,
                         round(centro, 2)])

    csv_path = os.path.join(args.root, 'centroidi_medie.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['file', 'canale', 'media_centro2s', 'std_centro2s', 'n_centro2s',
                    'media_intero', 'std_intero', 'n_intero', 'centro_s'])
        w.writerows(rows)
    print('scritto', csv_path)

    files = list(carica_csv(csv_path, 'media_intero').keys())
    suoni = [f for f in files if not f.startswith('NOISE')]
    noise = [f for f in files if f.startswith('NOISE')]
    R = os.path.join(args.root, 'centroide')
    os.makedirs(R, exist_ok=True)
    overview(csv_path, 'media_intero', suoni, 'centroide media (Hz) — file intero',
             os.path.join(R, 'centroidi_medie.png'))
    overview(csv_path, 'media_intero', noise, 'centroide media (Hz) — file intero',
             os.path.join(R, 'centroidi_medie_noise.png'), figw=8)
    heatmap(csv_path, 'media_intero', files, os.path.join(R, 'centroidi_heatmap.png'))
    profilo_onda(csv_path, 'media_intero', os.path.join(R, 'profilo_onda_canali.png'))
    profilo_onda_separati(csv_path, 'media_intero',
                          os.path.join(R, 'profilo_onda_separati.png'))
    print('rigenerati: insiemi (file intero, noise a parte), heatmap, profilo onda')


if __name__ == '__main__':
    main()
