#!/usr/bin/env python3
"""Tenuta del controllo a nodi su STRUMENTI ACUSTICI, lungo la distanza (review §3.1).

Usa i dati dell'esperimento di distanza (8 microfoni, 1--8 m, 16 descrittori per
canale). Fisso i due nodi sul microfono piu' vicino (ch1, 1 m) e misuro quanto la
lettura v di ciascun suono si stacca quando il microfono si allontana:

  - nodi fissi a 1 m  : i nodi restano al microfono vicino, il suono si allontana
  - nodi co-ripresi   : i nodi vengono presi allo stesso microfono del suono (elisione)

Asse dei nodi: cluster denso (+1) vs Do tonale (-1) del contrabbasso (trombino, oriz).
Riusa la taratura z-score congelata e load_frames di deriva_sintetico_ripreso.py.
"""
import os
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deriva_sintetico_ripreso import load_taratura, load_frames, DESCS, ANALISI  # noqa: E402
from controllo_nodi_ripresa import v_series, fit  # noqa: E402

LEAP = ANALISI / "distanza-banda-piena" / "centroide"
TAIL = "_hann_ov50_48000hz_analisi.csv"
ZS = np.eye(len(DESCS))

NODO_PIU = "CCB_trombino_oriz_CLUSTER1"   # +1  denso (cluster)
NODO_MENO = "CCB_trombino_oriz_DO"        # -1  tonale (Do grave)
CH_ANCORA = 1                              # microfono piu' vicino (1 m)

# I due assi della review §3.1: largo (registri diversi, la catena lo conserva) e
# stretto (suoni dello stesso strumento, l'onda stazionaria lo rimescola).
ASSI = {
    "largo (soprano / contrabbasso grave)": ("CS_oriz_CLUSTER1", "CCB_trombino_oriz_DO"),
    "stretto (cluster / Do, contrabbasso)": ("CCB_trombino_oriz_CLUSTER1", "CCB_trombino_oriz_DO"),
}


def csv_path(sample, ch):
    return LEAP / sample / f"{sample}_ch{ch}{TAIL}"


def vec(sample, ch, tar):
    """Vettore 16 (z-score congelato) medio sui frame validi del campione a quel mic."""
    p = csv_path(sample, ch)
    if not p.exists():
        return None
    Z, g = load_frames(p, tar)
    valid = ~g
    return Z[valid].mean(axis=0) if valid.any() else None


def v_of(sample, ch, pP, pM, tar):
    """v del campione al microfono ch, dati i due nodi (vettori)."""
    x = vec(sample, ch, tar)
    if x is None or pP is None or pM is None:
        return None
    return float(v_series(x[None, :], pP, pM, ZS)[0])


def test_samples(p_piu=NODO_PIU, p_meno=NODO_MENO):
    """Campioni strumentali oriz (CCB + CS), esclusi i due nodi."""
    out = []
    for d in sorted(os.listdir(LEAP)):
        if not (LEAP / d).is_dir():
            continue
        if "_oriz_" not in d:            # una sola orientazione, per isolare la distanza
            continue
        if d in (p_piu, p_meno):
            continue
        out.append(d)
    return out


def r_vs_distanza(p_piu, p_meno, tar, mics=range(2, 9)):
    """Per la coppia di nodi data, R (e k) di v ripreso vs v a 1 m, nodi fissi a 1 m,
    a ogni microfono. Restituisce (lista_mic, lista_R, lista_k)."""
    pP1 = vec(p_piu, CH_ANCORA, tar)
    pM1 = vec(p_meno, CH_ANCORA, tar)
    samples = test_samples(p_piu, p_meno)
    v_ref = {s: v_of(s, CH_ANCORA, pP1, pM1, tar) for s in samples}
    v_ref = {s: v for s, v in v_ref.items() if v is not None}
    mm, RR, kk = [], [], []
    for ch in mics:
        xs, ys = [], []
        for s in v_ref:
            vf = v_of(s, ch, pP1, pM1, tar)
            if vf is None:
                continue
            xs.append(v_ref[s]); ys.append(vf)
        R, k = fit(xs, ys)
        mm.append(ch); RR.append(R); kk.append(k)
    return mm, RR, kk


def main():
    tar = load_taratura()
    # Tenuta lungo la distanza, nodi fissi a 1 m, per i due assi della review §3.1.
    print("R (nodi fissi a 1 m) di v ripreso vs v a 1 m, lungo la distanza:\n")
    header = "  ".join(f"{m}m" for m in range(2, 9))
    print(f"{'asse':38s} | {header}")
    for nome, (p_piu, p_meno) in ASSI.items():
        mm, RR, kk = r_vs_distanza(p_piu, p_meno, tar)
        riga = "  ".join(f"{r:+.2f}" for r in RR)
        print(f"{nome:38s} | {riga}")


if __name__ == "__main__":
    main()
