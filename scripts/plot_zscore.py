#!/usr/bin/env python3
"""Plot dei descrittori z-scored: un PNG per CSV `*_zscore.csv`.

Quattro subplot (uno per famiglia) sullo stesso asse y in deviazioni
standard, con tutti i descrittori sovrapposti. Le regioni gated sono
mostrate in grigio chiaro sullo sfondo.

Uso:
  python plot_zscore.py path/al/CSV_zscore.csv
  python plot_zscore.py path/alla/cartella/   # ricorsivo
"""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Famiglie: il decrease/obsir_std e' gestito dinamicamente in base
# a cosa esiste nel CSV (corpus pre/post rigenerazione).
FAMIGLIE = {
    "forma":         ["centroid", "spread", "rolloff", "slope", "obsir_std", "decrease"],
    "distribuzione": ["flatness", "crest", "skewness", "kurtosis", "entropy"],
    "tonalita":      ["tpr", "n_peaks", "tonality"],
    "dinamica":      ["flux", "irregularity", "zcr"],
}

YMIN, YMAX = -4.0, 4.0


def plot_csv(csv_path: Path) -> Path:
    df = pd.read_csv(csv_path)
    t = df["time"].to_numpy()
    gated = df["gated"].to_numpy() if "gated" in df.columns else np.zeros(len(df))

    fig, axs = plt.subplots(4, 1, figsize=(12, 10), sharex=True, sharey=True)
    fig.suptitle(csv_path.stem, fontsize=10)

    for ax, (fam, cols) in zip(axs, FAMIGLIE.items()):
        cols_present = [c for c in cols if c in df.columns]
        # sfondo gated
        if gated.any():
            ax.fill_between(t, YMIN, YMAX, where=gated > 0,
                            color="lightgrey", alpha=0.4, step="mid", linewidth=0)
        # linee guida ±1σ, ±2σ
        for y in (-2, -1, 0, 1, 2):
            ax.axhline(y, color="black", linewidth=0.3, alpha=0.3)
        for c in cols_present:
            ax.plot(t, df[c].to_numpy(), label=c, linewidth=0.8)
        ax.set_ylim(YMIN, YMAX)
        ax.set_ylabel(f"{fam}\n(σ)", fontsize=9)
        ax.legend(loc="upper right", fontsize=7, ncol=len(cols_present), frameon=False)

    axs[-1].set_xlabel("tempo (s)")
    fig.tight_layout()

    out_path = csv_path.with_name(csv_path.name.replace("_zscore.csv", "_zscore.png"))
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", type=Path, help="CSV singolo o cartella (ricorsiva su *_zscore.csv)")
    args = ap.parse_args()

    if args.target.is_file():
        csvs = [args.target]
    else:
        csvs = sorted(args.target.rglob("*_zscore.csv"))

    if not csvs:
        print("nessun CSV trovato")
        sys.exit(1)

    for csv in csvs:
        out = plot_csv(csv)
        print(f">> {out}")


if __name__ == "__main__":
    main()
