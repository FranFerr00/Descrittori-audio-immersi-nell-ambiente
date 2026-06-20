#!/usr/bin/env python3
"""
Taglia il file WAV unico in segmenti separati,
crea una cartella per ogni segnale e lancia l'analisi.
"""

import os
import subprocess
import soundfile as sf
import numpy as np

INPUT_WAV = 'segnali/test_segnali.wav'
OUTPUT_DIR = 'analisi'

# segmenti prima degli impulsi (invariati)
SEGMENTS_PRE = [
    ('01_sinusoide_440', 1, 6),
    ('02_noise_bianco', 7, 12),
    ('03_tanh_drive1', 13, 18),
    ('04_tanh_drive5', 19, 24),
    ('05_tanh_drive20', 25, 30),
    ('06_noise_bp_q500', 31, 36),
    ('07_noise_bp_q200', 37, 42),
    ('08_noise_bp_q50', 43, 48),
]

# segmenti dopo gli impulsi (tempi del file Csound originale)
SEGMENTS_POST = [
    ('10_fm_idx05', 55, 60),
    ('11_fm_idx3', 61, 66),
    ('12_fm_idx10', 67, 72),
    ('13_sin100', 73, 78),
    ('14_sin75_noise25', 79, 84),
    ('15_sin50_noise50', 85, 90),
    ('16_sin25_noise75', 91, 96),
    ('17_noise100', 97, 102),
    ('18_sin_crescendo', 103, 108),
    ('19_sin_diminuendo', 109, 114),
    ('20_sin_crescdim', 115, 120),
    ('21_noise_crescendo', 121, 126),
    ('22_noise_diminuendo', 127, 132),
    ('23_noise_crescdim', 133, 138),
    ('24_bin_esatto_40', 139, 144),
    ('25_fuori_bin_40', 145, 150),
    ('26_bin_esatto_80', 151, 156),
    ('27_fuori_bin_80', 157, 162),
    ('28_gliss_lento_200_2000', 163, 173),
    ('29_gliss_veloce_200_2000', 174, 177),
    ('30_gliss_lento_2000_200', 178, 188),
    ('31_gliss_micro_440_460', 189, 199),
    ('32_2sin_200_4000', 200, 205),
    ('33_2sin_400_1000', 206, 211),
    ('34_2sin_100_8000', 212, 217),
    ('35_2sin_200cresc_4000dim', 218, 226),
    ('36_2sin_200dim_4000cresc', 227, 235),
    ('37_2sin_convergono_1000', 236, 251),
    ('38_2sin_divergono_1000', 252, 267),
    ('39_2sin_convergono_unisono', 268, 283),
    ('40_tanh_drive_cresc', 284, 294),
    ('41_tanh_drive_decresc', 295, 305),
    ('42_fm_idx_cresc', 306, 316),
    ('43_fm_idx_decresc', 317, 327),
    ('44_tanh_drive_cresc_veloce', 328, 331),
    ('45_fm_idx_cresc_veloce', 332, 335),
]

# file originale: con impulsi
SEGMENTS = SEGMENTS_PRE + [('09_impulsi_100', 49, 54)] + SEGMENTS_POST

# registrazioni: senza impulsi, tempi spostati di -6 s
SHIFT = 6  # 5 s segnale + 1 s silenzio rimossi
SEGMENTS_RECS = SEGMENTS_PRE + [(n, s - SHIFT, e - SHIFT) for n, s, e in SEGMENTS_POST]

ANALISI_ARGS = ['--max-freq', '48000']

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Taglia WAV e analizza ogni segmento')
    parser.add_argument('file', nargs='?', default=INPUT_WAV,
                        help='File WAV da tagliare (default: test_segnali.wav)')
    parser.add_argument('--recs', action='store_true',
                        help='Usa segmenti per registrazioni (senza impulsi, tempi spostati) '
                             'e scrivi in segnali/<nome_file>/')
    parser.add_argument('--subdir', action='store_true',
                        help='Usa i segmenti completi (come il sintetico) ma scrivi in '
                             'segnali/<nome_file>/. Utile per varianti del file sintetico '
                             '(es. scalato a -30 dB) che mantengono gli impulsi.')
    parser.add_argument('--no-analisi', action='store_true',
                        help='Solo taglio, senza lanciare analisi')
    parser.add_argument('--max-freq', type=float, default=48000,
                        help='Frequenza massima per analisi (default: 48000, banda piena)')
    parser.add_argument('--gate-dbfs', type=float, default=None,
                        help='Gate assoluto in dBFS passato ad analisi.py e temporali.py')
    parser.add_argument('--gate-rel-db', type=float, default=None,
                        help='Gate relativo al peak del file in dB')
    args = parser.parse_args()

    if args.recs and args.subdir:
        parser.error('--recs e --subdir sono mutuamente esclusivi')

    input_wav = args.file
    segments = SEGMENTS_RECS if args.recs else SEGMENTS

    data, sr = sf.read(input_wav)
    print(f"Caricato {input_wav}: {len(data)} campioni, SR {sr}")
    if args.recs:
        print(f"Modalita' registrazioni: {len(segments)} segmenti (senza impulsi, shift -{SHIFT}s)")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    analisi_path = os.path.join(script_dir, 'analisi.py')
    temporali_path = os.path.join(script_dir, 'temporali.py')

    # cartella di output: analisi/sintetici per i sintetici, analisi/<nome> per le varianti
    base_name = os.path.splitext(os.path.basename(input_wav))[0]
    if args.recs or args.subdir:
        out_dir = os.path.join(OUTPUT_DIR, base_name)
    else:
        out_dir = os.path.join(OUTPUT_DIR, 'sintetici')
    os.makedirs(out_dir, exist_ok=True)

    # taglio e analisi dei segmenti
    print(f"\n=== Taglio in {len(segments)} segmenti ===\n")

    for name, t_start, t_end in segments:
        folder = os.path.join(out_dir, name)
        os.makedirs(folder, exist_ok=True)

        s_start = int(t_start * sr)
        s_end = int(t_end * sr)
        segment = data[s_start:s_end]

        wav_path = os.path.join(folder, f'{name}.wav')
        sf.write(wav_path, segment, sr, subtype='FLOAT')

        duration = len(segment) / sr
        print(f"  {name}: {duration:.1f}s -> {wav_path}")

        if not args.no_analisi:
            gate_args = []
            if args.gate_dbfs is not None:
                gate_args += ['--gate-dbfs', str(args.gate_dbfs)]
            if args.gate_rel_db is not None:
                gate_args += ['--gate-rel-db', str(args.gate_rel_db)]

            subprocess.run([
                'python', analisi_path, wav_path,
                '--max-freq', str(int(args.max_freq)),
                '--output-dir', folder,
                '--no-plot',
            ] + gate_args, cwd=script_dir)

            subprocess.run([
                'python', temporali_path, wav_path,
                '--output-dir', folder,
                '--no-plot',
            ] + gate_args, cwd=script_dir)

    print(f"\nFatto: {len(segments)} segmenti in {out_dir}/")
