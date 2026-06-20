import numpy as np
from scipy.signal import find_peaks
import soundfile as sf
import csv
import sys
import os
import matplotlib.pyplot as plt

# --- Parametri ---

FFT_SIZE = 8192
HOP_SIZE = 4096  # 50% overlap
WINDOW = 'hann'  # 'rectangular' o 'hann'
THRESHOLD_DB = -60  # soglia relativa al picco del frame (in dB)
GATE_DBFS = None  # gate assoluto sul picco raw del frame (None = nessun gate)
EPSILON = 1e-19
LOG_EPSILON = 1e-7  # protezione log in arraylog.c
MAX_FREQ = None  # limite frequenza in Hz (None = Nyquist)

# bande log-ottava per OBSI/OBSIR (Essid, Richard, David 2006, IEEE TASLP)
# edges in Hz; 6 bande coprono 200 Hz - 10 kHz.
OBSI_EDGES = [200.0, 400.0, 800.0, 1600.0, 3200.0, 6400.0, 10000.0]


def load_audio(path, channel=None):
    data, sr = sf.read(path, dtype='float64')
    if data.ndim > 1:
        if channel is None:
            data = np.mean(data, axis=1)
        else:
            data = data[:, channel]
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
    # soglia relativa: tieni solo bin entro threshold_db dal picco
    threshold = peak * 10 ** (threshold_db / 20.0)
    mag_th = np.where(mag > threshold, mag, 0.0)
    return mag, mag_th


# === FORMA DELLO SPETTRO ===

def spectral_centroid(mag_th, freqs):
    total = np.sum(mag_th)
    if total == 0:
        return 0.0
    return np.sum(freqs * mag_th) / total


def spectral_spread(mag_th, freqs, centroid):
    total = np.sum(mag_th)
    if total == 0:
        return 0.0
    return np.sqrt(np.sum((freqs - centroid) ** 2 * mag_th) / total)


def spectral_rolloff(mag_th, freqs, percentile=0.85):
    total = np.sum(mag_th)
    if total == 0:
        return 0.0
    cumsum = np.cumsum(mag_th)
    idx = np.searchsorted(cumsum, percentile * total)
    if idx >= len(freqs):
        idx = len(freqs) - 1
    return freqs[idx]


def spectral_slope(mag_th, f_oct_all, freq_pos):
    # Regressione dB/ottava: asse X = log2(Hz), asse Y = dB magnitudine.
    # Risolve il problema di scala della formula lineare (Lerch/Peeters):
    # i valori in ampl/Hz risultano ~1e-8 perche' il denominatore Hz^2
    # e' signal-independent. Con log2(Hz) e dB il range utile e' ~-20..+5.
    # Fonte: openSMILE/GeMAPS, Kazazis et al. 2022.
    #
    # f_oct_all: log2(freqs) precalcolato per le bin con freqs > 0
    #            (costante per tutti i frame, lunghezza = freq_pos.sum())
    # freq_pos : maschera booleana freqs > 0 (costante)
    mask_sig = mag_th[freq_pos] > 0
    if np.sum(mask_sig) < 2:
        return 0.0
    f_oct  = f_oct_all[mask_sig]
    s_db   = 20.0 * np.log10(mag_th[freq_pos][mask_sig] + EPSILON)
    f_mean = np.mean(f_oct)
    f_c    = f_oct - f_mean
    den    = np.sum(f_c ** 2)
    if den == 0:
        return 0.0
    s_mean = np.mean(s_db)
    num    = np.sum(f_c * (s_db - s_mean))
    return num / den


def spectral_obsir_std(mag, freqs, edges=OBSI_EDGES):
    # OBSIR: log-energy difference tra bande ottavali consecutive
    # (Essid, Richard, David 2006). La std delle OBSIR misura quanto
    # il decadimento spettrale non e' uniforme tra ottave, ed e'
    # ortogonale allo slope globale (slope = pendenza media, OBSIR-std
    # = irregolarita' della pendenza per banda).
    #
    # Nota: usa la magnitudine piena (non mag_th) per evitare che la
    # soglia relativa azzeri intere bande e produca log-energie -inf,
    # come discusso in compass_artifact decrease (la soglia distrugge
    # il gradiente su cui il decrease si basava).
    power = mag ** 2
    log_E = np.empty(len(edges) - 1)
    for i in range(len(edges) - 1):
        band = power[(freqs >= edges[i]) & (freqs < edges[i + 1])]
        log_E[i] = np.log10(np.sum(band) + EPSILON)
    if len(log_E) < 2:
        return 0.0
    obsir = np.diff(log_E)
    return float(np.std(obsir))


