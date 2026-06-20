#!/usr/bin/env python3
"""Medie per canale dei 16 descrittori, in stile centroidi_medie, una PNG per famiglia.

Legge i CSV per-canale prodotti da analizza_divisi.py (tutti e 16 i descrittori),
calcola la media di ogni descrittore sulla finestra 2 s (la stessa di
centroidi_riepilogo.py) per ogni file x canale, e disegna 4 figure sugli strumenti
(forma / distribuzione / tonalita / dinamica). In ogni figura un pannello per
descrittore nello stile di centroidi_medie.png: X = i file, una linea per canale con
pastiglia del canale e il valore annotato sul dot, separatori e nomi dei gruppi.
Disegna inoltre, per il rumore: medie_<famiglia>_noise.png (stesso stile delle figure
strumenti, X = file NOISE, pastiglia per canale) e medie_noise.png (vista compatta dei
16 descrittori vs distanza, canale = metri, una curva per orientamento).

Uso:
    python esperimento_distanza/profili_famiglie.py analisi/distanza
"""
import argparse
import csv
import glob
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from centroidi_riepilogo import famiglia

# Stesse 4 famiglie/etichette di scripts/aggrega_grafici.py (CATEGORIES), ricopiate
# qui per tenere lo script locale autosufficiente.
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
DESCRITTORI = [d for _, lst in CATEGORIES.items() for d, _ in lst]
CMAP = plt.get_cmap('tab10')


def leggi_canali_multi(d, base):
    """{ch: [(time, {desc: val})]} sui frame non-gated, per la cartella d."""
    perch = {}
    for ch in range(1, 9):
        cs = glob.glob(os.path.join(d, f'{base}_ch{ch}_*_analisi.csv'))
        if not cs:
            continue
        righe = []
        with open(cs[0]) as fh:
            for r in csv.DictReader(fh):
                if r['gated'] != '0':
                    continue
                righe.append((float(r['time']),
                              {desc: float(r[desc]) for desc in DESCRITTORI if desc in r}))
        perch[ch] = righe
    return perch


def medie_file(d, base):
    """{ch: {desc: media}} su tutta la parte attiva del file (frame non-gated; vuoto se
    niente attivo)."""
    perch = leggi_canali_multi(d, base)
    tutti_t = [t for ch in perch for t, _ in perch[ch]]
    if not tutti_t:
        return {}
    lo, hi = min(tutti_t), max(tutti_t)
    out = {}
    for ch, righe in perch.items():
        in_win = [vals for t, vals in righe if lo <= t <= hi]
        if not in_win:
            continue
        medie = {}
        for desc in DESCRITTORI:
            v = [vals[desc] for vals in in_win if desc in vals]
            if v:
                medie[desc] = float(np.mean(v))
        out[ch] = medie
    return out


def medie_tutti_file(root, solo_noise=False):
    """(files, {file: {ch: {desc: media}}}) in ordine. Di default i file non-NOISE;
    con solo_noise=True i soli file NOISE (per le figure di famiglia del rumore)."""
    files = []
    perfile = {}
    for d in sorted(glob.glob(os.path.join(root, 'centroide', '*'))):
        if not os.path.isdir(d):
            continue
        base = os.path.basename(d)
        if base.startswith('NOISE') != solo_noise:
            continue
        mf = medie_file(d, base)
        if not mf:
            continue
        files.append(base)
        perfile[base] = mf
    return files, perfile


def _fmt_valore(v):
    """Formato adattivo: piu' decimali per descrittori a scala piccola."""
    a = abs(v)
    if a >= 100:
        return f'{v:.0f}'
    if a >= 1:
        return f'{v:.2f}'
    if a >= 0.01:
        return f'{v:.3f}'
    return f'{v:.4f}'


def _disegna_overview(ax, dati, files, mostra_label):
    """Disegna un pannello stile centroidi_medie su `ax`.

    `dati` = {file: {canale: valore}}. Pastiglia = numero canale, valore annotato
    sul dot, separatori e nomi dei gruppi di segnale (via famiglia()). Replica lo
    stile di centroidi_riepilogo.overview.
    """
    x = np.arange(len(files))
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
            ax.annotate(_fmt_valore(yi), (xi, yi), textcoords='offset points',
                        xytext=(0, 7), ha='center', va='bottom', fontsize=4.5,
                        color=col_ch, zorder=2)
    fams = [famiglia(f) for f in files]
    for i in range(1, len(files)):
        if fams[i] != fams[i - 1]:
            ax.axvline(i - 0.5, color='gray', ls=':', lw=0.8)
    if mostra_label:
        seen = {}
        for i, fm in enumerate(fams):
            seen.setdefault(fm, []).append(i)
        ymax = ax.get_ylim()[1]
        for fm, idx in seen.items():
            ax.text(np.mean(idx), ymax, fm, ha='center', va='bottom',
                    fontsize=8, color='dimgray')
    ax.margins(y=0.08)


