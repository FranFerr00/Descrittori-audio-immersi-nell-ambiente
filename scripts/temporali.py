"""
Descrittori temporali per il catalogo gesti strumentali.

Calcola descrittori che descrivono la forma dell'inviluppo nel tempo
(non il contenuto spettrale di un singolo frame). Complementare ad
analisi.py, che produce i 16 descrittori istantanei frame per frame.

Uso:
    python temporali.py file.wav
    python temporali.py file.wav --gate-dbfs -65 --gate-rel-db -30
    python temporali.py cartella/  (analizza tutti i .wav nella cartella)
"""

import numpy as np
import soundfile as sf
import csv
import os
import sys
import argparse
import matplotlib.pyplot as plt


# --- Parametri ---

HOP_SIZE = 4096       # stesso di analisi.py per allineare i frame
GATE_DBFS = None
GATE_REL_DB = None


def load_audio(path):
    data, sr = sf.read(path, dtype='float64')
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    return data, sr


def rms_envelope(data, hop):
    """Calcola l'inviluppo RMS frame per frame."""
    n_frames = (len(data) - hop) // hop + 1
    env = np.zeros(n_frames)
    for i in range(n_frames):
        start = i * hop
        frame = data[start:start + hop]
        env[i] = np.sqrt(np.mean(frame ** 2))
    return env


def apply_gate(env, data, hop, gate_dbfs=None, gate_rel_db=None):
    """Restituisce una maschera booleana: True = frame valido."""
    mask = np.ones(len(env), dtype=bool)

    gate_lin = 10 ** (gate_dbfs / 20.0) if gate_dbfs is not None else None

    if gate_rel_db is not None:
        file_peak = np.max(np.abs(data))
        gate_rel_lin = file_peak * 10 ** (gate_rel_db / 20.0)
    else:
        gate_rel_lin = None

    for i in range(len(env)):
        start = i * hop
        frame = data[start:start + hop]
        raw_peak = np.max(np.abs(frame))
        if gate_lin is not None and raw_peak < gate_lin:
            mask[i] = False
        if gate_rel_lin is not None and raw_peak < gate_rel_lin:
            mask[i] = False

    return mask


def temporal_centroid(env, mask, hop, sr):
    """Centro di gravita' temporale dell'energia (in secondi)."""
    valid_env = env * mask
    energy = valid_env ** 2
    total = np.sum(energy)
    if total == 0:
        return 0.0
    times = np.arange(len(env)) * hop / sr
    return np.sum(times * energy) / total


def attack_time(env, mask, hop, sr, low=0.1, high=0.9):
    """Tempo di attacco: da low% a high% del picco (in ms).

    Cerca la prima salita significativa. Se il segnale non raggiunge
    la soglia high, restituisce 0.
    """
    valid_env = env * mask
    peak = np.max(valid_env)
    if peak == 0:
        return 0.0

    low_thr = peak * low
    high_thr = peak * high

    # trova il primo frame sopra high_thr (indice del picco di attacco)
    above_high = np.where(valid_env >= high_thr)[0]
    if len(above_high) == 0:
        return 0.0
    peak_idx = above_high[0]

    # cerca indietro dal picco il primo frame sotto low_thr
    below_low = np.where(valid_env[:peak_idx + 1] <= low_thr)[0]
    if len(below_low) == 0:
        start_idx = 0
    else:
        start_idx = below_low[-1]

    dt = (peak_idx - start_idx) * hop / sr * 1000  # ms
    return dt


def decay_time(env, mask, hop, sr, high=0.9, low=0.1):
    """Tempo di decadimento: da high% a low% del picco dopo il massimo (in ms)."""
    valid_env = env * mask
    peak = np.max(valid_env)
    if peak == 0:
        return 0.0

    peak_idx = np.argmax(valid_env)
    after_peak = valid_env[peak_idx:]

    high_thr = peak * high
    low_thr = peak * low

    # primo frame dopo il picco che scende sotto high
    below_high = np.where(after_peak <= high_thr)[0]
    if len(below_high) == 0:
        start_idx = 0
    else:
        start_idx = below_high[0]

    # primo frame dopo start_idx che scende sotto low
    below_low = np.where(after_peak[start_idx:] <= low_thr)[0]
    if len(below_low) == 0:
        return (len(after_peak) - start_idx) * hop / sr * 1000
    end_idx = start_idx + below_low[0]

    dt = (end_idx - start_idx) * hop / sr * 1000  # ms
    return dt


