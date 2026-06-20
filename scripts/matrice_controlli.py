#!/usr/bin/env python3
"""
Simulazione offline dei 5 controlli derivati dalla matrice di correlazione
rolling fra i descrittori.

Per ogni frame t calcola la matrice di correlazione M(t) sui frame della
finestra mobile (default N=64) e ne estrae cinque scalari:

    C1  mean(r_ij)          coerenza media segnata           in [-1, +1]
    C2  2*lambda1/sum - 1   concentrazione assiale           in [-1, +1]
    C3  (n+ - n-)/totale    asimmetria di segno              in [-1, +1]
    E1  ||M(t) - M(t-D)||_F velocita' di evoluzione          >= 0
    E2  |v1(t)*v1(t-D)|     |coseno| dei primi autovettori   in [0, 1]

I primi tre vanno direttamente ai 3 ingressi continui del bicomb. Gli
ultimi due alimentano i due contatori (con soglia + refrattarieta').

Uso:
    python matrice_controlli.py <analisi.csv> [--out <dir>] [-N 64] [-D 32]
        [--soglia-E1 0.5] [--soglia-E2 0.7] [--refrattario-ms 200]

Esempio:
    python matrice_controlli.py \
        analisi/recs-004/02_noise_bianco/02_noise_bianco_hann_ov50_10000hz_analisi.csv \
        --out /tmp/test_controlli
"""

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


NON_DESC = {'frame', 'time', 'gated', 'n_peaks'}

# Famiglie di descrittori: ciascuna misura una dimensione timbrica diversa.
# Le sottomatrici di M(t) ristrette a ogni famiglia danno un C_F dedicato.
FAMIGLIE = {
    'collocazione': ['centroid', 'rolloff', 'spread', 'slope'],
    'grana':        ['flatness', 'tonality', 'tpr', 'irregularity', 'entropy'],
    'forma':        ['skewness', 'kurtosis', 'crest'],
    'dinamica':     ['flux', 'zcr', 'obsir_std', 'zscore'],
}


def N_per_famiglia(K):
    """Finestra rolling adattata alla taglia della famiglia."""
    return max(16, 4 * K)


def processa_famiglia(X_F, nome, t_axis, D_ratio=0.5):
    """Calcola scalari rolling sulla matrice di una sola famiglia.

    X_F: array (T, K_F) dei descrittori della famiglia
    Ritorna dict con C1, C2, E1, E2 per ogni frame.
    """
    T, K = X_F.shape
    N = N_per_famiglia(K)
    D = max(2, int(round(N * D_ratio)))

    M = rolling_matrix(X_F, N)
    C1 = np.full(T, np.nan)
    C2 = np.full(T, np.nan)
    V1 = np.full((T, K), np.nan)
    for i in range(T):
        c1, c2, c3, sm, ku, po, fw, v1 = scalars_from_matrix(M[i])
        C1[i] = c1
        C2[i] = c2 if K >= 3 else np.nan
        if v1 is not None:
            V1[i] = v1

    norm = float(np.sqrt(max(K * (K - 1), 1)))
    E1 = np.full(T, np.nan)
    for i in range(D, T):
        diff = M[i] - M[i - D]
        diff[np.isnan(diff)] = 0.0
        E1[i] = float(np.sqrt(np.sum(diff ** 2))) / norm

    E2 = np.full(T, np.nan)
    for i in range(D, T):
        a, b = V1[i], V1[i - D]
        if np.any(np.isnan(a)) or np.any(np.isnan(b)):
            continue
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na < 1e-12 or nb < 1e-12:
            continue
        # |coseno|: l'autovettore e' definito a meno del segno, quindi conta
        # solo l'orientamento dell'asse, non il verso (evita i salti +1/-1)
        E2[i] = float(abs(np.dot(a, b)) / (na * nb))

    return {'nome': nome, 'K': K, 'N': N, 'D': D,
            'C1': C1, 'C2': C2, 'E1': E1, 'E2': E2}


