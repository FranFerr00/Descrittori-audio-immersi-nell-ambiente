#!/usr/bin/env python3
"""Tenuta del controllo a nodi su assi DIVERSI (estensione per la review §3.1).

La review chiede: il controllo regge anche su coppie di nodi MENO separate
(assi "sottili"), non solo sull'asse di massima varianza sinusoide/rumore?
Qui rigiro la stessa misura (R, k di v ripreso vs v sui sintetici, z-score) per
piu' coppie di nodi e riporto come degrada la tenuta al restringersi dell'asse.

Riusa la pipeline di deriva_sintetico_ripreso.py e le funzioni di
controllo_nodi_ripresa.py.
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deriva_sintetico_ripreso import (  # noqa: E402
    load_taratura, CONFIGS, DESCS, ANALISI, REF, SUFFIX,
)
from controllo_nodi_ripresa import node_vector, v_mean, fit  # noqa: E402

ZSCORE = np.eye(len(DESCS))

# coppie di nodi: (nome, +1, -1).  La prima e' l'asse canonico (max varianza).
COPPIE = [
    ("tonale/rumore (canonico)", "01_sinusoide_440", "02_noise_bianco"),
    ("saturazione (drive 1/20)", "03_tanh_drive1", "05_tanh_drive20"),
    ("FM (indice 0,5 / 10)",     "10_fm_idx05",    "12_fm_idx10"),
    ("misto tonale/rumore 75-25/25-75", "14_sin75_noise25", "16_sin25_noise75"),
    ("banda stretta Q500/Q50",   "06_noise_bp_q500", "08_noise_bp_q50"),
]


def signals_all(tar):
    """Tutti i 45 segnali (per il v_studio servono tutti tranne i due nodi)."""
    import os
    d = ANALISI / REF
    return sorted(x for x in os.listdir(d) if (d / x).is_dir())


def run_pair(p_plus, p_minus, tar):
    """Per la coppia (p_plus,p_minus): R,k (nodi tarati sui sintetici) per config,
    piu' la separazione dei due nodi in z-score sui sintetici."""
    pP = node_vector(p_plus, REF, tar)
    pM = node_vector(p_minus, REF, tar)
    if pP is None or pM is None:
        return None
    sep = float(np.linalg.norm(pP - pM))
    sigs = [s for s in signals_all(tar) if s not in (p_plus, p_minus)]
    # v sui sintetici
    vs = {}
    for s in sigs:
        v = v_mean(s, REF, pP, pM, ZSCORE, tar)
        if v is not None:
            vs[s] = v
    out = {"sep": sep}
    for cfg in CONFIGS:
        xs, ys = [], []
        for s, v0 in vs.items():
            if not (ANALISI / cfg / s / (s + SUFFIX)).exists():
                continue
            vf = v_mean(s, cfg, pP, pM, ZSCORE, tar)  # nodi tarati sui sintetici
            if vf is not None:
                xs.append(v0); ys.append(vf)
        R, k = fit(xs, ys)
        out[cfg] = (R, k, len(xs))
    return out


def main():
    tar = load_taratura()
    print(f"{'coppia':34s} {'sep':>5s}  " + "  ".join(f"{CONFIGS[c]:>12s}" for c in CONFIGS))
    for nome, pp, pm in COPPIE:
        r = run_pair(pp, pm, tar)
        if r is None:
            print(f"{nome:34s}  (dati mancanti)")
            continue
        cells = []
        for c in CONFIGS:
            R, k, n = r[c]
            cells.append(f"R{R:+.2f} k{k:+.2f}")
        print(f"{nome:34s} {r['sep']:5.1f}  " + "  ".join(f"{c:>12s}" for c in cells))


if __name__ == "__main__":
    main()