def plot_famiglia(fam, descs, perfile, files, out_png, figw=20):
    """Una figura per famiglia: un pannello stile centroidi_medie per descrittore."""
    n = len(descs)
    fig, axes = plt.subplots(n, 1, figsize=(figw, 2.8 * n), squeeze=False)
    for i, (desc, label) in enumerate(descs):
        ax = axes[i][0]
        dati = {f: {ch: perfile[f][ch][desc]
                    for ch in perfile[f] if desc in perfile[f][ch]}
                for f in files}
        _disegna_overview(ax, dati, files, mostra_label=(i == 0))
        ax.set_ylabel(label, fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_xticks(range(len(files)))
        if i == n - 1:
            ax.set_xticklabels(files, rotation=90, fontsize=7)
        else:
            ax.set_xticklabels([])
    fig.suptitle(f'Medie per canale — famiglia {fam} '
                 f'(pastiglia = canale, sopra = valore; 2 s, DO intero)', fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.99])
    fig.savefig(out_png, dpi=150)
    plt.close(fig)


# I file NOISE a distanza sono una spazzata sui canali (ch_n = n metri): per loro
# l'asse naturale e' la distanza, una curva per orientamento.
NOISE_DISTANZA = [
    ('NOISE_oriz_1-9mt', 'orizzontale', 'C0'),
    ('NOISE_vert_1-9mt', 'verticale', 'C1'),
]


def curve_noise_distanza(root):
    """[(label, colore, {ch: {desc: media}})] per i file NOISE a distanza presenti."""
    out = []
    for base, label, col in NOISE_DISTANZA:
        d = os.path.join(root, 'centroide', base)
        if not os.path.isdir(d):
            continue
        mf = medie_file(d, base)
        if mf:
            out.append((label, col, mf))
    return out


def plot_noise(root, out_png):
    """Griglia righe-per-famiglia dei 16 descrittori del rumore vs distanza (canale=metri),
    una curva per orientamento. Ritorna False se non ci sono file NOISE a distanza."""
    curve = curve_noise_distanza(root)
    if not curve:
        return False
    fams = list(CATEGORIES.items())
    nrow = len(fams)
    ncol = max(len(descs) for _, descs in fams)
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.3 * ncol, 3.0 * nrow), squeeze=False)
    handles = {}
    for ri, (fam, descs) in enumerate(fams):
        for ci in range(ncol):
            ax = axes[ri][ci]
            if ci >= len(descs):
                ax.axis('off')
                continue
            desc, label = descs[ci]
            for nome, col, mf in curve:
                y = [mf.get(ch, {}).get(desc, np.nan) for ch in range(1, 9)]
                ln, = ax.plot(range(1, 9), y, marker='o', ms=4, lw=1.4, color=col, label=nome)
                handles[nome] = ln
            ax.set_title(label, fontsize=9)
            ax.set_xticks(range(1, 9))
            ax.tick_params(labelsize=7)
            ax.grid(True, alpha=0.3)
            if ci == 0:
                ax.set_ylabel(fam, fontsize=10, fontweight='bold')
            if ri == nrow - 1:
                ax.set_xlabel('distanza (m)', fontsize=8)
    fig.legend(handles.values(), handles.keys(), loc='lower center',
               ncol=len(handles), fontsize=9)
    fig.suptitle('Descrittori del rumore per distanza (canale = metri), per famiglia: '
                 'orizzontale e verticale', fontsize=13)
    fig.tight_layout(rect=[0, 0.04, 1, 0.97])
    fig.savefig(out_png, dpi=140)
    plt.close(fig)
    return True


# Per i profili-onda: la deviazione per-canale dalla media del file. Tre oggetti d'analisi
# (cluster del contrabbasso, Do del contrabbasso, cluster del soprano), ciascuno nella sua
# sottocartella. Sul contrabbasso si separano le due campane (PETALONIO e trombino) e le due
# riprese (orizzontale/verticale); il soprano e' una curva sola.
# Voci: (sottocartella, base-del-file, etichetta, [(label, selettore, colore), ...]).
def _ccb(campana, oriz, gesto):
    pref = 'CCB_petalonio' if campana == 'pet' else 'CCB_trombino'
    orient = '_oriz_' if oriz else '_vert_'
    if gesto == 'cluster':
        return lambda f: f.startswith(pref) and orient in f and 'CLUSTER' in f
    return lambda f: f.startswith(pref) and orient in f and f.endswith('_DO')


