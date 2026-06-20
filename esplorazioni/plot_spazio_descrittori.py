#!/usr/bin/env python3
"""Rappresentazione grafica dei nostri suoni nello spazio dei descrittori.

Usa gli stessi dati del catalogo Pd (genera_suoni_pd.py) e la stessa taratura
congelata di prova_ancore.py. Produce una figura con due pannelli:

  sinistra  proiezione PCA dei 64 suoni (solo per guardare la nuvola: la
            riduzione qui e' una FOTO, non la mappatura di controllo), colorati
            per famiglia. Le percentuali sugli assi mostrano quanto pesa ogni
            direzione (la brillantezza domina la prima).
  destra    vista a ancore clarinetto (+1) / timpano (-1): asse orizzontale =
            posizione lungo la retta fra le due ancore, colore = valore v vero
            calcolato in 16 dimensioni. E' la figura fedele al nostro metodo.

Esce: spazio_descrittori.png
"""
import csv
import numpy as np
import matplotlib.pyplot as plt

DESCS = ["centroid", "spread", "rolloff", "slope", "obsir_std", "flatness",
         "crest", "skewness", "kurtosis", "entropy", "tpr", "n_peaks",
         "tonality", "flux", "irregularity", "zcr"]
SOMMARIO = "analisi/tabelle/segnali_sommario.csv"


def raccogli():
    """64 suoni (nome, vettore grezzo DESCS, famiglia)."""
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
    """media e dev congelate dal corpus (come prova_ancore.py)."""
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

raw = np.array([v for _, v, _ in cat])          # 64 x 16 grezzo
Z = (raw - m) / sd                              # 64 x 16 in z
fam = np.array([f for _, _, f in cat])

# --- ancore: media (grezza) di ciascuna famiglia, poi in z ---
Pp = (raw[fam == "clarinetto"].mean(axis=0) - m) / sd   # +1
Pm = (raw[fam == "timpano"].mean(axis=0) - m) / sd      # -1

# --- v vero in 16 dimensioni per ogni suono ---
dp = np.linalg.norm(Z - Pp, axis=1)
dm = np.linalg.norm(Z - Pm, axis=1)
v = (dm - dp) / (dm + dp)

# ================= PANNELLO 1: PCA (solo foto) =================
mu = Z.mean(axis=0)
U, S, Vt = np.linalg.svd(Z - mu, full_matrices=False)
PC = (Z - mu) @ Vt[:2].T
var = (S ** 2) / (S ** 2).sum() * 100

# brillantezza dominante: peso assoluto dei descrittori sulla prima componente
load1 = sorted(zip(DESCS, Vt[0]), key=lambda t: -abs(t[1]))[:3]

colori = {"sintetico": "#b0b0b0", "clarinetto": "#1f77b4", "timpano": "#d62728"}
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.2))

for f in ["sintetico", "clarinetto", "timpano"]:
    s = fam == f
    ax1.scatter(PC[s, 0], PC[s, 1], s=42, c=colori[f], label=f,
                edgecolor="white", linewidth=0.5, alpha=0.9)
ax1.set_xlabel(f"PC1  ({var[0]:.0f}% della varianza)")
ax1.set_ylabel(f"PC2  ({var[1]:.0f}%)")
ax1.set_title("Proiezione PCA dei 64 suoni (foto della nuvola)")
ax1.axhline(0, color="0.85", lw=0.8, zorder=0)
ax1.axvline(0, color="0.85", lw=0.8, zorder=0)
ax1.legend(title="famiglia", loc="best")
sub = "PC1 pesa soprattutto: " + ", ".join(d for d, _ in load1)
ax1.text(0.5, -0.13, sub, transform=ax1.transAxes, ha="center",
         fontsize=9, color="0.3")

# ============ PANNELLO 2: vista a ancore, colore = v ============
# asse x = posizione lungo la retta clarinetto->timpano (direzione Pp-Pm in z)
u = Pp - Pm
u = u / np.linalg.norm(u)
x = (Z - (Pp + Pm) / 2) @ u                 # 0 a meta' fra le ancore
# asse y = direzione ortogonale di massima dispersione (per spalmare i punti)
resid = (Z - mu) - np.outer((Z - mu) @ u, u)
_, _, Vt2 = np.linalg.svd(resid, full_matrices=False)
y = resid @ Vt2[0]

sc = ax2.scatter(x, y, c=v, cmap="RdBu_r", vmin=-1, vmax=1, s=55,
                 edgecolor="0.3", linewidth=0.5, zorder=3)
# le due ancore
xpp = (Pp - (Pp + Pm) / 2) @ u
xpm = (Pm - (Pp + Pm) / 2) @ u
ax2.scatter([xpp], [0], marker="*", s=480, c="#d62728", edgecolor="black",
            linewidth=1.2, zorder=5)
ax2.scatter([xpm], [0], marker="*", s=480, c="#1f77b4", edgecolor="black",
            linewidth=1.2, zorder=5)
ax2.annotate("ancora +1\nclarinetto (media)", (xpp, 0), textcoords="offset points",
             xytext=(0, 18), ha="center", fontsize=9, color="#d62728")
ax2.annotate("ancora -1\ntimpano (media)", (xpm, 0), textcoords="offset points",
             xytext=(0, -34), ha="center", fontsize=9, color="#1f77b4")
ax2.axvline(0, color="0.6", lw=1.0, ls="--", zorder=1)
ax2.text(0, ax2.get_ylim()[1], " v = 0", color="0.4", fontsize=9, va="top")
ax2.set_xlabel("posizione lungo l'asse  timpano (-1)  <->  clarinetto (+1)   (in z)")
ax2.set_ylabel("dispersione ortogonale")
ax2.set_title("Vista a ancore: colore = valore v (16 dimensioni)")
cb = fig.colorbar(sc, ax=ax2, fraction=0.046, pad=0.04)
cb.set_label("v   (-1 = timpano,  +1 = clarinetto)")

fig.suptitle("I nostri suoni nello spazio dei descrittori", fontsize=14, y=0.99)
fig.tight_layout(rect=(0, 0, 1, 0.97))
fig.savefig("spazio_descrittori.png", dpi=130)
print("scritto spazio_descrittori.png")
print(f"PC1 {var[0]:.1f}%  PC2 {var[1]:.1f}%  (prime due: {var[0]+var[1]:.1f}%)")
print(f"v: clarinetto medio {v[fam=='clarinetto'].mean():+.2f}, "
      f"timpano medio {v[fam=='timpano'].mean():+.2f}, "
      f"sintetici medio {v[fam=='sintetico'].mean():+.2f}")