# === DISTRIBUZIONE ===

def spectral_flatness(mag_th, epsilon):
    # calcola solo sulle bin attive (sopra soglia)
    active = mag_th[mag_th > 0]
    if len(active) == 0:
        return 0.0
    safe = active + epsilon
    log_mean = np.mean(np.log(safe))
    arith_mean = np.mean(active)
    if arith_mean == 0:
        return 0.0
    return np.exp(log_mean) / arith_mean


def spectral_crest(mag_th):
    active = mag_th[mag_th > 0]
    if len(active) == 0:
        return 0.0
    return np.max(active) / np.mean(active)


def spectral_skewness(mag_th, freqs, centroid, spread):
    if spread == 0 or np.sum(mag_th) == 0:
        return 0.0
    total = np.sum(mag_th)
    return np.sum(((freqs - centroid) / spread) ** 3 * mag_th) / total


def spectral_kurtosis(mag_th, freqs, centroid, spread):
    if spread == 0 or np.sum(mag_th) == 0:
        return 0.0
    total = np.sum(mag_th)
    return np.sum(((freqs - centroid) / spread) ** 4 * mag_th) / total - 3.0


def tonality_coefficient(flatness):
    # Peeters 9.1: SFM in dB, poi min(SFM_dB / -60, 1)
    if flatness <= 0:
        return 1.0
    sfm_db = 10.0 * np.log10(flatness + 1e-19)
    return min(sfm_db / -60.0, 1.0)


def spectral_entropy(mag_th):
    # Shannon entropy di p(k) = |X(k)|^2 / sum|X|^2, normalizzata in [0,1]
    # dividendo per log2(N_totale). Shen et al. 1998, Misra et al. 2004.
    # Segnali con poche bin attive (sinusoide) hanno entropy bassa,
    # segnali con tutte le bin uniformi (noise) hanno entropy ~1.
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


# === TONALITA' ===

def tonal_power_ratio(mag, lobe_width=1):
    power = mag ** 2
    total_power = np.sum(power)
    if total_power == 0:
        return 0.0, 0

    # massimi locali con distanza minima 3 bin
    peaks, _ = find_peaks(power, distance=3)

    if len(peaks) == 0:
        return 0.0, 0

    # regola MPEG-1: un picco e' tonale solo se supera i vicini a ±2 bin
    # di almeno 7 dB in potenza (fattore ~5 in potenza lineare)
    ratio_threshold = 10 ** (7.0 / 10.0)
    epsilon = 1e-30

    tonal_peaks = []
    for pk in peaks:
        p = power[pk]
        left_ok  = (pk < 2)              or (p / (power[pk - 2] + epsilon) >= ratio_threshold)
        right_ok = (pk >= len(power) - 2) or (p / (power[pk + 2] + epsilon) >= ratio_threshold)
        if left_ok and right_ok:
            tonal_peaks.append(pk)

    n_peaks = len(tonal_peaks)
    if n_peaks == 0:
        return 0.0, 0

    # somma energia del lobo ±1 bin per ogni picco tonale
    tonal_power = 0.0
    for pk in tonal_peaks:
        lo = max(0, pk - lobe_width)
        hi = min(len(power), pk + lobe_width + 1)
        tonal_power += np.sum(power[lo:hi])

    # fix 3: rapporto tonal/noise in dB invece di tonal/total lineare.
    # tonal/noise = tonal_power / (total_power - tonal_power)
    # range tipico: -20 dB (tutto noise) ... +25 dB (tutto tonale)
    noise_power = max(total_power - tonal_power, epsilon)
    tpr = 10.0 * np.log10(tonal_power / noise_power)
    return tpr, n_peaks


