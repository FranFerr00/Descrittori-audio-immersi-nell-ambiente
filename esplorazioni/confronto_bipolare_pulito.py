#!/usr/bin/env python3
"""Confronto pulito, a parita' di forma: entrambi i sistemi resi BIPOLARI
(un valore con segno, +1 tonale / -1 rumore). Una riga per metodo.
Eseguire dalla radice di descrittori/."""
import csv, glob, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RECS = "analisi/recs-003"
DESCS = ["centroid", "spread", "rolloff", "slope", "obsir_std", "flatness",
         "crest", "skewness", "kurtosis", "entropy", "tpr", "n_peaks",
         "tonality", "flux", "irregularity", "zcr"]

def per_frame(seg):
    pf = f"{RECS}/{seg}/{seg}_hann_ov50_10000hz_analisi.csv"
    fr = [f for f in csv.DictReader(open(pf)) if f.get("gated", "0") == "0"]
    return np.array([[float(f[d]) for d in DESCS] for f in fr])

segnali = sorted(os.path.basename(os.path.dirname(p))
                 for p in glob.glob(f"{RECS}/*/*_hann_ov50_10000hz_analisi.csv"))
pool = np.concatenate([per_frame(s) for s in segnali])
MU, SD = pool.mean(0), np.where(pool.std(0) > 0, pool.std(0), 1.0)
zmat = lambda raw: (raw - MU) / SD
nodo = lambda seg: zmat(per_frame(seg)).mean(0)

A_piu, A_meno = nodo("13_sin100"), nodo("17_noise100")
SWEEP = ["13_sin100", "14_sin75_noise25", "15_sin50_noise50",
         "16_sin25_noise75", "17_noise100"]
X = np.concatenate([zmat(per_frame(s)) for s in SWEEP])
t = np.arange(len(X))
d_piu  = np.sqrt(((X - A_piu)  ** 2).sum(1))
d_meno = np.sqrt(((X - A_meno) ** 2).sum(1))

# entrambi bipolari, stesso intervallo [-1, +1]
v_bip = (d_meno - d_piu) / (d_meno + d_piu)
def v_gauss(sigma):
    wp = np.exp(-d_piu ** 2 / (2 * sigma ** 2))
    wm = np.exp(-d_meno ** 2 / (2 * sigma ** 2))
    return (wp - wm) / (wp + wm)

fig, ax = plt.subplots(figsize=(11, 5.5))
ax.axhline(0, color="k", lw=.5)
ax.plot(t, v_bip,        color="k",       lw=2.5, label="bipolare (prova_ancore): v=(d⁻−d⁺)/(d⁻+d⁺)")
ax.plot(t, v_gauss(2.5), color="#1f77b4", lw=1.6, label="gaussiano reso bipolare, σ=2.5 (deciso)")
ax.plot(t, v_gauss(5.0), color="#d62728", lw=1.6, label="gaussiano reso bipolare, σ=5.0 (morbido)")
ax.set_ylim(-1.08, 1.08)
ax.set_ylabel("valore con segno")
ax.set_yticks([1, 0, -1]); ax.set_yticklabels(["+1\ntonale", "0\nmetà", "-1\nrumore"])
ax.set_xlabel("frame: da tonale (sinistra) a rumoroso (destra)")
ax.set_title("Stesso oggetto, due metodi resi bipolari: il σ del gaussiano è la manopola che il bipolare non ha")
ax.legend(loc="center right", fontsize=9)
fig.tight_layout()
OUT = "esplorazioni/confronto_bipolare_pulito.png"
fig.savefig(OUT, dpi=120)
print("PNG salvato:", OUT)
