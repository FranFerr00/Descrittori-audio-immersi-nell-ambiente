#!/usr/bin/env python3
"""Traiettorie dei gesti in 3D con assi INTERPRETABILI (descrittori veri).

Invece delle componenti PCA, quattro descrittori scelti uno per famiglia:
  x = centroid (brillantezza)   y = tpr (tonalita')   z = flux (movimento)
  colore = flatness (rumorosita')   percorso = tempo.
Cinque dimensioni leggibili senza tradurre i numeri. Esce: traiettorie_3d_interp.gif

Per cambiare assi, modifica AX/AY/AZ/AC qui sotto (nomi DESCS).
"""
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d.art3d import Line3DCollection

AX, AY, AZ, AC = "centroid", "tpr", "flux", "flatness"
ETICH = {"centroid": "centroid (brillantezza)", "tpr": "tpr (tonalita')",
         "flux": "flux (movimento)", "flatness": "flatness (rumorosita')"}
PASSO = 3

GESTI = {
    "clarinetto": [("clarinettocb", c) for c in
                   ["001", "002", "003", "004", "005", "006", "007", "010", "013"]],
    "timpano": [("timpano", c) for c in
                ["004", "005", "006", "007", "008", "015", "016", "018", "023", "025"]],
}


def frames(strum, cid, cols):
    path = f"analisi/{strum}/analisi/{cid}/{cid}_hann_ov50_10000hz_analisi.csv"
    rows = [r for r in csv.DictReader(open(path)) if r.get("gated", "0") != "1"]
    rows = rows[::PASSO]
    return np.array([[float(r[c]) for c in cols] for r in rows])


def liscia(a, w=7):
    if len(a) < w:
        return a
    return np.convolve(a, np.ones(w) / w, mode="same")


cols = [AX, AY, AZ, AC]
traj, allf = {}, []
for fam, lst in GESTI.items():
    for strum, cid in lst:
        D = frames(strum, cid, cols)
        traj[(fam, cid)] = D
        allf.append(D)
allD = np.vstack(allf)

# scala colore robusta
vmin, vmax = np.percentile(allD[:, 3], 2), np.percentile(allD[:, 3], 98)
norm = plt.Normalize(vmin, vmax)

fig = plt.figure(figsize=(8.2, 7.4))
ax = fig.add_subplot(111, projection="3d")
sm = None
for (fam, cid), D in traj.items():
    x, y, z, c = (liscia(D[:, 0]), liscia(D[:, 1]), liscia(D[:, 2]), liscia(D[:, 3]))
    pts = np.array([x, y, z]).T.reshape(-1, 1, 3)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = Line3DCollection(segs, cmap="plasma", norm=norm)
    lc.set_array((c[:-1] + c[1:]) / 2)
    lc.set_linewidth(2.0)
    ax.add_collection3d(lc)
    sm = lc
    mk = "o" if fam == "clarinetto" else "^"
    ax.scatter([x[0]], [y[0]], [z[0]], marker=mk, color="black", s=28, depthshade=False)

ax.set_xlim(np.percentile(allD[:, 0], 1), np.percentile(allD[:, 0], 99))
ax.set_ylim(np.percentile(allD[:, 1], 1), np.percentile(allD[:, 1], 99))
ax.set_zlim(np.percentile(allD[:, 2], 1), np.percentile(allD[:, 2], 99))
ax.set_xlabel(ETICH[AX])
ax.set_ylabel(ETICH[AY])
ax.set_zlabel(ETICH[AZ])
cb = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.08)
cb.set_label(ETICH[AC])
ax.set_title("Traiettorie dei gesti su assi interpretabili\n"
             "o = inizio clarinetto, triangolo = inizio timpano", fontsize=10)
fig.tight_layout()

N = 60
def step(i):
    ax.view_init(elev=18, azim=i * (360 / N))
    return ()

anim = FuncAnimation(fig, step, frames=N, interval=100, blit=False)
anim.save("traiettorie_3d_interp.gif", writer=PillowWriter(fps=11), dpi=90)
print("scritto traiettorie_3d_interp.gif")
print(f"assi: x={AX}  y={AY}  z={AZ}  colore={AC}")
