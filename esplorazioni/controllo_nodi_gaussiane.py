#!/usr/bin/env python3
"""Prototipo: controllo a nodi con kernel gaussiani (Nadaraya-Watson) sui
descrittori veri del corpus. Cursore = il suono (traiettoria x(t)).

Mostra: i pesi normalizzati w_i(t) di ogni nodo mentre il suono evolve, al
variare della sigma (manopola di durezza), con valvola anti-zone-vuote.

Esegui dalla radice del repo descrittori/. Salva un PNG nello scratchpad.
"""
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import glob, os
REPO = "/home/francesco/gitlab/descrittori"
RECS = f"{REPO}/analisi/recs-003"
DESCS = ["centroid", "spread", "rolloff", "slope", "obsir_std", "flatness",
         "crest", "skewness", "kurtosis", "entropy", "tpr", "n_peaks",
         "tonality", "flux", "irregularity", "zcr"]

def per_frame(seg):
    """Matrice grezza (T,16) dei frame non-gated di un segnale recs-003."""
    pf = f"{RECS}/{seg}/{seg}_hann_ov50_10000hz_analisi.csv"
    fr = [f for f in csv.DictReader(open(pf)) if f.get("gated", "0") == "0"]
    return np.array([[float(f[d]) for d in DESCS] for f in fr])

# --- z-score CONGELATO sul corpus recs-003 (pool di tutti i frame) ----------
segnali = sorted(os.path.basename(os.path.dirname(p))
                 for p in glob.glob(f"{RECS}/*/*_hann_ov50_10000hz_analisi.csv"))
pool = np.concatenate([per_frame(s) for s in segnali])
MU = pool.mean(0)
SD = np.where(pool.std(0) > 0, pool.std(0), 1.0)
zmat = lambda raw: (raw - MU) / SD                     # (T,16) grezzo -> z

# nodo = media dei frame z-scorati di un segnale
nodo = lambda seg: zmat(per_frame(seg)).mean(0)

# --- nodi (prototipi) -------------------------------------------------------
NODI = {
    "tonale (sin100)":      nodo("13_sin100"),      # estremo 'tonale' dello sweep
    "rumoroso (noise100)":  nodo("17_noise100"),    # estremo 'rumore' dello sweep
    "armonico (tanh20)":    nodo("05_tanh_drive20"),  # distrattore, fuori rotta
}
nomi_nodi = list(NODI)
C = np.stack([NODI[n] for n in nomi_nodi])           # (N_nodi, 16)

# --- traiettoria x(t): continuo tonale->rumore, mix reali concatenati frame
#     per frame e z-scorati con lo STESSO congelato del corpus ---------------
SWEEP = ["13_sin100", "14_sin75_noise25", "15_sin50_noise50",
         "16_sin25_noise75", "17_noise100"]
X_parts, bordi, etich = [], [], []
n = 0
for seg in SWEEP:
    Xs = zmat(per_frame(seg))
    X_parts.append(Xs)
    etich.append((n + len(Xs) / 2, seg.split("_", 1)[1]))
    n += len(Xs); bordi.append(n)
X = np.concatenate(X_parts)                                  # (T, 16)
t = np.arange(len(X))                                        # pseudo-tempo (frame)
TRAIETTORIA = "sweep tonale->rumore (13->17)"

# --- kernel gaussiano + normalizzazione + valvola zone-vuote ----------------
def pesi(X, C, sigma, eps=1e-3):
    """Ritorna w (T, N) normalizzati e occupazione (T,) = somma pesi grezzi.
    eps = nodo di riposo implicito: assorbe il caso 'lontano da tutti'."""
    d2 = ((X[:, None, :] - C[None, :, :]) ** 2).sum(-1)   # (T, N) dist^2
    w = np.exp(-d2 / (2 * sigma ** 2))                    # gaussiana
    occ = w.sum(1)                                        # quanto sei 'coperto'
    w = w / (occ[:, None] + eps)                          # partizione unita'
    return w, occ

SIGME = [1.0, 2.5, 5.0]            # duro -> molle (in unita' z-score)
COLORI = ["#1f77b4", "#d62728", "#2ca02c"]

fig, axes = plt.subplots(len(SIGME) + 1, 1, figsize=(11, 9), sharex=True)

# pannello 0: due descrittori chiave della traiettoria (in z)
ax = axes[0]
ic, ifl = DESCS.index("centroid"), DESCS.index("flatness")
ax.plot(t, X[:, ic], label="centroid (z)", color="#555")
ax.plot(t, X[:, ifl], label="flatness (z)", color="#999", ls="--")
ax.axhline(0, color="k", lw=.5)
for x0, lab in etich:
    ax.text(x0, ax.get_ylim()[1], lab, ha="center", va="top", fontsize=7,
            color="#444")
ax.set_title(f"Traiettoria: {TRAIETTORIA} (mix reali concatenati)")
ax.legend(loc="center left", fontsize=8); ax.set_ylabel("z")

# pannelli 1..K: pesi normalizzati per ogni sigma (aree impilate)
for k, sigma in enumerate(SIGME):
    ax = axes[k + 1]
    w, occ = pesi(X, C, sigma)
    ax.stackplot(t, w.T, labels=nomi_nodi, colors=COLORI, alpha=.85)
    # zona-vuota: dove la copertura grezza e' bassa
    fuori = occ < 0.05
    if fuori.any():
        ax.fill_between(t, 0, 1, where=fuori, color="k", alpha=.12, step="mid",
                        label="fuori zona")
    for b in bordi[:-1]:
        ax.axvline(b, color="w", lw=.8, alpha=.6)
    ax.set_ylim(0, 1); ax.set_ylabel(f"σ = {sigma}\npeso")
    if k == 0:
        ax.legend(loc="upper center", fontsize=7, ncol=4)
axes[-1].set_xlabel("frame (pseudo-tempo): da tonale a rumoroso")
fig.suptitle("Controllo a nodi con gaussiane: pesi normalizzati w_i(t)  "
             "(duro in alto σ=1, molle in basso σ=5)", fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.97])
OUT = "esplorazioni/controllo_nodi_gaussiane.png"
fig.savefig(OUT, dpi=120)
print("PNG salvato:", OUT)

# --- tabella numerica a tre istanti, sigma=2.5 ------------------------------
w, occ = pesi(X, C, 2.5)
print(f"\nNodi: {nomi_nodi}")
print(f"Traiettoria: {TRAIETTORIA}  ({len(t)} frame)\n")
print(f"{'punto':>14} | " + " | ".join(f"{n[:12]:>12}" for n in nomi_nodi) +
      f" | {'copertura':>9}")
print("-" * 72)
tappe = [("inizio (sin100)", 0)] + \
        [(SWEEP[i].split("_", 1)[1], bordi[i] - 1) for i in range(len(SWEEP))]
for lab, idx in tappe:
    riga = " | ".join(f"{w[idx, j]:12.3f}" for j in range(len(nomi_nodi)))
    print(f"{lab:>14} | {riga} | {occ[idx]:9.3f}")

# quanto cambia il nodo dominante lungo la traiettoria (prova che si muove)
dom = np.array(nomi_nodi)[w.argmax(1)]
cambi = (dom[1:] != dom[:-1]).sum()
print(f"\nNodo dominante: parte '{dom[0]}' -> finisce '{dom[-1]}' "
      f"({cambi} cambi di dominanza lungo il percorso)")
