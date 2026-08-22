#!/usr/bin/env python3
"""Figura LEAP: centroide media per canale su tutto il corpus strumentale.

Riproduce il layout di overview() di centroidi_riepilogo.py:
  - asse x = ogni campione-sorgente non-NOISE (nell'ordine del CSV);
  - una linea colorata per ciascuno degli 8 canali (= distanza in metri);
  - pastiglia circolare col numero di canale + annotazione Hz sopra il punto;
  - separatori verticali tratteggiati fra configurazioni;
  - etichetta di configurazione in alto (anonimizzata per il paper);
  - griglia su y.

I prefissi grezzi (CCB/CS/petalonio/trombino) restano SOLO come chiavi di
filtro nel codice; nel testo visibile della figura compaiono solo le etichette
anonimizzate.
"""
from pathlib import Path
import csv

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent

CSV_PATH = ROOT / "analisi/distanza-banda-piena/centroidi_medie.csv"
OUT_PDF  = HERE / "figura_leap_corpus.pdf"

CMAP = plt.get_cmap("tab10")


# ---------- helpers copiati / adattati da centroidi_riepilogo.py ----------

def carica_csv(path, col):
    """Restituisce {nome_file: {canale_int: valore_float}}."""
    dati = {}
    for r in csv.DictReader(open(path)):
        if r[col] == "":
            continue
        dati.setdefault(r["file"], {})[int(r["canale"])] = float(r[col])
    return dati


def etichetta_config(nome_file):
    """Mappa il prefisso di configurazione all'etichetta anonimizzata del paper.

    Le chiavi sono prefissi grezzi (mai visibili in figura); le values sono le
    etichette da mostrare.
    """
    # Ordine: dal più specifico al più generico
    mapping = [
        ("CCB_petalonio_oriz", "contrabbasso, campana custom, orizz."),
        ("CCB_petalonio_vert", "contrabbasso, campana custom, vert."),
        ("CCB_trombino_oriz",  "contrabbasso, campana originale, orizz."),
        ("CCB_trombino_vert",  "contrabbasso, campana originale, vert."),
        ("CS_oriz",            "soprano, orizz."),
        ("CS_vert",            "soprano, vert."),
    ]
    for prefisso, etichetta in mapping:
        if nome_file.startswith(prefisso):
            return etichetta
    return "altro"


def etichetta_xtick(nome_file):
    """Converte il nome file grezzo nell'etichetta di tick anonimizzata."""
    # Suffissi da mappare
    per_suffisso = {
        "CLUSTER1": "cluster 1",
        "CLUSTER2": "cluster 2",
        "CLUSTER3": "cluster 3",
        "DO":       "Do",
    }
    for suf, label in per_suffisso.items():
        if nome_file.endswith(suf):
            return label
    return nome_file  # fallback: non dovrebbe accadere


# ---------- grafico (adattamento di overview()) ----------

def genera_figura():
    dati  = carica_csv(CSV_PATH, "media_intero")
    files = [f for f in dati if f.startswith("CCB")]  # solo contrabbasso, ordine CSV

    x = np.arange(len(files))
    fig, ax = plt.subplots(figsize=(13, 4.2))

    # -- 8 linee colorate, una per canale --
    for ci, ch in enumerate(range(1, 9)):
        y = [dati[f].get(ch, np.nan) for f in files]
        col_ch = CMAP(ci)
        ax.plot(x, y, lw=1.0, color=col_ch, alpha=0.6, zorder=1)
        for xi, yi in zip(x, y):
            if np.isnan(yi):
                continue
            # pastiglia circolare col numero di canale
            ax.text(xi, yi, str(ch),
                    ha="center", va="center", fontsize=6,
                    fontweight="bold", color="white", zorder=3,
                    bbox=dict(boxstyle="circle,pad=0.16", fc=col_ch, ec="none"))

    # -- separatori verticali fra configurazioni --
    configs = [etichetta_config(f) for f in files]
    for i in range(1, len(files)):
        if configs[i] != configs[i - 1]:
            ax.axvline(i - 0.5, color="gray", ls=":", lw=0.8)

    # -- etichette di configurazione in alto --
    seen = {}
    for i, cfg in enumerate(configs):
        seen.setdefault(cfg, []).append(i)
    # forziamo i limiti y prima di posizionare le etichette
    ax.margins(y=0.08)
    ax.autoscale_view()
    ymax = ax.get_ylim()[1]
    for cfg, idx in seen.items():
        ax.text(np.mean(idx), ymax, cfg,
                ha="center", va="bottom", fontsize=8, color="dimgray")

    # -- assi e griglia --
    ax.set_xticks(x)
    ax.set_xticklabels([etichetta_xtick(f) for f in files],
                       rotation=90, fontsize=7)
    ax.set_ylabel("centroide medio (Hz)")
    ax.grid(True, alpha=0.3, axis="y")

    # -- legenda: punto colorato + numero = microfono (1 m ... 8 m) --
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], marker="o", linestyle="none",
                      markerfacecolor=CMAP(ci), markeredgecolor="none",
                      markersize=7, label=str(ch))
               for ci, ch in enumerate(range(1, 9))]
    leg = ax.legend(handles=handles, ncol=8, loc="upper center",
                    bbox_to_anchor=(0.5, -0.28), frameon=False, fontsize=7,
                    title="microfono (numero nel punto = distanza: 1 = 1 m dalla sorgente … 8 = 8 m)",
                    handletextpad=0.2, columnspacing=1.2)
    plt.setp(leg.get_title(), fontsize=7)

    plt.tight_layout()
    fig.savefig(OUT_PDF, dpi=150, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"Salvato: {OUT_PDF}")

    # -- stampa valori per controllo --
    print("\nValori per file e canale (media_intero, Hz):")
    for f in files:
        vals = "  ".join(
            f"ch{ch}={dati[f].get(ch, float('nan')):.0f}"
            for ch in range(1, 9)
        )
        print(f"  {f}: {vals}")


if __name__ == "__main__":
    genera_figura()