def cf_famiglia(M: np.ndarray, idx: list):
    """Media segnata delle correlazioni nel triangolo sup. della sottomatrice
    di M indicizzata da idx (>= 2 elementi). Ritorna NaN se non valida."""
    if len(idx) < 2:
        return np.nan
    sub = M[np.ix_(idx, idx)]
    iu = np.triu_indices(len(idx), k=1)
    triu = sub[iu]
    triu = triu[~np.isnan(triu)]
    if triu.size == 0:
        return np.nan
    return float(np.mean(triu))


def _safe_corr(a, b):
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    m = ~(np.isnan(a) | np.isnan(b))
    if m.sum() < 3:
        return np.nan
    sa, sb = a[m].std(), b[m].std()
    if sa < 1e-12 or sb < 1e-12:
        return np.nan
    return float(np.corrcoef(a[m], b[m])[0, 1])


def load(csv_path: Path, drop_gated=True):
    df = pd.read_csv(csv_path)
    if drop_gated and 'gated' in df.columns:
        df = df[df['gated'] == 0].reset_index(drop=True)
    cols = [c for c in df.columns
            if c not in NON_DESC and np.issubdtype(df[c].dtype, np.number)]
    return df, cols


def rolling_matrix(X: np.ndarray, N: int):
    """X di forma (T, K). Per ogni t >= N-1 calcola corr su finestra
    [t-N+1, t]. Ritorna un tensore (T, K, K) con NaN per i primi N-1 frame
    e per coppie con varianza nulla.
    """
    T, K = X.shape
    out = np.full((T, K, K), np.nan)
    for t in range(N - 1, T):
        W = X[t - N + 1 : t + 1]
        # corrcoef e' costoso ma K=15 e' piccolo
        with np.errstate(invalid='ignore', divide='ignore'):
            sd = W.std(axis=0)
            ok = sd > 1e-12
            if ok.sum() < 2:
                continue
            sub = W[:, ok]
            c = np.corrcoef(sub.T)
        M = np.full((K, K), np.nan)
        idx = np.where(ok)[0]
        M[np.ix_(idx, idx)] = c
        out[t] = M
    return out


def scalars_from_matrix(M: np.ndarray):
    """M (K,K). Ritorna (C1, C2, C3, sigmaM, v1) o nan se invalida."""
    K = M.shape[0]
    iu = np.triu_indices(K, k=1)
    triu = M[iu]
    triu = triu[~np.isnan(triu)]
    if triu.size == 0:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, None

    C1 = float(np.mean(triu))
    sigmaM = float(np.std(triu))
    # Kurtosis (Fisher: 0 = normale). Robusto a varianze piccole.
    m = triu - triu.mean()
    var = (m ** 2).mean()
    if var < 1e-12:
        kurt = np.nan
    else:
        kurt = float(((m ** 4).mean() / (var ** 2)) - 3.0)
    # Polarizzazione: |C1| / mean(|r|). Tende a 1 se tutte stesso segno.
    abs_mean = float(np.mean(np.abs(triu)))
    polar = abs(C1) / abs_mean if abs_mean > 1e-12 else np.nan
    # Frazione di celle deboli (|r| < 0.2)
    frac_weak = float(np.mean(np.abs(triu) < 0.2))
    n_pos = int((triu > 0).sum())
    n_neg = int((triu < 0).sum())
    tot = n_pos + n_neg
    C3 = (n_pos - n_neg) / tot if tot else np.nan

    # Eigen su sotto-matrice senza NaN
    nan_rows = np.all(np.isnan(M), axis=1) | np.all(np.isnan(M), axis=0)
    keep = ~nan_rows
    if keep.sum() < 2:
        return C1, np.nan, C3, sigmaM, kurt, polar, frac_weak, None
    sub = M[np.ix_(keep, keep)].copy()
    # Tappa eventuali NaN residui (coppie singole non definite) con 0
    sub[np.isnan(sub)] = 0.0
    # Simmetrizza per sicurezza numerica
    sub = (sub + sub.T) / 2.0
    try:
        w, V = np.linalg.eigh(sub)
    except np.linalg.LinAlgError:
        return C1, np.nan, C3, sigmaM, kurt, polar, frac_weak, None
    # eigh ritorna in ordine crescente; vogliamo il piu' grande in modulo
    order = np.argsort(np.abs(w))[::-1]
    w = w[order]; V = V[:, order]
    lam_sum = np.sum(np.abs(w))
    if lam_sum < 1e-12:
        return C1, np.nan, C3, sigmaM, kurt, polar, frac_weak, None
    C2 = 2.0 * abs(w[0]) / lam_sum - 1.0
    # Ricostruisci v1 alla dimensione K originale
    v1_full = np.zeros(K)
    v1_full[keep] = V[:, 0]
    # Segno: rendi deterministico (prima componente non nulla positiva)
    nz = np.flatnonzero(np.abs(v1_full) > 1e-12)
    if nz.size and v1_full[nz[0]] < 0:
        v1_full = -v1_full
    return C1, C2, C3, sigmaM, kurt, polar, frac_weak, v1_full


