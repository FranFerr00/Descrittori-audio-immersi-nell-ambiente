#!/usr/bin/env python3
"""Confronto: metodo BIPOLARE (prova_ancore.py)  vs  gaussiane a due nodi.
Due nodi: tonale (+1) e rumoroso (-1). Lungo lo sweep tonale->rumore mostra:
 - il valore con segno dei due metodi (chi sta vincendo, da +1 a -1)
 - la copertura: dove il bipolare 'inventa' un valore pur essendo lontano da tutto.
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

A_piu  = nodo("13_sin100")      # +1  tonale
A_meno = nodo("17_noise100")    # -1  rumoroso

SWEEP = ["13_sin100", "14_sin75_noise25", "15_sin50_noise50",
         "16_sin25_noise75", "17_noise100"]
X = np.concatenate([zmat(per_frame(s)) for s in SWEEP])
t = np.arange(len(X))

d_piu  = np.sqrt(((X - A_piu)  ** 2).sum(1))
d_meno = np.sqrt(((X - A_meno) ** 2).sum(1))

# --- BIPOLARE (prova_ancore.py): rapporto di distanze grezze ----------------
v_bip = (d_meno - d_piu) / (d_meno + d_piu)        # +1 sul tonale, -1 sul rumore

# --- GAUSSIANO a due nodi: quota+ - quota- (= tanh) -------------------------
def v_gauss(sigma):
    wp = np.exp(-d_piu  ** 2 / (2 * sigma ** 2))
    wm = np.exp(-d_meno ** 2 / (2 * sigma ** 2))
    v = (wp - wm) / (wp + wm)
    cop = wp + wm                                   # copertura (presenza totale)
    return v, cop

fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)

a1.axhline(0, color="k", lw=.5)
a1.plot(t, v_bip, color="k", lw=2, label="bipolare (prova_ancore)")
for sigma, c in [(2.5, "#1f77b4"), (5.0, "#d62728")]:
    v, _ = v_gauss(sigma)
    a1.plot(t, v, color=c, lw=1.3, label=f"gaussiano σ={sigma}")
a1.set_ylim(-1.05, 1.05)
a1.set_ylabel("valore con segno\n+1 tonale   ·   -1 rumore")
a1.set_title("Bipolare vs gaussiano: chi comanda lungo lo sweep tonale->rumore")
a1.legend(loc="center right", fontsize=8)

for sigma, c in [(2.5, "#1f77b4"), (5.0, "#d62728")]:
    _, cop = v_gauss(sigma)
    a2.plot(t, cop, color=c, label=f"copertura gaussiana σ={sigma}")
a2.axhline(0.05, color="gray", ls=":", lw=.7)
a2.text(2, 0.07, "sotto questa linea: 'fuori zona'", fontsize=7, color="gray")
a2.set_ylabel("copertura\n(presenza totale)")
a2.set_xlabel("frame: da tonale (sinistra) a rumoroso (destra)")
a2.set_title("Il bipolare NON ha copertura: dà sempre un valore, anche nel vuoto")
a2.legend(loc="upper center", fontsize=8)

fig.tight_layout()
OUT = "esplorazioni/confronto_bipolare_gaussiane.png"
fig.savefig(OUT, dpi=120)
print("PNG salvato:", OUT)

# tabella alle tappe
print(f"\n{'punto':>14} | {'bipolare':>9} | {'gauss2.5':>9} | {'gauss5.0':>9} | {'cop2.5':>7}")
print("-" * 60)
bordi = np.cumsum([len(per_frame(s)) for s in SWEEP])
v25, c25 = v_gauss(2.5); v50, _ = v_gauss(5.0)
for i, s in enumerate(SWEEP):
    k = bordi[i] - 1
    print(f"{s.split('_',1)[1]:>14} | {v_bip[k]:9.2f} | {v25[k]:9.2f} | "
          f"{v50[k]:9.2f} | {c25[k]:7.3f}")
