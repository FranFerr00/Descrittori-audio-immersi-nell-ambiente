#!/usr/bin/env python3
"""
Analizza i campioni di un catalogo di gesti strumentali.

Struttura attesa del catalogo (creata a mano):
    <catalog_dir>/
        catalog.json
        samples/NNN.wav

Struttura generata dallo script:
    <output_root>/
        analisi/NNN/NNN_hann_ov50_48000hz_analisi.csv
        analisi/NNN/NNN_hann_ov50_48000hz_<categoria>.png

Se --output-root non e' specificato, scrive in <catalog_dir>/analisi/.

I WAV multicanale vengono ridotti a mono (omni) tramite media dei canali
dentro `load_audio` in `analisi.py`.

Uso:
    python analizza_catalogo.py segnali/francesco/clarinettocb --output-root analisi/clarinettocb
    python analizza_catalogo.py segnali/francesco/timpano --output-root analisi/timpano
"""

import argparse
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('catalog_dir', help='Cartella del catalogo (contiene samples/*.wav)')
    parser.add_argument('--max-freq', type=float, default=48000,
                        help='Frequenza massima di analisi in Hz (default: 48000, banda piena)')
    parser.add_argument('--gate-dbfs', type=float, default=-65,
                        help='Gate assoluto in dBFS (default: -65)')
    parser.add_argument('--gate-rel-db', type=float, default=-30,
                        help='Gate relativo in dB dal peak globale (default: -30)')
    parser.add_argument('--output-root', default=None,
                        help='Cartella di output (default: <catalog_dir>). '
                             'I risultati vanno in <output_root>/analisi/NNN/.')
    args = parser.parse_args()

    catalog_dir = os.path.abspath(args.catalog_dir)
    samples_dir = os.path.join(catalog_dir, 'samples')
    if not os.path.isdir(samples_dir):
        print(f'Errore: manca {samples_dir}', file=sys.stderr)
        sys.exit(1)

    dest = os.path.abspath(args.output_root) if args.output_root else catalog_dir
    out_root = os.path.join(dest, 'analisi')
    os.makedirs(out_root, exist_ok=True)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    analisi_path = os.path.join(script_dir, 'analisi.py')

    wavs = sorted(f for f in os.listdir(samples_dir) if f.lower().endswith('.wav'))
    if not wavs:
        print(f'Errore: nessun .wav in {samples_dir}', file=sys.stderr)
        sys.exit(1)

    print(f'{len(wavs)} campioni in {samples_dir}')

    for wav in wavs:
        name = os.path.splitext(wav)[0]
        out_dir = os.path.join(out_root, name)
        os.makedirs(out_dir, exist_ok=True)
        wav_path = os.path.join(samples_dir, wav)
        print(f'  {name}')
        cmd = ['python', analisi_path, wav_path,
               '--max-freq', str(int(args.max_freq)),
               '--output-dir', out_dir,
               '--no-plot']
        if args.gate_dbfs is not None:
            cmd += ['--gate-dbfs', str(args.gate_dbfs)]
        if args.gate_rel_db is not None:
            cmd += ['--gate-rel-db', str(args.gate_rel_db)]
        subprocess.run(cmd, cwd=script_dir, check=True)

    print(f'\nFatto: {len(wavs)} campioni analizzati in {out_root}/')


if __name__ == '__main__':
    main()
