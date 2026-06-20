# Spectral Crest Factor (SCF): il descrittore che misura la dominanza del picco spettrale

## Definizione matematica

Lo **Spectral Crest Factor (SCF)** è il rapporto tra il valore massimo dello spettro di magnitudine e la media aritmetica dello stesso spettro. Nella formulazione di Lerch (2023, sez. 3.5.9):

$$\text{SCF}(n) = \frac{\max_{0 \leq k \leq K/2} |X(k, n)|}{\frac{1}{K/2+1} \sum_{k=0}^{K/2} |X(k, n)|}$$

dove $X(k, n)$ è lo spettro di magnitudine al frame $n$ e $K$ è la dimensione della FFT.

### Variante con somma al denominatore

Nella formulazione alternativa (usata da Lerch nella versione compatta), il denominatore è la **somma** anziché la media:

$$\text{SCF}(n) = \frac{\max_k |X(k, n)|}{\sum_k |X(k, n)|}$$

In questo caso il range è $\frac{2}{K+2} \leq \text{SCF} \leq 1$. Con la media al denominatore il range diventa $1 \leq \text{SCF} \leq \frac{K+2}{2}$.

La scelta tra le due formulazioni influenza solo la scala numerica, non la direzione interpretativa. Peeters (2004, sez. 9.1) usa la media al denominatore, producendo valori ≥ 1.

### Range e significato dei valori estremi

Con la formulazione di Peeters (max/mean su bin attive, quella usata nel progetto), il range teorico e' **[1, +∞)**.

