#!/usr/bin/env python3
"""Estrae la centroide per canale di tutti i wav multicanale di una cartella.

Per ogni file <nome>.wav lancia scripts/analisi.py con --per-canale (gate da
registrazione reale) e mette gli 8 CSV in <out>/<nome>/.

Uso:
    python esperimento_distanza/analizza_divisi.py \
        esperimento_distanza/2026-06-13-FRAFER-TEST-DISTANZA-GIUSTO/divisi \
        analisi/distanza

Poi: python esperimento_distanza/centroidi_riepilogo.py analisi/distanza
"""
import argparse
import glob
import os
import subprocess
import sys

# radice del repo = due livelli sopra questo file (esperimento_distanza/<file>)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('src', help='cartella con i wav multicanale')
    p.add_argument('out', help='cartella di output (una sottocartella per file)')
    p.add_argument('--max-freq', type=float, default=48000)
    p.add_argument('--gate-dbfs', type=float, default=-65)
    p.add_argument('--gate-rel-db', type=float, default=-30)
    args = p.parse_args(argv)

    analisi = os.path.join(ROOT, 'scripts', 'analisi.py')
    wavs = sorted(glob.glob(os.path.join(args.src, '*.wav')))
    if not wavs:
        sys.exit(f'nessun wav in {args.src}')
    os.makedirs(args.out, exist_ok=True)

    for f in wavs:
        base = os.path.splitext(os.path.basename(f))[0]
        outdir = os.path.join(args.out, 'centroide', base)
        os.makedirs(outdir, exist_ok=True)
        subprocess.run([
            sys.executable, analisi, f,
            '--max-freq', str(args.max_freq),
            '--gate-dbfs', str(args.gate_dbfs), '--gate-rel-db', str(args.gate_rel_db),
            '--no-plot', '--per-canale', '--output-dir', outdir,
        ], check=True, stdout=subprocess.DEVNULL)
        print(f'ok  {base}')

    print(f'\nestratte le centroidi per canale di {len(wavs)} file in {args.out}')


if __name__ == '__main__':
    main()
