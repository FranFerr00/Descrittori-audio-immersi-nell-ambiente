#!/usr/bin/env python3
"""Tenuta del controllo a nodi sotto ripresa reale: figura (due pannelli) per il paper.

Pannello sinistro: sui sintetici nella stanza, v a due metri contro v a un metro
(entrambi ripresi), con i nodi tarati una volta nell'ambiente a un metro. E' la
condizione del vivo (niente riferimento asciutto): la firma comune della stanza entra
in entrambi i termini e si elide, e i punti restano sulla diagonale. Calcolo in
esplorazioni/controllo_nodi_ripresa.py (v_pairs_distanza).

Pannello destro: R lungo la distanza (2--8 m), nodi fissi a 1 m, per due assi di nodi
sugli strumenti acustici (esplorazioni/controllo_nodi_distanza.py): un asse largo fra
registri diversi (soprano / contrabbasso grave), che la catena conserva, e un asse
stretto fra suoni dello stesso strumento, che l'onda stazionaria rimescola.

I dati sono risolti dalla radice del repo via __file__, quindi gira sia da paper/
sia dalla radice.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "esplorazioni"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from controllo_nodi_ripresa import v_pairs_distanza, fit, ZSCORE  # noqa: E402
from controllo_nodi_distanza import r_vs_distanza, ASSI  # noqa: E402
from deriva_sintetico_ripreso import load_taratura  # noqa: E402


def main():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.6, 2.8))

    pairs = v_pairs_distanza(ZSCORE, "recs-002", "recs-004")   # 1 m vs 2 m, nodi a 1 m
    xa = np.array([p[1] for p in pairs])
    yb = np.array([p[2] for p in pairs])
    R, k = fit(xa, yb)
    axL.plot([-1, 1], [-1, 1], "k:", lw=0.8, label="ideale")
    axL.axhline(0, color="gray", lw=0.4); axL.axvline(0, color="gray", lw=0.4)
    axL.scatter(xa, yb, s=14, alpha=0.6, color="#3a6ea5")
    axL.plot([-1, 1], [-k, k], color="#3a6ea5", lw=1.4,
             label=f"$R={R:.2f}$, $k={k:.2f}$")
    axL.set_xlim(-1, 1); axL.set_ylim(-1, 1)
    axL.set_xlabel("$v$ a un metro", fontsize=8)
    axL.set_ylabel("$v$ a due metri", fontsize=8)
    axL.tick_params(labelsize=7)
    axL.legend(fontsize=6.5, frameon=False, loc="upper left")
    axL.set_title("sintetici nella stanza", fontsize=8)

    tar = load_taratura()
    axR.axhline(0, color="gray", lw=0.4)
    for (nome, (p_piu, p_meno)), col in zip(ASSI.items(), ["#3a6ea5", "#c0603a"]):
        mm, RR, _ = r_vs_distanza(p_piu, p_meno, tar)
        etichetta = nome.split(" (")[0]
        axR.plot(mm, RR, "o-", color=col, lw=1.4, ms=4, label=f"asse {etichetta}")
    axR.set_xlim(2, 8); axR.set_ylim(-0.4, 1.0)
    axR.set_xlabel("distanza del microfono (m)", fontsize=8)
    axR.set_ylabel("$R$ ($v$ ripreso vs $v$ a 1 m)", fontsize=8)
    axR.tick_params(labelsize=7)
    axR.set_title("strumenti, lungo la distanza", fontsize=8)
    axR.legend(fontsize=6.5, frameon=False, loc="lower left")

    fig.tight_layout()
    out = HERE / "figura_controllo_nodi.pdf"
    fig.savefig(out)
    print(f"scritto {out}")


if __name__ == "__main__":
    main()
