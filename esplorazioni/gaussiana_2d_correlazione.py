#!/usr/bin/env python3
"""In 2D: due descrittori correlati (centroid, rolloff, r=+0.91). Mostra come la
campana del nodo passa da CERCHIO (isotropo, ignora la correlazione) a ELLISSE
INCLINATA (Mahalanobis, allineata alla nuvola), e come lo sbiancamento raddrizza
tutto. Eseguire dalla radice di descrittori/."""
import csv, glob, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RECS = "analisi/recs-003"
DESCS = ["centroid", "spread", "rolloff", "slope", "obsir_std", "flatness",
         "crest", "skewness", "kurtosis", "entropy", "tpr", "n_peaks",
         "tonality", "flux", "irregularity", "zcr"]
D1, D2 = "centroid", "rolloff"

def per_frame(seg):
    p = f"{RECS}/{seg}/{seg}_hann_ov50_10000hz_analisi.csv"
    fr = [f for f in csv.DictReader(open(p)) if f.get("gated", "0") == "0"]
    return np.array([[float(f[d]) for d in DESCS] for f in fr])

segs = sorted(os.path.basename(os.path.dirname(p))
              for p in glob.glob(f"{RECS}/*/*_hann_ov50_10000hz_analisi.csv"))
pool = np.concatenate([per_frame(s) for s in segs])
MU, SD = pool.mean(0), np.where(pool.std(0) > 0, pool.std(0), 1.0)
Z = (pool - MU) / SD
i1, i2 = DESCS.index(D1), DESCS.index(D2)
P = Z[:, [i1, i2]]                                  # nuvola 2D (z)

c = P.mean(0)                                        # nodo = centro nuvola
S = np.cov(P.T)                                      # covarianza 2x2
vals, vecs = np.linalg.eigh(S)
W = vecs @ np.diag(vals ** -0.5) @ vecs.T            # sbiancamento Σ^-1/2

def ellisse(cov, centro, k, **kw):
    val, vec = np.linalg.eigh(cov)
    th = np.linspace(0, 2 * np.pi, 200)
    circ = np.stack([np.cos(th), np.sin(th)])
    e = centro[:, None] + (vec @ np.diag(np.sqrt(val) * k) @ circ)
    return e

# due punti alla STESSA distanza euclidea dal nodo: uno LUNGO la nuvola, uno
# DI TRAVERSO -> il cerchio li tratta uguali, l'ellisse no
r = 2.2
P_lungo  = c + r * np.array([1, 1]) / np.sqrt(2)     # lungo la correlazione
P_trav   = c + r * np.array([1, -1]) / np.sqrt(2)    # di traverso

def maha(p):  # distanza di Mahalanobis dal nodo
    d = p - c
    return float(np.sqrt(d @ np.linalg.inv(S) @ d))

fig, (ax, axw) = plt.subplots(1, 2, figsize=(12, 6))

# --- pannello A: spazio originale ---
ax.scatter(P[:, 0], P[:, 1], s=3, alpha=.12, color="#888")
ax.plot(*c, "ko", ms=8); ax.annotate("nodo", c + 0.2, fontsize=9)
ax.plot(*ellisse(np.eye(2), c, r), color="#1f77b4", lw=2,
        label="cerchio (σ isotropa): ignora la correlazione")
ax.plot(*ellisse(S, c, r), color="#d62728", lw=2,
        label="ellisse (Mahalanobis): segue la nuvola")
for p, lab in [(P_lungo, "lungo"), (P_trav, "di traverso")]:
    ax.plot(*p, "k^", ms=9)
    ax.annotate(f"{lab}\nMaha={maha(p):.2f}", p + 0.15, fontsize=8)
ax.set_xlabel(f"{D1} (z)"); ax.set_ylabel(f"{D2} (z)")
ax.set_title(f"Spazio originale: {D1} e {D2} correlati (r=+0.91)")
ax.legend(loc="upper left", fontsize=8); ax.set_aspect("equal")
ax.set_xlim(-4, 4); ax.set_ylim(-4, 4)

# --- pannello B: spazio sbiancato ---
Pw = (P - c) @ W
ax_pts = Pw
axw.scatter(ax_pts[:, 0], ax_pts[:, 1], s=3, alpha=.12, color="#888")
axw.plot(0, 0, "ko", ms=8)
th = np.linspace(0, 2 * np.pi, 200)
# stessa ellisse di Mahalanobis -> diventa un cerchio
axw.plot(np.cos(th), np.sin(th), color="#d62728", lw=2,
         label="l'ellisse e' diventata un cerchio")
for p, lab in [(P_lungo, "lungo"), (P_trav, "di traverso")]:
    pw = (p - c) @ W
    axw.plot(*pw, "k^", ms=9)
    axw.annotate(f"{lab}\ndist={np.linalg.norm(pw):.2f}", pw + 0.1, fontsize=8)
axw.set_xlabel("asse sbiancato 1"); axw.set_ylabel("asse sbiancato 2")
axw.set_title("Spazio sbiancato: la correlazione e' raddrizzata")
axw.legend(loc="upper left", fontsize=8); axw.set_aspect("equal")
axw.set_xlim(-4, 4); axw.set_ylim(-4, 4)

fig.tight_layout()
OUT = "esplorazioni/gaussiana_2d_correlazione.png"
fig.savefig(OUT, dpi=120)
print("PNG salvato:", OUT)
print(f"\npunto 'lungo'      la nuvola: euclidea {r:.2f}  ->  Mahalanobis {maha(P_lungo):.2f}")
print(f"punto 'di traverso' la nuvola: euclidea {r:.2f}  ->  Mahalanobis {maha(P_trav):.2f}")
print("(stessa distanza euclidea, ma Mahalanobis diversissime: il cerchio li")
print(" pesa uguale, l'ellisse no.)")