# === DINAMICA ===

def spectral_flux(mag_th, mag_th_prev):
    diff = np.abs(mag_th - mag_th_prev)
    return np.sum(diff)


def spectral_irregularity(mag_th, log_epsilon):
    # come in irregularity.pd: abs(log(S[k]) - log(S[k+1]))
    safe = np.where(mag_th > 0, mag_th, log_epsilon)
    log_mag = np.log(safe)
    return np.sum(np.abs(np.diff(log_mag)))


def zero_crossing_rate(frame):
    signs = np.sign(frame)
    # conta i cambi di segno
    crossings = np.sum(np.abs(np.diff(signs)) > 0)
    return crossings / (len(frame) - 1) if len(frame) > 1 else 0.0


# === ANALISI ===

def _expand_deps(only):
    """Aggiunge le dipendenze necessarie ai descrittori richiesti."""
    need = set(only)
    if 'spread'   in need: need.add('centroid')
    if 'skewness' in need: need |= {'centroid', 'spread'}
    if 'kurtosis' in need: need |= {'centroid', 'spread'}
    if 'tonality' in need: need.add('flatness')
    return need


def analyze(path, fft_size=FFT_SIZE, hop_size=HOP_SIZE,
            window=WINDOW, threshold_db=THRESHOLD_DB, epsilon=EPSILON,
            max_freq=MAX_FREQ, flux_lag=1, gate_dbfs=GATE_DBFS,
            gate_rel_db=None, only=None, channel=None):
    data, sr = load_audio(path, channel=channel)
    if hop_size is None:
        hop_size = fft_size

    win = make_window(fft_size, window)
    n_frames = (len(data) - fft_size) // hop_size + 1
    freqs = np.fft.rfftfreq(fft_size, d=1.0 / sr)

    # limite di frequenza: taglia i vettori
    if max_freq is not None:
        max_bin = int(max_freq / (sr / fft_size)) + 1
        max_bin = min(max_bin, len(freqs))
    else:
        max_bin = len(freqs)

    freqs = freqs[:max_bin]

    # precalcolo per spectral_slope: log2(freqs) e' costante per tutti i frame
    _freq_pos  = freqs > 0
    _f_oct_all = np.log2(freqs[_freq_pos])

    # set di descrittori da calcolare (None = tutti)
    need = _expand_deps(only) if only else None

    def want(d):
        return need is None or d in need

    results = []
    mag_th_history = []

    # gate assoluto: calcola la soglia in ampiezza lineare (None = disattivato)
    gate_lin = 10 ** (gate_dbfs / 20.0) if gate_dbfs is not None else None

    # gate relativo: soglia in ampiezza lineare riferita al peak globale del file
    if gate_rel_db is not None:
        file_peak = np.max(np.abs(data))
        gate_rel_lin = file_peak * 10 ** (gate_rel_db / 20.0)
    else:
        gate_rel_lin = None

    for i in range(n_frames):
        start = i * hop_size
        raw_frame = data[start:start + fft_size]

        # gate sul peak del frame raw (prima della finestratura)
        gated = False
        if gate_lin is not None or gate_rel_lin is not None:
            raw_peak = np.max(np.abs(raw_frame))
            if gate_lin is not None and raw_peak < gate_lin:
                gated = True
            if gate_rel_lin is not None and raw_peak < gate_rel_lin:
                gated = True

        if gated:
            time_s = start / sr
            results.append({
                'frame': i,
                'time': round(time_s, 4),
                'centroid': 0.0, 'spread': 0.0, 'rolloff': 0.0,
                'slope': 0.0, 'obsir_std': 0.0,
                'flatness': 0.0, 'crest': 0.0,
                'skewness': 0.0, 'kurtosis': 0.0, 'tonality': 0.0,
                'entropy': 0.0,
                'tpr': 0.0, 'n_peaks': 0,
                'flux': 0.0, 'irregularity': 0.0, 'zcr': 0.0,
                'gated': 1,
            })
            # niente storia flux per i frame gated: il prossimo frame valido
            # confrontera' col precedente frame valido
            continue

        frame = raw_frame * win

        mag, mag_th = compute_spectrum(frame, fft_size, threshold_db)
        mag = mag[:max_bin]
        mag_th = mag_th[:max_bin]

        # forma dello spettro
        centroid = spectral_centroid(mag_th, freqs)       if want('centroid')   else 0.0
        spread   = spectral_spread(mag_th, freqs, centroid) if want('spread')   else 0.0
        rolloff  = spectral_rolloff(mag_th, freqs)         if want('rolloff')   else 0.0
        slope     = spectral_slope(mag_th, _f_oct_all, _freq_pos) if want('slope')     else 0.0
        obsir_std = spectral_obsir_std(mag, freqs)                if want('obsir_std') else 0.0

        # distribuzione
        flatness = spectral_flatness(mag_th, epsilon)              if want('flatness')  else 0.0
        crest    = spectral_crest(mag_th)                          if want('crest')     else 0.0
        skewness = spectral_skewness(mag_th, freqs, centroid, spread) if want('skewness') else 0.0
        kurtosis = spectral_kurtosis(mag_th, freqs, centroid, spread) if want('kurtosis') else 0.0
        tonality = tonality_coefficient(flatness)                  if want('tonality')  else 0.0
        entropy  = spectral_entropy(mag_th)                        if want('entropy')   else 0.0

        # tonalita'
        tpr, n_peaks = tonal_power_ratio(mag) if (want('tpr') or want('n_peaks')) else (0.0, 0)

        # dinamica
        irregularity = spectral_irregularity(mag_th, LOG_EPSILON) if want('irregularity') else 0.0
        zcr          = zero_crossing_rate(raw_frame)               if want('zcr')          else 0.0

        if want('flux') and len(mag_th_history) >= flux_lag:
            flux = spectral_flux(mag_th, mag_th_history[-flux_lag])
        else:
            flux = 0.0

        if want('flux'):
            mag_th_history.append(mag_th.copy())

        time_s = start / sr

        results.append({
            'frame': i,
            'time': round(time_s, 4),
            # forma
            'centroid': round(centroid, 2),
            'spread': round(spread, 4),
            'rolloff': round(rolloff, 2),
            'slope': round(slope, 10),
            'obsir_std': round(obsir_std, 6),
            # distribuzione
            'flatness': round(flatness, 6),
            'crest': round(crest, 4),
            'skewness': round(skewness, 4),
            'kurtosis': round(kurtosis, 4),
            'tonality': round(tonality, 6),
            'entropy': round(entropy, 6),
            # tonalita'
            'tpr': round(tpr, 6),
            'n_peaks': n_peaks,
            # dinamica
            'flux': round(flux, 6),
            'irregularity': round(irregularity, 4),
            'zcr': round(zcr, 6),
            'gated': 0,
        })

    return results, sr


