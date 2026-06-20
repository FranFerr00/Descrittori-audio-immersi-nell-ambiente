"""
Script temporaneo per testare due descrittori aggiuntivi non presenti in
analisi.py:

  - Spectral Entropy (Shannon entropy dello spettro di potenza normalizzato)
  - Spectral Contrast (differenza tra picchi e valli in bande per ottava)

Parametri allineati ad analisi.py: FFT 8192, hop 4096, Hann, max_freq 10 kHz,
soglia relativa -60 dB, gate (--gate-dbfs / --gate-rel-db).

NON fa parte dei 16 descrittori ufficiali: serve solo a vedere se il segnale
e' interessante sul corpus prima di integrarlo.
"""

import numpy as np
import soundfile as sf
import csv
import os
import matplotlib.pyplot as plt

# --- Parametri ---

FFT_SIZE = 8192
HOP_SIZE = 4096
WINDOW = 'hann'
THRESHOLD_DB = -60
GATE_DBFS = None
EPSILON = 1e-19
MAX_FREQ = None

# bande di contrast: edge per ottava, come Jiang et al. 2002.
# entro max_freq = 10 kHz produciamo 6 bande (200 Hz - 10 kHz).
CONTRAST_EDGES = [200.0, 400.0, 800.0, 1600.0, 3200.0, 6400.0, 10000.0]
CONTRAST_QUANTILE = 0.02  # quantile basso/alto per valle/picco (Jiang: ~2%)
CONTRAST_ALPHA = 1e-6     # floor valley = alpha * peak (cap ~60 dB)


def load_audio(path):
    data, sr = sf.read(path, dtype='float64')
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    return data, sr


def make_window(size, kind):
    if kind == 'hann':
        return np.hanning(size)
    return np.ones(size)


def compute_spectrum(frame, fft_size, threshold_db):
    X = np.fft.rfft(frame, n=fft_size)
    mag = np.abs(X) / fft_size
    peak = np.max(mag)
    if peak == 0:
        return mag, np.zeros_like(mag)
    threshold = peak * 10 ** (threshold_db / 20.0)
    mag_th = np.where(mag > threshold, mag, 0.0)
    return mag, mag_th


# === NUOVI DESCRITTORI ===

def spectral_entropy(mag_th):
    # Shannon entropy di p(k) = |X(k)|^2 / sum|X|^2.
    # Normalizzata in [0, 1] dividendo per log2(N_totale): segnali con
    # poche bin attive (sinusoide) hanno entropy bassa, segnali con tutte
    # le bin uniformi (noise) hanno entropy ~1.
    # Shen et al. 1998, Misra et al. 2004.
    n_total = len(mag_th)
    if n_total < 2:
        return 0.0
    power = mag_th ** 2
    total = np.sum(power)
    if total == 0:
        return 0.0
    p = power[power > 0] / total
    if len(p) < 1:
        return 0.0
    H = -np.sum(p * np.log2(p))
    return H / np.log2(n_total)


def spectral_contrast(mag, freqs, edges, quantile):
    # Jiang et al. 2002: per ogni banda log-ottava, differenza in dB tra
    # il quantile alto (picco) e il quantile basso (valle) della magnitudine.
    # Valori alti (tanti dB) = banda tonale con picchi dominanti;
    # valori bassi (pochi dB) = banda piatta tipo noise.
    # Output: vettore di len(edges)-1 valori.
    power = mag ** 2
    n_bands = len(edges) - 1
    out = np.zeros(n_bands)
    for b in range(n_bands):
        mask = (freqs >= edges[b]) & (freqs < edges[b + 1])
        band = power[mask]
        if len(band) < 2 or np.sum(band) == 0:
            out[b] = 0.0
            continue
        band_sorted = np.sort(band)
        n = len(band_sorted)
        k_low = max(1, int(np.ceil(n * quantile)))
        k_high = max(1, int(np.ceil(n * quantile)))
        valley = np.mean(band_sorted[:k_low])
        peak = np.mean(band_sorted[-k_high:])
        # floor alla librosa: evita che valley scenda al rumore numerico
        # e che il rapporto peak/valley saturi a >100 dB.
        floor = CONTRAST_ALPHA * peak
        if valley < floor:
            valley = floor if floor > 0 else EPSILON
        out[b] = 10.0 * np.log10(peak / valley)
    return out


# === ANALISI ===

