# Sei descrittori audio avanzati per il progetto Interfantasia

Il progetto Interfantasia può arricchire significativamente il proprio spazio timbrico integrando sei descrittori audio complementari a quelli già implementati: **Spectral Entropy, Spectral Contrast, Harmonic Spectral Deviation, Odd-to-Even Harmonic Ratio, Dissonance e Tristimulus**. Ciascuno cattura una dimensione percettiva distinta — dalla "rumorosità" globale alla struttura fine delle armoniche, fino alla rugosità sensoriale — e tutti dispongono di implementazioni software mature e basi teoriche solide. Il rapporto che segue documenta per ognuno la formula matematica esatta, le implementazioni disponibili, i valori tipici per segnali standard, i riferimenti bibliografici chiave e una valutazione della rilevanza per un sistema di mapping timbro → parametri di sintesi in tempo reale con Pure Data.

---

## 1. Spectral Entropy: la misura informazionale della "rumorosità" spettrale

### Definizione matematica

La Spectral Entropy tratta lo spettro di potenza normalizzato come una distribuzione di probabilità e ne calcola l'entropia di Shannon. Dato lo spettro in uscita dalla STFT con *N* bin frequenziali:

$$p(k) = \frac{|X(k)|^2}{\sum_{k=0}^{N-1} |X(k)|^2}$$

$$H = -\sum_{k=0}^{N-1} p(k) \cdot \log_2 p(k)$$

La **versione normalizzata** (valori in [0, 1]) divide per l'entropia massima possibile:

$$H_{\text{norm}} = \frac{H}{\log_2(N)}$$

Quando $p(k) = 0$, il termine $p(k) \cdot \log_2 p(k)$ è definito come 0 per continuità del limite. Per frame silenziosi (energia totale nulla), l'entropia viene convenzionalmente restituita come 0.

### Interpretazione percettiva e relazione con la Spectral Flatness

Un valore basso di $H_{\text{norm}}$ (prossimo a 0) indica uno spettro con energia concentrata in pochi bin — suoni tonali, armonici, con struttura formantica chiara. Un valore alto (prossimo a 1) indica uno spettro piatto, uniforme — suoni rumorosi, atonali, imprevedibili. La Spectral Entropy e la Spectral Flatness misurano entrambe l'uniformità spettrale, ma con operazioni matematiche fondamentalmente diverse:

| Aspetto | Spectral Entropy | Spectral Flatness |
|---------|-----------------|-------------------|
| **Operazione** | Entropia di Shannon del PSD normalizzato | Rapporto media geometrica / media aritmetica |
| **Base teorica** | Teoria dell'informazione | Disuguaglianza AM-GM |
| **Bin a zero** | Gestiti senza problemi (0·log(0) = 0) | **Problematico**: un solo bin a zero azzera la media geometrica e collassa la flatness a 0 |
| **Sensibilità** | Alla forma complessiva della distribuzione | A valori estremi (zeri, outlier) |

Questa **robustezza ai bin a zero** rende l'entropia spettrale più affidabile per l'analisi di segnali reali, dove lo spettro presenta frequentemente bin con energia trascurabile, specialmente alle alte frequenze.

La **Wiener entropy** è un termine spesso usato come sinonimo di Spectral Flatness (rapporto GM/AM), particolarmente nella ricerca sul canto degli uccelli (Tchernichovski et al. 2000). Non va confusa con la Shannon spectral entropy, che è una misura differente nonostante entrambe quantifichino l'uniformità spettrale.

### Valori tipici per segnali standard

| Segnale | $H_{\text{norm}}$ tipica | Note |
|---------|--------------------------|------|
| Sinusoide pura | ~0.0–0.05 | Energia in ~1 bin; valore esatto dipende dall'allineamento FFT e dal finestraggio |
| Rumore bianco | ~0.95–1.0 | Spettro quasi uniforme |
| Voce (parlato voiced) | ~0.3–0.6 | Struttura formantica chiara con picchi multipli |
| Fricative (unvoiced) | ~0.7–0.9 | Rumore a banda larga |
| Strumenti musicali (nota tenuta) | ~0.2–0.5 | Serie armonica con picchi multipli |
| Suoni percussivi | ~0.6–0.85 | Spettro transitorio a banda larga |

### Applicazioni principali

L'applicazione più consolidata è la **Voice Activity Detection (VAD)**: il parlato voiced ha entropia più bassa (picchi formantici) rispetto al rumore di fondo (spettro piatto). Misra et al. (2004) hanno dimostrato l'efficacia come feature per sistemi ASR robusti al rumore, utilizzandola in framework multi-stream HMM/ANN insieme a PLP/MFCC. Altre applicazioni includono la **classificazione di genere musicale**, la **segmentazione audio** (discriminazione parlato/musica/silenzio) e, in ambito biomedico, il monitoraggio della profondità dell'anestesia e la rilevazione di crisi epilettiche via EEG.

### Implementazioni software