def save_csv(results, output_path, only=None):
    if not results:
        return
    if only:
        keep = {'frame', 'time', 'gated'} | set(only)
        rows = [{k: v for k, v in r.items() if k in keep} for r in results]
    else:
        rows = results
    keys = rows[0].keys()
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(results, only=None):
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
    all_keys = ['centroid', 'spread', 'rolloff', 'slope', 'obsir_std',
                'flatness', 'crest', 'skewness', 'kurtosis', 'entropy',
                'tpr', 'n_peaks', 'tonality',
                'flux', 'irregularity', 'zcr']
    keys = [k for k in all_keys if only is None or k in only]
    print(f"\n{'Descrittore':<16} {'Min':>10} {'Max':>10} {'Media':>10} {'Std':>10}")
    print("-" * 58)
    for k in keys:
        vals = [r[k] for r in valid]
        print(f"{k:<16} {min(vals):>10.4f} {max(vals):>10.4f} "
              f"{np.mean(vals):>10.4f} {np.std(vals):>10.4f}")
    if n_gated > 0:
        print(f"\nFrame totali: {n_total} (validi: {n_valid}, gated: {n_gated})")
    else:
        print(f"\nFrame totali: {n_total}")


# lista canonica dei descrittori, nell'ordine di stampa
_DESC_ORDER = ['centroid', 'spread', 'rolloff', 'slope', 'obsir_std',
               'flatness', 'crest', 'skewness', 'kurtosis', 'entropy',
               'tpr', 'n_peaks', 'tonality',
               'flux', 'irregularity', 'zcr']


