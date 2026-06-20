# Why spectral slope fails and how to fix it

**The tiny, undiscriminating values you observe are not a bug — they are a mathematical inevitability of computing linear regression with Hz-scale frequencies as the x-axis.** When bin frequencies reach 10,000+ Hz, the denominator Σ[(f(k) − f̄)²] explodes to ~10⁸–10¹⁰, while the numerator (cross-products of large frequency deviations with small magnitude deviations) remains comparatively tiny. The result: slopes on the order of **10⁻⁷ to 10⁻⁸** regardless of signal content. This is a known, well-documented limitation that openSMILE explicitly flagged with a legacy "incorrectly scaled" mode (`oldSlopeScale`). The fix requires changing what you regress against, what you regress, or both.

## The denominator problem is pure arithmetic

The standard formula you implemented is correct per Lerch (2023) and Peeters (2004):

```
slope = Σ[(f(k) - f̄) · (X(k) - X̄)] / Σ[(f(k) - f̄)²]
```

The problem is dimensional. For a signal sampled at 44.1 kHz with a 4096-point FFT, the positive-frequency bins span 0 to ~22,050 Hz in ~2,048 steps. The mean frequency f̄ ≈ 11,025 Hz. Each term (f(k) − f̄)² can reach ~1.2 × 10⁸ Hz², and summing across all bins yields a denominator of roughly **2 × 10¹⁰ Hz²**. Meanwhile, linear magnitude values from an FFT typically range from 0 to perhaps 100 (unnormalized) or 0 to 1 (normalized), with mean deviations (X(k) − X̄) on the order of 0.01–0.1. The numerator sums cross-products of ~±5,000 Hz × ~±0.05 magnitude ≈ ±250, accumulated across ~2,000 bins to perhaps 10³–10⁴. Dividing 10⁴ by 10¹⁰ gives **10⁻⁶ to 10⁻⁸** — exactly what you observe.

Critically, the denominator is **signal-independent** (it depends only on FFT size and sample rate), so the only signal-dependent variation comes from the numerator's covariance term. But since most natural signals share a broadly similar spectral shape (energy concentrated in lower frequencies, decaying toward higher ones), the numerator varies little across different signals. This makes the raw spectral slope nearly useless for discrimination.

Your additional threshold that removes low-energy bins actually worsens the problem. By eliminating bins, you reduce the numerator's potential variation while the remaining bins still have large frequency spreads. The threshold homogenizes the spectrum before slope computation.

## How pyACA and other libraries implement it

