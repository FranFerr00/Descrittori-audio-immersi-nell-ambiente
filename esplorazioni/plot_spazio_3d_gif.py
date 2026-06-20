#!/usr/bin/env python3
"""GIF che ruota: PCA 3D dei 64 suoni nello spazio dei descrittori.

Stessa nuvola della versione ferma, ma in rotazione, cosi' la profondita' si
legge a colpo d'occhio. Colore = famiglia. Esce: spazio_descrittori_3d.gif
"""
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

DESCS = ["centroid", "spread", "rolloff", "slope", "obsir_std", "flatness",
         "crest", "skewness", "kurtosis", "entropy", "tpr", "n_peaks",
         "tonality", "flux", "irregularity", "zcr"]
SOMMARIO = "analisi/tabelle/segnali_sommario.csv"


def raccogli():
    cat = []
    for r in csv.DictReader(open(SOMMARIO)):
        cat.append((r["segnale"], [float(r[d + "_mean"]) for d in DESCS], "sintetico"))
    UFF = {"clarinettocb": [("001", "p1"), ("002", "p2"), ("003", "mf"), ("004", "f"),
                            ("005", "cresc1"), ("006", "cresc2"), ("007", "dim"),
                            ("010", "cresc-dim"), ("013", "dim-cresc")],
           "timpano": [("004", "p"), ("005", "mf"), ("006", "f1"), ("007", "f2"),
                       ("008", "mf2"), ("015", "cresc"), ("016", "dim"),
                       ("018", "dim-cresc-lungo"), ("023", "dim-cresc-corto"), ("025", "cresc-dim")]}
    pref = {"clarinettocb": "clar", "timpano": "timp"}
    fam = {"clarinettocb": "clarinetto", "timpano": "timpano"}
    for strum, items in UFF.items():
        for cid, lab in items:
            path = f"analisi/{strum}/analisi/{cid}/{cid}_hann_ov50_10000hz_analisi.csv"
            rows = [r for r in csv.DictReader(open(path)) if r.get("gated", "0") != "1"]
            c = rows[len(rows) // 2]
            cat.append((f"{pref[strum]}{cid}_{lab}", [float(c[d]) for d in DESCS], fam[strum]))
    return cat


def taratura():
    rows = list(csv.DictReader(open(SOMMARIO)))
    media, dev = {}, {}
    for d in DESCS:
        c = [float(r[d + "_mean"]) for r in rows]
        mm = sum(c) / len(c)
        sd = (sum((x - mm) ** 2 for x in c) / len(c)) ** 0.5 or 1.0
        media[d], dev[d] = mm, sd
    return media, dev


cat = raccogli()
media, dev = taratura()
m = np.array([media[d] for d in DESCS])
sd = np.array([dev[d] for d in DESCS])
raw = np.array([v for _, v, _ in cat])
Z = (raw - m) / sd
fam = np.array([f for _, _, f in cat])

mu = Z.mean(axis=0)
U, S, Vt = np.linalg.svd(Z - mu, full_matrices=False)
PC = (Z - mu) @ Vt[:3].T
var = (S ** 2) / (S ** 2).sum() * 100

colori = {"sintetico": "#b0b0b0", "clarinetto": "#1f77b4", "timpano": "#d62728"}
fig = plt.figure(figsize=(7.2, 7))
ax = fig.add_subplot(111, projection="3d")
for f in ["sintetico", "clarinetto", "timpano"]:
    s = fam == f
    ax.scatter(PC[s, 0], PC[s, 1], PC[s, 2], s=45, c=colori[f], label=f,
               edgecolor="white", linewidth=0.4, depthshade=True)
ax.set_xlabel(f"PC1 ({var[0]:.0f}%)")
ax.set_ylabel(f"PC2 ({var[1]:.0f}%)")
ax.set_zlabel(f"PC3 ({var[2]:.0f}%)")
ax.legend(title="famiglia", loc="upper left")
tot = var[0] + var[1] + var[2]
ax.set_title(f"PCA 3D dei 64 suoni  (3 componenti = {tot:.0f}% della varianza)")
fig.tight_layout()

N = 72
def step(i):
    ax.view_init(elev=20, azim=i * (360 / N))
    return ()

anim = FuncAnimation(fig, step, frames=N, interval=90, blit=False)
anim.save("spazio_descrittori_3d.gif", writer=PillowWriter(fps=12), dpi=95)
print("scritto spazio_descrittori_3d.gif")