- **SCF = 1** (minimo teorico): max e mean coincidono, ovvero **tutte le bin attive hanno lo stesso modulo**. E' la condizione di spettro perfettamente piatto. Il caso ideale e' il rumore bianco (sul corpus: noise bianco ≈ 3.0, leggermente sopra 1 perche' le fluttuazioni statistiche del noise reale lasciano sempre una bin un po' piu' alta delle altre). Il caso patologico e' la **sinusoide su bin esatto**, dove restano attive solo 2-3 bin del lobo Hann tutte simili in modulo: SCF crolla a **1.50** anche se il segnale e' tonale (limite numerico, simmetrico al caso `bin_esatto` della SFM).
- **SCF → ∞** (nessun limite superiore): una singola bin domina su tutte le altre. Nessun segnale reale arriva all'infinito perche' l'inviluppo Hann distribuisce sempre l'energia di una sinusoide su almeno 3-5 bin, ma il valore puo' diventare molto grande quando il picco emerge da un pavimento di rumore di basso livello. Sul corpus il massimo osservato e' **138** (sinusoide al 25% di noise bianco): il picco resta intatto, le bin del rumore abbassano la mean, il rapporto esplode. Sotto microfono la sinusoide pura sale fino a 50-65 per lo stesso motivo (rumore ambientale che riempie il pavimento).

Nella pratica, sul corpus dei test:
- **1.0 - 3.5** → spettro uniforme o caso patologico bin esatto
- **5 - 15** → segnali tonali "normali" (sinusoidi, tanh, FM, doppie sinusoidi)
- **15 - 50** → bandpass stretto, sinusoidi microfonate, picchi su pavimento di rumore
- **50 - 140** → mix sinusoide+rumore (caso d'uso ideale del descrittore)

SCF alto = un picco domina nettamente. SCF basso = energia distribuita uniformemente o caso degenere a poche bin.

### Calcolo per sotto-bande

Come la SFM, il crest factor può essere calcolato per **sotto-bande frequenziali**. Peeters (2004) lo definisce come:

$$\text{SCM}(b) = \frac{\max(a(k \in \text{band}_b))}{\frac{1}{K_b} \sum_{k \in \text{band}_b} a(k)}$$

dove $b$ è l'indice di banda. Questa formulazione è usata nell'audio fingerprinting MPEG-7, dove SFM e SCF vengono calcolati congiuntamente nelle stesse 24 bande quarter-octave (250 Hz – 16 kHz).

---

## Interpretazione percettiva e fisica

Lo SCF misura la **"peakiness"** (piccatezza) dello spettro: quanto il picco massimo domina sulla distribuzione complessiva dell'energia.

- **SCF alto** → una componente frequenziale domina nettamente sulle altre (segnale tonale con fondamentale forte, filtro stretto)
- **SCF basso** → l'energia è distribuita uniformemente (rumore, segnale a banda larga)

### Relazione inversa con la Spectral Flatness

Lo SCF è l'**inverso concettuale** della SFM. Entrambi appartengono alla famiglia dei "flatness measures" (Lerch 2023, Peeters 2004), ma:

- La **SFM** usa la media geometrica vs aritmetica → sensibile alla distribuzione **globale**
- Lo **SCF** usa il massimo vs media aritmetica → sensibile solo al **singolo picco più alto**

Questo produce comportamenti diversi in casi specifici: uno spettro con due picchi di uguale altezza su sfondo silenzioso avrà SCF identico a uno con un solo picco della stessa altezza (il max è lo stesso), ma SFM diversa (la media geometrica cambia).

### Differenza dal Crest Factor temporale

Il termine "crest factor" in ingegneria elettrica e audio mastering indica il rapporto **picco/RMS** di una forma d'onda nel dominio del tempo (IEC 61672-1). Per un'onda sinusoidale il crest factor temporale è √2 ≈ 3 dB. Nel mastering audio, si usa per valutare la dinamica: un crest factor temporale basso indica forte compressione (loudness war).

Lo **spectral** crest factor opera invece nel **dominio frequenziale** su singoli frame STFT ed è una misura di tonalità/rumorosità, non di dinamica.

---

## Valori tipici dai test

Dai test condotti nel progetto (segnali Csound, SR 96000, FFT 8192, Hann, 50% overlap, max-freq 10000 Hz, calcolo su bin attive):

| Segnale | SCF | Note |
|---------|-----|------|
| Sinusoide 440 Hz | 3.3 | Pochi bin attivi, fondamentale domina |
| Noise bianco | 2.5 | Energia distribuita, nessun picco domina |
| Tanh drive 1 | 4.4 | Fondamentale forte, poche armoniche deboli |
| Tanh drive 5 | 8.0 | Fondamentale cresce rispetto alle armoniche |
| Tanh drive 20 | 9.4 | Fondamentale domina sulle armoniche più deboli |
| Noise BP Q=50 | 12.2 | Filtro stretto concentra l'energia |
| Mix sin 50% + noise 50% | 36.9 | La sinusoide è un picco netto su pavimento di rumore |

**Osservazione chiave**: il crest factor cattura bene la **distorsione** (tanh drive 1 → 5 → 20: 4.4 → 8.0 → 9.4), perché la fondamentale cresce di livello rispetto alle armoniche sempre più deboli. Il valore più alto si ha per la miscela sin+noise al 50%: la sinusoide emerge come un picco netto sul pavimento di rumore, massimizzando il rapporto max/media.

---

## Applicazioni principali

### Audio fingerprinting

Lo SCF è una delle feature principali nei sistemi di fingerprinting audio basati su MPEG-7. L'algoritmo **AudioID di Fraunhofer** e il sistema di **Mapelli et al.** utilizzano congiuntamente SFM e SCF calcolati per sotto-bande come rappresentazione del fingerprint. La robustezza dello SCF alla compressione lossy è stata studiata in dettaglio: è meno robusto della SFM rispetto alla compressione MP3/AAC, motivo per cui MPEG-7 ha adottato la SFM (non lo SCF) come descrittore ufficiale per l'Audio Signature Description Scheme. Tuttavia, lo SCF resta usato come feature complementare alla SFM in molti sistemi.

### Discriminazione tonale/rumoroso

Come la SFM, lo SCF è impiegato per distinguere componenti tonali da componenti noise-like. Nell'ambito della codifica percettiva audio, Johnston (1988) usa la SFM per questa discriminazione, ma il crest factor offre un'alternativa computazionalmente più economica (non richiede il calcolo del logaritmo). Alcuni sistemi di Voice Activity Detection usano lo SCF come feature complementare.

### Classificazione di genere e MIR

Lo SCF è incluso come feature in molti sistemi di classificazione automatica di genere musicale, riconoscimento di strumenti e segmentazione audio. Essentia lo calcola sistematicamente su bande Bark, Mel e ERB nel suo estrattore standard (`barkbands_crest`, `melbands_crest`, `erbbands_crest`), aggregando poi con statistiche (media, varianza, min, max) su interi brani.

### Analisi del timbro

Nella percezione del timbro, lo SCF è correlato alla sensazione di "chiarezza" o "definizione" del suono. Un suono con SCF alto ha una fondamentale (o componente dominante) che si distingue nettamente dal resto dello spettro. Krimphoff et al. (1994) non includono direttamente il crest factor tra le dimensioni percettive principali del timbro (centroide, tempo di attacco, irregolarità spettrale), ma la sua correlazione con la "definizione armonica" lo rende utile come feature aggiuntiva.

---

## Implementazioni nelle librerie

### Essentia (C++/Python)

L'algoritmo **`Crest`** in Essentia è generico: calcola il rapporto max/mean di un qualsiasi array in input. Non è specifico per lo spettro. Nella pipeline standard, viene applicato a:
- Spettro di magnitudine diretto (`spectral_crest` non è un nome standard in Essentia)
- Energie in bande Bark → `barkbands_crest`
- Energie in bande Mel → `melbands_crest`
- Energie in bande ERB → `erbbands_crest`
- Vettore HPCP → `hpcp_crest`

Non può essere calcolato su array vuoti o contenenti valori negativi (lancia eccezione). Riferimento: Peeters (2004).

### MATLAB Audio Toolbox

La funzione **`spectralCrest(x, fs)`** calcola il rapporto max/mean dello spettro di potenza con supporto per sotto-bande tramite il parametro `Range`. Restituisce anche separatamente il picco spettrale e la media spettrale. Riferimento: Peeters (2004).

### librosa (Python)

librosa **non ha** una funzione `spectral_crest` dedicata. Ha invece **`spectral_contrast`** (Jiang et al., 2002), che è concettualmente simile ma diversa: calcola il rapporto tra picchi e valli **per sotto-banda** usando quantili (non il max globale). Lo spectral contrast divide lo spettro in sotto-bande e per ciascuna confronta l'energia nel quantile superiore (peaks) con quella nel quantile inferiore (valleys). È più robusto del crest factor semplice ma non è la stessa misura. Se si vuole il crest factor classico in librosa, va calcolato manualmente:

```python
S = np.abs(librosa.stft(y))
crest = np.max(S, axis=0) / np.mean(S, axis=0)
```

### Meyda (JavaScript)

Meyda **non implementa** direttamente lo spectral crest factor. Ha `spectralFlatness` ma non il crest. Lo si può calcolare dall'`amplitudeSpectrum` accessibile nel framework.

### aubio (C/Python)

aubio include **spectral kurtosis** nel suo `specdesc`, che è concettualmente affine al crest factor (misura la "peakiness" dal quarto momento statistico) ma non è la stessa misura.

### FluCoMa

La libreria FluCoMa (Fluid Corpus Manipulation) include il crest nello **SpectralShape** descriptor, definito come rapporto tra la magnitudine massima e l'RMS del frame di analisi.

### Two!Ears Auditory Model

Il modello auditory Two!Ears implementa `'crest'` come rapporto max/mean della rate-map (rappresentazione uditiva), seguendo Peeters (2011) e Lerch (2012).

| Libreria | Nome | Input | Per bande | Riferimento |
|----------|------|-------|-----------|-------------|
| Essentia | `Crest` | Qualsiasi array | Sì (via pipeline) | Peeters 2004 |
| MATLAB | `spectralCrest` | Spettro di potenza | Sì (`Range`) | Peeters 2004 |
| librosa | — | — | `spectral_contrast` (diverso) | Jiang 2002 |
| Meyda | — | — | — | — |
| aubio | `specdesc` (kurtosis) | Spettro | No | — |
| FluCoMa | `SpectralShape` | Spettro | No | — |

---

## Problemi noti e limitazioni

### Sensibilità al singolo outlier

Lo SCF dipende esclusivamente dal valore massimo dello spettro. Un singolo bin con energia anomalamente alta (ad esempio un artefatto FFT o un'interferenza) può produrre un SCF artificiosamente elevato. La SFM, che usa la media geometrica dell'intero spettro, è più robusta in questo senso.

### Non definito per frame silenziosi

Se l'energia totale dello spettro è zero, il denominatore (media o somma) è zero e lo SCF non è definito. Lerch (2023) nota esplicitamente che "the spectral crest factor is not defined for audio blocks with no spectral energy". Le implementazioni tipicamente restituiscono 0 in questi casi.

### Non distingue configurazioni spettrali diverse

Lo SCF non cattura la struttura complessiva dello spettro oltre al picco massimo. Due spettri con lo stesso massimo e la stessa media ma distribuzioni completamente diverse (uno con un picco e rumore uniforme, l'altro con molti picchi di altezze diverse) avranno lo stesso SCF. Per questo motivo, lo SCF è quasi sempre usato in combinazione con la SFM e/o l'entropia spettrale.

### Dipendenza dalla risoluzione frequenziale

Con FFT più lunghe, il picco di una sinusoide è concentrato in meno bin, producendo un massimo più alto rispetto alla media → SCF più alto. Con FFT corte, l'energia si distribuisce su più bin (spectral leakage) → SCF più basso. Questo rende i valori assoluti dipendenti dai parametri di analisi.

### Meno robusto della SFM alla compressione

Negli studi sull'audio fingerprinting (Allamanche et al., 2001; Mapelli et al., 2003), la SFM si è dimostrata più robusta dello SCF rispetto a distorsioni come la compressione lossy, l'equalizzazione e l'aggiunta di rumore. Questo è il motivo principale per cui MPEG-7 ha scelto la SFM (non lo SCF) come base per l'Audio Signature Description Scheme.

---

## Relazione con altri descrittori

### SCF e SFM

Sono la coppia fondamentale per misurare la tonalità/rumorosità di uno spettro. Peeters (2004) li presenta insieme nella stessa sezione (9.1). Sono **inversamente correlati** ma non sono l'uno il reciproco dell'altro: la SFM considera l'intera distribuzione (media geometrica), lo SCF solo il picco (max).

### SCF e Spectral Contrast (Jiang 2002)

Lo spectral contrast generalizza il concetto di crest factor calcolando separatamente per sotto-bande la differenza (in dB) tra picchi e valli dello spettro. È più discriminativo dello SCF semplice per la classificazione di genere musicale.

### SCF e Spectral Kurtosis

Entrambi misurano la "peakiness" dello spettro, ma con approcci matematici diversi: lo SCF usa max/mean (operazione di ordine 0/1), la kurtosis usa il quarto momento statistico. La kurtosis è più sensibile a distribuzioni con code pesanti, lo SCF è più sensibile al singolo valore estremo.

### SCF e Tonality Coefficient (Johnston 1988)

Il coefficiente di tonalità α di Johnston è derivato dalla **SFM** (non dallo SCF), ma lo SCF può essere usato come approssimazione rapida della tonalità in contesti dove il costo computazionale del logaritmo nella SFM è un problema.

---

## Riferimenti bibliografici chiave

- **Peeters, G. (2004)**. "A Large Set of Audio Features for Sound Description." IRCAM. — Sez. 9.1: definizione SCF per sotto-bande, insieme alla SFM.
- **Lerch, A. (2023)**. *An Introduction to Audio Content Analysis*. 2nd ed. — Sez. 3.5.9: definizione, range, implementazione, relazione con flatness.
- **Johnston, J.D. (1988)**. "Transform Coding of Audio Signals Using Perceptual Noise Criteria." — Contesto originale della discriminazione tonale/noise nei codec.
- **Allamanche, E. et al. (2001)**. "Content-Based Identification of Audio Material Using MPEG-7 Low Level Description." *Proc. ISMIR*. — Uso di SFM e SCF per audio fingerprinting MPEG-7.
- **Mapelli, V. et al. (2003)**. "Scalable Robust Audio Fingerprinting Using MPEG-7 Content Description." — Confronto robustezza SFM vs SCF.
- **Jiang, D.-N. et al. (2002)**. "Music Type Classification by Spectral Contrast Feature." *Proc. ICME*. — Spectral contrast come generalizzazione del crest factor.
- **Krimphoff, J., McAdams, S. & Winsberg, S. (1994)**. "Caractérisation du timbre des sons complexes." — Dimensioni percettive del timbro.
