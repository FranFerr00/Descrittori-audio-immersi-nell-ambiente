# Spectral Centroid: varianti della formula e implicazioni

## La formula che usi

La tua implementazione calcola il centroide classico sullo **spettro di magnitudine**:

$$\mu_1 = \frac{\sum_{k=0}^{N-1} f(k) \cdot |X(k)|}{\sum_{k=0}^{N-1} |X(k)|}$$

Questa è la definizione più comune in MIR (Peeters 2004 sez. 6.1.1, librosa, Meyda). Ma esistono almeno **7 varianti documentate** in letteratura, ciascuna con motivazioni specifiche.

---

## Variante 1: Spettro di potenza (power spectrum)

$$\mu_1^{(P)} = \frac{\sum_k f(k) \cdot |X(k)|^2}{\sum_k |X(k)|^2}$$

**Chi la usa**: Lerch (2023, eq. 3.44) la presenta come alternativa; MPEG-7 AudioSpectrumCentroid la prescrive; MATLAB `spectralCentroid` la usa come default.

**Differenza pratica**: lo spettro di potenza **enfatizza i picchi** rispetto allo sfondo. Per una sinusoide pura il risultato è identico. Per segnali complessi con componenti deboli, la versione power "ignora" di più le componenti a bassa energia, producendo un centroide più vicino alla frequenza dominante. La versione magnitude dà più peso alle componenti deboli.

**Impatto sui tuoi segnali**: per la tanh drive 20 (fondamentale forte + armoniche deboli), la versione power produrrebbe un centroide **più basso** (più vicino alla fondamentale) rispetto alla tua versione magnitude. Per il noise, i due valori sarebbero quasi identici.

**Nota di Lerch**: "il calcolo deve essere coerente — se il centroide usa il power spectrum, lo spread deve usarlo pure."

---

## Variante 2: MPEG-7 AudioSpectrumCentroid (scala logaritmica)

$$\mu_1^{(\log)} = \frac{\sum_{k=k_{\min}}^{K/2} \log_2\!\left(\frac{f(k)}{f_{\text{ref}}}\right) \cdot |X(k)|^2}{\sum_{k=k_{\min}}^{K/2} |X(k)|^2}$$

dove $f_{\text{ref}} = 1000$ Hz e $k_{\min}$ corrisponde a 62.5 Hz (tutte le bin sotto 62.5 Hz sono raggruppate in una singola banda con frequenza centrale 31.25 Hz).

**Chi la usa**: MPEG-7 standard (ISO/IEC 15938-4), Lerch (2023, eq. 3.45).