**pyACA** (Lerch's reference implementation) follows the textbook literally. Based on confirmed code patterns from adjacent files in the repository (FeatureSpectralSkewness.py, FeatureSpectralKurtosis.py, FeatureSpectralRolloff.py — all successfully retrieved), the implementation uses Hz frequencies via `f = np.arange(0, X.shape[0]) / (X.shape[0] - 1) * f_s / 2` as the x-axis and raw linear magnitude `np.abs(fft)` as the y-axis. **No normalization is applied** beyond the centering inherent in the regression formula. The output unit is effectively "magnitude change per Hz" — an inherently tiny number. MATLAB's `spectralSlope()` function, which explicitly references Lerch (2012), confirms identical behavior and documents the output unit as "1/Hz."

The other major libraries diverge significantly in their approaches:

- **Meyda.js** and **YAAFE** both implement the standard OLS regression formula on linear amplitude spectra, essentially matching pyACA. Meyda's documentation claims output range "0.0–1.0," which appears nominal and likely incorrect for most real signals. Both cite Peeters (2004) as their reference.

- **librosa** has no dedicated spectral slope function at all. The closest equivalent is `poly_features(order=1)`, which fits a first-order polynomial via `numpy.polyfit` and returns the linear coefficient. The x-axis can be either bin indices or a custom frequency array, which at least gives the user control over scaling.

- **Essentia** also lacks a "SpectralSlope" algorithm. Its `Decrease` algorithm computes an OLS regression coefficient but includes a `range` parameter (defaulting to 1.0) that should be set to Nyquist frequency for spectral applications — a form of normalization.

- **openSMILE** is the most sophisticated and the most revealing. Its `cSpectral` component includes a configuration flag called `oldSlopeScale` (default: 1.0, enabled for backward compatibility) documented as enabling "*(incorrectly) scaled spectral slope computation (pre July 2013).*" The documentation explicitly warns: **"Disable in new designs!"** This confirms that the openSMILE developers discovered and fixed a scaling issue identical to yours. The corrected version (`oldSlopeScale = 0`) applies proper normalization.

## openSMILE's GeMAPS shows the right approach

The **Geneva Minimalistic Acoustic Parameter Set (GeMAPS)**, the de facto standard for speech emotion recognition, uses openSMILE's spectral slope in a fundamentally different way from the raw Lerch/Peeters formula. Its configuration reveals three critical modifications:

1. **Log power spectrum** (`squareInput = 1`, `useLogSpectrum = 1`): Input magnitudes are squared to power, then log-transformed. This converts the y-axis from linear magnitude to dB-like values, dramatically expanding the dynamic range of the regression.

2. **Sub-band computation** (`slopes[0] = 0-500`, `slopes[1] = 500-1500`): Instead of one slope across the entire spectrum, GeMAPS computes separate slopes for the **0–500 Hz** and **500–1500 Hz** bands. This drastically shrinks the denominator (frequency range of 500 or 1000 Hz instead of 22,000 Hz) and captures perceptually relevant differences in spectral tilt.

3. **Limited frequency range** (`freqRange = 0-5000`): Even the overall analysis is restricted to 0–5 kHz, avoiding the noise-dominated high frequencies that dilute discrimination.

4. **Corrected scaling** (`oldSlopeScale = 0`): Disables the legacy incorrect scaling.

The resulting feature names in GeMAPS output are `pcm_fftMag_logSpectralSlopeOfBand0-500` and `pcm_fftMag_logSpectralSlopeOfBand500-1500` — values with much better discrimination for voice quality, emotion, and affect recognition.

## Six normalization strategies ranked by effectiveness

Based on the literature and cross-implementation analysis, here are the available strategies for producing discriminating spectral slope values, ordered from simplest to most effective:

**Strategy 1 — Use bin indices instead of Hz.** Replace f(k) with k (0 to N−1). The denominator drops from ~10¹⁰ to ~N³/12 ≈ 7 × 10⁸ for N = 2048, a ~10× improvement. Simple but insufficient alone, since values remain small.

**Strategy 2 — Normalize frequency to [0, 1].** Divide all f(k) by Nyquist. The denominator becomes ~N/12 ≈ 170. This scales the output into a reasonable range and is the easiest fix. The slope now represents "magnitude change per normalized frequency unit."

**Strategy 3 — Use log-magnitude (dB).** Convert X(k) to 20·log₁₀(X(k)) before regression. Spectral amplitudes in dB typically span −60 to 0 dB, so magnitude deviations become ±10–30 dB instead of ±0.01–0.1. This amplifies the numerator by ~100–1000×.

**Strategy 4 — Use log-frequency axis.** Replace Hz with mel, Bark, ERB, or log₂(f) (octaves). Combined with dB magnitude, the slope becomes **dB/octave** — the most perceptually meaningful unit. Kazazis, Depalle, and McAdams (2022, *Frontiers in Psychology*) used dB/octave in their psychophysical scaling experiments on spectral slope perception, confirming this aligns with how humans actually hear spectral tilt. A typical voiced speech sound has a slope of roughly **−6 dB/octave** (modal voice), while breathy voice might reach −12 dB/octave and pressed voice may approach −3 dB/octave.

**Strategy 5 — Compute sub-band slopes.** Following the Kreiman et al. (2014, *JASA*) voice source model, compute slopes in perceptually motivated bands: 0–500 Hz, 500–1500 Hz, 1500–5000 Hz. Each sub-band has a small frequency range (small denominator) and captures distinct aspects of timbre. This is what GeMAPS/eGeMAPS standardizes.

**Strategy 6 — Combine strategies 3 + 4 + 5.** The optimal approach: compute linear regression of **dB magnitude vs. log₂(frequency)** within **sub-bands**. This yields slopes in dB/octave per band with values in the range of roughly **−20 to +5**, with clear discrimination between signal types.

## Spectral slope vs. decrease vs. tilt vs. rolloff

These four descriptors are often confused but measure fundamentally different things. **Spectral slope** is the OLS regression coefficient of magnitude (or power or log-power) against frequency — a single global linear fit. **Spectral decrease** (Peeters 2004) weights lower frequencies more heavily via a 1/(k−1) factor: `decrease = Σ_{k=2}^{K} (X(k) − X(1))/(k−1) / Σ_{k=2}^{K} X(k)`. This perceptual weighting makes it more discriminating for music and instrument timbres than raw slope. **Spectral rolloff** is not a slope at all but a threshold frequency — the frequency below which 85% (or 95%) of the total spectral energy lies. It captures brightness effectively but loses shape information. **Spectral tilt** in the speech science literature refers to something quite different from slope: it is typically measured as the amplitude ratio **H1−H2** (first harmonic vs. second harmonic, in dB) and related sub-band ratios (H2−H4, H4−2kHz, 2kHz−5kHz), or derived from the first LPC reflection coefficient.

For timbre discrimination specifically, the most effective approach depends on the domain. In speech, the **H1−H2 and sub-band spectral tilt** measures (Garellek 2020, Kreiman et al. 2014) are far more discriminating than any single global slope, since they capture voice quality differences (breathy, modal, pressed) with large, interpretable dB values. In music, **spectral decrease** outperforms raw slope for instrument recognition because the 1/(k−1) weighting better matches auditory frequency resolution. For general-purpose timbre analysis, **MFCC c₁** (the second mel-frequency cepstral coefficient, index 1) serves as an effective proxy for overall spectral tilt, with the advantage that it operates inherently on a perceptual frequency scale with log-magnitude compression.

## MPEG-7 AudioSpectrumSlope is not what you think

A common misconception is that "AudioSpectrumSlope" is a normative MPEG-7 descriptor. It is not. The **MPEG-7 standard (ISO/IEC 15938-4)** defines four basic spectral shape descriptors: AudioSpectrumEnvelope, AudioSpectrumCentroid, AudioSpectrumSpread, and AudioSpectrumFlatness. The "AudioSpectrumSlope" descriptor was defined by Peeters (2004) as part of the **CUIDADO project** extensions to MPEG-7, indicated by the prefix `cuidado:AudioSpectrumSlope` rather than `mpeg7:`. It uses the same global linear regression formula with no sub-band structure. The MPEG-7 normative descriptors that do use sub-band computation are AudioSpectrumEnvelope and AudioSpectrumFlatness, which divide the spectrum into logarithmic sub-bands (default 1/4 octave resolution from 62.5 Hz to 16 kHz) — an architecture that would have been better for slope computation but was not adopted for that purpose in the standard.

## Practical recommendations for your implementation

The most impactful single change is to **regress dB magnitude against log₂(frequency) in sub-bands**. Here is a concrete approach:

Convert magnitude to dB: `S_dB(k) = 20 · log₁₀(X(k) + ε)` where ε prevents log(0). Convert frequency to octaves: `f_oct(k) = log₂(f(k))`. Define 2–3 sub-bands (e.g., 100–500 Hz, 500–2000 Hz, 2000–8000 Hz). Within each band, perform OLS regression of S_dB vs. f_oct. The result is a vector of 2–3 values in dB/octave, typically ranging from **−15 to +5**, with clear differentiation: a sine wave will show near-zero slope within its band, white noise will be near 0 dB/octave across all bands, a distorted signal will show flatter slopes than a clean one, and a bandpass-filtered noise will show steep positive slope below center frequency and steep negative slope above it.

Alternatively, if you need a single scalar, the simplest effective fix is to normalize the frequency axis to [0, 1] and use log-magnitude: `slope = Σ[(f_norm(k) − f̄_norm) · (S_dB(k) − S̄_dB)] / Σ[(f_norm(k) − f̄_norm)²]`. This preserves the Lerch formula's structure but produces values in a usable range of roughly **−100 to +20**.

## Conclusion

The spectral slope's scaling problem is not an implementation error but a design limitation of regressing small magnitudes against large Hz values. The field has converged on two solutions: openSMILE/GeMAPS's **sub-band log-power slopes** for speech applications, and **dB/octave regression** for general audio analysis. The raw Lerch/Peeters formula, while mathematically correct, is pedagogical rather than practical — as pyACA's own documentation notes, the code "showcases algorithmic principles" and is "not entirely suitable for practical usage without parameter optimization." For a maximally discriminating spectral shape descriptor that avoids slope's pitfalls entirely, consider using MFCC c₁ as a tilt proxy or Peeters' spectral decrease formula, both of which produce well-scaled, signal-discriminating values without any normalization gymnastics.