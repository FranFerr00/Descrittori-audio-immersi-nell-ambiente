#!/usr/bin/env python3
"""Livelli RMS per canale dei wav multicanale dell'esperimento distanza.

Helper condiviso da calibrazione_rms.py e attenuazione_distanza.py: legge un wav a
N canali, individua la finestra attiva (frame sopra una soglia relativa al frame piu'
forte del segnale medio) e calcola l'RMS per canale su quella finestra, in lineare e
in dBFS. Il rumore e' acceso/spento simultaneamente su tutti i canali, quindi la
finestra si stima una volta sul segnale medio e si applica a tutti i canali (cosi' i
canali lontani, deboli, non vengono gateati via).
"""
import numpy as np
import soundfile as sf

EPS = 1e-12


def rms(x):
    x = np.asarray(x, dtype=float)
    return float(np.sqrt(np.mean(np.square(x)))) if x.size else 0.0


def db(x):
    return 20.0 * np.log10(np.asarray(x, dtype=float) + EPS)


def finestra_attiva(mono, sr, frame=4096, rel_db=-30.0):
    """(i0, i1) campioni della regione attiva: dal primo all'ultimo frame il cui RMS
    supera (max RMS di frame) + rel_db. Ritorna (0, len) se non trova nulla."""
    mono = np.asarray(mono, dtype=float)
    n = len(mono)
    if n < frame:
        return 0, n
    nf = n // frame
    e = np.array([rms(mono[i * frame:(i + 1) * frame]) for i in range(nf)])
    if not np.any(e > 0):
        return 0, n
    soglia = e.max() * (10.0 ** (rel_db / 20.0))
    attivi = np.where(e >= soglia)[0]
    if len(attivi) == 0:
        return 0, n
    # +1: l'ultimo frame attivo e' incluso nella finestra
    return int(attivi[0] * frame), int((attivi[-1] + 1) * frame)


def rms_per_canale(path, frame=4096, rel_db=-30.0):
    """Legge il wav, stima la finestra attiva dal segnale medio e ritorna
    (rms_lineare, dbfs) come np.array di lunghezza n_canali."""
    data, sr = sf.read(path, always_2d=True)  # (N, n_canali)
    mono = data.mean(axis=1)
    i0, i1 = finestra_attiva(mono, sr, frame, rel_db)
    seg = data[i0:i1, :]
    lin = np.array([rms(seg[:, c]) for c in range(seg.shape[1])])
    return lin, db(lin)