| Libreria | Funzione | Note |
|----------|----------|------|
| **Essentia** | `Entropy` (categoria Statistics) | Calcola l'entropia di Shannon di qualsiasi array; va alimentato con lo spettro di potenza normalizzato |
| **openSMILE** | `cSpectral` con flag `entropy=1` | Parte dei feature set ComParE; configurabile su range di frequenza specifici |
| **MATLAB** | `spectralEntropy()` (Signal Processing Toolbox) | Sostituisce la deprecata `pentropy()`; supporta modalità istantanea e scalare |
| **Python (entropy lib)** | `entropy.spectral_entropy()` (Raphael Vallat) | Supporta metodi Welch/multitaper/FFT; `pip install entropy` |
| **librosa** | ❌ Non disponibile | Deve essere implementata manualmente da `np.abs(librosa.stft(y))**2` |
| **Meyda** | ❌ Non implementata | |
| **aubio** | ❌ Non disponibile | |
| **Pure Data** | ❌ Nessun external dedicato | Implementabile con `[rfft~]` → potenza → normalizzazione → `[expr]` per -Σp·log₂(p). La libreria `timbreID` di William Brent potrebbe offrire feature simili |

### Riferimenti bibliografici chiave

- **Misra, H., Ikbal, S., Bourlard, H. & Hermansky, H. (2004).** "Spectral entropy based feature for robust ASR." *Proceedings of IEEE ICASSP'04*, Montreal, Canada. DOI: 10.1109/ICASSP.2004.1325955
- **Misra, H., Ikbal, S., Bourlard, H. & Hermansky, H. (2005).** "Multi-resolution spectral entropy based feature for robust ASR." *ICASSP 2005*, Philadelphia.
- **Dubnov, S. (2004).** "Generalization of spectral flatness measure for non-Gaussian linear processes." *IEEE Signal Processing Letters*, 11(8), 698–701.
- **Peeters, G. (2004).** "A large set of audio features for sound description." IRCAM Technical Report, CUIDADO Project.

### Limitazioni e problemi noti

La versione non normalizzata dipende dalla dimensione *N* della FFT, rendendo impossibili confronti tra analisi con risoluzioni diverse. La scelta della finestra di analisi influisce sullo spectral leakage e quindi sull'entropia: finestre più lunghe producono picchi spettrali più stretti (entropia più bassa) ma peggiorano la risoluzione temporale. Il descrittore **non è pitch-aware**: un complesso armonico con molti parziali ha entropia più alta di una sinusoide pura, anche se entrambi sono "tonali". Infine, come tutti i descrittori scalari, collassa l'intera informazione spettrale in un singolo numero, perdendo informazione su *dove* nello spettro si trovi la struttura.

### Valutazione per il mapping timbrico in Pure Data

**Utilità: alta.** Computazionalmente leggero (O(N), singola passata sui bin), range normalizzato [0, 1] che si mappa naturalmente a parametri di sintesi (mix rumore/oscillatore, Q del filtro, indice di modulazione FM). L'implementazione in Pd è diretta: `[rfft~]` → magnitudine quadrata → normalizzazione → calcolo dell'entropia con `[expr]`. Si accoppia bene con il centroide spettrale per formare uno spazio timbrico 2D (luminosità × tonicità).

---

## 2. Spectral Contrast: il profilo banda-per-banda della "chiarezza armonica"

### Definizione matematica

Lo Spectral Contrast (Jiang et al. 2002) divide l'asse frequenziale in sotto-bande approssimativamente in scala di ottave e calcola, per ciascuna banda, la differenza tra i **picchi** (top quantile) e le **valli** (bottom quantile) dello spettro di magnitudine.

**Definizione delle sotto-bande** (dato $f_{\min}$ e $n_{\text{bands}}$):
- Banda 0: $[0, f_{\min}]$
- Banda $k$: $[2^{k-1} \cdot f_{\min},\; 2^k \cdot f_{\min}]$ per $k = 1, \ldots, n_{\text{bands}}$
- L'ultima banda si estende fino alla frequenza di Nyquist.

**Per ciascuna sotto-banda $b$**, dati $N_b$ bin spettrali ordinati in ordine crescente:

$$\text{Valley}_b = \log\!\left(\frac{1}{\alpha N_b} \sum_{i=1}^{\alpha N_b} x_i\right) \qquad \text{Peak}_b = \log\!\left(\frac{1}{\alpha N_b} \sum_{i=N_b - \alpha N_b + 1}^{N_b} x_i\right)$$

$$SC_b = \text{Peak}_b - \text{Valley}_b$$

dove $\alpha$ è la frazione di bin utilizzata per il calcolo (quantile). L'output è un **vettore** di dimensione $n_{\text{bands}} + 1$, non uno scalare.

### Differenza dal Spectral Crest Factor

Lo Spectral Crest Factor usa il rapporto max/media per banda ed è quindi **sensibile a singoli outlier**: un solo bin con un artefatto domina la misura. Lo Spectral Contrast, usando la media dei quantili superiori e inferiori, è **più robusto** e cattura il "range dinamico" complessivo all'interno di ciascuna banda, non solo la prominenza del bin più forte.

