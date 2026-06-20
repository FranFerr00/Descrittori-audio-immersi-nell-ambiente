#!/usr/bin/env python3
"""Figura LEAP: centroide del rumore vs distanza, a banda piena e con tetto a 10 kHz.

Il rumore registrato dagli 8 microfoni in fila (canale = metri) mostra, a banda
piena, un centroide che cala con la distanza (assorbimento dell'aria sugli acuti);
con il tetto a 10 kHz lo stesso centroide appare quasi piatto, perche' il calo sta
proprio sopra i 10 kHz. Dati: centroidi_medie.csv (colonna media_intero) prodotti
da centroidi_riepilogo.py nelle due cartelle di analisi.
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
PIENA = ROOT / "analisi/distanza-banda-piena/centroidi_medie.csv"
DIECIK = ROOT / "analisi/distanza/centroidi_medie.csv"


def curva(path, nome_file):
    """Centroide medio (file intero) per canale, per un dato file del rumore."""
    dist, cen = [], []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["file"] == nome_file and r["media_intero"]:
                dist.append(int(r["canale"]))
                cen.append(float(r["media_intero"]))
    coppie = sorted(zip(dist, cen))
    return [d for d, _ in coppie], [c for _, c in coppie]


def main():
    fig, ax = plt.subplots(figsize=(3.4, 2.7))
    casi = [
        ("NOISE_oriz_1-9mt", "orizzontale"),
        ("NOISE_vert_1-9mt", "verticale"),
    ]
    colori = {"orizzontale": "C0", "verticale": "C1"}
    for nome, etich in casi:
        dp, cp = curva(PIENA, nome)
        dd, cd = curva(DIECIK, nome)
        ax.plot(dp, cp, "-o", color=colori[etich], ms=3,
                label=f"{etich}, banda piena")
        ax.plot(dd, cd, "--s", color=colori[etich], ms=3, alpha=0.6,
                label=f"{etich}, fino a 10 kHz")
        print(f"{nome}: banda piena {cp[0]:.0f}->{cp[-1]:.0f} Hz; "
              f"10 kHz {cd[0]:.0f}->{cd[-1]:.0f} Hz")
    ax.set_xlabel("distanza dal microfono (m)", fontsize=8)
    ax.set_ylabel("centroide del rumore (Hz)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=6, loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(HERE / "figura_leap_centroide_rumore.pdf", bbox_inches="tight")


if __name__ == "__main__":
    main()
