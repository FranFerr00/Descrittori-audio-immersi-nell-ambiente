#!/usr/bin/env python3
"""Traiettorie dei gesti in 3D + colore: cinque dimensioni in una GIF rotante.

  assi x,y,z = PC1, PC2, PC3   colore = PC4   percorso della linea = tempo.
Ogni gesto strumentale e' una linea che segue i suoi frame. Cerchio = inizio
(clarinetto), triangolo = inizio (timpano). Esce: traiettorie_3d.gif
"""
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d.art3d import Line3DCollection

DESCS = ["centroid", "spread", "rolloff", "slope", "obsir_std", "flatness",
         "crest", "skewness", "kurtosis", "entropy", "tpr", "n_peaks",
         "tonality", "flux", "irregularity", "zcr"]
PASSO = 3

GESTI = {
    "clarinetto": [("clarinettocb", c, "") for c in
                   ["001", "002", "003", "004", "005", "006", "007", "010", "013"]],
    "timpano": [("timpano", c, "") for c in
                ["004", "005", "006", "007", "008", "015", "016", "018", "023", "025"]],
}


def frames(strum, cid):
    path = f"analisi/{strum}/analisi/{cid}/{cid}_hann_ov50_10000hz_analisi.csv"
    rows = [r for r in csv.DictReader(open(path)) if r.get("gated", "0") != "1"]
    rows = rows[::PASSO]
    return np.array([[float(r[d]) for d in DESCS] for r in rows])


def liscia(a, w=7):
    if len(a) < w:
        return a
    return np.convolve(a, np.ones(w) / w, mode="same")


traj_raw, allraw = {}, []
for fam, lst in GESTI.items():
    for strum, cid, _ in lst:
        R = frames(strum, cid)
        traj_raw[(fam, cid)] = R
        allraw.append(R)
allR = np.vstack(allraw)
cmean, cstd = allR.mean(axis=0), allR.std(axis=0)
cstd[cstd == 0] = 1.0
allZ = (allR - cmean) / cstd
mu = allZ.mean(axis=0)
U, S, Vt = np.linalg.svd(allZ - mu, full_matrices=False)
for k in range(4):
    if Vt[k][np.argmax(np.abs(Vt[k]))] < 0:
        Vt[k] = -Vt[k]
var = (S ** 2) / (S ** 2).sum() * 100

allP4 = (allZ - mu) @ Vt[3]
vmin, vmax = np.percentile(allP4, 2), np.percentile(allP4, 98)
norm = plt.Normalize(vmin, vmax)

fig = plt.figure(figsize=(8, 7.4))
ax = fig.add_subplot(111, projection="3d")
sm = None
for (fam, cid), R in traj_raw.items():
    Z = (R - cmean) / cstd
    P = (Z - mu) @ Vt[:4].T
    x, y, z, c = liscia(P[:, 0]), liscia(P[:, 1]), liscia(P[:, 2]), liscia(P[:, 3])
    pts = np.array([x, y, z]).T.reshape(-1, 1, 3)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = Line3DCollection(segs, cmap="plasma", norm=norm)
    lc.set_array((c[:-1] + c[1:]) / 2)
    lc.set_linewidth(2.0)
    ax.add_collection3d(lc)
    sm = lc
    mk = "o" if fam == "clarinetto" else "^"
    ax.scatter([x[0]], [y[0]], [z[0]], marker=mk, color="black", s=28, depthshade=False)

# limiti robusti (percentili): un transiente isolato non deve stirare gli assi
allP = (allZ - mu) @ Vt[:3].T
ax.set_xlim(np.percentile(allP[:, 0], 1), np.percentile(allP[:, 0], 99))
ax.set_ylim(np.percentile(allP[:, 1], 1), np.percentile(allP[:, 1], 99))
ax.set_zlim(np.percentile(allP[:, 2], 1), np.percentile(allP[:, 2], 99))
ax.set_xlabel(f"PC1 ({var[0]:.0f}%)")
ax.set_ylabel(f"PC2 ({var[1]:.0f}%)")
ax.set_zlabel(f"PC3 ({var[2]:.0f}%)")
cb = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.08)
cb.set_label(f"PC4 ({var[3]:.0f}%) = colore")
ax.set_title("Traiettorie dei gesti: PC1/PC2/PC3 + colore PC4 + tempo\n"
             "o = inizio clarinetto, triangolo = inizio timpano", fontsize=10)
fig.tight_layout()

N = 60
def step(i):
    ax.view_init(elev=18, azim=i * (360 / N))
    return ()

anim = FuncAnimation(fig, step, frames=N, interval=100, blit=False)
anim.save("traiettorie_3d.gif", writer=PillowWriter(fps=11), dpi=90)
print("scritto traiettorie_3d.gif")
print(f"PC1 {var[0]:.0f}%  PC2 {var[1]:.0f}%  PC3 {var[2]:.0f}%  PC4 {var[3]:.0f}%")
