#!/usr/bin/env python3
"""Tenuta del controllo a nodi sotto ripresa reale (mini-esperimento §nodi-e-distanza).

Il paper sostiene che il controllo bipolare

    v = (d_meno - d_piu) / (d_meno + d_piu)

resti leggibile sotto ripresa perche' ingresso e nodi condividono lo stesso ambiente:
la colorazione comune si elide nel rapporto fra le distanze. Qui lo misuro.

METRICA. Per un *controllo* non conta che l'errore puntuale sia piccolo, ma che la
lettura ripresa segua ancora quella sui sintetici: cioe' correlazione, guadagno e
ordine fra v ripreso e v sui sintetici. (Una media |v_ripreso - v_studio| inganna:
e' piccola quando tutto crolla a zero, cioe' col controllo spento.) Per ogni
segnale prendo il v medio sui frame validi.

DUE CASI di taratura dei nodi:
  - tarati sui sintetici : nodi fissati una volta sui sintetici (asciutti)
  - ripresi nell'ambiente    : nodi ricalibrati nello stesso ambiente dell'ingresso (reale)

DUE SPAZI di distanza:
  - z-score (euclidea)        : la metrica robusta sotto ripresa
  - Mahalanobis (sbiancata)   : amplifica flux/irregularity, i descrittori che
                                l'ambiente gonfia, e rompe il controllo (caveat).

Riusa taratura e pipeline di deriva_sintetico_ripreso.py.
"""
import csv
from pathlib import Path
import numpy as np

from deriva_sintetico_ripreso import (
    load_taratura, load_frames, signal_dirs, whitening_matrix,
    CONFIGS, DESCS, ANALISI, REF, SUFFIX,
)

HERE = Path(__file__).resolve().parent

# nodi: la coppia di polarita' canonica di prova_ancore.py
NODO_PIU = "01_sinusoide_440"    # +1  (tonale)
NODO_MENO = "02_noise_bianco"    # -1  (piatto)

ZSCORE = np.eye(len(DESCS))      # distanza euclidea sugli z-score


def node_vector(sig, where, tar):
    """Posizione del nodo (vettore 16) in una versione: media sui frame validi.

    `where` e' REF (sintetici) o una chiave di CONFIGS (ripresa). Ricalibrare il
    nodo nell'ambiente = prenderne la media dei frame ripresi li'.
    """
    csv_path = ANALISI / where / sig / (sig + SUFFIX)
    Z, gated = load_frames(csv_path, tar)
    valid = ~gated
    if not valid.any():
        return None
    return Z[valid].mean(axis=0)


def v_series(X, p_piu, p_meno, M):
    """v per ogni riga di X (n,16) dati i due nodi, distanza definita da M.

    M = eye(16) -> z-score euclideo; M = Sigma^{-1} -> Mahalanobis.
    """
    dp = X - p_piu
    dm = X - p_meno
    d_piu = np.sqrt(np.einsum("ij,jk,ik->i", dp, M, dp))
    d_meno = np.sqrt(np.einsum("ij,jk,ik->i", dm, M, dm))
    s = d_meno + d_piu
    out = np.zeros_like(s)
    np.divide(d_meno - d_piu, s, out=out, where=s > 0)
    return out


def v_mean(sig, where, p_piu, p_meno, M, tar):
    """v medio del segnale in una versione, sui suoi frame validi (None se muto)."""
    Z, g = load_frames(ANALISI / where / sig / (sig + SUFFIX), tar)
    valid = ~g
    if not valid.any():
        return None
    return float(v_series(Z[valid], p_piu, p_meno, M).mean())


