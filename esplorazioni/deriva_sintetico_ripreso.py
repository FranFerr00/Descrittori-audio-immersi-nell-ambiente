#!/usr/bin/env python3
"""Deriva sintetico -> ripreso, frame per frame.

Per ogni segnale, misura quanto le versioni riprese si allontanano dal sintetico
nello spazio dei descrittori (z-score e Mahalanobis sbiancata), sui soli frame
validi (gated=0) in entrambe. Calibrazione congelata del corpus, come prova_ancore.py.
"""
import csv
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]   # radice del repo
HERE = Path(__file__).resolve().parent       # esplorazioni/
SOMMARIO = ROOT / "analisi/tabelle/segnali_sommario.csv"
ANALISI = ROOT / "analisi"
SUFFIX = "_hann_ov50_48000hz_analisi.csv"  # banda piena (Nyquist 96 kHz), allineato a §5/LEAP
REF = "sintetici"

DESCS = ["centroid", "spread", "rolloff", "slope", "obsir_std", "flatness",
         "crest", "skewness", "kurtosis", "entropy", "tpr", "n_peaks",
         "tonality", "flux", "irregularity", "zcr"]

# config ripresa -> etichetta leggibile (ordine = colonne della tabella)
CONFIGS = {
    "test_segnali_-30db": "−30 dB (controllo)",
    "recs-002": "1 m",
    "recs-003": "2 m sporco",
    "recs-004": "2 m pulito",
}


def load_taratura(sommario_path=SOMMARIO):
    """Media e deviazione standard (popolazione) congelate dal corpus, per descrittore.

    Legge le colonne <descr>_mean di segnali_sommario.csv, identico a prova_ancore.py.
    """
    with open(sommario_path) as f:
        rows = list(csv.DictReader(f))
    tar = {}
    for d in DESCS:
        c = [float(r[d + "_mean"]) for r in rows]
        m = sum(c) / len(c)
        sd = (sum((x - m) ** 2 for x in c) / len(c)) ** 0.5 or 1.0
        tar[d] = (m, sd)
    return tar


def load_frames(csv_path, taratura):
    """Ritorna (Z, gated): Z[n,16] z-scored dai grezzi, gated[n] bool."""
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
    Z = np.array([[(float(r[d]) - taratura[d][0]) / taratura[d][1] for d in DESCS]
                  for r in rows], dtype=float)
    gated = np.array([r.get("gated", "0") == "1" for r in rows], dtype=bool)
    return Z, gated


def whitening_from_Z(Z):
    """Inversa della matrice di correlazione di Z[n,16] (Mahalanobis, come --sbianca)."""
    return np.linalg.inv(np.atleast_2d(np.corrcoef(np.asarray(Z).T)))


def corpus_zscores(taratura, sommario_path=SOMMARIO):
    """Matrice [n_segnali, 16] degli z-score delle medie per-segnale del corpus."""
    with open(sommario_path) as f:
        rows = list(csv.DictReader(f))
    return np.array([[(float(r[d + "_mean"]) - taratura[d][0]) / taratura[d][1]
                      for d in DESCS] for r in rows], dtype=float)


def whitening_matrix(taratura, sommario_path=SOMMARIO):
    """Matrice di Mahalanobis congelata sul corpus."""
    return whitening_from_Z(corpus_zscores(taratura, sommario_path))


def frame_drift(Zref, gref, Zcfg, gcfg, MAH):
    """Distanze per-frame sui soli frame validi (gated=0) in entrambe le versioni.

    Ritorna (d_z, d_mah, n_valid, n_total). Allinea sul minimo numero di frame
    (in pratica gia' uguali) e seleziona i frame validi in entrambe.
    """
    n = min(len(Zref), len(Zcfg))
    Zref, gref, Zcfg, gcfg = Zref[:n], gref[:n], Zcfg[:n], gcfg[:n]
    valid = (~gref) & (~gcfg)
    D = Zcfg[valid] - Zref[valid]
    d_z = np.sqrt((D * D).sum(axis=1))
    d_mah = np.sqrt(np.einsum("ij,jk,ik->i", D, MAH, D))
    return d_z, d_mah, int(valid.sum()), n


def summarize(d_z, d_mah, n_valid, n_total):
    """Sintesi per (segnale, config): media/mediana/max e copertura."""
    cov = (n_valid / n_total) if n_total else 0.0
    nan = float("nan")
    if n_valid == 0:
        return dict(mean_z=nan, median_z=nan, max_z=nan,
                    mean_mah=nan, median_mah=nan, max_mah=nan, coverage=cov)
    return dict(
        mean_z=float(d_z.mean()), median_z=float(np.median(d_z)), max_z=float(d_z.max()),
        mean_mah=float(d_mah.mean()), median_mah=float(np.median(d_mah)),
        max_mah=float(d_mah.max()), coverage=cov)


def signal_dirs():
    """Nomi dei segnali sintetici (cartelle con il CSV di analisi)."""
    base = ANALISI / REF
    out = []
    for d in sorted(p.name for p in base.iterdir() if p.is_dir()):
        if (base / d / (d + SUFFIX)).exists():
            out.append(d)
    return out


