#!/usr/bin/env python3
"""Confronto numeri 10000 Hz vs 48000 Hz (banda piena) per i punti del paper.

Stampa, per ogni numero citato in §4, il valore vecchio (10k) e nuovo (48k),
cosi' da aggiornare la prosa e le tabelle e verificare se le conclusioni reggono.
Legge le medie sui frame validi (gated=0) dai CSV per-segmento.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "analisi"


def mean_valid(csv_path, cols):
    """Media sui frame non-gated di ogni colonna in cols."""
    acc = {c: [] for c in cols}
    with open(csv_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("gated", "0") == "1":
                continue
            for c in cols:
                acc[c].append(float(r[c]))
    return {c: (sum(v) / len(v) if v else float("nan")) for c, v in acc.items()}


def both_bands(folder, name, cols):
    """Ritorna {col: (v10k, v48k)} per un segmento, dai due CSV di banda."""
    p10 = folder / f"{name}_hann_ov50_10000hz_analisi.csv"
    p48 = folder / f"{name}_hann_ov50_48000hz_analisi.csv"
    m10 = mean_valid(p10, cols) if p10.exists() else {c: float("nan") for c in cols}
    m48 = mean_valid(p48, cols) if p48.exists() else {c: float("nan") for c in cols}
    return {c: (m10[c], m48[c]) for c in cols}


def show(title, folder, name, cols):
    print(f"\n### {title}  ({name})")
    print(f"{'descr':<14}{'10k':>12}{'48k':>12}")
    bb = both_bands(folder, name, cols)
    for c in cols:
        v10, v48 = bb[c]
        print(f"{c:<14}{v10:>12.4g}{v48:>12.4g}")
    return bb


def main():
    # --- Clarinetto: piano=001, mezzoforte=003, forte=004 ---
    clar_dir = A / "clarinettocb" / "analisi"
    clar_cols = ["centroid", "rolloff", "irregularity", "flatness", "tonality", "kurtosis"]
    print("\n========== CLARINETTO (analisi/clarinettocb/analisi) ==========")
    cl = {}
    for dyn, sid in [("piano", "001"), ("mezzoforte", "003"), ("forte", "004")]:
        cl[dyn] = show(f"clar {dyn}", clar_dir / sid, sid, clar_cols)
    print("\n-- rapporti forte/piano (48k) --")
    for c in clar_cols:
        p = cl["piano"][c][1]; f = cl["forte"][c][1]
        print(f"  {c:<14} forte/piano = {f/p:.2f}x   (piano={p:.4g} forte={f:.4g})")

    # --- Timpano: piano=004, mezzoforte=005, forte=006 ---
    timp_dir = A / "timpano" / "analisi"
    timp_cols = ["centroid", "spread", "rolloff", "irregularity", "flux", "entropy", "n_peaks"]
    print("\n\n========== TIMPANO (analisi/timpano/analisi) ==========")
    for dyn, sid in [("piano", "004"), ("mezzoforte", "005"), ("forte", "006")]:
        show(f"timp {dyn}", timp_dir / sid, sid, timp_cols)

    # --- bin esatto (sintetici 24, 26) ---
    print("\n\n========== BIN ESATTO (sintetici) ==========")
    bin_cols = ["flatness", "tpr", "spread", "crest"]
    for name in ["24_bin_esatto_40", "26_bin_esatto_80", "25_fuori_bin_40", "27_fuori_bin_80"]:
        show(name, A / "sintetici" / name, name, bin_cols)

    # --- noise centroid (sanity: white/pink at banda piena) ---
    print("\n\n========== RUMORE: centroide a banda piena (sanity) ==========")
    for name in ["02_noise_bianco", "17_noise100"]:
        show(name, A / "sintetici" / name, name, ["centroid", "rolloff"])


if __name__ == "__main__":
    main()