def descriptor_means(results, only=None):
    """media e std (popolazione) di ogni descrittore sui frame non-gated.

    Ritorna {descrittore: (media, std)}; {} se non ci sono frame validi.
    """
    valid = [r for r in results if not r.get('gated', 0)]
    if not valid:
        return {}
    keys = [k for k in _DESC_ORDER if only is None or k in only]
    out = {}
    for k in keys:
        vals = [r[k] for r in valid]
        out[k] = (float(np.mean(vals)), float(np.std(vals)))
    return out


def _path_con_canale(path, ch):
    """inserisce _ch{ch} prima dell'estensione (o in coda se assente)."""
    root, ext = os.path.splitext(path)
    return f'{root}_ch{ch}{ext}'


def _stampa_riepilogo_canali(riepilogo, only):
    """tabella a video: per ogni descrittore, media e std per canale."""
    if not riepilogo:
        return
    descr = [k for k in _DESC_ORDER if only is None or k in only]
    for k in descr:
        print(f"\n=== Riepilogo medie per canale: {k} ===")
        print(f"{'Canale':<8} {'Media':>12} {'Std':>12}")
        print("-" * 34)
        for ch in sorted(riepilogo):
            stats = riepilogo[ch].get(k)
            if stats is None:
                print(f"ch{ch:<6} {'(nessun frame valido)':>25}")
            else:
                media, std = stats
                print(f"ch{ch:<6} {media:>12.4f} {std:>12.4f}")


# === GRAFICI PER CATEGORIA ===

def _plot_header(axes, idx, audio_data, sr):
    """Disegna forma d'onda e spettrogramma nei primi due pannelli."""
    if audio_data is None:
        return idx

    # forma d'onda
    ax = axes[idx]
    t_audio = np.arange(len(audio_data)) / sr
    ax.plot(t_audio, audio_data, linewidth=0.3, color='gray')
    ax.set_ylabel('Ampiezza')
    ax.set_ylim(-1, 1)
    ax.grid(True, alpha=0.3)
    ax.set_title('Forma d\'onda', fontsize=9, loc='left')
    idx += 1

    # spettrogramma
    ax = axes[idx]
    n_fft = FFT_SIZE
    hop = HOP_SIZE if HOP_SIZE else FFT_SIZE
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

    return idx


