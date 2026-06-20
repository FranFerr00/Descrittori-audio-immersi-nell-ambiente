# Fonti consultate — Spectral Flatness Measure

## Articoli e paper scientifici

- **Johnston, J.D. (1988)**. "Transform Coding of Audio Signals Using Perceptual Noise Criteria." *IEEE Journal on Selected Areas in Communications*, 6(2), 314–323. — Introduzione della SFM nella codifica percettiva e formula del coefficiente di tonalità α.

- **Dubnov, S. (2004)**. "Generalization of Spectral Flatness Measure for Non-Gaussian Linear Processes." *IEEE Signal Processing Letters*, 11(8), 698–701. http://dub.ucsd.edu/Papers/SPL.pdf — Equivalenza SFM / dual total correlation e generalizzazione GSFM.

- **Madhu, N. (2009)**. "Note on measures for spectral flatness." *Electronics Letters*, 45(23), 1195–1196. https://doi.org/10.1049/el.2009.1977 — Analisi critica della SFM classica, proposta della misura alternativa F₂ basata su entropia di Shannon.

- **Peeters, G. (2004)**. "A Large Set of Audio Features for Sound Description." IRCAM, Parigi. — Calcolo SFM per 4 bande (250–4000 Hz), Spectral Crest Factor, conversione in Tonality.

- **Lerch, A. (2023)**. *An Introduction to Audio Content Analysis*. 2nd ed., Wiley-IEEE Press. — Sez. 3.5.10: definizione, implementazione MATLAB/Python, problema bin a zero, smoothing, raccomandazione MPEG-7.

- **Park, T.H. (2004)**. *Towards Automatic Musical Instrument Timbre Recognition*. Ph.D. thesis, Princeton University. — Riferimento MPEG-7, base dell'implementazione nel progetto.

- **Krimphoff, J., McAdams, S. & Winsberg, S. (1994)**. "Caractérisation du timbre des sons complexes. II: Analyses acoustiques et quantification psychophysique." *Journal de Physique IV*, 4(C5), 625–628. — Dimensioni percettive del timbro, irregolarità spettrale.

- **Ma, Y. & Nishihara, A. (2013)**. "Efficient voice activity detection algorithm using long-term spectral flatness measure." *EURASIP Journal on Audio, Speech, and Music Processing*, 2013:21. https://asmp-eurasipjournals.springeropen.com/articles/10.1186/1687-4722-2013-21 — LSFM per VAD, confronto con G.729B/AMR.

- **Taghipour, A. et al. (2014)**. "A Psychoacoustic Model with Partial Spectral Flatness Measure for Tonality Estimation." *Proc. EUSIPCO 2014*. https://www.eurasip.org/Proceedings/Eusipco/Eusipco2014/HTML/papers/1569918015.pdf — PSFM con DFT adattive per basse/medie/alte frequenze.

- **Misra, H. et al. (2004)**. "Spectral Entropy as Speech Features for Speech Recognition." *Proc. Eurospeech*. — Entropia spettrale come misura di piattezza, equivalenza con Wiener entropy.

- **Izmirli, O. (2000)**. "Using a Spectral Flatness Based Feature for Audio Segmentation and Retrieval." *Proc. ISMIR 2000*. https://ismir2000.ismir.net/posters/izmirli.pdf — Segmentazione audio basata su SFM.

- **Scheirer, E. & Slaney, M. (1997)**. "Construction and Evaluation of a Robust Multifeature Speech/Music Discriminator." *Proc. ICASSP*. — Discriminazione parlato/musica con SFM.

- **Tchernichovski, O. et al. (2000)**. "A procedure for an automated measurement of song similarity." *Animal Behaviour*, 59(6), 1167–1176. — Wiener entropy nell'analisi del canto degli uccelli.

- **Gray, R.M. & Markel, J.D. (1974)**. — Introduzione originale della SFM nel contesto della predizione lineare.

## Standard tecnici

- **ISO/IEC 15938-4:2002** — MPEG-7 Part 4: Audio. Definizione di AudioSpectralFlatness (24 bande quarter-octave, 250 Hz – 16 kHz).

- **ITU-R BS.1387** — PEAQ (Perceptual Evaluation of Audio Quality). Modello psicoacustico con decomposizione in bande Bark.

- **IETF RFC 6716** — Definition of the Opus Audio Codec. https://www.rfc-editor.org/rfc/rfc6716 — Uso della flatness nel layer SILK per VAD/DTX.

- **US Patent 5,341,457 / EP 0424016A2** — Johnston/AT&T, "Perceptual coding of audio signals." Brevetto originale del modello psicoacustico con SFM.

- **Kabal, P. (2002)**. "An Examination and Interpretation of ITU-R BS.1387." McGill University. https://www.mmsp.ece.mcgill.ca/Documents/Reports/2002/KabalR2002v2.pdf — Analisi dettagliata dello standard PEAQ.

## Documentazione librerie software

- **librosa** — `spectral_flatness()`: https://librosa.org/doc/main/generated/librosa.feature.spectral_flatness.html — Sorgente: https://github.com/librosa/librosa/blob/main/librosa/feature/spectral.py

- **Essentia** — `Flatness` e `FlatnessDB`: http://essentia.upf.edu/documentation/reference/std_Flatness.html / https://essentia.upf.edu/reference/std_FlatnessDB.html

- **MATLAB Audio Toolbox** — `spectralFlatness`: https://www.mathworks.com/help/signal/ref/spectralflatness.html — Spectral Descriptors overview: https://www.mathworks.com/help/audio/ug/spectral-descriptors.html

- **Meyda** (JavaScript) — Audio features: https://meyda.js.org/audio-features.html — Sorgente: https://github.com/meyda/meyda/blob/main/docs/audio-features.md

- **aubio** — Spectral features: https://aubio.readthedocs.io/en/latest/py_spectral.html (nota: non implementa SFM come GM/AM)

- **OpenAE** — Spectral flatness: https://openae.io/standards/features/latest/spectral-flatness/

- **Two!Ears Auditory Model** — Spectral features: http://docs.twoears.eu/en/latest/afe/available-processors/spectral-features/

## Enciclopedie e risorse web

- **Wikipedia** — Spectral flatness: https://en.wikipedia.org/wiki/Spectral_flatness

- **HandWiki** — Spectral flatness: https://handwiki.org/wiki/Spectral_flatness

- **Grokipedia** — Spectral flatness: https://grokipedia.com/page/Spectral_flatness

- **ScienceDirect Topics** — Spectral Flatness: https://www.sciencedirect.com/topics/computer-science/spectral-flatness

- **John D. Cook** — "Spectral flatness: quantifying how tonal or noisy sound is": https://www.johndcook.com/blog/2016/05/03/spectral-flatness/

- **BilAudio-7** (Bilkent University) — MPEG-7 audio descriptors: http://www.cs.bilkent.edu.tr/~bilmdg/bilaudio-7/MPEG7.html

- **PubMed Central** — "Music Identification System Using MPEG-7 Audio Signature Descriptors": https://pmc.ncbi.nlm.nih.gov/articles/PMC3606779/