def trigger_events(signal, threshold, refractory_frames, above=True):
    """Ritorna array binario degli eventi (1 dove trigger), rispettando il
    tempo di refrattarieta'. above=True scatta quando supera la soglia in
    salita; above=False quando scende sotto.
    """
    n = len(signal)
    ev = np.zeros(n, dtype=int)
    last = -refractory_frames - 1
    prev = signal[0] if not np.isnan(signal[0]) else 0.0
    for i in range(1, n):
        v = signal[i]
        if np.isnan(v):
            prev = v
            continue
        crossed = (prev <= threshold < v) if above else (prev >= threshold > v)
        if crossed and (i - last) > refractory_frames:
            ev[i] = 1
            last = i
        prev = v
    return ev


def processa_gesto(csv_path: Path, out_dir: Path, N, D,
                   soglia_E1, soglia_E2, refrattario_ms,
                   etichetta_cartella=None, fa_plot=True, verbose=True,
                   soglia_FIR=None, soglia_IIR=None):
    stem = csv_path.stem.replace('_hann_ov50_10000hz_analisi', '')
    sub_dir = out_dir if etichetta_cartella is None else out_dir / etichetta_cartella
    sub_dir.mkdir(parents=True, exist_ok=True)

    df, cols = load(csv_path)
    if len(df) < N + D + 1:
        if verbose:
            print(f'  [{stem}] troppi pochi frame ({len(df)})')
        return None
    X = df[cols].to_numpy(dtype=float)
    t = df['time'].to_numpy() if 'time' in df.columns else np.arange(len(df))

    if verbose:
        print(f'Gesto: {stem}  {len(df)} frame, {len(cols)} desc, N={N} D={D}')

    # Indici delle famiglie nel vettore cols (descrittori mancanti vengono saltati)
    fam_idx = {}
    for nome, membri in FAMIGLIE.items():
        idx = [cols.index(c) for c in membri if c in cols]
        if len(idx) >= 2:
            fam_idx[nome] = idx
    if verbose:
        for nome, idx in fam_idx.items():
            K_F = len(idx)
            print(f'  famiglia {nome}: K={K_F} N={N_per_famiglia(K_F)} '
                  f'-> {[cols[i] for i in idx]}')

    # Matrici per famiglia: ognuna ha la propria finestra rolling
    fam_out = {}
    for nome, idx in fam_idx.items():
        X_F = X[:, idx]
        fam_out[nome] = processa_famiglia(X_F, nome, None)

    # Matrice rolling
    M = rolling_matrix(X, N)
    T = M.shape[0]
    C1 = np.full(T, np.nan)
    C2 = np.full(T, np.nan)
    C3 = np.full(T, np.nan)
    SM = np.full(T, np.nan)
    KU = np.full(T, np.nan)
    PO = np.full(T, np.nan)
    FW = np.full(T, np.nan)
    V1 = np.full((T, len(cols)), np.nan)
    CF = {nome: np.full(T, np.nan) for nome in fam_idx}
    for i in range(T):
        c1, c2, c3, sm, ku, po, fw, v1 = scalars_from_matrix(M[i])
        C1[i], C2[i], C3[i], SM[i] = c1, c2, c3, sm
        KU[i], PO[i], FW[i] = ku, po, fw
        if v1 is not None:
            V1[i] = v1
        for nome, idx in fam_idx.items():
            CF[nome][i] = cf_famiglia(M[i], idx)

    # E1: Frobenius distance fra M(t) e M(t-D), normalizzata.
    # Normalizzazione: dividiamo per sqrt(K*(K-1)), cioe' la radice del
    # numero di celle fuori-diagonale, cosi' E1 e' indipendente dalla
    # taglia della matrice e ha senso fissare la soglia.
    K = M.shape[1]
    norm_E1 = float(np.sqrt(K * (K - 1)))
    E1 = np.full(T, np.nan)
    for i in range(D, T):
        A, B = M[i], M[i - D]
        diff = A - B
        diff[np.isnan(diff)] = 0.0
        E1[i] = float(np.sqrt(np.sum(diff ** 2))) / norm_E1

    # E2: coseno fra v1(t) e v1(t-D)
    E2 = np.full(T, np.nan)
    for i in range(D, T):
        a, b = V1[i], V1[i - D]
        if np.any(np.isnan(a)) or np.any(np.isnan(b)):
            continue
        na = np.linalg.norm(a); nb = np.linalg.norm(b)
        if na < 1e-12 or nb < 1e-12:
            continue
        # |coseno|: l'autovettore e' definito a meno del segno, quindi conta
        # solo l'orientamento dell'asse, non il verso (evita i salti +1/-1)
        E2[i] = float(abs(np.dot(a, b)) / (na * nb))
    # Coseno: rendiamo "1 - |cos|" come distanza, e |cos| come stabilita';
    # qui teniamo cos grezzo: stabilita' alta = +1, rotazione = piu' basso

    # Trigger
    # Frame rate per refrattarieta'
    if 'time' in df.columns and len(t) > 1:
        dt = float(np.median(np.diff(t)))
        fr_per_ms = 1.0 / (1000.0 * dt) if dt > 0 else 0.0
    else:
        fr_per_ms = 0.0
    refr_frames = int(round(refrattario_ms * fr_per_ms))
    ev_E1 = trigger_events(E1, soglia_E1, refr_frames, above=True)
    # E2: trigger quando |cos| cala sotto soglia
    ev_E2 = trigger_events(np.abs(E2), soglia_E2, refr_frames, above=False)

    # Trigger della mappatura definitiva: E1 della dinamica (FIR), E2 della
    # forma (IIR). Soglie indipendenti; se non specificate ereditano dai
    # trigger globali per retrocompatibilità.
    th_FIR = soglia_E1 if soglia_FIR is None else soglia_FIR
    th_IIR = soglia_E2 if soglia_IIR is None else soglia_IIR
    ev_FIR = np.zeros(T, dtype=int)
    ev_IIR = np.zeros(T, dtype=int)
    if 'dinamica' in fam_out:
        ev_FIR = trigger_events(fam_out['dinamica']['E1'],
                                th_FIR, refr_frames, above=True)
    if 'forma' in fam_out:
        ev_IIR = trigger_events(np.abs(fam_out['forma']['E2']),
                                th_IIR, refr_frames, above=False)

    # CSV di output
    out = pd.DataFrame({
        'time': t,
        'C1_coerenza_media': C1,
        'C2_concentrazione_assiale': C2,
        'C3_asimmetria_segno': C3,
        'sigmaM_dispersione': SM,
        **{f'CF_{nome}': CF[nome] for nome in CF},
        **{f'C1_{n}': fam_out[n]['C1'] for n in fam_out},
        **{f'C2_{n}': fam_out[n]['C2'] for n in fam_out},
        **{f'E1_{n}': fam_out[n]['E1'] for n in fam_out},
        **{f'E2_{n}': fam_out[n]['E2'] for n in fam_out},
        'E1_frobenius': E1,
        'E2_coseno_v1': E2,
        'trigger_E1': ev_E1,
        'trigger_E2': ev_E2,
        'trigger_FIR': ev_FIR,
        'trigger_IIR': ev_IIR,
    })
    out.to_csv(sub_dir / f'{stem}_controlli.csv', index=False, float_format='%.5f')

    if not fa_plot:
        if verbose:
            print(f'  C1m={np.nanmean(C1):+.2f}  C2m={np.nanmean(C2):+.2f}  '
                  f'C3m={np.nanmean(C3):+.2f}  E1mx={np.nanmax(E1):.2f}  '
                  f'trigE1={ev_E1.sum()} trigE2={ev_E2.sum()}')
        return {
            'gesto': stem,
            'n_frame': int(len(df)),
            'C1_media': float(np.nanmean(C1)),
            'C1_std': float(np.nanstd(C1)),
            'C1_range': float(np.nanmax(C1) - np.nanmin(C1)),
            'C2_media': float(np.nanmean(C2)),
            'C2_std': float(np.nanstd(C2)),
            'C2_range': float(np.nanmax(C2) - np.nanmin(C2)),
            'C3_media': float(np.nanmean(C3)),
            'C3_std': float(np.nanstd(C3)),
            'C3_range': float(np.nanmax(C3) - np.nanmin(C3)),
            'sigmaM_media': float(np.nanmean(SM)),
            'kurt_media': float(np.nanmean(KU)),
            'polar_media': float(np.nanmean(PO)),
            'frac_weak_media': float(np.nanmean(FW)),
            'corr_C1_C3': float(_safe_corr(C1, C3)),
            'corr_C1_sigmaM': float(_safe_corr(C1, SM)),
            'corr_C2_sigmaM': float(_safe_corr(C2, SM)),
            'corr_C1_kurt': float(_safe_corr(C1, KU)),
            'corr_C2_kurt': float(_safe_corr(C2, KU)),
            'corr_C1_polar': float(_safe_corr(C1, PO)),
            'corr_C2_polar': float(_safe_corr(C2, PO)),
            'corr_C1_fracweak': float(_safe_corr(C1, FW)),
            'corr_C2_fracweak': float(_safe_corr(C2, FW)),
            **{f'CF_{n}_media': float(np.nanmean(CF[n])) for n in CF},
            **{f'CF_{n}_std':   float(np.nanstd(CF[n]))  for n in CF},
            **{f'corr_C1_CF_{n}': float(_safe_corr(C1, CF[n])) for n in CF},
            **{f'corr_C2_CF_{n}': float(_safe_corr(C2, CF[n])) for n in CF},
            **{f'C1_{n}_media': float(np.nanmean(fam_out[n]['C1'])) for n in fam_out},
            **{f'C1_{n}_std':   float(np.nanstd(fam_out[n]['C1']))  for n in fam_out},
            **{f'C2_{n}_media': float(np.nanmean(fam_out[n]['C2'])) for n in fam_out},
            **{f'E1_{n}_max':   float(np.nanmax(fam_out[n]['E1'])) for n in fam_out},
            **{f'E2_{n}_min':   float(np.nanmin(fam_out[n]['E2'])) for n in fam_out},
            'E1_max': float(np.nanmax(E1)),
            'E1_media': float(np.nanmean(E1)),
            'E2_min': float(np.nanmin(E2)),
            'E2_media': float(np.nanmean(E2)),
            'trigger_E1': int(ev_E1.sum()),
            'trigger_E2': int(ev_E2.sum()),
            'trigger_FIR': int(ev_FIR.sum()),
            'trigger_IIR': int(ev_IIR.sum()),
        }

    # Plot
    fig, axes = plt.subplots(5, 1, figsize=(11, 9), sharex=True)
    axes[0].plot(t, C1, color='C0'); axes[0].set_ylabel('C1\ncoerenza\nmedia')
    axes[0].axhline(0, color='k', lw=0.3); axes[0].set_ylim(-1.05, 1.05)
    axes[1].plot(t, C2, color='C1'); axes[1].set_ylabel('C2\nconcentrazione\nassiale')
    axes[1].axhline(0, color='k', lw=0.3); axes[1].set_ylim(-1.05, 1.05)
    axes[2].plot(t, C3, color='C2'); axes[2].set_ylabel('C3\nasimmetria\nsegno')
    axes[2].axhline(0, color='k', lw=0.3); axes[2].set_ylim(-1.05, 1.05)
    axes[3].plot(t, E1, color='C3'); axes[3].set_ylabel('E1\nFrobenius\n|M(t)-M(t-D)|')
    axes[3].axhline(soglia_E1, color='r', lw=0.5, ls='--')
    for i in np.where(ev_E1)[0]:
        axes[3].axvline(t[i], color='r', alpha=0.4, lw=0.8)
    axes[4].plot(t, E2, color='C4'); axes[4].set_ylabel('E2\ncos(v1(t), v1(t-D))')
    axes[4].axhline(soglia_E2, color='m', lw=0.5, ls='--')
    axes[4].axhline(-soglia_E2, color='m', lw=0.5, ls='--')
    axes[4].set_ylim(-1.05, 1.05)
    for i in np.where(ev_E2)[0]:
        axes[4].axvline(t[i], color='m', alpha=0.4, lw=0.8)
    axes[-1].set_xlabel('tempo (s)')
    fig.suptitle(f'{stem}  —  N={N} D={D}  '
                 f'eventi E1={ev_E1.sum()} E2={ev_E2.sum()}', fontsize=10)
    fig.tight_layout()
    fig.savefig(sub_dir / f'{stem}_controlli.png', dpi=140)
    plt.close(fig)

    if verbose:
        print(f'  C1 [{np.nanmin(C1):+.2f},{np.nanmax(C1):+.2f}] m={np.nanmean(C1):+.2f}  '
              f'C2 [{np.nanmin(C2):+.2f},{np.nanmax(C2):+.2f}] m={np.nanmean(C2):+.2f}  '
              f'E1mx={np.nanmax(E1):.2f}  trig E1={ev_E1.sum()} E2={ev_E2.sum()}')

    return {
        'gesto': stem,
        'n_frame': int(len(df)),
        'C1_media': float(np.nanmean(C1)),
        'C1_std': float(np.nanstd(C1)),
        'C1_range': float(np.nanmax(C1) - np.nanmin(C1)),
        'C2_media': float(np.nanmean(C2)),
        'C2_std': float(np.nanstd(C2)),
        'C2_range': float(np.nanmax(C2) - np.nanmin(C2)),
        'C3_media': float(np.nanmean(C3)),
        'C3_std': float(np.nanstd(C3)),
        'C3_range': float(np.nanmax(C3) - np.nanmin(C3)),
        'E1_max': float(np.nanmax(E1)),
        'E1_media': float(np.nanmean(E1)),
        'E2_min': float(np.nanmin(E2)),
        'E2_media': float(np.nanmean(E2)),
        'trigger_E1': int(ev_E1.sum()),
        'trigger_E2': int(ev_E2.sum()),
    }