def analyze(path, fft_size=FFT_SIZE, hop_size=HOP_SIZE,
            window=WINDOW, threshold_db=THRESHOLD_DB,
            max_freq=MAX_FREQ, gate_dbfs=GATE_DBFS, gate_rel_db=None):
    data, sr = load_audio(path)
    if hop_size is None:
        hop_size = fft_size

    win = make_window(fft_size, window)
    n_frames = (len(data) - fft_size) // hop_size + 1
    freqs = np.fft.rfftfreq(fft_size, d=1.0 / sr)

    if max_freq is not None:
        max_bin = int(max_freq / (sr / fft_size)) + 1
        max_bin = min(max_bin, len(freqs))
    else:
        max_bin = len(freqs)

    freqs = freqs[:max_bin]
    n_bands = len(CONTRAST_EDGES) - 1

    results = []

    gate_lin = 10 ** (gate_dbfs / 20.0) if gate_dbfs is not None else None
    if gate_rel_db is not None:
        file_peak = np.max(np.abs(data))
        gate_rel_lin = file_peak * 10 ** (gate_rel_db / 20.0)
    else:
        gate_rel_lin = None

    for i in range(n_frames):
        start = i * hop_size
        raw_frame = data[start:start + fft_size]

        gated = False
        if gate_lin is not None or gate_rel_lin is not None:
            raw_peak = np.max(np.abs(raw_frame))
            if gate_lin is not None and raw_peak < gate_lin:
                gated = True
            if gate_rel_lin is not None and raw_peak < gate_rel_lin:
                gated = True

        if gated:
            time_s = start / sr
            row = {
                'frame': i,
                'time': round(time_s, 4),
                'entropy': 0.0,
                'contrast_mean': 0.0,
                'gated': 1,
            }
            for b in range(n_bands):
                row[f'contrast_b{b}'] = 0.0
            results.append(row)
            continue

        frame = raw_frame * win
        mag, mag_th = compute_spectrum(frame, fft_size, threshold_db)
        mag = mag[:max_bin]
        mag_th = mag_th[:max_bin]

        entropy = spectral_entropy(mag_th)
        contrast = spectral_contrast(mag, freqs, CONTRAST_EDGES,
                                     CONTRAST_QUANTILE)

        time_s = start / sr
        row = {
            'frame': i,
            'time': round(time_s, 4),
            'entropy': round(entropy, 6),
            'contrast_mean': round(float(np.mean(contrast)), 4),
            'gated': 0,
        }
        for b in range(n_bands):
            row[f'contrast_b{b}'] = round(float(contrast[b]), 4)
        results.append(row)

    return results, sr


def save_csv(results, output_path):
    if not results:
        return
    keys = list(results[0].keys())
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)


def print_summary(results):
    if not results:
        print("Nessun frame analizzato.")
        return
    valid = [r for r in results if not r.get('gated', 0)]
    n_total = len(results)
    n_valid = len(valid)
    n_gated = n_total - n_valid
    if not valid:
        print(f"Nessun frame valido (tutti i {n_total} frame sono sotto il gate).")
        return

    n_bands = len(CONTRAST_EDGES) - 1
    keys = ['entropy', 'contrast_mean'] + [f'contrast_b{b}' for b in range(n_bands)]

    print(f"\n{'Descrittore':<16} {'Min':>10} {'Max':>10} {'Media':>10} {'Std':>10}")
    print("-" * 58)
    for k in keys:
        vals = [r[k] for r in valid]
        print(f"{k:<16} {min(vals):>10.4f} {max(vals):>10.4f} "
              f"{np.mean(vals):>10.4f} {np.std(vals):>10.4f}")

    print(f"\nBande contrast (Hz):")
    for b in range(n_bands):
        print(f"  b{b}: {CONTRAST_EDGES[b]:.0f} - {CONTRAST_EDGES[b+1]:.0f}")

    if n_gated > 0:
        print(f"\nFrame totali: {n_total} (validi: {n_valid}, gated: {n_gated})")
    else:
        print(f"\nFrame totali: {n_total}")


