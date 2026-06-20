#!/usr/bin/env python3
"""Traiettorie frame per frame dei gesti strumentali nello spazio dei descrittori.

Ogni gesto (campione strumentale) non e' piu' un punto-media ma una LINEA che
segue i suoi frame nel tempo. Quattro dimensioni in una figura piatta:
  x = PC1, y = PC2, colore = PC3 (la dimensione in piu'), percorso = tempo.
Un cerchio segna l'inizio del gesto, un quadrato la fine.
Esce: traiettorie_descrittori.png
"""
import csv
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

# quale componente porta il colore: PC3 default, PC4 con  python3 ... 4
COLORPC = int(sys.argv[1]) if len(sys.argv) > 1 else 3

DESCS = ["centroid", "spread", "rolloff", "slope", "obsir_std", "flatness",
         "crest", "skewness", "kurtosis", "entropy", "tpr", "n_peaks",
         "tonality", "flux", "irregularity", "zcr"]
SOMMARIO = "analisi/tabelle/segnali_sommario.csv"
PASSO = 2  # tieni un frame ogni PASSO, per alleggerire le linee

GESTI = {
    "clarinetto": [("clarinettocb", "001", "p1"), ("clarinettocb", "002", "p2"),
                   ("clarinettocb", "003", "mf"), ("clarinettocb", "004", "f"),
                   ("clarinettocb", "005", "cresc1"), ("clarinettocb", "006", "cresc2"),
                   ("clarinettocb", "007", "dim"), ("clarinettocb", "010", "cresc-dim"),
                   ("clarinettocb", "013", "dim-cresc")],
    "timpano": [("timpano", "004", "p"), ("timpano", "005", "mf"),
                ("timpano", "006", "f1"), ("timpano", "007", "f2"),
                ("timpano", "008", "mf2"), ("timpano", "015", "cresc"),
                ("timpano", "016", "dim"), ("timpano", "018", "dim-cresc-lungo"),
                ("timpano", "023", "dim-cresc-corto"), ("timpano", "025", "cresc-dim")],
}


def frames(strum, cid):
    path = f"analisi/{strum}/analisi/{cid}/{cid}_hann_ov50_10000hz_analisi.csv"
    rows = [r for r in csv.DictReader(open(path)) if r.get("gated", "0") != "1"]
    rows = rows[::PASSO]
    return np.array([[float(r[d]) for d in DESCS] for r in rows])


# carica tutte le traiettorie (grezze) e tienine traccia
traj_raw = {}
allraw = []
for fam, lst in GESTI.items():
    for strum, cid, lab in lst:
        Rg = frames(strum, cid)
        traj_raw[(fam, cid, lab)] = Rg
        allraw.append(Rg)
allR = np.vstack(allraw)

# standardizza ogni descrittore SUI FRAME (cosi' nessuno domina per pura scala:
# senza, la kurtosis a code pesanti si prende il 90% della varianza). Per la
# foto va bene; il righello del corpus serve al metodo (v), non a questa figura.
cmean = allR.mean(axis=0)
cstd = allR.std(axis=0)
cstd[cstd == 0] = 1.0
traj = {k: (R - cmean) / cstd for k, R in traj_raw.items()}
allZ = (allR - cmean) / cstd

mu = allZ.mean(axis=0)
U, S, Vt = np.linalg.svd(allZ - mu, full_matrices=False)
NC = max(3, COLORPC)
for k in range(NC):
    if Vt[k][np.argmax(np.abs(Vt[k]))] < 0:
        Vt[k] = -Vt[k]
var = (S ** 2) / (S ** 2).sum() * 100
ci = COLORPC - 1  # indice 0-based della componente colore


def liscia(a, w=7):
    if len(a) < w:
        return a
    k = np.ones(w) / w
    return np.convolve(a, k, mode="same")


def proj(Zg):
    P = (Zg - mu) @ Vt[:NC].T
    return liscia(P[:, 0]), liscia(P[:, 1]), liscia(P[:, ci])


# range globale della componente colore per la scala comune
allPc = ((allZ - mu) @ Vt[ci])
vmin, vmax = np.percentile(allPc, 2), np.percentile(allPc, 98)

fig, axes = plt.subplots(1, 2, figsize=(15, 7), sharex=True, sharey=True)
sm = None
for ax, fam in zip(axes, ["clarinetto", "timpano"]):
    for (f2, cid, lab), Zg in traj.items():
        if f2 != fam:
            continue
        x, y, c3 = proj(Zg)
        pts = np.array([x, y]).T.reshape(-1, 1, 2)
        segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
        lc = LineCollection(segs, cmap="viridis", norm=plt.Normalize(vmin, vmax))
        lc.set_array((c3[:-1] + c3[1:]) / 2)
        lc.set_linewidth(2.2)
        sm = ax.add_collection(lc)
        ax.plot(x[0], y[0], "o", color="black", ms=5, zorder=5)        # inizio
        ax.plot(x[-1], y[-1], "s", color="black", ms=5, zorder=5)      # fine
        ax.annotate(f"{cid} {lab}", (x[-1], y[-1]), textcoords="offset points",
                    xytext=(4, 4), fontsize=7, color="0.25")
    ax.set_title(f"{fam}  ({len(GESTI[fam])} gesti)")
    ax.set_xlabel(f"PC1 ({var[0]:.0f}%)")
    ax.autoscale()
axes[0].set_ylabel(f"PC2 ({var[1]:.0f}%)")
cb = fig.colorbar(sm, ax=axes, fraction=0.04, pad=0.02)
cb.set_label(f"PC{COLORPC} ({var[ci]:.0f}%)  = la dimensione del colore")

t1 = sorted(zip(DESCS, Vt[0]), key=lambda t: -abs(t[1]))[:3]
t2 = sorted(zip(DESCS, Vt[1]), key=lambda t: -abs(t[1]))[:3]
tc = sorted(zip(DESCS, Vt[ci]), key=lambda t: -abs(t[1]))[:3]
fig.suptitle("Traiettorie frame per frame dei gesti  (o = inizio, quadrato = fine)  |  "
             f"PC1: {','.join(d for d,_ in t1)}   PC2: {','.join(d for d,_ in t2)}   "
             f"PC{COLORPC}: {','.join(d for d,_ in tc)}", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.96))
out = f"traiettorie_descrittori_colorePC{COLORPC}.png"
fig.savefig(out, dpi=130)
print("scritto", out)
print(f"PC1 {var[0]:.0f}%  PC2 {var[1]:.0f}%  PC{COLORPC} {var[ci]:.0f}%  (frame strumentali, standardizzati)")
print("PC1:", t1, "\nPC2:", t2, f"\nPC{COLORPC}:", tc)