def v_triples(M, tar=None):
    """Per ogni (segnale, config): v sui sintetici, v con nodi tarati sui sintetici,
    v con nodi ripresi nell'ambiente.

    Distanze nello spazio definito da M. Esclude i due nodi dai segnali di prova.
    Ritorna (rows, missing).
    """
    tar = tar or load_taratura()
    pP_st = node_vector(NODO_PIU, REF, tar)
    pM_st = node_vector(NODO_MENO, REF, tar)
    test = [s for s in signal_dirs() if s not in (NODO_PIU, NODO_MENO)]
    rows, missing = [], []
    for sig in test:
        vs = v_mean(sig, REF, pP_st, pM_st, M, tar)
        if vs is None:
            continue
        for cfg in CONFIGS:
            if not (ANALISI / cfg / sig / (sig + SUFFIX)).exists():
                missing.append((sig, cfg)); continue
            pP_c = node_vector(NODO_PIU, cfg, tar)
            pM_c = node_vector(NODO_MENO, cfg, tar)
            if pP_c is None or pM_c is None:
                missing.append((sig, cfg)); continue
            vf = v_mean(sig, cfg, pP_st, pM_st, M, tar)   # nodi tarati sui sintetici
            vc = v_mean(sig, cfg, pP_c, pM_c, M, tar)     # nodi ripresi nell'ambiente
            if vf is None or vc is None:
                continue
            rows.append(dict(signal=sig, config=cfg,
                             v_studio=vs, v_frozen=vf, v_coripresi=vc))
    return rows, missing


def v_pairs_distanza(M, cfg_a, cfg_b, tar=None):
    """Per ogni sintetico: (v in cfg_a, v in cfg_b), ENTRAMBI ripresi nell'ambiente,
    con i due nodi tarati UNA volta nell'ambiente in cfg_a (come al soundcheck).

    E' la condizione del vivo (niente riferimento asciutto): misura se la lettura
    sopravvive a uno spostamento di distanza dentro la stanza, dove la firma comune
    dell'ambiente entra in entrambi i termini e si elide. Esclude i due nodi e i
    segnali non ripresi in entrambe le configurazioni. Ritorna lista (sig, v_a, v_b).
    """
    tar = tar or load_taratura()
    pP = node_vector(NODO_PIU, cfg_a, tar)
    pM = node_vector(NODO_MENO, cfg_a, tar)
    out = []
    for sig in signal_dirs():
        if sig in (NODO_PIU, NODO_MENO):
            continue
        if not all((ANALISI / c / sig / (sig + SUFFIX)).exists() for c in (cfg_a, cfg_b)):
            continue
        va = v_mean(sig, cfg_a, pP, pM, M, tar)
        vb = v_mean(sig, cfg_b, pP, pM, M, tar)
        if va is None or vb is None:
            continue
        out.append((sig, va, vb))
    return out


def fit(x, y):
    """Correlazione R e pendenza k della retta y = k x + b. (n>=3)."""
    x, y = np.asarray(x), np.asarray(y)
    if len(x) < 3 or x.std() == 0:
        return float("nan"), float("nan")
    k = float(np.polyfit(x, y, 1)[0])
    R = float(np.corrcoef(x, y)[0, 1])
    return R, k


def corr_summary(rows):
    """Per configurazione: (R, k) di nodi-sui-sintetici e nodi-nell'ambiente vs v sintetico."""
    out = {}
    for cfg in CONFIGS:
        sel = [r for r in rows if r["config"] == cfg]
        if not sel:
            continue
        x = [r["v_studio"] for r in sel]
        Rf, kf = fit(x, [r["v_frozen"] for r in sel])
        Rc, kc = fit(x, [r["v_coripresi"] for r in sel])
        out[cfg] = dict(R_frozen=Rf, k_frozen=kf, R_cori=Rc, k_cori=kc, n=len(sel))
    return out


def _fmt(x):
    return "—" if (x != x) else f"{x:+.2f}".replace(".", ",")