def trova_catalogo(p: Path, root: Path):
    """Estrae il nome del catalogo dal path relativo a root."""
    try:
        rel = p.relative_to(root)
    except ValueError:
        return ''
    parts = rel.parts
    if not parts:
        return ''
    cat = parts[0]
    for i, seg in enumerate(parts):
        if seg == 'analisi' and i > 0:
            cat = parts[i - 1]
            break
    return cat


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('path', help='File _analisi.csv OPPURE cartella radice (modalita batch)')
    ap.add_argument('--out', default='cataloghi/controlli',
                    help='Cartella di output')
    ap.add_argument('-N', type=int, default=64,
                    help='Frame della finestra rolling (default 64)')
    ap.add_argument('-D', type=int, default=32,
                    help='Lag in frame per E1/E2 (default 32)')
    ap.add_argument('--soglia-E1', type=float, default=0.15,
                    help='Soglia su E1 (Frobenius normalizzata) per trigger')
    ap.add_argument('--soglia-E2', type=float, default=0.9,
                    help='Soglia su E2 (coseno autov.) per trigger; scatta in discesa')
    ap.add_argument('--soglia-FIR', type=float, default=None,
                    help='Soglia su E1_dinamica (FIR). Se omessa usa --soglia-E1')
    ap.add_argument('--soglia-IIR', type=float, default=None,
                    help='Soglia su |E2_forma| (IIR). Se omessa usa --soglia-E2')
    ap.add_argument('--refrattario-ms', type=float, default=200,
                    help='Tempo morto fra trigger (ms)')
    ap.add_argument('--no-plot', action='store_true',
                    help='In batch: salta i plot per andare piu veloce')
    args = ap.parse_args()

    path = Path(args.path).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if path.is_file():
        processa_gesto(path, out_dir, args.N, args.D,
                       args.soglia_E1, args.soglia_E2, args.refrattario_ms,
                       fa_plot=not args.no_plot,
                       soglia_FIR=args.soglia_FIR, soglia_IIR=args.soglia_IIR)
        return

    # Modalita' batch: trova tutti i CSV sotto path
    csvs = sorted(path.rglob('*_analisi.csv'))
    if not csvs:
        print(f'Nessun *_analisi.csv sotto {path}')
        return
    print(f'Batch: {len(csvs)} gesti sotto {path}')
    rows = []
    for csv_path in csvs:
        cat = trova_catalogo(csv_path, path)
        res = processa_gesto(csv_path, out_dir, args.N, args.D,
                             args.soglia_E1, args.soglia_E2, args.refrattario_ms,
                             etichetta_cartella=cat,
                             fa_plot=not args.no_plot, verbose=True,
                             soglia_FIR=args.soglia_FIR, soglia_IIR=args.soglia_IIR)
        if res is not None:
            res['catalogo'] = cat
            rows.append(res)
    if rows:
        riepilogo = pd.DataFrame(rows)
        cols_order = ['catalogo', 'gesto', 'n_frame',
                      'C1_media', 'C1_std', 'C1_range',
                      'C2_media', 'C2_std', 'C2_range',
                      'C3_media', 'C3_std', 'C3_range',
                      'sigmaM_media', 'kurt_media', 'polar_media', 'frac_weak_media',
                      'corr_C1_C3', 'corr_C1_sigmaM', 'corr_C2_sigmaM',
                      'corr_C1_kurt', 'corr_C2_kurt',
                      'corr_C1_polar', 'corr_C2_polar',
                      'corr_C1_fracweak', 'corr_C2_fracweak',
                      'E1_max', 'E1_media', 'E2_min', 'E2_media',
                      'trigger_E1', 'trigger_E2', 'trigger_FIR', 'trigger_IIR']
        extra = [c for c in riepilogo.columns if c not in cols_order]
        riepilogo = riepilogo[cols_order + extra]
        riepilogo.to_csv(out_dir / 'riepilogo_controlli.csv', index=False,
                         float_format='%.4f')
        print(f'\nRiepilogo salvato: {out_dir / "riepilogo_controlli.csv"}')
        print(f'  {len(riepilogo)} gesti, {riepilogo["catalogo"].nunique()} cataloghi')


if __name__ == '__main__':
    main()