**Motivazione**: approssima la **scala Bark**, cioè la risoluzione non lineare dell'orecchio umano. L'orecchio distingue bene le basse frequenze tra loro (100 Hz vs 200 Hz è un'ottava) ma meno le alte (5000 Hz vs 5100 Hz è quasi nulla). La scala logaritmica comprime le alte frequenze e dà più peso alle differenze nelle basse.

**Differenza pratica**: il risultato è in **ottave rispetto a 1 kHz**, non in Hz. Per una sinusoide a 440 Hz: $\log_2(440/1000) \approx -1.18$ (poco più di un'ottava sotto il riferimento). Per noise bianco: $\approx 0$ (centrato intorno a 1 kHz in scala log). Per convertire in Hz: $f = f_{\text{ref}} \cdot 2^{\mu_1^{(\log)}}$.

**Rilevanza per interfantasia**: se il mapping verso il bicomb deve rispettare la percezione umana, questa variante è più appropriata. Un salto di centroide da 200 a 400 Hz (un'ottava) verrebbe percepito come "grande" quanto un salto da 2000 a 4000 Hz — e la scala log li tratta allo stesso modo, mentre la scala lineare dà 200 Hz al primo e 2000 Hz al secondo.

---

## Variante 3: Sharpness di Zwicker (centroide percettivo)

$$S = 0.11 \cdot \frac{\sum_{z=1}^{N_{\text{band}}} z \cdot g(z) \cdot N'(z)}{\sum_{z=1}^{N_{\text{band}}} N'(z)}$$

dove $z$ è l'indice di banda Bark, $N'(z)$ è la **loudness specifica** (in sone) della banda $z$, e $g(z)$ è una funzione di ponderazione: $g(z) = 1$ per $z < 15$ (~2700 Hz), e $g(z) = 0.66 \cdot e^{0.171z}$ per $z \geq 15$.

**Chi la usa**: Zwicker & Fastl (1990/1999), standard DIN 45692, Essentia (come opzione in openSMILE), il toolbox Pure Data di Torres Porres.

**Motivazione**: è il **centroide percettivo vero**. A differenza del centroide spettrale, usa la loudness (non la magnitudine) e una scala frequenziale percettiva (Bark). La funzione $g(z)$ dà peso extra alle alte frequenze (sopra ~3 kHz) perché l'orecchio è particolarmente sensibile alla "acutezza" in quella regione.

**Differenza pratica**: per suoni con contenuto sotto 3 kHz, la sharpness è molto simile al centroide su scala Bark. Per suoni con contenuto sopra 3 kHz, la sharpness cresce molto più velocemente del centroide lineare a causa della ponderazione $g(z)$.

**Unità**: acum. 1 acum = sharpness di un noise a banda stretta (1 Bark) centrato a 1 kHz a 60 dB SPL.

**Rilevanza per interfantasia**: se il tuo obiettivo è catturare la percezione di "brillantezza" in senso stretto, la sharpness di Zwicker è la misura gold standard. Ma richiede un modello di loudness (non banale da implementare in Pure Data realtime).

---

## Variante 4: Spectral Subband Centroids (SSC)

Invece di un singolo centroide globale, si calcola il centroide **per ciascuna sotto-banda**:

$$\text{SSC}_i = \frac{\sum_{k=l_i}^{u_i} f(k) \cdot |X(k)|^2}{\sum_{k=l_i}^{u_i} |X(k)|^2}$$

dove $l_i$ e $u_i$ sono i bordi della sotto-banda $i$.

**Chi la usa**: Paliwal (1998) per speech recognition; Bellettini & Mazzini (2006) per audio fingerprinting; speaker verification (NIST).

**Motivazione**: cattura dove si concentra l'energia **all'interno di ciascuna regione frequenziale**. Un singolo centroide globale non distingue un suono con energia bilanciata a 500 Hz e 4 kHz da uno con energia concentrata a 2 kHz (entrambi possono avere centroide ~2.5 kHz). I subband centroids li distinguono.

**Differenza pratica**: produce un **vettore** (tipicamente 4-16 valori) invece di uno scalare. Più informativo ma più complesso da mappare.

**Rilevanza per interfantasia**: se il bicomb ha parametri che agiscono su regioni frequenziali diverse, gli SSC potrebbero alimentare direttamente ciascun parametro con il centroide della regione corrispondente.

---

## Variante 5: Harmonic Spectral Centroid (HSC)

$$\text{HSC} = \frac{\sum_{h=1}^{H} f_h \cdot A_h^2}{\sum_{h=1}^{H} A_h^2}$$

dove $f_h$ e $A_h$ sono frequenza e ampiezza della $h$-esima armonica, e $H$ è il numero di armoniche.

**Chi la usa**: MPEG-7 AudioHarmonicSpectralCentroid; Essentia `HarmonicPeaks` → `SpectralCentroid`.

**Motivazione**: calcola il centroide **solo sulle armoniche** (componenti periodiche), ignorando il rumore di fondo e le componenti non armoniche. Richiede prima un'estrazione di pitch (F0) e poi l'identificazione delle armoniche.

**Differenza pratica**: per la tua sinusoide pura, HSC = centroide classico. Per la tanh drive 20, HSC dà il centroide delle sole armoniche (senza il rumore residuo tra i picchi). Per il noise, HSC non è definito o non ha senso.

**Rilevanza per interfantasia**: molto utile se vuoi separare il "colore armonico" dal "colore rumoroso" di un suono. Potresti usare il centroide classico come misura globale e l'HSC come misura della struttura armonica.

---

## Variante 6: Centroide su spettro logaritmico (log-magnitude)

$$\mu_1^{(\text{logmag})} = \frac{\sum_k f(k) \cdot \log|X(k)|}{\sum_k \log|X(k)|}$$

**Chi la usa**: openSMILE (opzione `logSpectral`); alcune pipeline di speech processing.

**Motivazione**: il logaritmo comprime la dinamica dello spettro, dando relativamente più peso alle componenti deboli. In un certo senso è l'opposto dello spettro di potenza (che enfatizza i picchi).

**Differenza pratica**: per la tanh drive 20, il centroide log-magnitude salirebbe **più in alto** rispetto alla versione lineare, perché le armoniche deboli nelle alte frequenze pesano relativamente di più dopo la compressione logaritmica.

**Attenzione**: richiede gestione delle bin a zero (come per la flatness).

---

## Variante 7: Centroide mediano (spectral median)

Alcuni autori usano la **mediana** dello spettro invece della media pesata: la frequenza che divide lo spettro in due metà di uguale energia.

$$\text{mediana}: \sum_{k=0}^{k_m} |X(k)|^2 = \frac{1}{2} \sum_{k=0}^{K/2} |X(k)|^2$$

**Chi la usa**: Wikipedia lo cita come variante; usato in EEG come "spectral edge frequency" (SEF 50%).

**Motivazione**: la mediana è robusta agli outlier. Un singolo picco molto forte non trascina la mediana quanto la media.

**Differenza pratica**: per noise bianco, mediana ≈ centroide. Per una sinusoide pura su sfondo silenzioso, la mediana è proprio la frequenza della sinusoide (come il centroide). Per spettri asimmetrici (come la tanh con fondamentale forte e armoniche decrescenti), la mediana è **più bassa** del centroide perché non è trascinata dalle armoniche alte.

**Nota**: è concettualmente simile allo spectral rolloff al 50% (il tuo rolloff è al 85%).

---

## Confronto riassuntivo

| Variante | Tipo spettro | Scala freq. | Sensibilità | Output |
|----------|-------------|-------------|-------------|--------|
| **Tua (classica)** | Magnitudine | Lineare (Hz) | Equilibrata | Scalare (Hz) |
| Power spectrum | Potenza | Lineare (Hz) | Enfatizza picchi | Scalare (Hz) |
| MPEG-7 log | Potenza | Log (ottave) | Percettiva | Scalare (ottave) |
| Zwicker sharpness | Loudness | Bark | Percettiva + g(z) | Scalare (acum) |
| Subband centroids | Potenza | Lineare per banda | Per-banda | Vettore |
| Harmonic SC | Armoniche | Lineare (Hz) | Solo armoniche | Scalare (Hz) |
| Log-magnitude | Log-magnitudine | Lineare (Hz) | Enfatizza deboli | Scalare (Hz) |
| Mediana | Potenza | Lineare (Hz) | Robusta outlier | Scalare (Hz) |

---

## Il problema del centroide e l'F0

Un punto critico emerso dalla letteratura (Schubert & Wolfe 2006, Marozeau et al.): il centroide classico è **confuso con il pitch**. Se suoni la stessa nota di tromba un'ottava sopra, il centroide sale — non perché il timbro è cambiato, ma perché tutte le armoniche sono traslate in frequenza. Alcuni autori hanno proposto un "F0-adjusted centroid":

$$\text{F0AC} = \frac{\mu_1}{f_0}$$

cioè il centroide normalizzato per la fondamentale. Un valore di 3.5 significherebbe "il centroide è a 3.5× la fondamentale" — indipendente dal registro. Tuttavia Schubert & Wolfe (2006) hanno dimostrato sperimentalmente che la percezione di brillantezza **dipende dal centroide assoluto**, non dall'F0AC: suonare la stessa nota più acuta la rende percettivamente più brillante, anche se il rapporto armonico è invariato.

**Per interfantasia**: se i segnali captati hanno F0 variabile (ad esempio voce o strumenti), il centroide assoluto mescola informazione di pitch e timbro. Se vuoi isolare il timbro, potresti considerare di normalizzare per F0 (usando l'ACF max per stimare il pitch). Ma se il tuo mapping non distingue pitch da timbro (e non deve farlo), il centroide assoluto va benissimo.

---

## Raccomandazioni per interfantasia

1. **La tua formula attuale è corretta e standard** — è la più usata in MIR.

2. **Considera la versione MPEG-7 log** se il mapping verso il bicomb deve essere percettivamente uniforme. In pratica basta sostituire `f(k)` con `log2(f(k)/1000)` nella formula. Il costo computazionale è trascurabile.

3. **La versione power spectrum** potrebbe essere preferibile se i tuoi segnali hanno molto rumore di fondo a basso livello: la potenza "pulisce" il centroide dalle componenti deboli.

4. **Non implementare la sharpness di Zwicker** a meno che tu non abbia già un modello di loudness in Pure Data — il costo implementativo è alto e per segnali sintetici (non captati da microfono in ambiente) il beneficio è marginale.

5. **L'HSC è interessante ma richiede F0 detection** — il tuo ACF max già stima la periodicità, ma estrarre le singole armoniche è un passo ulteriore.

---

## Fonti

### Paper e libri

- **Lerch, A. (2023)**. *An Introduction to Audio Content Analysis*. 2nd ed. — Sez. 3.5.1: centroide classico e variante power spectrum; eq. 3.44, 3.45 per MPEG-7 log.
- **Peeters, G. (2004)**. "A Large Set of Audio Features." IRCAM. — Sez. 6.1.1.
- **Zwicker, E. & Fastl, H. (1999)**. *Psychoacoustics: Facts and Models*. 3rd ed. Springer. — Modello di sharpness, scala Bark, loudness specifica.
- **Schubert, E. & Wolfe, J. (2006)**. "Does Timbral Brightness Scale with Frequency and Spectral Centroid?" *Acta Acustica*, 92, 820–825. https://newt.phys.unsw.edu.au/~jw/reprints/SchubertWolfe06.pdf — Dimostrazione che la brillantezza dipende dal centroide assoluto, non dall'F0AC.
- **Krimphoff, J. et al. (1994)**. "Caractérisation du timbre des sons complexes." — Il centroide come prima dimensione percettiva del timbro.
- **Grey, J.M. (1977)**. "Multidimensional Perceptual Scaling of Musical Timbres." *JASA*, 61(5), 1270–1277. — Lavoro pionieristico, centroide come dimensione dominante.
- **Paliwal, K.K. (1998)**. "Spectral Subband Centroid Features for Speech Recognition." *Proc. ICASSP*. — SSC per speech.
- **Jiang, D.-N. et al. (2002)**. "Music Type Classification by Spectral Contrast Feature." *Proc. ICME*. — Spectral contrast (correlato ai subband centroids).
- **Marui, A. & Martens, W.L. (2006)**. "Predicting perceived sharpness of broadband noise from multiple moments." *JASA Express Letters*. https://www.geidai.ac.jp/~marui/files/200602_marui_martens_jasa.pdf — Sharpness predetta da centroide + spread.
- **Saitis, C. et al. (2022)**. "Interval and Ratio Scaling of Spectral Audio Descriptors." *Frontiers in Psychology*. https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.835401/full — Scale psicofisiche per centroide, spread, skewness.

### Documentazione software

- **librosa** — `spectral_centroid`: magnitudine, Hz. https://librosa.org/doc/main/generated/librosa.feature.spectral_centroid.html
- **MATLAB** — `spectralCentroid`: power spectrum, Hz. https://www.mathworks.com/help/audio/ug/spectral-descriptors.html
- **Essentia** — `Centroid`: generico (su qualsiasi array). https://essentia.upf.edu/reference/std_Centroid.html
- **openSMILE** — `cSpectral`: opzioni per log spectrum, power, sharpness. https://audeering.github.io/opensmile/_components/cSpectral.html
- **Wikipedia** — Spectral centroid: https://en.wikipedia.org/wiki/Spectral_centroid
- **ScienceDirect** — Spectral Centroid overview: https://www.sciencedirect.com/topics/engineering/spectral-centroid

### Standard

- **ISO/IEC 15938-4:2002** — MPEG-7 Part 4: AudioSpectrumCentroid (scala log, power spectrum, f_ref = 1000 Hz, f_min = 62.5 Hz).
- **DIN 45692:2009** — Sharpness di Zwicker.