def onset_count(env, mask, hop, sr, threshold_ratio=0.15, min_distance_ms=100):
    """Conta gli onset: picchi nell'inviluppo RMS sopra una soglia relativa.

    threshold_ratio: soglia relativa al picco globale per considerare un onset.
    min_distance_ms: distanza minima fra onset consecutivi.
    """
    valid_env = env * mask
    peak = np.max(valid_env)
    if peak == 0:
        return 0

    thr = peak * threshold_ratio
    min_dist_frames = int(min_distance_ms / 1000 * sr / hop)

    # derivata positiva dell'inviluppo (differenza prima)
    diff = np.diff(valid_env)
    diff = np.maximum(diff, 0)

    # picchi nella derivata (punti di massima salita)
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(diff, height=thr * 0.3, distance=min_dist_frames)

    # filtra: un onset e' valido solo se l'inviluppo raggiunge la soglia
    # entro qualche frame dal picco di derivata
    onsets = []
    lookahead = max(3, min_dist_frames // 4)
    for p in peaks:
        window = valid_env[p:min(p + lookahead, len(valid_env))]
        if len(window) > 0 and np.max(window) >= thr:
            onsets.append(p)

    return len(onsets)


def rms_range_db(env, mask):
    """Escursione dinamica dell'inviluppo RMS in dB (max - min dei frame validi)."""
    valid = env[mask]
    if len(valid) == 0 or np.max(valid) == 0:
        return 0.0
    valid_nonzero = valid[valid > 0]
    if len(valid_nonzero) == 0:
        return 0.0
    max_db = 20 * np.log10(np.max(valid_nonzero))
    min_db = 20 * np.log10(np.min(valid_nonzero))
    return max_db - min_db


def envelope_symmetry(env, mask):
    """Simmetria dell'inviluppo: temporal_centroid normalizzato a [0,1].

    0.5 = perfettamente simmetrico (campana centrata).
    < 0.5 = energia concentrata all'inizio (dim).
    > 0.5 = energia concentrata alla fine (cresc).
    """
    valid_env = env * mask
    energy = valid_env ** 2
    total = np.sum(energy)
    if total == 0:
        return 0.5
    positions = np.arange(len(env)) / max(len(env) - 1, 1)
    return np.sum(positions * energy) / total


def analyze_temporal(path, hop=HOP_SIZE, gate_dbfs=None, gate_rel_db=None):
    """Analisi temporale di un singolo file.

    Restituisce (result_dict, data, sr, env, mask) per permettere
    la generazione dei grafici senza ricaricare l'audio.
    """
    data, sr = load_audio(path)
    env = rms_envelope(data, hop)
    mask = apply_gate(env, data, hop, gate_dbfs, gate_rel_db)

    n_valid = int(np.sum(mask))
    n_total = len(env)
    duration_s = len(data) / sr

    tc = temporal_centroid(env, mask, hop, sr)
    att = attack_time(env, mask, hop, sr)
    dec = decay_time(env, mask, hop, sr)
    onsets = onset_count(env, mask, hop, sr)
    dyn_range = rms_range_db(env, mask)
    symmetry = envelope_symmetry(env, mask)

    # RMS medio e picco sui frame validi
    valid_env = env[mask]
    rms_mean = np.mean(valid_env) if len(valid_env) > 0 else 0.0
    rms_peak = np.max(valid_env) if len(valid_env) > 0 else 0.0

    result = {
        'file': os.path.basename(path),
        'duration_s': round(duration_s, 3),
        'n_frames_valid': n_valid,
        'n_frames_total': n_total,
        'temporal_centroid_s': round(tc, 3),
        'symmetry': round(symmetry, 3),
        'attack_ms': round(att, 1),
        'decay_ms': round(dec, 1),
        'onset_count': onsets,
        'rms_mean': round(rms_mean, 6),
        'rms_peak': round(rms_peak, 6),
        'dynamic_range_db': round(dyn_range, 1),
    }
    return result, data, sr, env, mask


def _waveform_panel(ax, data, sr):
    """Pannello forma d'onda (riutilizzato in tutti i grafici)."""
    t = np.arange(len(data)) / sr
    ax.plot(t, data, linewidth=0.3, color='gray')
    ax.set_ylabel('Ampiezza')
    ax.set_ylim(-1, 1)
    ax.grid(True, alpha=0.3)
    ax.set_title('Forma d\'onda', fontsize=9, loc='left')


def _gate_shading(ax, env, mask, hop, sr):
    """Evidenzia i frame esclusi dal gate in grigio chiaro."""
    t_frames = np.arange(len(env)) * hop / sr
    for i, valid in enumerate(mask):
        if not valid:
            ax.axvspan(t_frames[i], t_frames[i] + hop / sr,
                       color='lightgray', alpha=0.6, linewidth=0)


def _attack_decay_indices(valid_env):
    """Restituisce (att_start, att_end, dec_start, dec_end) come indici di frame."""
    peak_val = np.max(valid_env) if len(valid_env) > 0 else 0.0
    if peak_val == 0:
        return None
    high_thr = peak_val * 0.9
    low_thr = peak_val * 0.1

    above_high = np.where(valid_env >= high_thr)[0]
    if len(above_high) == 0:
        return None
    att_end = above_high[0]
    below_low = np.where(valid_env[:att_end + 1] <= low_thr)[0]
    att_start = below_low[-1] if len(below_low) > 0 else 0

    peak_abs = np.argmax(valid_env)
    after = valid_env[peak_abs:]
    below_high_dec = np.where(after <= high_thr)[0]
    if len(below_high_dec) == 0:
        return None
    dec_start = peak_abs + below_high_dec[0]
    below_low_dec = np.where(after[below_high_dec[0]:] <= low_thr)[0]
    dec_end = (peak_abs + below_high_dec[0] + below_low_dec[0]
               if len(below_low_dec) > 0 else len(valid_env) - 1)
    dec_end = min(dec_end, len(valid_env) - 1)

    return att_start, att_end, dec_start, dec_end


def plot_all_categories(data, sr, env, mask, result, base, out_dir):
    """Genera tre PNG separati per categoria, come analisi.py."""
    hop = HOP_SIZE
    t_audio = np.arange(len(data)) / sr
    t_frames = np.arange(len(env)) * hop / sr
    valid_env = env * mask
    title_base = result['file']

    # --- inviluppo: RMS + centroide temporale + simmetria ---
    fig, axes = plt.subplots(2, 1, figsize=(14, 6), sharex=True)
    fig.suptitle(f'{title_base} — inviluppo', fontsize=12)
    _waveform_panel(axes[0], data, sr)
    ax = axes[1]
    _gate_shading(ax, env, mask, hop, sr)
    ax.plot(t_frames, env, linewidth=0.8, color='steelblue')
    tc = result['temporal_centroid_s']
    ax.axvline(tc, color='crimson', linewidth=1.2, linestyle='--',
               label=f'centroide  {tc:.2f} s  (simmetria {result["symmetry"]:.3f})')
    ax.set_ylabel('RMS')
    ax.set_xlabel('Tempo (s)')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)
    ax.set_title('Inviluppo RMS', fontsize=9, loc='left')
    ax.text(0.01, 0.97,
            f"centroide: {result['temporal_centroid_s']:.3f} s   "
            f"simmetria: {result['symmetry']:.3f}   "
            f"durata: {result['duration_s']:.2f} s",
            transform=ax.transAxes, fontsize=8, va='top',
            bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7))
    plt.tight_layout()
    out = os.path.join(out_dir, f'{base}_temporali_inviluppo.png')
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  {out}")

    # --- attacco e decadimento ---
    fig, axes = plt.subplots(2, 1, figsize=(14, 6), sharex=True)
    fig.suptitle(f'{title_base} — attacco e decadimento', fontsize=12)
    _waveform_panel(axes[0], data, sr)
    ax = axes[1]
    _gate_shading(ax, env, mask, hop, sr)
    ax.plot(t_frames, env, linewidth=0.8, color='steelblue')
    idx = _attack_decay_indices(valid_env)
    if idx is not None:
        att_start, att_end, dec_start, dec_end = idx
        ax.axvspan(t_frames[att_start], t_frames[att_end],
                   color='orange', alpha=0.35,
                   label=f'attacco  {result["attack_ms"]:.0f} ms')
        ax.axvspan(t_frames[dec_start], t_frames[dec_end],
                   color='mediumseagreen', alpha=0.35,
                   label=f'decadimento  {result["decay_ms"]:.0f} ms')
        ax.legend(loc='upper right', fontsize=9)
    ax.set_ylabel('RMS')
    ax.set_xlabel('Tempo (s)')
    ax.grid(True, alpha=0.3)
    ax.set_title('Attacco e decadimento', fontsize=9, loc='left')
    ax.text(0.01, 0.97,
            f"attacco: {result['attack_ms']:.1f} ms   "
            f"decadimento: {result['decay_ms']:.1f} ms   "
            f"onset: {result['onset_count']}",
            transform=ax.transAxes, fontsize=8, va='top',
            bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7))
    plt.tight_layout()
    out = os.path.join(out_dir, f'{base}_temporali_attacco.png')
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  {out}")

    # --- ampiezza: inviluppo in dB + escursione dinamica ---
    fig, axes = plt.subplots(2, 1, figsize=(14, 6), sharex=True)
    fig.suptitle(f'{title_base} — ampiezza', fontsize=12)
    _waveform_panel(axes[0], data, sr)
    ax = axes[1]
    _gate_shading(ax, env, mask, hop, sr)
    env_db = np.where(env > 0, 20 * np.log10(np.maximum(env, 1e-10)), np.nan)
    ax.plot(t_frames, env_db, linewidth=0.8, color='steelblue')
    valid_db = env_db[mask]
    if len(valid_db) > 0:
        peak_db = np.nanmax(valid_db)
        floor_db = np.nanmin(valid_db)
        ax.axhline(peak_db, color='crimson', linewidth=0.8, linestyle=':',
                   label=f'picco  {peak_db:.1f} dB')
        ax.axhline(floor_db, color='steelblue', linewidth=0.8, linestyle=':',
                   label=f'minimo  {floor_db:.1f} dB  '
                         f'(escursione {result["dynamic_range_db"]:.1f} dB)')
    ax.set_ylabel('RMS (dB)')
    ax.set_xlabel('Tempo (s)')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)
    ax.set_title('Ampiezza', fontsize=9, loc='left')
    ax.text(0.01, 0.97,
            f"rms medio: {result['rms_mean']:.5f}   "
            f"rms picco: {result['rms_peak']:.5f}   "
            f"escursione: {result['dynamic_range_db']:.1f} dB",
            transform=ax.transAxes, fontsize=8, va='top',
            bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7))
    plt.tight_layout()
    out = os.path.join(out_dir, f'{base}_temporali_ampiezza.png')
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  {out}")