CURVE_CONFIG = [
    ('cluster', 'oriz', 'contrabbasso cluster orizzontale', [
        ('PETALONIO', _ccb('pet', True, 'cluster'), 'C0'),
        ('trombino',  _ccb('tro', True, 'cluster'), 'C3'),
    ]),
    ('cluster', 'vert', 'contrabbasso cluster verticale', [
        ('PETALONIO', _ccb('pet', False, 'cluster'), 'C0'),
        ('trombino',  _ccb('tro', False, 'cluster'), 'C3'),
    ]),
    ('do', 'oriz', 'contrabbasso Do orizzontale', [
        ('PETALONIO', _ccb('pet', True, 'do'), 'C0'),
        ('trombino',  _ccb('tro', True, 'do'), 'C3'),
    ]),
    ('do', 'vert', 'contrabbasso Do verticale', [
        ('PETALONIO', _ccb('pet', False, 'do'), 'C0'),
        ('trombino',  _ccb('tro', False, 'do'), 'C3'),
    ]),
    ('soprano', 'cluster', 'soprano cluster', [
        ('soprano', lambda f: f.startswith('CS') and 'CLUSTER' in f, 'C2'),
    ]),
]


def _carica_perfile(root):
    """{file: {ch: {desc: media}}} per i file non-NOISE con tutti gli 8 canali."""
    perfile = {}
    for d in sorted(glob.glob(os.path.join(root, 'centroide', '*'))):
        if not os.path.isdir(d):
            continue
        base = os.path.basename(d)
        if base.startswith('NOISE'):
            continue
        mf = medie_file(d, base)
        if len(mf) >= 8:
            perfile[base] = mf
    return perfile


def dev_profilo(perfile, sel):
    """{desc: (mean[8], std[8])} della deviazione per-canale dalla media del file, sui file
    selezionati da sel."""
    files = [f for f in perfile if sel(f)]
    gd = {}
    for desc in DESCRITTORI:
        M = []
        for f in files:
            vals = np.array([perfile[f][ch].get(desc, np.nan) for ch in range(1, 9)])
            if np.any(np.isnan(vals)):
                continue
            M.append(vals - vals.mean())
        if M:
            M = np.array(M)
            gd[desc] = (M.mean(axis=0), M.std(axis=0))
    return gd


def std_within_file(perfile):
    """{desc: std delle deviazioni dalla media del file, pooled sui file passati}. Riferimento
    z-score 'within-segnale': toglie le differenze di media fra file, cosi' la scala misura solo
    quanto i canali si scostano dalla media del proprio file. Va passato il sottoinsieme di file
    della figura (i segnali che si stanno analizzando), non tutti: l'analisi e' interna a quei
    segnali, non un confronto fra sorgenti diverse (la std globale gonfiava il denominatore dei
    descrittori che distinguono le sorgenti, es. n.picchi)."""
    out = {}
    for desc in DESCRITTORI:
        devs = []
        for f in perfile:
            vals = [perfile[f][ch][desc] for ch in perfile[f] if desc in perfile[f][ch]]
            if len(vals) >= 2:
                m = np.mean(vals)
                devs.extend(v - m for v in vals)
        s = float(np.std(devs)) if devs else 0.0
        out[desc] = s if s > 0 else 1.0
    return out


