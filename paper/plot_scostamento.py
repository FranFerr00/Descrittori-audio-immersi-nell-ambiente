#!/usr/bin/env python3
"""Scostamento per descrittore: 16 descrittori x 4 configurazioni di ripresa.

Decomposizione di figura_deriva: dove figura_deriva mostra lo scostamento TOTALE
per configurazione (sommato sui descrittori, distribuito sui 45 segnali), questa
heatmap lo apre descrittore per descrittore. Ogni cella e' lo scostamento medio
del descrittore rispetto alla ripresa diretta (sintetica), in z-score, mediato sui
frame validi (gated=0 in entrambe) e sui 45 segnali.

ATTENZIONE: misura quanto un descrittore si SPOSTA, non quanto resta utile. Uno
scostamento grande ma sistematico (es. lo slope, che sotto ripresa diventa
regolarmente negativo) non implica inutilizzabilita': per questo la mappa NON
coincide con la tassonomia di robustezza di sezione 4, che pesa anche la
prevedibilita' dello spostamento. La colonna -30 dB funge da controllo di
invarianza di scala (quasi tutta a zero, tranne flux e irregularity).

Riusa la pipeline e la taratura congelata di esplorazioni/deriva_sintetico_ripreso.py
(la stessa di figura_deriva), per coerenza. Genera figura_scostamento.pdf in paper/.
I dati sono risolti dalla radice del repo via __file__, quindi gira sia da paper/
sia dalla radice.
"""
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "esplorazioni"))

from deriva_sintetico_ripreso import (  # noqa: E402
    load_taratura, load_frames, signal_dirs, CONFIGS, DESCS, ANALISI, REF, SUFFIX,
)

# nomi leggibili, allineati alla Tabella 1 del paper
NAMES = {
    "centroid": "Centroide", "spread": "Spread", "rolloff": "Rolloff",
    "slope": "Slope", "obsir_std": "OBSIR-std", "flatness": "Flatness",
    "crest": "Crest", "skewness": "Skewness", "kurtosis": "Kurtosis",
    "entropy": "Entropy", "tpr": "TPR", "n_peaks": "N. picchi",
    "tonality": "Tonality", "flux": "Flux", "irregularity": "Irregularity",
    "zcr": "ZCR",
}
COL_LABELS = ["−30 dB", "1 m", "2 m\nsporco", "2 m\npulito"]


def compute_matrix():
    """Matrice [16, 4]: scostamento medio dalla diretta, per descrittore e config."""
    tar = load_taratura()
    cfgs = list(CONFIGS)
    per_cfg = {c: [] for c in cfgs}      # per ogni config: lista di array(16,) per-segnale
    for sig in signal_dirs():
        Zref, gref = load_frames(ANALISI / REF / sig / (sig + SUFFIX), tar)
        for c in cfgs:
            cfg_csv = ANALISI / c / sig / (sig + SUFFIX)
            if not cfg_csv.exists():
                continue
            Zcfg, gcfg = load_frames(cfg_csv, tar)
            n = min(len(Zref), len(Zcfg))
            valid = (~gref[:n]) & (~gcfg[:n])
            if not valid.any():
                continue
            D = np.abs(Zcfg[:n][valid] - Zref[:n][valid])   # (n_validi, 16)
            per_cfg[c].append(D.mean(axis=0))
    M = np.column_stack([np.mean(np.array(per_cfg[c]), axis=0) for c in cfgs])
    return M


def make_figure(M, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # La kurtosis fora la scala (scostamento enorme, sintomo della sua fragilita'
    # ai momenti di ordine alto): limito la scala colore cosi' da leggere il resto
    # della mappa; i valori veri restano scritti in cella.
    CAP = 2.5
    fig, ax = plt.subplots(figsize=(4.8, 4.4))
    im = ax.imshow(M, aspect="auto", cmap="YlOrRd", vmin=0, vmax=CAP)

    ax.set_xticks(range(len(COL_LABELS)), COL_LABELS, fontsize=8)
    ax.set_yticks(range(len(DESCS)), [NAMES[d] for d in DESCS], fontsize=8)
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)

    # valori in cella (la soglia del colore del testo usa il cap della scala)
    vmax = CAP
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            col = "white" if v > 0.6 * vmax else "black"
            ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                    color=col, fontsize=7)

    ax.set_xlim(-0.5, M.shape[1] - 0.5)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.12)
    cb.set_label("scostamento medio dalla diretta (z-score)", fontsize=8)
    cb.ax.tick_params(labelsize=7)

    fig.tight_layout()
    fig.savefig(path)
    print(f"scritto {path}")


if __name__ == "__main__":
    M = compute_matrix()
    make_figure(M, HERE / "figura_scostamento.pdf")