def _plot_category(results, title, output_path, descriptors, audio_data=None, sr=None):
    """Genera un PNG con forma d'onda, spettrogramma e i descrittori indicati."""
    if not results:
        return
    time = [r['time'] for r in results]
    n_desc = len(descriptors)
    n_panels = n_desc + (2 if audio_data is not None else 0)

    fig, axes = plt.subplots(n_panels, 1, figsize=(14, n_panels * 2.2), sharex=True)
    if n_panels == 1:
        axes = [axes]
    fig.suptitle(title, fontsize=13)

    idx = _plot_header(axes, 0, audio_data, sr)

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f']

    for j, (key, label) in enumerate(descriptors):
        ax = axes[idx]
        color = colors[j % len(colors)]
        ax.plot(time, [r[key] for r in results], label=label, linewidth=0.7, color=color)
        ax.set_ylabel(label)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
        if idx == n_panels - 1:
            ax.set_xlabel('Tempo (s)')
        idx += 1

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_all_categories(results, base_name, out_dir, audio_data=None, sr=None, suffix='',
                        only=None):
    """Genera PNG per categoria di descrittori.

    Se `only` e' specificato, genera un unico PNG con solo i descrittori richiesti
    invece dei 4 PNG per categoria.
    """
    all_categories = {
        'forma': [
            ('centroid', 'Centroid (Hz)'),
            ('spread', 'Spread (Hz)'),
            ('rolloff', 'Rolloff (Hz)'),
            ('slope', 'Slope'),
            ('obsir_std', 'OBSIR std'),
        ],
        'distribuzione': [
            ('flatness', 'Flatness'),
            ('crest', 'Crest Factor'),
            ('skewness', 'Skewness'),
            ('kurtosis', 'Kurtosis'),
            ('entropy', 'Entropy'),
        ],
        'tonalita': [
            ('tpr', 'TPR'),
            ('n_peaks', 'N. Picchi'),
            ('tonality', 'Tonality'),
        ],
        'dinamica': [
            ('flux', 'Flux'),
            ('irregularity', 'Irregularity'),
            ('zcr', 'ZCR'),
        ],
    }

    if only:
        # unico PNG con i soli descrittori richiesti
        descriptors = [(k, l) for cat in all_categories.values()
                       for k, l in cat if k in only]
        if descriptors:
            png_path = os.path.join(out_dir, f'{base_name}{suffix}_only.png')
            _plot_category(results, base_name, png_path, descriptors, audio_data, sr)
            print(f"Grafico: {png_path}")
        return

    for cat_name, descriptors in all_categories.items():
        title = f'{base_name} — {cat_name}'
        png_path = os.path.join(out_dir, f'{base_name}{suffix}_{cat_name}.png')
        _plot_category(results, title, png_path, descriptors, audio_data, sr)
        print(f"Grafico {cat_name}: {png_path}")


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description='Analisi descrittori audio')
    parser.add_argument('file', help='File WAV da analizzare')
    parser.add_argument('-o', '--output', help='File CSV di output')
    parser.add_argument('-w', '--window', default=WINDOW,
                        choices=['rectangular', 'hann'],
                        help='Tipo di finestra (default: rectangular)')
    parser.add_argument('--hop', type=int, default=None,
                        help='Hop size in campioni (default: fft_size, no overlap)')
    parser.add_argument('--overlap', type=float, default=None,
                        help='Overlap come frazione 0-1 (es. 0.5 = 50%%). Alternativa a --hop')
    parser.add_argument('--max-freq', type=float, default=None,
                        help='Frequenza massima in Hz (default: Nyquist)')
    parser.add_argument('--flux-lag', type=int, default=1,
                        help='Distanza in frame per il calcolo del flux (default: 1 = consecutivi)')
    parser.add_argument('--gate-dbfs', type=float, default=None,
                        help='Gate assoluto sul peak raw del frame in dBFS '
                             '(es. -50). I frame sotto soglia non vengono '
                             'analizzati e non entrano nelle medie. '
                             'Default: nessun gate.')
    parser.add_argument('--gate-rel-db', type=float, default=None,
                        help='Gate relativo sul peak raw del frame, riferito '
                             'al peak globale del file in dB (es. -40). '
                             'Auto-calibrato sul livello di registrazione. '
                             'Default: nessun gate. Combinabile con --gate-dbfs.')
    parser.add_argument('--output-dir', default=None,
                        help='Cartella di output per CSV e PNG (default: cartella dello script)')
    parser.add_argument('--only', default=None,
                        help='Descrittori da includere nell\'output, separati da virgola '
                             '(es. tpr,n_peaks). Gli altri vengono calcolati ma non scritti. '
                             'Se omesso, vengono scritti tutti i 16 descrittori.')
    parser.add_argument('--no-plot', action='store_true',
                        help='Salta la generazione dei PNG per-sample (forma, '
                             'distribuzione, tonalita, dinamica). Il CSV viene '
                             'comunque salvato.')
    parser.add_argument('--per-canale', action='store_true',
                        help='Analizza ogni canale separatamente invece di '
                             'mediarli in mono. Produce un CSV/PNG per canale '
                             'col suffisso _chN e una tabella riassuntiva delle '
                             'medie. Su file mono procede normale con un avviso.')

    args = parser.parse_args(argv)

    audio_path = args.file
    csv_path = args.output
    win_type = args.window

    # calcola hop da overlap se specificato
    if args.overlap is not None:
        hop = int(FFT_SIZE * (1 - args.overlap))
    elif args.hop is not None:
        hop = args.hop
    else:
        hop = HOP_SIZE  # default dalle costanti

    max_freq = args.max_freq
    flux_lag = args.flux_lag

    # suffisso per i nomi dei file di output
    hop_actual = hop if hop else FFT_SIZE
    overlap_pct = round((1 - hop_actual / FFT_SIZE) * 100)
    freq_suffix = f'_{int(max_freq)}hz' if max_freq else ''
    lag_suffix = f'_lag{flux_lag}' if flux_lag > 1 else ''
    suffix = f'_{win_type}_ov{overlap_pct}{freq_suffix}{lag_suffix}'

    freq_str = f', Max freq: {int(max_freq)} Hz' if max_freq else ''
    lag_str = f', Flux lag: {flux_lag} frame ({flux_lag * hop_actual / 96000 * 1000:.0f} ms)' if flux_lag > 1 else ''
    print(f"Analisi di: {audio_path}")
    print(f"FFT: {FFT_SIZE}, Hop: {hop_actual}, Finestra: {win_type}, Overlap: {overlap_pct}%{freq_str}{lag_str}")

    only = [d.strip() for d in args.only.split(',')] if args.only else None

    if args.per_canale:
        n_ch = sf.info(audio_path).channels
        if n_ch > 1:
            base = os.path.splitext(os.path.basename(audio_path))[0]
            if args.output_dir:
                out_dir = args.output_dir
            elif csv_path:
                # tieni i PNG accanto ai CSV richiesti con -o
                out_dir = os.path.dirname(os.path.abspath(csv_path))
            else:
                out_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.makedirs(out_dir, exist_ok=True)

            riepilogo = {}   # ch (1-based) -> {desc: (media, std)}
            for ch in range(n_ch):
                etich = ch + 1
                print(f"\n=== Canale {etich} ===")
                res, sr = analyze(audio_path, fft_size=FFT_SIZE, hop_size=hop,
                                  window=win_type, max_freq=max_freq,
                                  flux_lag=flux_lag, gate_dbfs=args.gate_dbfs,
                                  gate_rel_db=args.gate_rel_db, only=only,
                                  channel=ch)
                print(f"SR: {sr}")
                print_summary(res, only)
                riepilogo[etich] = descriptor_means(res, only)

                if csv_path:
                    out_csv = _path_con_canale(csv_path, etich)
                else:
                    out_csv = os.path.join(out_dir,
                                           f'{base}_ch{etich}{suffix}_analisi.csv')
                save_csv(res, out_csv, only)
                print(f"CSV salvato in: {out_csv}")

                if not args.no_plot:
                    canale_data, _ = load_audio(audio_path, channel=ch)
                    plot_all_categories(res, f'{base}_ch{etich}', out_dir,
                                        canale_data, sr, suffix, only)

            _stampa_riepilogo_canali(riepilogo, only)
            return

        print("Avviso: file mono (1 canale), procedo normale.")

    # carica audio per forma d'onda e spettrogramma
    audio_data, sr = load_audio(audio_path)

    results, sr = analyze(audio_path, fft_size=FFT_SIZE, hop_size=hop,
                          window=win_type, max_freq=max_freq,
                          flux_lag=flux_lag, gate_dbfs=args.gate_dbfs,
                          gate_rel_db=args.gate_rel_db, only=only)
    print(f"SR: {sr}")

    print_summary(results, only)

    base = os.path.splitext(os.path.basename(audio_path))[0]

    if args.output_dir:
        out_dir = args.output_dir
    elif only:
        # lo script sta in scripts/, la radice del repo e' un livello sopra
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        audio_dir = os.path.dirname(os.path.abspath(audio_path))
        parent = os.path.basename(audio_dir)
        if parent == 'samples':
            parent = os.path.basename(os.path.dirname(audio_dir))
        out_dir = os.path.join(root_dir, 'desc', '_'.join(only), parent, base)
        os.makedirs(out_dir, exist_ok=True)
    else:
        out_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if csv_path:
        save_csv(results, csv_path, only)
        print(f"\nCSV salvato in: {csv_path}")
    else:
        csv_path = os.path.join(out_dir, base + suffix + '_analisi.csv')
        save_csv(results, csv_path, only)
        print(f"\nCSV salvato in: {csv_path}")

    if not args.no_plot:
        plot_all_categories(results, base, out_dir, audio_data, sr, suffix, only)


if __name__ == '__main__':
    main()