### Interpretazione percettiva

Un contrasto alto in una banda indica **contenuto armonico forte** con parziali che emergono chiaramente dal pavimento di rumore — suoni risonanti, chiari. Un contrasto basso indica energia diffusa, rumorosa, omogenea nella banda. Il vantaggio fondamentale rispetto a descrittori globali (come flatness o entropy) è che lo Spectral Contrast fornisce una **mappa frequenza-specifica**: un suono può avere alto contrasto nelle bande basse (fondamentale + armoniche forti) e basso contrasto nelle bande alte (parziali superiori rumorosi). Questa rappresentazione multi-banda cattura sfumature timbriche che i descrittori scalari perdono.

### Implementazioni software

**librosa** offre `spectral_contrast()` con parametri configurabili: `n_bands=6` (default), `fmin=200.0` Hz, `quantile=0.02` (2%), `linear=False` (modalità logaritmica). L'output ha forma `(n_bands + 1, t)` — 7 valori per frame con impostazioni default, corrispondenti alle bande [0, 200], [200, 400], [400, 800], [800, 1600], [1600, 3200], [3200, 6400], [6400, 11025] Hz.

**Essentia** implementa `SpectralContrast` con parametri diversi: `neighbourRatio=0.4` (40% dei bin per picchi/valli, molto più ampio del 2% di librosa), `numberBands=6`, `staticDistribution=0.15`. Questa versione modificata è basata su Akkermans, Serrà & Herrera (SMC'09) e offre maggiore potere discriminativo. Le due implementazioni **non sono direttamente comparabili** per gli stessi segnali a causa della differente parametrizzazione.

**openSMILE**, Meyda e aubio **non includono** Spectral Contrast come feature nativa.

### Valori tipici

In modalità logaritmica (librosa, quantile=0.02): strumenti armonici (tromba, violino) mostrano contrasto di **20–40 dB** nelle bande basse e **10–20 dB** nelle bande alte; il rumore bianco ha contrasto di **0–5 dB** in tutte le bande; il parlato mostra valori intermedi di **10–25 dB** nelle bande basse e **5–15 dB** nelle alte.

### Riferimenti bibliografici chiave

- **Jiang, D.-N., Lu, L., Zhang, H.-J., Tao, J.-H. & Cai, L.-H. (2002).** "Music type classification by spectral contrast feature." *Proceedings of IEEE ICME'02*, vol. 1, pp. 113–116. DOI: 10.1109/ICME.2002.1035731
- **Akkermans, V., Serrà, J. & Herrera, P. (2009).** "Shape-based spectral contrast descriptor." *Sound and Music Computing Conference (SMC'09)*, pp. 143–148.
- **McFee, B. et al. (2015).** "librosa: Audio and music signal analysis in Python." *Proceedings of the 14th Python in Science Conference*.

### Limitazioni

La sensibilità alla **risoluzione frequenziale** è significativa: FFT piccole producono pochi bin per banda, rendendo le stime dei quantili instabili. Il parametro quantile ha un impatto drastico: il 2% di librosa vs il 40% di Essentia producono risultati molto diversi. La prima banda [0, $f_{\min}$] può contenere pochissimi bin, rendendo il contrasto inaffidabile.

### Valutazione per Pure Data

**Utilità: medio-alta.** L'output vettoriale (7 valori) offre una rappresentazione timbrica più ricca dei descrittori scalari e permette di controllare parametri di sintesi diversi per regione frequenziale (contrasto basso-banda → densità del sub-basso; contrasto alto-banda → rumorosità/breathiness). La sfida implementativa in Pd è l'ordinamento dei bin per banda (calcolo dei quantili), più complesso rispetto a semplici statistiche. Una versione semplificata (max/media per banda anziché quantili completi) potrebbe ridurre il costo computazionale.

---

## 3. Harmonic Spectral Deviation: quanto le armoniche "tradiscono" l'inviluppo

### Definizione matematica

L'Harmonic Spectral Deviation (HSD), come definita in Peeters (2004, sez. 7.1.4), misura quanto le ampiezze dei singoli parziali armonici deviano da un inviluppo spettrale liscio calcolato sulle armoniche stesse:

$$\text{HSD} = \frac{\sum_{h=1}^{H} |A_h - SE_h|}{\sum_{h=1}^{H} A_h}$$

dove $A_h$ è l'ampiezza dell'*h*-esima armonica e $SE_h$ è il valore dell'inviluppo spettrale liscio alla stessa armonica, calcolato tipicamente con una **media mobile a 3 punti**:

$$SE_h = \frac{A_{h-1} + A_h + A_{h+1}}{3} \qquad \text{per } 1 < h < H$$

$$SE_1 = \frac{A_1 + A_2}{2} \qquad SE_H = \frac{A_{H-1} + A_H}{2}$$

Lo standard **MPEG-7** (ISO/IEC 15938-4, descrittore `AudioHarmonicSpectralDeviation`) utilizza la stessa struttura ma opera su **ampiezze logaritmiche** anziché lineari, scelta motivata da risultati sperimentali sulla percezione timbrica.

### Differenza dalla Spectral Irregularity

Questa distinzione è cruciale e spesso fonte di confusione:

| Proprietà | HSD | Spectral Irregularity (Jensen 1999) |
|-----------|-----|--------------------------------------|
| **Input** | Solo i **picchi armonici** rilevati | **Tutti i bin** della FFT |
| **Richiede f₀** | Sì (necessita peak-tracking armonico) | No (opera sullo spettro grezzo) |
| **Formula** | Deviazione dall'inviluppo liscio delle armoniche | $\sum |A_k - A_{k+1}|$ o $\sum(A_k - A_{k+1})^2$ su tutti i bin |
| **Applicabilità** | Solo suoni armonici/tonali | Qualsiasi suono |

L'HSD è quindi una misura **mirata** della struttura fine armonica, mentre la Spectral Irregularity è una misura **globale** della rugosità spettrale.

### Interpretazione percettiva

Un **HSD basso** indica che le armoniche seguono un inviluppo liscio (es. onda a dente di sega con decadimento 1/n) — suono percepito come **liscio, pieno, regolare**. Un **HSD alto** indica deviazioni significative dall'inviluppo (es. risonanze del corpo strumentale, formanti) — suono percepito come **complesso, texturizzato, con struttura irregolare**. Caclin et al. (2005) hanno identificato la struttura fine dello spettro come una dimensione percettiva del timbro indipendente dal centroide spettrale e dal tempo d'attacco.

### Valori tipici

| Segnale | HSD approssimativo | Note |
|---------|---------------------|------|
| Sinusoide pura | 0.0 | Singola armonica, nessuna deviazione possibile |
| Dente di sega | ~0.0 (molto basso) | Decadimento 1/n liscio |
| Onda quadra | Basso-moderato | Solo dispari, ma decadimento 1/n liscio tra le dispari |
| Tromba (es. Peeters) | **~0.15** | Deviazione moderata, risonanze formantiche |
| Pianoforte | Più alto | La posizione del martello crea notch/formanti |
| Rumore | N/A | Nessuna struttura armonica da analizzare |

### Implementazioni software

Nessuna libreria mainstream offre un algoritmo HSD dedicato "pronto all'uso". **Essentia** non ha un `HarmonicSpectralDeviation` esplicito, ma fornisce la catena di processing necessaria: `PitchYinFFT` → `SpectralPeaks` → `HarmonicPeaks`, da cui calcolare la deviazione con codice custom. Il **Timbre Toolbox** (Peeters & McAdams 2011, MATLAB) include HSD tra i descrittori armonici. **LibXtract** (C) offre `xtract_irregularity_j` per la Spectral Irregularity di Jensen (su tutti i bin), non per l'HSD armonico. In **Pure Data**, l'implementazione richiede `[sigmund~]` per f₀ e tracking dei parziali, seguito da calcolo custom dell'inviluppo liscio e della deviazione.

### Riferimenti bibliografici chiave

- **Peeters, G. (2004).** "A large set of audio features for sound description." IRCAM/CUIDADO Technical Report. Sez. 7.1.4.
- **ISO/IEC 15938-4:2002.** MPEG-7 Audio, Part 4. Descrittore HarmonicSpectralDeviation.
- **Kim, H.-G., Moreau, N. & Sikora, T. (2005).** *MPEG-7 Audio and Beyond: Audio Content Indexing and Retrieval.* Wiley. Cap. 2.7.6.
- **Peeters, G., Giordano, B.L., Susini, P., Misdariis, N. & McAdams, S. (2011).** "The Timbre Toolbox: Extracting audio descriptors from musical signals." *JASA*, 130(5), 2902–2916.
- **Caclin, A., McAdams, S., Smith, B.K. & Winsberg, S. (2005).** "Acoustic correlates of timbre space dimensions." *JASA*, 118(1), 471–482.

### Limitazioni

L'HSD **dipende criticamente dalla qualità della stima di f₀**: un errore di ottava nell'f₀ assegna le armoniche sbagliate, rendendo la misura priva di senso. Il metodo di smoothing dell'inviluppo (media mobile a 3 punti) è semplice ma potrebbe non catturare strutture formantiche più ampie. MPEG-7 e Peeters differiscono sulla scala di ampiezza (logaritmica vs lineare), producendo risultati non direttamente comparabili.

### Valutazione per Pure Data

**Utilità: moderata.** Richiede tracking armonico affidabile (via `[sigmund~]`), il che aggiunge latenza e complessità. Una volta estratti i parziali, il calcolo è leggero. Mapping suggerito: HSD → profondità delle risonanze formantiche o irregolarità del banco di filtri. HSD basso → risposta del filtro piatta; HSD alto → picchi formantici pronunciati.

---

## 4. Odd-to-Even Harmonic Ratio: l'impronta del "vuoto" timbrico

### Definizione matematica

Il rapporto energia armoniche dispari / energia armoniche pari è definito come:

$$\text{OER} = \frac{\sum_{h \in \text{dispari}} A_h^2}{\sum_{h \in \text{pari}} A_h^2} = \frac{A_1^2 + A_3^2 + A_5^2 + \cdots}{A_2^2 + A_4^2 + A_6^2 + \cdots}$$

dove la fondamentale ($h = 1$) è classificata come armonica dispari. Le armoniche dispari si trovano a frequenze $f_0, 3f_0, 5f_0, \ldots$ e le pari a $2f_0, 4f_0, 6f_0, \ldots$

### Interpretazione percettiva

Il rapporto OER cattura una dimensione timbrica fondamentale — la percezione di "vuoto" (*hollow*) vs "pieno" (*full*):

| Forma d'onda / Strumento | OER atteso | Qualità percettiva |
|--------------------------|------------|---------------------|
| **Onda quadra** | → ∞ (solo dispari) | "Vuoto", "legnoso", "nasale" |
| **Onda triangolare** | → ∞ (solo dispari, rolloff più rapido) | "Vuoto", "smorzato", "morbido" |
| **Dente di sega** | ≈ 1.0 (tutte le armoniche) | "Pieno", "ronzante", "ricco" |
| **Clarinetto (registro basso)** | ~3–5 (es. Peeters: **3.2431**) | "Vuoto", "legnoso" — tubo chiuso, predominanza dispari |
| **Tromba** | ≈ 1.0 | "Brillante", "pieno" — spettro bilanciato |
| **Oboe** | ~1.0–1.5 | "Reed-like", ricco in tutte le armoniche |
| **Sinusoide pura** | max float (solo h=1, nessuna pari) | Essentia restituisce il massimo valore float |

L'assenza delle armoniche pari rimuove il rinforzo d'ottava che crea la percezione di "pienezza" nel timbro. Wei, Gan & Huang (2022, *Frontiers in Psychology*) confermano: "Se le ampiezze delle armoniche pari sono relativamente più basse delle dispari, il suono tende a essere percepito come hollow." Caclin et al. (2006, 2008) hanno dimostrato con studi MMN (mismatch negativity) che il cervello elabora la struttura fine spettrale (bilancio dispari/pari) **indipendentemente** dal centroide spettrale.

### Relazione con altri descrittori

L'OER è parzialmente correlato con il centroide spettrale ma cattura informazione diversa: un OER alto (dominanza dispari) può coesistere con centroide alto o basso a seconda di quali armoniche dispari sono più forti. Il Tristimulus è complementare: cattura il peso relativo fondamentale/medie/superiori, mentre l'OER cattura il pattern alternato dispari/pari. Insieme forniscono un profilo armonico più completo.

### Implementazioni software

**Essentia** offre `OddToEvenHarmonicEnergyRatio` (categoria Tonal): accetta vettori di frequenze e magnitudini dei picchi armonici (tipicamente dall'output di `HarmonicPeaks`), restituisce un singolo valore reale. Quando l'energia pari è zero, restituisce `numeric_limits<float>::max()`. **LibXtract** (C) fornisce `xtract_odd_even_ratio`. **librosa**, **openSMILE**, **Meyda** e **aubio** non offrono OER nativo — va calcolato manualmente dopo l'estrazione dei parziali armonici. In **Pure Data**, `[sigmund~]` o `[fiddle~]` forniscono frequenze e ampiezze dei parziali, da cui separare dispari e pari con operazioni modulo e calcolare il rapporto.

### Riferimenti bibliografici chiave

- **Peeters, G. (2004).** "A large set of audio features for sound description." IRCAM/CUIDADO Report. Sez. 7.1.5, Fig. 8.
- **Martin, K.D. & Kim, Y.E. (1998).** "Musical instrument identification: A pattern-recognition approach." *JASA*, 104(3), 1768.
- **Wei, J., Gan, L. & Huang, X. (2022).** "A Review of Research on the Neurocognition for Timbre Perception." *Frontiers in Psychology*, 13:869475.
- **Caclin, A., McAdams, S., Smith, B.K. & Winsberg, S. (2005).** "Acoustic correlates of timbre space dimensions." *JASA*, 118(1).
- **Caetano, M., Saitis, C. & Siedenburg, K. (2019).** "Audio Content Descriptors of Timbre." Cap. 11 in *Timbre: Acoustics, Perception, and Cognition*, Springer.

### Limitazioni

Il problema più critico riguarda gli **errori di stima di f₀**: se f₀ viene stimata un'ottava sotto il valore reale, le armoniche pari diventano dispari e viceversa, invertendo completamente il descrittore. Per strumenti con parziali inarmònici (es. pianoforte con stiramento), la classificazione dispari/pari diventa ambigua. Per note acute con poche armoniche nel range udibile, l'OER diventa instabile.

### Valutazione per Pure Data

**Utilità: molto alta.** L'OER ha mapping diretti e intuitivi verso parametri di sintesi: **pulse width** (OER alto → larghezza verso 50%, onda quadra; basso → impulso stretto); **bilancio armoniche dispari/pari in sintesi additiva** (mappare 1/OER al guadagno delle armoniche pari); **indice di waveshaping** (OER alto → distorsione "dispari" tipo clipping). Suggerimento pratico: applicare scala logaritmica `log(OER)` per ottenere un range simmetrico attorno a 0 (bilanciato = 0, dispari-dominante > 0). Smoothing temporale di 50–100 ms essenziale per stabilità frame-per-frame.

---

## 5. Dissonance sensoriale: la rugosità tra coppie di parziali

### Definizione matematica (parametrizzazione di Sethares)

Il modello di Plomp & Levelt (1965) quantifica la **rugosità sensoriale** (roughness) prodotta dai battimenti tra coppie di parziali vicini in frequenza. La dissonanza tra due sinusoidi di frequenze $f_1$ e $f_2$ (con $f_2 \geq f_1$) e ampiezze $a_1$, $a_2$ è:

$$d(f_1, f_2) = \ell_{12} \cdot \left[e^{b_1 \cdot s \cdot (f_2 - f_1)} - e^{b_2 \cdot s \cdot (f_2 - f_1)}\right]$$

dove:

$$s = \frac{D^*}{s_1 \cdot f_{\min} + s_2}$$

**Costanti fittate** (dai dati sperimentali di Plomp & Levelt):
- $b_1 = -3.51$, $b_2 = -5.75$
- $s_1 = 0.0207$, $s_2 = 18.96$
- $D^* = 0.24$ (punto di massima dissonanza, circa **1/4 della banda critica**)
- $C_1 = 5$, $C_2 = -5$

**Pesatura dell'ampiezza** $\ell_{12}$: nel modello originale (Sethares 1993) è $\ell_{12} = a_1 \cdot a_2$ (prodotto); nella revisione del 2005 (Appendice G) è $\ell_{12} = \min(a_1, a_2)$, giustificato dal fatto che l'ampiezza del battimento è determinata dal minore dei due segnali.

**Dissonanza totale** per un insieme di *N* parziali:

$$D_{\text{total}} = \sum_{i} \sum_{j > i} d(f_i, f_j)$$

Il parametro $s$ codifica la dipendenza dalla frequenza della **banda critica**: sotto 1000 Hz la banda critica è approssimativamente costante (~100 Hz), poi cresce proporzionalmente alla frequenza. La massima rugosità si verifica quando la differenza tra due frequenze è circa 1/4 della banda critica — il parametro $D^* = 0.24$ riflette esattamente questo.

### Distinzione dalla dissonanza musicale

Questa è una misura di **dissonanza sensoriale/psicoacustica**, basata puramente sulla rugosità percepita dai battimenti nella coclea. La dissonanza musicale/teorica incorpora condizionamento culturale, contesto armonico, condotta delle voci, aspettative tonali e risoluzioni. Il modello predice bene per **intervalli isolati** ma non può spiegare effetti contestuali (un tritono che risolve su una consonanza), effetti di familiarità, o variazioni culturali nei giudizi di consonanza.

### Valori tipici (relativi)

- **Unisono** (1:1): dissonanza = 0 (minimo)
- **Ottava** (2:1): molto bassa (prossima a 0 per timbri armonici)
- **Quinta giusta** (3:2): bassa (minimo locale sulla curva)
- **Quarta giusta** (4:3): bassa (minimo locale)
- **Seconda minore** (~1.06): **alta** (prossima al massimo — circa 1/4 di banda critica)
- **Tritono** (~1.414): moderatamente alta
- In Essentia: output normalizzato a **[0, 1]** — 0 = consonante, 1 = massimamente dissonante.

### Implementazioni software

**Essentia** offre l'algoritmo `Dissonance` (categoria Tonal): accetta vettori di frequenze (ordinate in modo crescente) e magnitudini, restituisce un valore reale normalizzato in [0, 1]. Tipicamente alimentato dall'output di `SpectralPeaks`. Implementazione basata su Plomp & Levelt 1965.

In **Pure Data**, la risorsa principale è la **libreria PSYCHO** di Alexandre Torres Porres (`pd-psycho`, GitHub: `porres/pd-psycho`), evoluzione del "Dissonance Model Toolbox" presentato a PdCon 2011. Include l'oggetto `[roughness]` che accetta liste di frequenze e ampiezze. Implementa modelli multipli basati su Terhardt, Sethares e Barlow. Il lavoro è documentato nella tesi di dottorato di Porres (2012, USP): "Modelos psicoacústicos de dissonância para eletrônica ao vivo".

In **MATLAB**, il codice originale di Sethares è disponibile su `sethares.engr.wisc.edu/comprog.html` con la funzione `dissmeasure`. In **Python**, l'implementazione di riferimento è il gist di endolith (`sethares.py`, GitHub Gist 3066664), una implementazione NumPy pulita che supporta entrambi i modelli di ampiezza ('product' e 'min').

### Riferimenti bibliografici chiave

- **Plomp, R. & Levelt, W.J.M. (1965).** "Tonal Consonance and Critical Bandwidth." *JASA*, 38(4), 548–560.
- **Sethares, W.A. (1993).** "Local Consonance and the Relationship Between Timbre and Scale." *JASA*, 94(3), 1218–1228.
- **Sethares, W.A. (2005).** *Tuning, Timbre, Spectrum, Scale* (2nd ed.). Springer. Il riferimento definitivo con derivazioni delle formule, codice MATLAB e applicazioni estese.
- **Vassilakis, P.N. (2001).** "Perceptual and Physical Properties of Amplitude Fluctuation and their Musical Significance." Tesi di dottorato, UCLA.
- **Vassilakis, P.N. (2005).** "Auditory Roughness as Means of Musical Expression." *Selected Reports in Ethnomusicology*, 12, 119–144.
- **Porres, A.T. (2011).** "Dissonance Model Toolbox in Pure Data." *PdCon11*, Berlin.

### Limitazioni

La complessità computazionale è **O(N²)** nel numero di parziali — ogni coppia deve essere valutata. Con 20 parziali si hanno 190 coppie, gestibile in tempo reale, ma con spettri complessi il costo cresce rapidamente. Il modello cattura solo la rugosità da battimenti, ignorando armonicità, contesto tonale e apprendimento culturale. Le costanti sono fittate su condizioni sperimentali specifiche e potrebbero non generalizzare perfettamente.

### Valutazione per Pure Data

**Utilità: alta, con caveat computazionali.** La libreria PSYCHO di Torres Porres offre oggetti Pd pronti all'uso. Con 6–20 parziali tipici, il calcolo O(N²) è gestibile a rate di controllo (ogni 10–50 ms). Mapping: dissonanza → cutoff del filtro, quantità di distorsione, ampiezza spaziale. Richiede partial tracking accurato (via `[sigmund~]`), aggiungendo latenza. Da usare a **control rate**, non audio rate.

---

## 6. Tristimulus: le coordinate cromatiche del timbro

### Definizione matematica

Il Tristimulus (Pollard & Jansson 1982) descrive il bilancio energetico armonico con tre valori che formano una partizione dell'unità:

$$T_1 = \frac{A_1}{\sum_{h=1}^{H} A_h} \qquad T_2 = \frac{A_2 + A_3 + A_4}{\sum_{h=1}^{H} A_h} \qquad T_3 = \frac{\sum_{h=5}^{H} A_h}{\sum_{h=1}^{H} A_h}$$

dove $A_h$ è l'ampiezza (magnitudine lineare, non al quadrato) dell'*h*-esima armonica. Il vincolo $T_1 + T_2 + T_3 = 1$ fa sì che solo due valori portino informazione indipendente.

**Nota importante sull'implementazione in Essentia:** contrariamente a quanto si potrebbe supporre, **Essentia include nativamente l'algoritmo `Tristimulus`** (categoria Tonal). Accetta vettori di frequenze e magnitudini (dall'output di `HarmonicPeaks`) e restituisce un vettore di 3 valori [T1, T2, T3]. Il codice sorgente è in `src/algorithms/tonal/tristimulus.cpp`.

### L'analogia con la colorimetria

L'analogia con le **coordinate tristimulus CIE XYZ** è esplicita e profonda. Come nella visione ogni colore percepito è decomponibile in tre componenti primarie che insieme ricostruiscono la sensazione cromatica, nella percezione timbrica il "colore" del suono armonico è approssimato da tre regioni spettrali. I valori T1, T2, T3 possono essere rappresentati su un **triangolo tristimulus**, dove i vertici rappresentano T1 = 1 (sinusoide pura), T2 = 1 (armoniche medie dominanti), T3 = 1 (armoniche superiori dominanti). Le traiettorie su questo triangolo tracciano l'evoluzione timbrica nel tempo — per esempio, l'attacco di una nota di flauto parte con T3 elevato (transitorio ricco) per poi stabilizzarsi con T1 dominante.

### Valori tipici per strumenti

| Strumento | T1 | T2 | T3 | Carattere timbrico |
|-----------|-----|-----|-----|---------------------|
| **Flauto** | 0.7–0.9 | 0.05–0.2 | 0.01–0.1 | Quasi sinusoidale, "puro" |
| **Clarinetto** | 0.4–0.6 | 0.1–0.2 | 0.2–0.4 | Armoniche dispari forti (3ª, 5ª, 7ª) distribuite tra T2 e T3 |
| **Oboe** | 0.15–0.3 | 0.25–0.4 | 0.3–0.5 | Energia distribuita, "reed-like" |
| **Tromba (ff)** | 0.1–0.25 | 0.2–0.35 | 0.4–0.6 | Brillante, molte armoniche superiori |
| **Violino (arco normale)** | 0.2–0.4 | 0.25–0.35 | 0.25–0.4 | Variabile con la tecnica |

### Relazione con altri descrittori spettrali

Un **T3 alto** correla positivamente con un **centroide spettrale elevato** (energia spostata verso le armoniche superiori). Una distribuzione equilibrata T1 ≈ T2 ≈ T3 corrisponde a uno **spread spettrale maggiore**. L'OER cattura informazione ortogonale al Tristimulus: il clarinetto ha forte predominanza di armoniche dispari (OER alto) ma questa informazione non è rappresentata direttamente dai confini T1/T2/T3.

### Implementazioni software

| Libreria | Disponibilità | Note |
|----------|--------------|------|
| **Essentia** | ✅ `Tristimulus` nativo | Catena: `Spectrum` → `SpectralPeaks` → `PitchDetection` → `HarmonicPeaks` → `Tristimulus` |
| **Timbre Toolbox** | ✅ (MATLAB) | Incluso tra i descrittori armonici |
| **librosa** | ❌ Non nativo | Calcolabile da harmonic analysis: `T1 = mags[0]/sum(mags)`, etc. |
| **Pure Data** | ❌ Nessun external | Implementabile facilmente: `[sigmund~]` → ampiezze parziali → somme e divisioni con oggetti math standard |
| **MIRtoolbox** | ✅ (MATLAB) | Include calcolo del tristimulus |

### Riferimenti bibliografici chiave

- **Pollard, H.F. & Jansson, E.V. (1982).** "A Tristimulus Method for the Specification of Musical Timbre." *Acta Acustica united with Acustica*, 51(3), 162–171.
- **Peeters, G. (2004).** "A large set of audio features for sound description." IRCAM/CUIDADO Report. Sez. 7.1.
- **Segnini, R. & Sapp, C. (2006).** "Timbrescape: A Musical Timbre and Structure Visualization Method using Tristimulus Data."
- **Riley, A. & Howard, D. (2004).** "A Real-Time Tristimulus Synthesizer." University of York.

### Limitazioni

Il raggruppamento (1), (2–4), (5+) è **arbitrario**: non esiste una giustificazione psicoacustica forte per questi confini specifici rispetto ad alternative (es. 1, 2–3, 4+). Il descrittore non cattura componenti inarmònici (rumore, transitori). Non è pesato percettivamente: usa ampiezze lineari senza considerare le curve di loudness equale. Poiché T1 + T2 + T3 = 1, solo **due valori sono indipendenti**.

### Valutazione per Pure Data

**Utilità: molto alta — il mapping più diretto verso la sintesi additiva.** T1 → guadagno dell'oscillatore fondamentale; T2 → guadagno delle armoniche 2–4; T3 → guadagno delle armoniche 5+. Questo crea un controllo timbrico a 3 parametri immediatamente intuitivo. Il costo computazionale è trascurabile una volta estratti i parziali (sole somme e divisioni). Lo spazio parametrico del triangolo tristimulus mappa in modo pulito la percezione timbrica (puro ↔ caldo ↔ brillante). L'analogia colorimetrica lo rende anche eccellente per mapping cross-modali verso parametri visivi o controller gestuali.

---

## Conclusione: quale priorità per Interfantasia

I sei descrittori coprono dimensioni timbriche complementari e non ridondanti. Per un sistema di mapping timbro → sintesi in tempo reale in Pure Data, la **priorità di implementazione** suggerita è:

La **Spectral Entropy** e il **Tristimulus** offrono il miglior rapporto utilità/complessità: sono computazionalmente leggeri, percettivamente intuitivi e mappano direttamente a parametri di sintesi fondamentali (mix rumore/tono per l'entropy; bilancio armonico per il tristimulus). L'**Odd-to-Even Ratio** è il terzo candidato naturale, con mapping immediato verso pulse width e bilancio dispari/pari in sintesi additiva. La **Dissonance** (Plomp-Levelt) è preziosa per il monitoraggio della rugosità sensoriale e dispone già di implementazioni Pd pronte (libreria PSYCHO di Torres Porres). Lo **Spectral Contrast** aggiunge informazione multi-banda unica ma richiede un'implementazione più complessa. L'**HSD** è il più specializzato e dipendente dalla qualità del tracking armonico, ma colma una nicchia importante nella descrizione della struttura fine dello spettro.

Tutti e sei i descrittori richiedono come prerequisito comune un **partial tracker affidabile** (con l'eccezione di Spectral Entropy e Spectral Contrast, che operano direttamente sullo spettro FFT). In Pure Data, `[sigmund~]` di Miller Puckette rappresenta la scelta più robusta per questa fase, offrendo sia stima di f₀ sia tracking dei parziali con latenza contenuta (~50 ms). La combinazione di questi sei descrittori con quelli già implementati (centroide, spread, flatness, crest, irregularity, flux) fornirebbe al progetto Interfantasia uno degli spazi di descrizione timbrica più completi disponibili in un ambiente di sintesi in tempo reale.