#!/usr/bin/env python3
"""Figura LEAP: attenuazione del rumore sulla distanza.

L'RMS del rumore per canale (gia' in dB relativi al microfono a 1 m, file
attenuazione_distanza.csv) si confronta con la retta 1/sqrt(r) (ampiezza ~ 1/sqrt(r),
-3 dB per raddoppio). I punti del fonometro in sala (96/93/90/87 dBA a 1/2/4/8 m)
confermano i -3 dB: in sala riverberante l'ampiezza segue 1/sqrt(r).
"""
import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
ATT = ROOT / "analisi/distanza-banda-piena/attenuazione_distanza.csv"

# Fonometro in sala (curva A) al variare della distanza, dB relativi a 1 m.
FONOMETRO_DBA = {1: 0.0, 2: -3.0, 4: -6.0, 8: -9.0}


def misura(modo):
    dist, rel = [], []
    with open(ATT, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["modo"] == modo:
                dist.append(float(r["distanza_m"]))
                rel.append(float(r["rel_db"]))
    coppie = sorted(zip(dist, rel))
    return [d for d, _ in coppie], [v for _, v in coppie]


def main():
    fig, ax = plt.subplots(figsize=(3.4, 2.7))
    d = [1, 2, 3, 4, 5, 6, 7, 8]
    ax.plot(d, [-10 * math.log10(x) for x in d], "k-", lw=1,
            label=r"$1/\sqrt{r}$ ($-3$ dB/raddoppio)")
    for modo, etich, col in [("oriz", "misura orizzontale", "C0"),
                             ("vert", "misura verticale", "C1")]:
        dm, rm = misura(modo)
        ax.plot(dm, rm, "o", color=col, ms=3, label=etich)
        print(f"{modo}: 8 m = {rm[-1]:.1f} dB rel 1 m")
    fd = sorted(FONOMETRO_DBA)
    ax.plot(fd, [FONOMETRO_DBA[x] for x in fd], "D", color="C3", ms=4,
            label="fonometro in sala")
    ax.set_xscale("log", base=2)
    ax.set_xticks(d)
    ax.set_xticklabels([str(x) for x in d])
    ax.set_xlabel("distanza dal microfono (m)", fontsize=8)
    ax.set_ylabel("livello relativo a 1 m (dB)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=6, loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(HERE / "figura_leap_attenuazione.pdf", bbox_inches="tight")


if __name__ == "__main__":
    main()
