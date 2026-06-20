#!/usr/bin/env python3
"""Figura LEAP: l'onda del centroide sui CCB lungo la fila di microfoni.

Sui cluster di clarinetto contrabbasso il centroide, mediato sui campioni, disegna
un'onda lungo gli 8 microfoni (cresta verso il mic 3, avvallamento verso i mic 5-6).
Le curve orizzontale e verticale quasi coincidono: l'onda non e' direttivita' del
microfono, ma una stazionaria della fondamentale nello spazio acustico. Dati a banda
piena (media_intero) dei cluster del trombino originale.
"""
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
PIENA = ROOT / "analisi/distanza-banda-piena/centroidi_medie.csv"


def media_per_canale(prefisso_modo):
    """Media del centroide (file intero) per canale sui cluster CCB trombino di un modo.

    prefisso_modo: 'CCB_trombino_oriz' o 'CCB_trombino_vert'.
    Considera i CLUSTER (non il DO singolo) per avere piu' campioni a canale.
    """
    acc = defaultdict(list)
    with open(PIENA, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            nome = r["file"]
            if nome.startswith(prefisso_modo) and "CLUSTER" in nome and r["media_intero"]:
                acc[int(r["canale"])].append(float(r["media_intero"]))
    canali = sorted(acc)
    medie = [sum(acc[c]) / len(acc[c]) for c in canali]
    return canali, medie


def main():
    fig, ax = plt.subplots(figsize=(3.4, 2.7))
    for prefisso, etich, col in [
        ("CCB_trombino_oriz", "orizzontale", "C0"),
        ("CCB_trombino_vert", "verticale", "C3"),
    ]:
        canali, medie = media_per_canale(prefisso)
        ax.plot(canali, medie, "-o", color=col, ms=3, label=etich)
        print(f"{prefisso}: " + " ".join(f"{m:.0f}" for m in medie))
    ax.set_xlabel("microfono (distanza in m)", fontsize=8)
    ax.set_ylabel("centroide dei CCB (Hz)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=7, loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(HERE / "figura_leap_onda_ccb.pdf", bbox_inches="tight")


if __name__ == "__main__":
    main()
