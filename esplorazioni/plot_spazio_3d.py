#!/usr/bin/env python3
"""PCA in 3D dei 64 suoni nello spazio dei descrittori.

Tiene tre componenti principali invece di due (cattura piu' varianza). La stessa
nuvola e' resa da due angolazioni, perche' in un'immagine ferma la profondita'
inganna. Colore = famiglia. Esce: spazio_descrittori_3d.png
"""
import csv
import numpy as np
import matplotlib.pyplot as plt

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
        m = sum(c) / len(c)
        sd = (sum((x - m) ** 2 for x in c) / len(c)) ** 0.5 or 1.0
        media[d], dev[d] = m, sd
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
fig = plt.figure(figsize=(15, 7))
for j, (elev, azim) in enumerate([(22, -60), (22, 40)]):
    ax = fig.add_subplot(1, 2, j + 1, projection="3d")
    for f in ["sintetico", "clarinetto", "timpano"]:
        s = fam == f
        ax.scatter(PC[s, 0], PC[s, 1], PC[s, 2], s=40, c=colori[f], label=f,
                   edgecolor="white", linewidth=0.4, depthshade=True)
    ax.set_xlabel(f"PC1 ({var[0]:.0f}%)")
    ax.set_ylabel(f"PC2 ({var[1]:.0f}%)")
    ax.set_zlabel(f"PC3 ({var[2]:.0f}%)")
    ax.view_init(elev=elev, azim=azim)
    if j == 0:
        ax.legend(title="famiglia", loc="upper left")
    ax.set_title(f"angolo {j + 1}")

tot = var[0] + var[1] + var[2]
fig.suptitle(f"PCA 3D dei 64 suoni nello spazio dei descrittori  "
             f"(tre componenti = {tot:.0f}% della varianza)", fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig("spazio_descrittori_3d.png", dpi=130)
print("scritto spazio_descrittori_3d.png")
print(f"PC1 {var[0]:.1f}%  PC2 {var[1]:.1f}%  PC3 {var[2]:.1f}%  tot {tot:.1f}%")