def plot_profili_onda(root, out_dir, z=False):
    """Per ogni voce di CURVE_CONFIG una griglia righe-per-famiglia col profilo per-canale
    (deviazione dalla media del file) di tutti i 16 descrittori, banda +/- std, salvata nella
    sottocartella del suo oggetto d'analisi (cluster/do/soprano). Sul contrabbasso le due
    campane (PETALONIO, trombino) sono curve distinte. Con z=True ogni profilo e' diviso per la
    std within-file del descrittore, calcolata sui SOLI segnali di quella figura (analisi interna
    ai segnali, non confronto fra sorgenti): assi in deviazioni standard."""
    perfile = _carica_perfile(root)
    fams = list(CATEGORIES.items())
    nrow = len(fams)
    ncol = max(len(descs) for _, descs in fams)
    x = np.arange(1, 9)
    nomi = []
    for sub, base, etich, curve in CURVE_CONFIG:
        prof = {lab: dev_profilo(perfile, sel) for lab, sel, _ in curve}
        if not any(prof.values()):
            continue
        sg = None
        if z:
            # riferimento within-file sui SOLI segnali di questa figura (analisi interna)
            sels = [sel for _, sel, _ in curve]
            perfile_fig = {f: v for f, v in perfile.items() if any(s(f) for s in sels)}
            sg = std_within_file(perfile_fig)
        fig, axes = plt.subplots(nrow, ncol, figsize=(3.3 * ncol, 3.0 * nrow),
                                 squeeze=False, sharey=z)
        handles = {}
        for ri, (fam, descs) in enumerate(fams):
            for ci in range(ncol):
                ax = axes[ri][ci]
                if ci >= len(descs):
                    ax.axis('off')
                    continue
                desc, label = descs[ci]
                for lab, sel, col in curve:
                    md = prof[lab].get(desc)
                    if md is None:
                        continue
                    m, s = md
                    if z:
                        m = m / sg[desc]
                        s = s / sg[desc]
                    ln, = ax.plot(x, m, marker='o', ms=3, lw=1.4, color=col, label=lab)
                    ax.fill_between(x, m - s, m + s, color=col, alpha=0.13)
                    handles[lab] = ln
                ax.axhline(0, color='gray', lw=0.7)
                ax.set_title(label, fontsize=9)
                ax.set_xticks(x)
                ax.tick_params(labelsize=7)
                ax.grid(True, alpha=0.3)
                if ci == 0:
                    ax.set_ylabel(fam, fontsize=10, fontweight='bold')
                if ri == nrow - 1:
                    ax.set_xlabel('canale (= m)', fontsize=8)
        rect = [0, 0, 1, 0.97]
        if len(handles) > 1:
            fig.legend(handles.values(), handles.keys(), loc='lower center',
                       ncol=len(handles), fontsize=9)
            rect = [0, 0.04, 1, 0.97]
        titolo = ('Profili per canale in z-score (deviazioni standard, assi condivisi) dei 16 '
                  if z else
                  'Profili per canale (deviazione dalla media del file) dei 16 ')
        fig.suptitle(titolo + f'descrittori, per famiglia: {etich}', fontsize=13)
        fig.tight_layout(rect=rect)
        subdir = os.path.join(out_dir, sub)
        os.makedirs(subdir, exist_ok=True)
        out = os.path.join(subdir, f'profili_onda_{base}{"_z" if z else ""}.png')
        fig.savefig(out, dpi=140)
        plt.close(fig)
        nomi.append(os.path.join(sub, os.path.basename(out)))
    return nomi