def compute_all():
    """Calcola la sintesi per ogni (segnale, config). Ritorna (rows, missing).

    rows: lista di dict con 'signal', 'config', e le chiavi di summarize().
    missing: lista di (signal, config) con file mancante.
    """
    tar = load_taratura()
    MAH = whitening_matrix(tar)
    rows, missing = [], []
    for sig in signal_dirs():
        ref_csv = ANALISI / REF / sig / (sig + SUFFIX)
        Zref, gref = load_frames(ref_csv, tar)
        for cfg in CONFIGS:
            cfg_csv = ANALISI / cfg / sig / (sig + SUFFIX)
            if not cfg_csv.exists():
                missing.append((sig, cfg)); continue
            Zcfg, gcfg = load_frames(cfg_csv, tar)
            d_z, d_mah, nv, nt = frame_drift(Zref, gref, Zcfg, gcfg, MAH)
            s = summarize(d_z, d_mah, nv, nt)
            s.update(signal=sig, config=cfg)
            rows.append(s)
    return rows, missing


def _fmt(x):
    return "—" if (x != x) else f"{x:.2f}".replace(".", ",")


def write_table(rows, missing, path):
    """Scrive la tabella Markdown: per (segnale, config) + aggregato per config."""
    lines = ["# Deriva sintetico → ripreso (frame by frame)", "",
             "Distanza media dei frame ripresi dal sintetico, sui soli frame validi "
             "(gated=0) in entrambe. `d_z` euclidea su z-score, `d_mah` Mahalanobis "
             "sbiancata; `cop.` = copertura (frazione di frame confrontati).", "",
             "**Nota sulla copertura.** La copertura è la frazione di frame "
             "effettivamente confrontati: il frame `t` entra nel calcolo solo se in "
             "entrambe le versioni il suono è sopra la soglia di rumore (gate −65 "
             "dBFS), perché sotto soglia i descrittori sono inaffidabili. 100% "
             "significa che nessun frame è stato scartato (il confronto ha usato "
             "l'intero segnale), non che i segnali siano identici: la somiglianza è "
             "data dalle distanze `d_z`/`d_mah`, non dalla copertura.", "",
             "| segnale | config | d_z | d_mah | cop. |",
             "|---|---|---:|---:|---:|"]
    for r in rows:
        lines.append(f"| {r['signal']} | {CONFIGS[r['config']]} | "
                     f"{_fmt(r['mean_z'])} | {_fmt(r['mean_mah'])} | "
                     f"{_fmt(r['coverage']*100)}% |")
    # aggregato per config: media delle medie per-segnale (ignora i NaN)
    lines += ["", "## Aggregato per configurazione",
              "(media delle derive per-segnale, esclusi i segnali senza frame validi)", "",
              "| config | d_z medio | d_mah medio | n segnali |",
              "|---|---:|---:|---:|"]
    for cfg in CONFIGS:
        vz = [r["mean_z"] for r in rows if r["config"] == cfg and r["mean_z"] == r["mean_z"]]
        vm = [r["mean_mah"] for r in rows if r["config"] == cfg and r["mean_mah"] == r["mean_mah"]]
        mz = sum(vz) / len(vz) if vz else float("nan")
        mm = sum(vm) / len(vm) if vm else float("nan")
        lines.append(f"| {CONFIGS[cfg]} | {_fmt(mz)} | {_fmt(mm)} | {len(vz)} |")
    if missing:
        lines += ["", "## File-config mancanti", ""]
        lines += [f"- {s} / {CONFIGS[c]}" for s, c in missing]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def trajectory(sig, cfg, taratura, MAH):
    """Curva di deriva (d_mah per frame) per un singolo (segnale, config)."""
    Zref, gref = load_frames(ANALISI / REF / sig / (sig + SUFFIX), taratura)
    Zcfg, gcfg = load_frames(ANALISI / cfg / sig / (sig + SUFFIX), taratura)
    _, d_mah, _, _ = frame_drift(Zref, gref, Zcfg, gcfg, MAH)
    return d_mah


def make_figure(rows, path, esempi=("01_sinusoide_440", "19_sin_diminuendo")):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    tar = load_taratura(); MAH = whitening_matrix(tar)
    cfgs = list(CONFIGS)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 3.0))

    # pannello A: box plot della deriva (d_mah media per-segnale) per config
    data = [[r["mean_mah"] for r in rows if r["config"] == c and r["mean_mah"] == r["mean_mah"]]
            for c in cfgs]
    ax1.boxplot(data, tick_labels=[CONFIGS[c] for c in cfgs])
    ax1.set_ylabel("deriva media (Mahalanobis)")
    ax1.set_title("Deriva per configurazione", fontsize=9)
    ax1.tick_params(axis="x", labelrotation=30, labelsize=7)
    ax1.grid(True, alpha=0.3)

    # pannello B: curve di deriva d'esempio (un ripreso reale: 2 m pulito)
    for sig in esempi:
        if (ANALISI / "recs-004" / sig / (sig + SUFFIX)).exists():
            y = trajectory(sig, "recs-004", tar, MAH)
            ax2.plot(range(len(y)), y, label=sig)
    ax2.set_xlabel("frame valido"); ax2.set_ylabel("deriva (Mahalanobis)")
    ax2.set_title("Curve di deriva (2 m pulito)", fontsize=9)
    ax2.legend(fontsize=6); ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(path)
    print(f"scritto {path}")


def main():
    rows, missing = compute_all()
    out_md = ANALISI / "tabelle" / "deriva_sintetico_ripreso.md"
    write_table(rows, missing, out_md)
    print(f"scritto {out_md} ({len(rows)} righe, {len(missing)} mancanti)")
    make_figure(rows, HERE / "deriva_per_config.png")
    return rows, missing


if __name__ == "__main__":
    main()