def plot_confronto(all_results, prefix, out_dir):
    """Grafici comparativi tra campioni: un pannello per descrittore.

    Genera tre PNG (inviluppo, attacco, ampiezza), uno per categoria,
    con barre orizzontali per ogni campione. Analogo ad aggrega_grafici.py
    per i descrittori temporali.
    """
    names = [r['file'] for r in all_results]
    n = len(names)
    y = np.arange(n)

    categories = {
        'inviluppo': [
            ('temporal_centroid_s', 'Centroide temporale (s)'),
            ('symmetry', 'Simmetria (0=dim, 1=cresc)'),
        ],
        'attacco': [
            ('attack_ms', 'Attacco (ms)'),
            ('decay_ms', 'Decadimento (ms)'),
            ('onset_count', 'Onset'),
        ],
        'ampiezza': [
            ('rms_mean', 'RMS medio'),
            ('rms_peak', 'RMS picco'),
            ('dynamic_range_db', 'Escursione dinamica (dB)'),
        ],
    }

    for cat_name, descriptors in categories.items():
        n_desc = len(descriptors)
        fig, axes = plt.subplots(1, n_desc, figsize=(6 * n_desc, max(4, n * 0.4 + 1)))
        if n_desc == 1:
            axes = [axes]
        fig.suptitle(f'{prefix} — {cat_name}', fontsize=12)

        for ax, (key, label) in zip(axes, descriptors):
            values = [r[key] for r in all_results]
            ax.barh(y, values, color='steelblue', alpha=0.8)
            ax.set_yticks(y)
            ax.set_yticklabels(names, fontsize=7)
            ax.set_xlabel(label, fontsize=9)
            ax.grid(True, alpha=0.3, axis='x')
            ax.invert_yaxis()

        plt.tight_layout()
        out = os.path.join(out_dir, f'{prefix}_temporali_{cat_name}.png')
        plt.savefig(out, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  {out}")


def print_results(results):
    """Stampa una tabella riassuntiva."""
    if not results:
        print("Nessun file analizzato.")
        return

    keys = ['file', 'duration_s', 'n_frames_valid', 'temporal_centroid_s',
            'symmetry', 'attack_ms', 'decay_ms', 'onset_count',
            'rms_mean', 'rms_peak', 'dynamic_range_db']

    # header
    header = f"{'file':<12} {'dur':>5} {'val':>4} {'tc_s':>6} {'sym':>5} " \
             f"{'att_ms':>7} {'dec_ms':>7} {'ons':>4} " \
             f"{'rms_m':>8} {'rms_pk':>8} {'dyn_dB':>6}"
    print(header)
    print("-" * len(header))

    for r in results:
        print(f"{r['file']:<12} {r['duration_s']:>5.1f} {r['n_frames_valid']:>4} "
              f"{r['temporal_centroid_s']:>6.2f} {r['symmetry']:>5.3f} "
              f"{r['attack_ms']:>7.1f} {r['decay_ms']:>7.1f} {r['onset_count']:>4} "
              f"{r['rms_mean']:>8.5f} {r['rms_peak']:>8.5f} {r['dynamic_range_db']:>6.1f}")


def save_csv(results, output_path):
    if not results:
        return
    keys = results[0].keys()
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Descrittori temporali per catalogo gesti strumentali')
    parser.add_argument('input', help='File WAV o cartella con file WAV')
    parser.add_argument('--hop', type=int, default=HOP_SIZE,
                        help=f'Hop size in campioni (default: {HOP_SIZE})')
    parser.add_argument('--gate-dbfs', type=float, default=None,
                        help='Gate assoluto in dBFS (es. -65)')
    parser.add_argument('--gate-rel-db', type=float, default=None,
                        help='Gate relativo al peak del file in dB (es. -30)')
    parser.add_argument('--output-dir', default=None,
                        help='Cartella di output per CSV e PNG '
                             '(default: cartella del file di input)')
    parser.add_argument('--no-plot', action='store_true',
                        help='Salta la generazione dei PNG per-sample (inviluppo, '
                             'attacco, ampiezza). Il CSV viene comunque salvato.')

    args = parser.parse_args()

    # raccogli i file da analizzare
    if os.path.isdir(args.input):
        wav_files = sorted([
            os.path.join(args.input, f)
            for f in os.listdir(args.input)
            if f.endswith('.wav')
        ])
        default_out_dir = args.input
    else:
        wav_files = [args.input]
        default_out_dir = os.path.dirname(os.path.abspath(args.input))

    if not wav_files:
        print(f"Nessun file WAV trovato in {args.input}")
        sys.exit(1)

    out_dir = args.output_dir if args.output_dir else default_out_dir
    os.makedirs(out_dir, exist_ok=True)

    all_results = []
    for path in wav_files:
        print(f"\n{os.path.basename(path)}")
        result, data, sr, env, mask = analyze_temporal(
            path, hop=args.hop,
            gate_dbfs=args.gate_dbfs,
            gate_rel_db=args.gate_rel_db)
        all_results.append(result)

        base = os.path.splitext(os.path.basename(path))[0]
        csv_path = os.path.join(out_dir, f'{base}_temporali.csv')
        save_csv([result], csv_path)
        print(f"  CSV: {csv_path}")

        if not args.no_plot:
            plot_all_categories(data, sr, env, mask, result, base, out_dir)

    if len(wav_files) > 1:
        prefix = os.path.basename(os.path.abspath(args.input).rstrip('/'))
        print(f"\n=== Grafici comparativi ({prefix}) ===")
        plot_confronto(all_results, prefix, out_dir)

    print_results(all_results)
