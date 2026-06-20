#!/usr/bin/env python3
"""Figura 2: la stessa dinamica letta da descrittori diversi.
Pannello A (clarinetto, crescendo): il centroide (forma) traccia il gesto.
Pannello B (timpano sostenuto): il centroide resta piatto, l'irregularity
e' l'unico che segue la dinamica.
Dati: CSV frame-per-frame dei cataloghi strumentali.
"""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]  # radice del repo (paper/ e' una sottocartella)
HERE = Path(__file__).resolve().parent      # cartella paper/
CLAR = ROOT / "analisi/clarinettocb/analisi/005/005_hann_ov50_48000hz_analisi.csv"
TIMP = ROOT / "analisi/timpano/analisi/015/015_hann_ov50_48000hz_analisi.csv"


def load(path, cols):
    out = {c: [] for c in cols}
    out["time"] = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("gated", "0") == "1":
                continue  # frame escluso dal gate
            out["time"].append(float(row["time"]))
            for c in cols:
                out[c].append(float(row[c]))
    return out


def main():
    clar = load(CLAR, ["centroid"])
    timp = load(TIMP, ["centroid", "irregularity"])

    fig, (a, b) = plt.subplots(2, 1, figsize=(3.4, 3.6), sharex=False)

    a.plot(clar["time"], clar["centroid"], color="C0")
    a.set_title("Clarinetto, crescendo: centroide segue il gesto", fontsize=8)
    a.set_ylabel("centroide (Hz)", fontsize=7)
    a.grid(True, alpha=0.3)

    b.plot(timp["time"], timp["centroid"], color="C0", label="centroide (Hz)")
    bt = b.twinx()
    bt.plot(timp["time"], timp["irregularity"], color="C3", label="irregularity")
    b.set_title("Timpano sostenuto: solo irregularity si muove", fontsize=8)
    b.set_xlabel("tempo (s)", fontsize=7)
    b.set_ylabel("centroide (Hz)", fontsize=7, color="C0")
    bt.set_ylabel("irregularity", fontsize=7, color="C3")
    b.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(HERE / "figura_gesto_strumenti.pdf")
    print("scritto figura_gesto_strumenti.pdf")


if __name__ == "__main__":
    main()
