#!/usr/bin/env python3
"""Curva di un descrittore in funzione della distanza microfono-sorgente.

Involucro sottile su `analisi.py`: applica `analyze()` in modalita' a un
descrittore (di norma il centroide) agli 8 microfoni in fila a 1..8 m, e ne
collaziona il valore lungo l'asse distanza. Non reimplementa i conti: il
centroide e' identico a quello del resto del paper (stessa FFT, finestra,
soglia).

L'unica aggiunta rispetto a `analisi.py` da riga di comando e' l'aggregazione:
per ogni file riassume i frame validi (non gated) con mediana + scarto
interquartile, e allinea i file all'asse metri leggendo `..._d<N>.wav`.

Uso:
    python distanza.py segnali/distanza/cluster_d*.wav
    python distanza.py --descrittori centroid,rolloff segnali/distanza/*.wav
    python distanza.py --self-test     # collaudo sintetico, senza audio reale
"""
import argparse
import csv
import os
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from analisi import analyze  # riuso, non reimplemento  # noqa: E402

GATE_REL_DB = -30.0  # gate relativo al picco del file: si auto-scala su ogni distanza


def distanza_da_nome(path):
    """Estrae la distanza in metri da un nome tipo 'cluster_d3.wav' -> 3."""
    m = re.search(r"d(\d+)", Path(path).stem)
    if m is None:
        raise ValueError(
            f"non riesco a leggere la distanza dal nome '{Path(path).name}' "
            f"(atteso un '..._d<metri>.wav')"
        )
    return int(m.group(1))


def riassumi(path, descrittori, gate_rel_db=GATE_REL_DB):
    """Riassume i frame validi di un file in mediana/IQR per ogni descrittore.

    Ritorna un dict {descrittore: (mediana, iqr)} piu' 'n_frame_validi', oppure
    None se nessun frame supera il gate.
    """
    results, _sr = analyze(
        str(path), only=list(descrittori), gate_dbfs=None, gate_rel_db=gate_rel_db
    )
    validi = [r for r in results if not r.get("gated", 0)]
    if not validi:
        return None
    out = {"n_frame_validi": len(validi)}
    for d in descrittori:
        v = np.array([r[d] for r in validi], dtype=float)
        out[d] = (float(np.median(v)), float(np.percentile(v, 75) - np.percentile(v, 25)))
    return out


def costruisci_curva(paths, descrittori, gate_rel_db=GATE_REL_DB):
    """Per ogni file calcola distanza + riassunto; ordina per distanza."""
    righe = []
    for p in paths:
        dist = distanza_da_nome(p)
        ris = riassumi(p, descrittori, gate_rel_db)
        if ris is None:
            print(f"  attenzione: '{Path(p).name}' non ha frame sopra il gate, saltato")
            continue
        righe.append((dist, ris))
    righe.sort(key=lambda t: t[0])
    return righe


def scrivi_csv(righe, descrittori, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    intestazione = ["distanza_m"]
    for d in descrittori:
        intestazione += [f"{d}_mediana", f"{d}_iqr"]
    intestazione.append("n_frame_validi")
    with open(output_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(intestazione)
        for dist, ris in righe:
            riga = [dist]
            for d in descrittori:
                mediana, iqr = ris[d]
                riga += [round(mediana, 2), round(iqr, 2)]
            riga.append(ris["n_frame_validi"])
            w.writerow(riga)
    return output_path


def _self_test():
    """Collaudo end-to-end senza audio reale.

    Genera rumore a banda larga e ne crea 8 versioni con passa-basso via via piu'
    severo (finta distanza: piu' lontano, piu' acute perse). Verifica che la
    pipeline produca una curva del centroide decrescente. Valida il calcolo,
    non sostituisce l'esperimento.
    """
    import tempfile
    import soundfile as sf
    from scipy.signal import butter, sosfilt

    sr = 44100
    durata = 2.0
    rng = np.random.default_rng(0)
    base = rng.standard_normal(int(sr * durata)).astype(np.float32)
    base /= np.max(np.abs(base))

    print("smoke-test sintetico: 8 'distanze' con passa-basso crescente")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        paths = []
        for d in range(1, 9):
            cutoff = 16000.0 / d  # piu' lontano -> taglio piu' basso -> meno acute
            sos = butter(4, cutoff, btype="low", fs=sr, output="sos")
            y = sosfilt(sos, base).astype(np.float32)
            y /= np.max(np.abs(y)) + 1e-12
            p = tmp / f"cluster_d{d}.wav"
            sf.write(p, y, sr)
            paths.append(p)

        righe = costruisci_curva(paths, ["centroid"])

    distanze = [dist for dist, _ in righe]
    centroidi = [ris["centroid"][0] for _, ris in righe]
    print(f"\n{'distanza (m)':>12} {'centroide (Hz)':>16}")
    for dist, c in zip(distanze, centroidi):
        print(f"{dist:>12} {c:>16.1f}")

    assert distanze == list(range(1, 9)), f"distanze non ordinate: {distanze}"
    assert centroidi[0] > centroidi[-1], "il centroide non scende con la distanza simulata"
    cali = all(b <= a + 1.0 for a, b in zip(centroidi, centroidi[1:]))
    assert cali, "la curva del centroide non e' monotona decrescente"
    print("\nOK: la pipeline gira end-to-end e la curva scende come atteso.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="*", help="i wav agli 8 microfoni (..._d<N>.wav)")
    parser.add_argument(
        "--descrittori",
        default="centroid",
        help="lista separata da virgole (default: centroid)",
    )
    parser.add_argument(
        "--gate-rel-db",
        type=float,
        default=GATE_REL_DB,
        help="gate relativo al picco del file in dB (default: -30)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="percorso CSV (default: analisi/distanza/<primo-descrittore>.csv)",
    )
    parser.add_argument("--self-test", action="store_true", help="collaudo sintetico")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()

    if not args.file:
        parser.error("indicare i file, oppure usare --self-test")

    descrittori = [d.strip() for d in args.descrittori.split(",") if d.strip()]
    righe = costruisci_curva(args.file, descrittori, args.gate_rel_db)
    if not righe:
        print("nessun file con frame validi: niente da scrivere")
        return 1

    out = args.out or (ROOT / "analisi" / "distanza" / f"{descrittori[0]}.csv")
    scrivi_csv(righe, descrittori, out)
    print(f"curva scritta in {out} ({len(righe)} distanze)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
