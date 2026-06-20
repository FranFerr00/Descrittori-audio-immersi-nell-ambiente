#!/usr/bin/env python3
"""Di cosa sono fatte le tre componenti principali (loadings).

Ogni componente PCA e' una combinazione pesata dei 16 descrittori. Qui stampo i
pesi e li disegno: tre pannelli (PC1, PC2, PC3), una barra per descrittore,
rossa se il peso e' positivo, blu se negativo. Esce: pca_loadings.png
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
        cat.append([float(r[d + "_mean"]) for d in DESCS])
    UFF = {"clarinettocb": ["001", "002", "003", "004", "005", "006", "007", "010", "013"],
           "timpano": ["004", "005", "006", "007", "008", "015", "016", "018", "023", "025"]}
    for strum, ids in UFF.items():
        for cid in ids:
            path = f"analisi/{strum}/analisi/{cid}/{cid}_hann_ov50_10000hz_analisi.csv"
            rows = [r for r in csv.DictReader(open(path)) if r.get("gated", "0") != "1"]
            c = rows[len(rows) // 2]
            cat.append([float(c[d]) for d in DESCS])
    return np.array(cat)


def taratura():
    rows = list(csv.DictReader(open(SOMMARIO)))
    m, sd = [], []
    for d in DESCS:
        c = [float(r[d + "_mean"]) for r in rows]
        mm = sum(c) / len(c)
        ss = (sum((x - mm) ** 2 for x in c) / len(c)) ** 0.5 or 1.0
        m.append(mm); sd.append(ss)
    return np.array(m), np.array(sd)


raw = raccogli()
m, sd = taratura()
Z = (raw - m) / sd
mu = Z.mean(axis=0)
U, S, Vt = np.linalg.svd(Z - mu, full_matrices=False)
var = (S ** 2) / (S ** 2).sum() * 100

# fisso il segno: la componente punti verso il suo descrittore di peso massimo
for k in range(3):
    if Vt[k][np.argmax(np.abs(Vt[k]))] < 0:
        Vt[k] = -Vt[k]

print("Pesi (loadings) delle tre componenti, in ordine DESCS:\n")
print(f"{'descrittore':12s} {'PC1':>7s} {'PC2':>7s} {'PC3':>7s}")
for i, d in enumerate(DESCS):
    print(f"{d:12s} {Vt[0][i]:+7.2f} {Vt[1][i]:+7.2f} {Vt[2][i]:+7.2f}")
print()
for k in range(3):
    top = sorted(zip(DESCS, Vt[k]), key=lambda t: -abs(t[1]))[:4]
    print(f"PC{k+1} ({var[k]:.0f}%) pesa su: " +
          ", ".join(f"{d} ({w:+.2f})" for d, w in top))

# ---------------- figura: tre pannelli a barre ----------------
fig, axes = plt.subplots(1, 3, figsize=(15, 6), sharey=True)
y = np.arange(len(DESCS))
for k, ax in enumerate(axes):
    w = Vt[k]
    col = ["#d62728" if x >= 0 else "#1f77b4" for x in w]
    ax.barh(y, w, color=col, edgecolor="0.3", linewidth=0.4)
    ax.axvline(0, color="0.5", lw=0.8)
    ax.set_title(f"PC{k+1}  ({var[k]:.0f}% della varianza)")
    ax.set_xlabel("peso del descrittore")
    ax.set_xlim(-0.9, 0.9)
    if k == 0:
        ax.set_yticks(y)
        ax.set_yticklabels(DESCS)
    ax.invert_yaxis()
fig.suptitle("Di cosa sono fatte le tre componenti principali  "
             "(rosso = contributo positivo, blu = negativo)", fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig("pca_loadings.png", dpi=130)
print("\nscritto pca_loadings.png")
