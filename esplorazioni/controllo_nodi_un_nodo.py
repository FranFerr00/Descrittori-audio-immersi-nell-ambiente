#!/usr/bin/env python3
"""Esempio minimo: UN nodo solo. Il peso = misuratore di vicinanza (0..1).
Mostra come la gaussiana del nodo 'rumoroso' si accende mentre il suono va da
tonale a rumore, per due sigma diverse. Eseguire dalla radice di descrittori/."""
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

# z-score congelato sul corpus recs-003
segnali = sorted(os.path.basename(os.path.dirname(p))
                 for p in glob.glob(f"{RECS}/*/*_hann_ov50_10000hz_analisi.csv"))
pool = np.concatenate([per_frame(s) for s in segnali])
MU, SD = pool.mean(0), np.where(pool.std(0) > 0, pool.std(0), 1.0)
zmat = lambda raw: (raw - MU) / SD

# UN nodo solo: 'rumoroso'
nodo = zmat(per_frame("17_noise100")).mean(0)

# traiettoria: continuo tonale -> rumore
SWEEP = ["13_sin100", "14_sin75_noise25", "15_sin50_noise50",
         "16_sin25_noise75", "17_noise100"]
X = np.concatenate([zmat(per_frame(s)) for s in SWEEP])
t = np.arange(len(X))

dist = np.sqrt(((X - nodo) ** 2).sum(1))           # distanza dal nodo (z)

fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

a1.plot(t, dist, color="#333")
a1.set_ylabel("distanza dal nodo\n(in z)")
a1.set_title("UN nodo solo ('rumoroso'): distanza e peso lungo lo sweep tonale->rumore")
a1.invert_yaxis()  # in alto = vicino

for sigma, col in [(2.5, "#1f77b4"), (5.0, "#d62728")]:
    w = np.exp(-dist ** 2 / (2 * sigma ** 2))      # peso grezzo = vicinanza 0..1
    a2.plot(t, w, color=col, label=f"σ = {sigma}")
a2.axhline(0.61, color="gray", lw=.6, ls=":")
a2.text(2, 0.62, "0.61 = a 1σ dal nodo", fontsize=7, color="gray")
a2.set_ylim(0, 1.02); a2.set_ylabel("peso (presenza)\n1=sopra il nodo, 0=lontano")
a2.set_xlabel("frame: da tonale (sinistra) a rumoroso (destra)")
a2.legend(loc="upper left", fontsize=9)

fig.tight_layout()
OUT = "esplorazioni/controllo_nodi_un_nodo.png"
fig.savefig(OUT, dpi=120)
print("PNG salvato:", OUT)
print(f"\ninizio (tonale): distanza {dist[0]:.1f}  -> peso(σ=2.5) {np.exp(-dist[0]**2/(2*2.5**2)):.3f}")
print(f"fine (rumore):   distanza {dist[-1]:.1f}  -> peso(σ=2.5) {np.exp(-dist[-1]**2/(2*2.5**2)):.3f}")
