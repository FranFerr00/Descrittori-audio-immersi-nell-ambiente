#!/usr/bin/env python3
"""Normalizza z-score per-sample i CSV prodotti da analisi.py.

Per ogni descrittore calcola media e std sui frame non-gated del singolo
CSV, poi applica z = (x - media) / std a tutta la colonna. Produce un
CSV companion `*_zscore.csv` nella stessa cartella del CSV di origine.

Uso:
  python zscore.py path/al/CSV.csv
  python zscore.py path/alla/cartella/   # ricorsivo su *_analisi.csv
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


META_COLS = {"frame", "time", "gated"}


def zscore_csv(csv_path: Path) -> Path | None:
    df = pd.read_csv(csv_path)
    if "gated" in df.columns:
        valid = df[df["gated"] == 0]
    else:
        valid = df
    if len(valid) == 0:
        print(f"!! {csv_path.name}: nessun frame valido, salto")
        return None

    out = df[[c for c in df.columns if c in META_COLS]].copy()
    for col in df.columns:
        if col in META_COLS:
            continue
        vals = df[col].astype(float).to_numpy()
        ref = valid[col].astype(float).to_numpy()
        mean = float(np.mean(ref))
        std = float(np.std(ref, ddof=0))
        if std == 0 or np.isnan(std):
            out[col] = 0.0
        else:
            out[col] = (vals - mean) / std

    out_path = csv_path.with_name(csv_path.name.replace("_analisi.csv", "_zscore.csv"))
    if out_path == csv_path:
        out_path = csv_path.with_suffix(".zscore.csv")
    out.to_csv(out_path, index=False, float_format="%.6f")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", type=Path, help="CSV singolo o cartella (ricorsiva su *_analisi.csv)")
    args = ap.parse_args()

    if args.target.is_file():
        csvs = [args.target]
    else:
        csvs = sorted(args.target.rglob("*_analisi.csv"))

    if not csvs:
        print("nessun CSV trovato")
        sys.exit(1)

    for csv in csvs:
        out = zscore_csv(csv)
        if out is not None:
            print(f">> {out}")


if __name__ == "__main__":
    main()