def plot_correlazioni_onda(root, out_png):
    """Barre: correlazione del profilo per-canale di ogni descrittore con quello del
    centroide, sul contrabbasso. Misura quanto ogni descrittore porta l'onda nodo/ventre."""
    perfile = _carica_perfile(root)
    dev = dev_profilo(perfile, lambda f: f.startswith('CCB') and 'CLUSTER' in f)
    if 'centroid' not in dev:
        return False
    cen = dev['centroid'][0]
    items = []
    for desc, label in [(d, l) for _, lst in CATEGORIES.items() for d, l in lst]:
        if desc in dev:
            items.append((label, float(np.corrcoef(dev[desc][0], cen)[0, 1])))
    items.sort(key=lambda t: t[1], reverse=True)
    labels = [l for l, _ in items]
    corr = [c for _, c in items]

    def colore(c):
        if abs(c) < 0.5:
            return '0.6'
        return 'C0' if c > 0 else 'C3'

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(corr)), corr, color=[colore(c) for c in corr])
    ax.axhline(0, color='gray', lw=0.8)
    ax.axhline(0.8, color='gray', ls=':', lw=0.8)
    ax.axhline(-0.8, color='gray', ls=':', lw=0.8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('correlazione col profilo del centroide')
    ax.set_title("Quanto ogni descrittore porta l'onda nodo/ventre (contrabbasso, soli cluster)")
    ax.set_ylim(-1.05, 1.05)
    ax.grid(True, alpha=0.3, axis='y')
    fig.tight_layout()
    fig.savefig(out_png, dpi=140)
    plt.close(fig)
    return True


def plot_kurtosis_do(root, out_png):
    """Kurtosis per canale sul Do grave, le quattro combinazioni campana x orientamento:
    mostra lo scoppio del PETALONIO orizzontale al ventre."""
    serie = [
        ('PETALONIO orizzontale', 'CCB_petalonio_oriz_DO', 'C0', 2.4, '-'),
        ('PETALONIO verticale',   'CCB_petalonio_vert_DO', 'C0', 1.3, '--'),
        ('trombino orizzontale',  'CCB_trombino_oriz_DO',  'C3', 2.4, '-'),
        ('trombino verticale',    'CCB_trombino_vert_DO',  'C3', 1.3, '--'),
    ]
    x = np.arange(1, 9)
    fig, ax = plt.subplots(figsize=(9, 5))
    trovato = False
    for nome, base, col, lw, ls in serie:
        d = os.path.join(root, 'centroide', base)
        if not os.path.isdir(d):
            continue
        mf = medie_file(d, base)
        if len(mf) < 8:
            continue
        y = [mf[ch].get('kurtosis', np.nan) for ch in range(1, 9)]
        ax.plot(x, y, marker='o', ms=5, lw=lw, ls=ls, color=col, label=nome)
        trovato = True
    if not trovato:
        plt.close(fig)
        return False
    ax.set_xlabel('canale (= distanza in m)')
    ax.set_ylabel('kurtosis spettrale')
    ax.set_title('Kurtosis del Do grave per canale: lo scoppio del PETALONIO '
                 'orizzontale al ventre')
    ax.set_xticks(x)
    ax.set_xticklabels([f'ch{k}' for k in x])
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_png, dpi=140)
    plt.close(fig)
    return True


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('root', help='cartella di output di analizza_divisi.py')
    args = p.parse_args(argv)

    figdir = os.path.join(args.root, 'descrittori')
    os.makedirs(figdir, exist_ok=True)

    files, perfile = medie_tutti_file(args.root)
    nomi = []
    # medie combinate (tutti gli strumenti, X = i file): restano nella radice, le usa il report
    for fam, descs in CATEGORIES.items():
        out = os.path.join(figdir, f'medie_{fam}.png')
        plot_famiglia(fam, descs, perfile, files, out)
        nomi.append(os.path.basename(out))

    # medie separate per oggetto d'analisi, ciascuna nella sua sottocartella
    categorie = [
        ('cluster', lambda f: f.startswith('CCB') and 'CLUSTER' in f),
        ('do',      lambda f: f.startswith('CCB') and f.endswith('_DO')),
        ('soprano', lambda f: f.startswith('CS')),
    ]
    for sub, sel in categorie:
        sfiles = [f for f in files if sel(f)]
        if not sfiles:
            continue
        sperfile = {f: perfile[f] for f in sfiles}
        sdir = os.path.join(figdir, sub)
        os.makedirs(sdir, exist_ok=True)
        for fam, descs in CATEGORIES.items():
            out = os.path.join(sdir, f'medie_{fam}.png')
            plot_famiglia(fam, descs, sperfile, sfiles, out, figw=max(7, 1.2 * len(sfiles)))
            nomi.append(os.path.join(sub, os.path.basename(out)))

    # noise: medie per famiglia (X = i file NOISE) + vista compatta a distanza, in noise/
    nfiles, nperfile = medie_tutti_file(args.root, solo_noise=True)
    if nfiles:
        ndir = os.path.join(figdir, 'noise')
        os.makedirs(ndir, exist_ok=True)
        for fam, descs in CATEGORIES.items():
            out = os.path.join(ndir, f'medie_{fam}.png')
            plot_famiglia(fam, descs, nperfile, nfiles, out, figw=8)
            nomi.append(os.path.join('noise', os.path.basename(out)))
        if plot_noise(args.root, os.path.join(ndir, 'medie_noise.png')):
            nomi.append('noise/medie_noise.png')

    # profili per canale dei 16 descrittori, un file per configurazione (oriz, vert, sopr),
    # in unita' proprie e in z-score
    nomi += plot_profili_onda(args.root, figdir)
    nomi += plot_profili_onda(args.root, figdir, z=True)

    # figure di sintesi per il "comportamento dei descrittori"
    if plot_correlazioni_onda(args.root, os.path.join(figdir, 'onda_correlazioni.png')):
        nomi.append('onda_correlazioni.png')
    if plot_kurtosis_do(args.root, os.path.join(figdir, 'kurtosis_do.png')):
        nomi.append('kurtosis_do.png')
    print('scritte in descrittori/:', ', '.join(nomi))


if __name__ == '__main__':
    main()
