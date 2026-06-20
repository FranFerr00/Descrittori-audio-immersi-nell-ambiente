# Fonti consultate — Spectral Crest Factor

## Articoli e paper scientifici

- **Peeters, G. (2004)**. "A Large Set of Audio Features for Sound Description (Similarity and Classification) in the CUIDADO Project." Technical Report, IRCAM, Parigi. — Sez. 9.1: definizione SCF per sotto-bande, formula, relazione con SFM.

- **Lerch, A. (2023)**. *An Introduction to Audio Content Analysis*. 2nd ed., Wiley-IEEE Press. — Sez. 3.5.9: definizione, implementazione MATLAB/Python, range, frame silenziosi.

- **Johnston, J.D. (1988)**. "Transform Coding of Audio Signals Using Perceptual Noise Criteria." *IEEE JSAC*, 6(2), 314–323. — Contesto della discriminazione tonale/noise.

- **Allamanche, E. et al. (2001)**. "Content-Based Identification of Audio Material Using MPEG-7 Low Level Description." *Proc. ISMIR*. https://www.researchgate.net/publication/3927293 — Uso di SFM e SCF per fingerprinting MPEG-7, confronto robustezza.

- **Mapelli, V. et al. (2003)**. "Scalable Robust Audio Fingerprinting Using MPEG-7 Content Description." https://www.researchgate.net/publication/4017332 — SFM e SCF come feature di fingerprint, risposta alla compressione.

- **Jiang, D.-N., Lu, L., Zhang, H.-J., Tao, J.-H. & Cai, L.-H. (2002)**. "Music Type Classification by Spectral Contrast Feature." *Proc. ICME*. — Spectral contrast come generalizzazione del crest factor.

- **Krimphoff, J., McAdams, S. & Winsberg, S. (1994)**. "Caractérisation du timbre des sons complexes." *Journal de Physique IV*, C5, 625–628. — Dimensioni percettive del timbro.

- **Bellettini, C. & Mazzini, G. (2006)**. "Audio Fingerprinting Based on Normalized Spectral Subband Moments." *IEEE Signal Processing Letters*. https://ieeexplore.ieee.org/document/1605240 — Confronto momenti spettrali vs SFM/SCF.

- **You, Y. (2013)**. "Music Identification System Using MPEG-7 Audio Signature Descriptors." *The Scientific World Journal*. https://onlinelibrary.wiley.com/doi/full/10.1155/2013/752464 — Sistema di identificazione musicale con MPEG-7, 24 sotto-bande.

- **Stables, R. et al. (2015)**. "An Evaluation of Audio Feature Extraction Toolboxes." *Proc. DAFx-15*. https://www.ntnu.edu/documents/1001201110/1266017954/DAFx-15_submission_43_v2.pdf — Confronto toolbox (Essentia, librosa, MIRtoolbox, Meyda, aubio, etc.).

- **Correya, A. et al. (2021)**. "Audio and Music Analysis on the Web using Essentia.js." *Transactions of ISMIR*, 4(1), 167–181. https://doi.org/10.5334/tismir.111 — Benchmark Essentia.js vs Meyda.

## Standard tecnici

- **ISO/IEC 15938-4:2002** — MPEG-7 Part 4: Audio. AudioSpectralFlatness (usato con SCF per fingerprinting).

- **IEC 61672-1** — Definizione del crest factor nel dominio del tempo per strumentazione acustica.

## Documentazione librerie software

- **Essentia** — `Crest` algorithm: https://essentia.upf.edu/reference/streaming_Crest.html — Music extractor (barkbands_crest, melbands_crest, erbbands_crest): https://essentia.upf.edu/streaming_extractor_music.html

- **MATLAB Audio Toolbox** — `spectralCrest`: https://www.mathworks.com/help/signal/ref/spectralcrest.html — Spectral Descriptors overview: https://www.mathworks.com/help/audio/ug/spectral-descriptors.html

- **librosa** — `spectral_contrast` (correlato ma diverso): https://librosa.org/doc/main/generated/librosa.feature.spectral_contrast.html — Sorgente spectral.py: https://github.com/librosa/librosa/blob/main/librosa/feature/spectral.py — Nota: librosa non ha `spectral_crest` nativo.

- **FluCoMa** — SpectralShape (include crest): https://learn.flucoma.org/reference/spectralshape/

- **Two!Ears Auditory Model** — Spectral features (crest): http://docs.twoears.eu/en/latest/afe/available-processors/spectral-features/

- **Meyda** — Audio features: https://meyda.js.org/audio-features.html — Nota: non implementa spectral crest.

## Enciclopedie e risorse web

- **Wikipedia** — Crest factor (dominio del tempo): https://en.wikipedia.org/wiki/Crest_factor

- **ScienceDirect Topics** — Spectral Flatness (include SCF): https://www.sciencedirect.com/topics/computer-science/spectral-flatness — Spectral Centroid (include SCF): https://www.sciencedirect.com/topics/engineering/spectral-centroid

- **iZotope** — "What Is Crest Factor and Why Is It Important?" (dominio del tempo, mastering): https://www.izotope.com/en/learn/what-is-crest-factor

- **PySoundConcat** — Audio Descriptor Definitions (SCF): http://pezz89.github.io/PySoundConcat/descriptor_defs.html

## Knowledge del progetto

- `dispensa-descrittori.tex` / `dispensadescrittori.pdf` — Sez. 3.2: formula, valori tipici, osservazioni dai test.
- `diario.md` — Test con segnali Csound, confronto finestratura/overlap.
- `tabella-segnali.md` / `tabella-segnali-10khz.md` — Valori per tutti i segnali di test.
- Lerch (2023), cap. 3 — nel PDF del progetto.
- Peeters (2004) — nel PDF del progetto.