def write_table(rows_z, rows_m, path):
    z = corr_summary(rows_z)
    m = corr_summary(rows_m)
    lines = [
        "# Tenuta del controllo a nodi sotto ripresa reale", "",
        "Correlazione `R` e guadagno `k` (pendenza) di `v` ripreso rispetto a `v` sui "
        f"quarantacinque sintetici, nodi `{NODO_PIU}` (+1) / `{NODO_MENO}` (−1). "
        "`R`/`k` positivi e vicini a 1 = il controllo conserva la lettura. "
        "`sint` = nodi tarati sui sintetici; `amb` = nodi ripresi nell'ambiente.", "",
        "## z-score (euclidea) — la metrica robusta", "",
        "| config | R sint | k sint | R amb | k amb |",
        "|---|---:|---:|---:|---:|"]
    for cfg in CONFIGS:
        if cfg not in z:
            continue
        p = z[cfg]
        lines.append(f"| {CONFIGS[cfg]} | {_fmt(p['R_frozen'])} | {_fmt(p['k_frozen'])} | "
                     f"{_fmt(p['R_cori'])} | {_fmt(p['k_cori'])} |")
    lines += ["",
              "Le curve si conservano (R positivo) anche coi nodi tarati sui "
              "sintetici; riprenderli nell'ambiente recupera guadagno e correlazione, "
              "come previsto dall'elisione.", "",
              "## Mahalanobis (sbiancata) — caveat", "",
              "| config | R sint | k sint | R amb | k amb |",
              "|---|---:|---:|---:|---:|"]
    for cfg in CONFIGS:
        if cfg not in m:
            continue
        p = m[cfg]
        lines.append(f"| {CONFIGS[cfg]} | {_fmt(p['R_frozen'])} | {_fmt(p['k_frozen'])} | "
                     f"{_fmt(p['R_cori'])} | {_fmt(p['k_cori'])} |")
    lines += ["",
              "Lo sbiancamento amplifica flux e irregularity (varianza piccola nel "
              "corpus), cioe' proprio l'irregolarita' che l'ambiente aggiunge: coi "
              "nodi tarati sui sintetici il controllo si appiattisce e si inverte (R negativo). "
              "Sotto ripresa conviene restare in z-score."]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def draw_scatter(ax, rows, cfg="recs-004"):
    """Disegna sull'asse dato lo scatter v ripreso vs v sui sintetici (z-score)."""
    sel = [r for r in rows if r["config"] == cfg]
    x = np.array([r["v_studio"] for r in sel])
    yf = np.array([r["v_frozen"] for r in sel])
    yc = np.array([r["v_coripresi"] for r in sel])
    xx = np.linspace(-1, 1, 2)

    ax.plot([-1, 1], [-1, 1], "k:", lw=0.8, label="ideale")
    ax.axhline(0, color="gray", lw=0.4); ax.axvline(0, color="gray", lw=0.4)
    for y, col, lab in [(yf, "#c0603a", "tarati sui sintetici"),
                        (yc, "#3a6ea5", "ripresi nell'ambiente")]:
        R, k = fit(x, y)
        ax.scatter(x, y, s=14, alpha=0.6, color=col)
        ax.plot(xx, k * xx, color=col, lw=1.4, label=f"{lab} ($k={k:.2f}$)")
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)
    ax.set_xlabel("$v$ sui sintetici", fontsize=8)
    ax.set_ylabel("$v$ sotto ripresa", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=6.5, frameon=False, loc="upper left")


def make_figure(rows, path, cfg="recs-004"):
    """Scatter v ripreso vs v sui sintetici (z-score) per una configurazione."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(3.3, 3.0))
    draw_scatter(ax, rows, cfg)
    fig.tight_layout()
    fig.savefig(path)
    print(f"scritto {path}")


def main():
    tar = load_taratura()
    rows_z, missing = v_triples(ZSCORE, tar)
    rows_m, _ = v_triples(whitening_matrix(tar), tar)
    out_md = ANALISI / "tabelle" / "controllo_nodi_ripresa.md"
    write_table(rows_z, rows_m, out_md)
    print(f"scritto {out_md} ({len(rows_z)} righe, {len(missing)} mancanti)")
    z = corr_summary(rows_z)
    for cfg in CONFIGS:
        if cfg in z:
            p = z[cfg]
            print(f"  {CONFIGS[cfg]:20s} z-score  sint R{p['R_frozen']:+.2f} "
                  f"k{p['k_frozen']:+.2f}   amb R{p['R_cori']:+.2f} k{p['k_cori']:+.2f}")
    make_figure(rows_z, HERE / "controllo_nodi_ripresa.png")
    return rows_z, rows_m, missing


if __name__ == "__main__":
    main()