def plot_results(results, base_name, output_path, audio_data=None, sr=None):
    if not results:
        return
    time = [r['time'] for r in results]
    n_bands = len(CONTRAST_EDGES) - 1

    n_panels = 3 + (2 if audio_data is not None else 0)
    fig, axes = plt.subplots(n_panels, 1, figsize=(14, n_panels * 2.2), sharex=True)
    if n_panels == 1:
        axes = [axes]
    fig.suptitle(f'{base_name} — entropy + contrast', fontsize=13)

    idx = 0
    if audio_data is not None:
        ax = axes[idx]
        t_audio = np.arange(len(audio_data)) / sr
        ax.plot(t_audio, audio_data, linewidth=0.3, color='gray')
        ax.set_ylabel('Ampiezza')
        ax.set_ylim(-1, 1)
        ax.grid(True, alpha=0.3)
        ax.set_title('Forma d\'onda', fontsize=9, loc='left')
        idx += 1

        ax = axes[idx]
        n_fft = FFT_SIZE
        hop = HOP_SIZE
        n_frames_spec = (len(audio_data) - n_fft) // hop + 1
        spec = np.zeros((n_fft // 2 + 1, n_frames_spec))
        win = make_window(n_fft, WINDOW)
        for i in range(n_frames_spec):
            start = i * hop
            frame = audio_data[start:start + n_fft] * win
            X = np.fft.rfft(frame, n=n_fft)
            spec[:, i] = 20 * np.log10(np.abs(X) / n_fft + 1e-10)
        extent = [0, len(audio_data) / sr, 0, sr / 2]
        ax.imshow(spec, aspect='auto', origin='lower', extent=extent,
                  cmap='inferno', vmin=-80, vmax=0)
        ax.set_ylabel('Hz')
        ax.set_ylim(0, min(sr / 2, 10000))
        ax.set_title('Spettrogramma', fontsize=9, loc='left')
        idx += 1

    ax = axes[idx]
    ax.plot(time, [r['entropy'] for r in results], color='#1f77b4', linewidth=0.7)
    ax.set_ylabel('Entropy')
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    idx += 1

    ax = axes[idx]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    for b in range(n_bands):
        label = f'{CONTRAST_EDGES[b]:.0f}-{CONTRAST_EDGES[b+1]:.0f} Hz'
        ax.plot(time, [r[f'contrast_b{b}'] for r in results],
                label=label, linewidth=0.6, color=colors[b % len(colors)])
    ax.set_ylabel('Contrast (dB)')
    ax.legend(loc='upper right', fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)
    idx += 1

    ax = axes[idx]
    ax.plot(time, [r['contrast_mean'] for r in results],
            color='#d62728', linewidth=0.8)
    ax.set_ylabel('Contrast mean')
    ax.set_xlabel('Tempo (s)')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Test descrittori aggiuntivi: entropy + contrast')
    parser.add_argument('file', help='File WAV da analizzare')
    parser.add_argument('-o', '--output', help='File CSV di output')
    parser.add_argument('-w', '--window', default=WINDOW,
                        choices=['rectangular', 'hann'])
    parser.add_argument('--hop', type=int, default=None)
    parser.add_argument('--max-freq', type=float, default=None)
    parser.add_argument('--gate-dbfs', type=float, default=None)
    parser.add_argument('--gate-rel-db', type=float, default=None)
    parser.add_argument('--output-dir', default=None)
    parser.add_argument('--no-plot', action='store_true',
                        help='Salta generazione PNG')

    args = parser.parse_args()

    audio_path = args.file
    win_type = args.window
    hop = args.hop if args.hop is not None else HOP_SIZE
    max_freq = args.max_freq

    print(f"Analisi di: {audio_path}")
    print(f"FFT: {FFT_SIZE}, Hop: {hop}, Finestra: {win_type}")

    audio_data, sr = load_audio(audio_path)
    results, sr = analyze(audio_path, fft_size=FFT_SIZE, hop_size=hop,
                          window=win_type, max_freq=max_freq,
                          gate_dbfs=args.gate_dbfs,
                          gate_rel_db=args.gate_rel_db)
    print(f"SR: {sr}")
    print_summary(results)

    base = os.path.splitext(os.path.basename(audio_path))[0]
    if args.output_dir:
        out_dir = args.output_dir
        os.makedirs(out_dir, exist_ok=True)
    else:
        # lo script sta in scripts/, la radice del repo e' un livello sopra
        out_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    freq_suffix = f'_{int(max_freq)}hz' if max_freq else ''
    suffix = f'_{win_type}_nuovi{freq_suffix}'

    csv_path = args.output or os.path.join(out_dir, base + suffix + '.csv')
    save_csv(results, csv_path)
    print(f"\nCSV salvato in: {csv_path}")

    if not args.no_plot:
        png_path = os.path.join(out_dir, base + suffix + '.png')
        plot_results(results, base, png_path, audio_data, sr)
        print(f"Grafico: {png_path}")
