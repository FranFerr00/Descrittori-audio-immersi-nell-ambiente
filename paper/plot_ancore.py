#!/usr/bin/env python3
"""Figura: il campo del valore con segno v fra due nodi (larghezza colonna, vettoriale).

Ricostruisce lo schema del controllo a nodi e distanza: in uno spazio di due
descrittori, v = (d- - d+) / (d- + d+) vale +1 sul nodo positivo, -1 sul nodo
negativo, 0 sul piano mediano. Sostituisce la vecchia figura raster.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent

A_MENO = np.array([-2.5, 0.0])   # nodo -1 (parametro giù)
A_PIU = np.array([2.5, 0.0])     # nodo +1 (parametro su)
INGRESSO = np.array([1.2, 1.9])  # suono in ingresso (esempio)


def main():
    x = np.linspace(-6, 6, 400)
    y = np.linspace(-3.5, 3.5, 300)
    xx, yy = np.meshgrid(x, y)
    d_meno = np.hypot(xx - A_MENO[0], yy - A_MENO[1])
    d_piu = np.hypot(xx - A_PIU[0], yy - A_PIU[1])
    v = (d_meno - d_piu) / (d_meno + d_piu)

    fig, ax = plt.subplots(figsize=(3.4, 2.5))
    cf = ax.contourf(xx, yy, v, levels=np.linspace(-1, 1, 21),
                     cmap="RdBu_r", vmin=-1, vmax=1)
    ax.contour(xx, yy, v, levels=[-0.5, 0.0, 0.5], colors="k",
               linewidths=0.4, alpha=0.4)
    ax.axvline(0, color="k", ls="--", lw=0.6, alpha=0.6)  # piano mediano v=0

    # nodi
    for p, lab in ((A_MENO, "nodo $-1$"), (A_PIU, "nodo $+1$")):
        ax.plot(*p, "o", mfc="white", mec="k", ms=8, mew=1.2)
    ax.annotate("nodo $-1$\n(parametro giù)", A_MENO, textcoords="offset points",
                xytext=(0, -22), ha="center", fontsize=6)
    ax.annotate("nodo $+1$\n(parametro su)", A_PIU, textcoords="offset points",
                xytext=(0, -22), ha="center", fontsize=6)

    # suono in ingresso + distanze
    ax.plot(*INGRESSO, "k^", ms=6)
    ax.annotate("suono in ingresso", INGRESSO, textcoords="offset points",
                xytext=(4, 6), fontsize=6)
    for p in (A_MENO, A_PIU):
        ax.plot([INGRESSO[0], p[0]], [INGRESSO[1], p[1]], "k-", lw=0.6, alpha=0.7)

    ax.set_xlabel("asse descrittore A", fontsize=7)
    ax.set_ylabel("asse descrittore B", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.set_title(r"Campo di $v=\frac{d_- - d_+}{d_- + d_+}$ fra due nodi", fontsize=8)
    cb = fig.colorbar(cf, ax=ax, ticks=[-1, 0, 1], fraction=0.046, pad=0.04)
    cb.set_label("$v$", fontsize=7)
    cb.ax.tick_params(labelsize=6)

    fig.tight_layout()
    fig.savefig(HERE / "figura_ancore.pdf")
    print("scritto figura_ancore.pdf")


if __name__ == "__main__":
    main()
