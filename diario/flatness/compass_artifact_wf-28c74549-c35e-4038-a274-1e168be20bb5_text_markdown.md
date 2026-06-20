# Spectral Flatness Measure: il descrittore che distingue tono da rumore

La **Spectral Flatness Measure (SFM)** è il rapporto tra la media geometrica e la media aritmetica dello spettro di potenza di un segnale audio, e produce un singolo scalare nell'intervallo [0, 1] che quantifica quanto uno spettro è "piatto" (rumoroso) rispetto a "piccato" (tonale). Introdotta formalmente da **Gray e Markel (1974)** nel contesto della predizione lineare del parlato, è diventata fondamentale nella codifica percettiva audio grazie al lavoro di **Johnston (1988)**, che la impiegò per stimare la tonalità di ogni banda critica e interpolare le soglie di mascheramento nei codec perceptual come MP3 e AAC. Oggi la SFM è uno dei descrittori spettrali più utilizzati in music information retrieval, voice activity detection, discriminazione parlato/musica e codifica audio, ed è standardizzata nello standard MPEG-7 come **AudioSpectralFlatness**. Il suo legame profondo con la teoria dell'informazione — dimostrato da **Dubnov (2004)**, che ha provato l'equivalenza con la dual total correlation — ne fa un ponte tra elaborazione del segnale e teoria dell'informazione.

---

## Definizione matematica e varianti della formula

### Formula canonica

Data una sequenza di **N** valori dello spettro di potenza $x(n) = |X(n)|^2$, la SFM è definita come:

$$\text{SFM} = \frac{\left(\prod_{n=0}^{N-1} x(n)\right)^{1/N}}{\frac{1}{N}\sum_{n=0}^{N-1} x(n)}$$

dove il numeratore è la **media geometrica** e il denominatore è la **media aritmetica**. Poiché il prodotto di molti valori può causare overflow o underflow numerico, la forma computazionalmente preferita utilizza la trasformazione logaritmica:

$$\text{SFM} = \frac{\exp\!\left(\frac{1}{N}\sum_{n=0}^{N-1} \ln x(n)\right)}{\frac{1}{N}\sum_{n=0}^{N-1} x(n)}$$

Questa formulazione è matematicamente equivalente ma **numericamente stabile**, ed è adottata da tutte le principali implementazioni software (librosa, Essentia, MATLAB).

### Variante per sotto-bande (MPEG-7)

Per una sotto-banda che comprende i bin da $b_1$ a $b_2$:

$$F(b) = \frac{\left(\prod_{k=b_1}^{b_2} c(k)\right)^{1/(b_2 - b_1)}}{\frac{1}{b_2 - b_1}\sum_{k=b_1}^{b_2} c(k)}$$

dove $c(k)$ rappresenta i coefficienti dello spettro di potenza all'interno della banda $b$.

### Spettro di potenza vs spettro di ampiezza

La definizione canonica (MPEG-7, Johnston 1988) utilizza lo **spettro di potenza** $|X(n)|^2$. Tuttavia, alcune librerie (Essentia, Meyda) calcolano la SFM sullo **spettro di ampiezza** $|X(n)|$. Madhu e Martin (2009) nel loro articolo "Note on measures for spectral flatness" analizzano entrambe le varianti. La scelta influenza i valori numerici ma non la direzione interpretativa: entrambe le versioni producono valori alti per spettri piatti e bassi per spettri piccati.

### Versione in dB e coefficiente di tonalità

Johnston (1988) introdusse la conversione in decibel e il **coefficiente di tonalità α**:

$$\text{SFM}_{\text{dB}} = 10 \cdot \log_{10}(\text{SFM})$$

Il range diventa **[−∞, 0] dB**, dove 0 dB indica rumore bianco e valori molto negativi indicano segnali tonali. Da questa misura si ricava il coefficiente:

$$\alpha = \min\!\left(\frac{\text{SFM}_{\text{dB}}}{-60},\ 1\right)$$

dove $\alpha = 0$ indica un segnale completamente noise-like ($\text{SFM}_{\text{dB}} = 0$), $\alpha = 1$ indica un segnale completamente tonale ($\text{SFM}_{\text{dB}} \leq -60$ dB), e $\alpha = 0.5$ corrisponde a $\text{SFM}_{\text{dB}} = -30$ dB. Questo coefficiente viene usato nei codec audio per **interpolare geometricamente** tra le soglie di mascheramento: l'offset per banda critica è $O_n = \alpha \cdot (14.5 + n) + (1 - \alpha) \cdot 5.5$ dB, dove $n$ è l'indice di banda Bark.

### Fondamento matematico: la disuguaglianza AM-GM

La SFM è limitata nell'intervallo **[0, 1]** grazie alla disuguaglianza tra media aritmetica e media geometrica (AM-GM): per valori non negativi, la media geometrica è sempre ≤ alla media aritmetica, con uguaglianza se e solo se tutti i valori sono identici. Inoltre, la SFM è **invariante per scala**: moltiplicare tutti i valori spettrali per una costante non cambia il risultato, poiché entrambe le medie si scalano linearmente. In pratica, un campione finito di rumore bianco produce SFM tipicamente intorno a **0.5–0.6**, non 1.0, perché lo spettro è piatto solo in valore atteso.

---

## Interpretazione percettiva e fisica del descrittore

La SFM misura il grado di **"piattezza"** di uno spettro, che corrisponde percettivamente alla distinzione tra **tonalità** (tonal) e **rumorosità** (noisy). Un segnale sinusoidale puro concentra tutta l'energia in un singolo bin frequenziale, producendo una SFM prossima a zero. Al contrario, il rumore bianco ideale distribuisce energia uniformemente su tutte le frequenze, producendo SFM = 1.

Johnston (1988) osservò empiricamente i seguenti range nella scala dB:

- **Segnali tonali** (organo, flauto, sinusoidi): SFM_dB prossimo a −60 dB o inferiore
- **Percussioni** (sezioni transitorie): da −5 a −15 dB
- **Parlato** (banda 200–3200 Hz): da −20 a −30 dB

La SFM cattura un aspetto complementare rispetto allo **Spectral Crest Factor**, che misura il rapporto tra il massimo e la media dello spettro. Il crest factor è sensibile a un singolo picco dominante, mentre la SFM considera la distribuzione globale attraverso la media geometrica.

### Equivalenza con la Wiener entropy

La SFM è **matematicamente equivalente alla Wiener entropy**, termine usato prevalentemente nell'analisi del parlato e nella bioacustica (Tchernichovski et al., 2000, per l'analisi del canto degli uccelli). Entrambe le misure esprimono lo stesso rapporto media geometrica/media aritmetica; la differenza è puramente terminologica.

### Connessione con la teoria dell'informazione (Dubnov, 2004)

Dubnov ha dimostrato che per processi gaussiani con densità spettrale di potenza $S(\omega)$, la SFM è legata al **Marginal Information Redundancy (MIR)**:

$$\text{SFM} = e^{-2\delta}$$

dove $\delta = H(x_n) - H(x_n | x^{n-1})$, ossia la differenza tra l'entropia marginale di un campione e l'entropia condizionata dati tutti i campioni precedenti. In termini continui:

$$\text{SFM} = \frac{\exp\!\left(\frac{1}{2\pi}\int \ln S(\omega)\,d\omega\right)}{\frac{1}{2\pi}\int S(\omega)\,d\omega}$$

Per processi non gaussiani, Dubnov introdusse la **Generalized SFM (GSFM)**: $\text{GSFM}(x) = \text{SFM}(x) \cdot e^{-2(J(\varepsilon) - J(x))}$, dove $J(\cdot)$ è la negentropia. La SFM è quindi equivalente al concetto di **dual total correlation** (mutua informazione), confermando che **un segnale con SFM alta è intrinsecamente meno predicibile**.

---

## Standard tecnici: MPEG-7 e impiego nei codec

### MPEG-7 AudioSpectralFlatness (ISO/IEC 15938-4)

Il descrittore **AudioSpectralFlatness** è definito nella Parte 4 dello standard MPEG-7 (ISO/IEC 15938-4:2002) come parte dei descrittori spettrali di basso livello. Le specifiche chiave includono:

- **Range frequenziale**: da **250 Hz a 16 kHz** (6 ottave)
- **Numero di bande**: **24 sotto-bande** a spaziatura **quarter-octave** (4 bande per ottava)
- **Frequenze di confine**: calcolate moltiplicando iterativamente per $2^{1/4} \approx 1.1892$ a partire da 250 Hz
- **Sovrapposizione**: le bande si sovrappongono del **10%** (la larghezza di banda calcolata viene moltiplicata per 1.1)
- **Spettro**: calcolato da FFT dello spettro di potenza con finestra di Hamming
- **Parametri temporali**: hop size di 30 ms, lunghezza finestra = 3× hop (~90 ms), FFT size = prima potenza di 2 ≥ lunghezza finestra

La matrice risultante di **24 bande × frame temporali** viene usata anche nel sistema di fingerprinting audio MPEG-7 (Audio Signature Description Scheme).

### Impiego nei codec audio

**AAC/MP3**: Il Psychoacoustic Model 2 di MPEG-1 Layer III e MPEG-2/4 AAC eredita direttamente l'approccio di Johnston. La SFM determina quanti bit allocare: **bande con SFM alta (noise-like) necessitano di meno bit** perché godono di maggiore mascheramento, mentre bande tonali richiedono maggiore precisione. Taghipour et al. (2013–2014, Fraunhofer IIS) svilupparono la **Partial Spectral Flatness Measure (PSFM)**, che calcola la SFM su filtri IIR passa-banda individuali (104 bande) con risoluzioni DFT adattive (4096, 2048, 1024 campioni per basse, medie e alte frequenze).

**Opus**: Il codec Opus utilizza la spectral flatness nel layer SILK per il **Voice Activity Detection (VAD)** e le decisioni di **Discontinuous Transmission (DTX)**. Il segnale viene suddiviso in 4 sotto-bande tramite filterbank half-band. Dalla versione 1.3 (2018), una rete neurale ricorrente (RNN) incorpora features spettrali inclusa la flatness per migliorare la classificazione parlato/musica.

**ITU-R BS.1387 (PEAQ)**: Lo standard PEAQ non calcola esplicitamente la SFM come Model Output Variable, ma il suo modello psicoacustico incorpora implicitamente la distinzione tonale/noise attraverso pattern di eccitazione, soglie di mascheramento e spreading frequenziale. Usa una decomposizione in **109 bande a 1/4 di Bark** (versione Basic) o 55 bande a 1/2 Bark (versione Advanced).

---

## Il problema dei bin a zero e le sue soluzioni

Il **difetto fondamentale** della SFM è che un singolo bin frequenziale con valore zero azzera la media geometrica, producendo SFM = 0 indipendentemente dal contenuto di tutti gli altri bin. Questo è particolarmente problematico con frame silenziosi o quasi-silenziosi. Sono state documentate diverse strategie:

**Aggiunta di epsilon (ε)**: L'approccio più comune prevede l'aggiunta di una piccola costante positiva a tutti i valori dello spettro prima del calcolo: $x'(n) = \max(\varepsilon, x(n))$. In librosa, il parametro `amin` ha valore default di **1e-10**. Tuttavia, come osservato da Madhu (2009), "adding a bias provides numerical stability, but the output of the measure remains inconsistent" — il bias è euristico e un singolo zero in una sequenza altrimenti piatta produce comunque valori artificialmente bassi.

**Misura basata su entropia (Madhu, 2009)**: Nel suo articolo "Note on measures for spectral flatness" (Electronics Letters), Madhu propose una misura alternativa $F_2$ basata sull'entropia di Shannon dello spettro normalizzato: $F_2 = \exp(H(\mathbf{p}))$ dove $H$ è l'entropia di Shannon della distribuzione normalizzata. Questa misura **degrada gracefully**: per una sequenza piatta con un singolo zero, $F_2 \approx 1$ (come atteso), mentre per una sequenza piccata $F_2 \approx 0$.

**LSFM — media spettrale a lungo termine**: Ma e Nishihara (2013) proposero la **Long-term Spectral Flatness Measure**, che media stime spettrali di $R$ frame consecutivi con il metodo di Welch-Bartlett prima di calcolare la SFM. Questo riduce la probabilità di bin a zero attraverso l'averaging temporale.

**Calcolo su bin attive**: Alcune implementazioni escludono i bin con valore zero dal calcolo, modificando il denominatore effettivo. L'implementazione di riferimento OpenAE, ad esempio, restituisce direttamente 0.0 se rileva bin nulli: `if np.any(ps == 0): return 0.0`.

Un aspetto critico è il **comportamento con frame silenziosi**, dove tutti i bin sono circa zero. Il rapporto 0/0 è indefinito, e le implementazioni divergono: librosa restituisce valori prossimi a **1.0** (poiché il floor ε rende tutti i bin uguali, producendo uno spettro "piatto"), mentre Essentia restituisce **0.0** o lancia un'eccezione. Questa è la differenza implementativa più significativa tra le librerie.

---

## Relazione con entropia spettrale e altri descrittori

### Spectral entropy vs SFM

Entrambe misurano l'uniformità spettrale, ma con operazioni matematiche diverse. L'entropia spettrale normalizzata è definita come:

$$H_{\text{norm}} = \frac{-\sum_{m=0}^{M-1} p(m) \cdot \log_2 p(m)}{\log_2 M}$$

dove $p(m) = x(m) / \sum x(m)$ è lo spettro normalizzato trattato come distribuzione di probabilità. **SFM e entropia spettrale sono correlate monotonicamente** — entrambe crescono con l'uniformità — ma non sono proporzionali. Misra et al. (2004) notarono che l'entropia spettrale "measures the power spectral flatness" e la descrissero come Wiener entropy. L'entropia di Shannon è tuttavia più **robusta ai bin a zero**, il che la rende l'alternativa preferita nei casi in cui la SFM tradizionale è instabile.

### Spectral Crest Factor

Lo **Spectral Crest Factor** (SCF) $= \max(x(n)) / \text{mean}(x(n))$ è l'**inverso concettuale** della SFM. Produce valori alti per segnali tonali (picco dominante) e bassi per segnali noise-like. La differenza chiave è che lo SCF dipende esclusivamente dal valore massimo, rendendolo sensibile a un singolo picco, mentre la SFM considera l'intera distribuzione tramite la media geometrica. Lerch (2012) e Peeters (2011) li classificano come misure complementari nella stessa famiglia di descrittori di "piattezza".

### Spectral kurtosis

La curtosi spettrale misura la "peakiness" dello spettro dal quarto momento statistico, quantificando la non-gaussianità della distribuzione. È concettualmente affine alla SFM ma cattura aspetti diversi: è più sensibile ai picchi outlier, mentre la SFM è più sensibile alla forma globale della distribuzione. Entrambe diminuiscono con l'aggiunta di rumore.

---

## Implementazioni open source a confronto

Le principali librerie implementano la stessa formula fondamentale ma con scelte progettuali divergenti che possono produrre **risultati significativamente diversi** sullo stesso segnale.

**librosa** (Python) offre `spectral_flatness()` con parametri `power=2.0` (spettro di potenza di default) e `amin=1e-10` come floor per evitare log(0). L'FFT di default è 2048 campioni con hop di 512 e finestra Hann. Il calcolo segue `gmean = exp(mean(log(max(amin, S)))) / mean(S)`. La scelta di amin=1e-10 fa sì che **frame silenziosi producano flatness ≈ 1.0**, un comportamento che può essere controintuitivo.

**Essentia** (C++/Python) separa il calcolo in due algoritmi: `Flatness` (scala lineare) e `FlatnessDB` (scala dB, $10 \cdot \log_{10}$). L'algoritmo `Flatness` è un'operazione generica su array, non prescrive il tipo di spettro in input; nella pipeline standard `LowLevelSpectralExtractor`, riceve lo **spettro di ampiezza** (non di potenza). Non ha parametro epsilon: **bin a zero producono flatness = 0** e input vuoti generano eccezione.

**MATLAB Audio Toolbox** offre `spectralFlatness(x, f)` con supporto nativo per **sotto-bande** tramite il parametro `Range` e la possibilità di restituire separatamente media aritmetica e geometrica. Cita esplicitamente Johnston (1988) come riferimento. Opera su spettro di potenza.

**MIRtoolbox** (MATLAB) implementa `mirflatness` nella pipeline `miraudio → mirframe → mirspectrum → mirflatness`, operando sullo spettro di ampiezza prodotto dalla FFT. Descrive esplicitamente la misura come "Wiener entropy".

**Meyda** (JavaScript) calcola `spectralFlatness` sullo `amplitudeSpectrum` (ampiezza, non potenza) con FFT di default a 512 punti e finestra Hanning. Non ha gestione dei bin a zero.

**aubio** (C/Python) **non implementa** la SFM come rapporto media geometrica/aritmetica. Il suo `specdesc` include la curtosi spettrale, che misura "flatness" nel senso statistico del quarto momento, ma non è equivalente alla SFM.

| Libreria | Spettro | FFT default | Gestione zeri | dB nativo | Sotto-bande |
|----------|---------|-------------|---------------|-----------|-------------|
| librosa | Potenza | 2048 | amin=1e-10 → flatness ≈ 1 | No | No |
| Essentia | Ampiezza* | 2048 | Nessuna → flatness = 0 | Sì (FlatnessDB) | No |
| MATLAB | Potenza | 1024 | Non documentata | No | Sì (Range) |
| MIRtoolbox | Ampiezza | Configurabile | Non documentata | No | Via filterbank |
| Meyda | Ampiezza | 512 | Nessuna → flatness = 0 | No | No |

*Nella pipeline LowLevelSpectralExtractor; l'algoritmo Flatness è generico.

---

## Applicazioni principali della Spectral Flatness

### Discriminazione parlato/musica e VAD

L'impiego più classico della SFM è nella **discriminazione parlato/musica** (Scheirer e Slaney, 1997, ICASSP). Il parlato possiede una struttura spettrale armonica concentrata nelle regioni formantiche che produce SFM relativamente bassa, mentre molti generi musicali — specialmente quelli percussivi o con ampia larghezza di banda — possono produrre valori più alti. Nella **Voice Activity Detection**, Ma e Nishihara (2013) dimostrarono che la loro Long-term SFM (LSFM) nella banda 500 Hz – 4 kHz superava gli standard G.729B, AMR1 e AMR2 in 12 tipi di rumore a SNR da −10 a +10 dB. L'approccio sfrutta una soglia adattiva basata sulle ultime 100 misure LSFM.

### Codifica audio percettiva

Nella codifica audio, la SFM è il meccanismo primario per determinare il **trade-off tra mascheramento tonale e noise**: bande con alta SFM (noise-like) mascherano più efficacemente il rumore di quantizzazione, richiedendo meno bit. Questo principio, introdotto da Johnston (1988), è alla base di tutti i codec percettivi moderni da MP3 ad AAC. Nel codec **Opus**, la flatness spettrale guida le decisioni DTX e la scelta tra modalità SILK (parlato) e CELT (musica).

### Audio fingerprinting e MIR

Nello standard MPEG-7, i 24 valori di flatness per frame costituiscono parte dell'**Audio Signature Description Scheme** per l'identificazione di contenuti audio. In MIR, la SFM viene utilizzata come feature per classificazione di genere, riconoscimento di strumenti, segmentazione audio (Izmirli, 2000) e rilevamento della voce cantata in musica polifonica.

### Applicazioni non convenzionali

La SFM (come Wiener entropy) trova applicazione anche in **bioacustica** (analisi del canto degli uccelli, Tchernichovski et al., 2000), **monitoraggio strutturale** (rilevamento di cambiamenti di rigidezza in strutture metalliche tramite variazioni dell'uniformità spettrale delle vibrazioni) e persino nell'**analisi EEG** per il rilevamento di crisi epilettiche.

---

## Limiti, critiche e casi in cui la SFM non è informativa

La SFM presenta limitazioni strutturali che ne condizionano l'affidabilità in scenari specifici. I **segnali tonali a banda larga** — come toni complessi con numerose armoniche — possono produrre valori di SFM moderati nonostante siano percettivamente chiaramente tonali, perché l'energia è distribuita su molti bin anche se concentrata in picchi discreti. Analogamente, il **rumore colorato** (rosa, marrone) produce valori intermedi che si sovrappongono al range del parlato, generando ambiguità classificatoria.

La SFM è una **metrica globale** (o per banda) che non cattura la struttura locale dello spettro: due segnali con la stessa SFM possono suonare completamente diversi se uno ha pochi picchi forti e l'altro molti picchi moderati. Come notato nella letteratura sul watermarking audio (Filler et al., 2011), "as any global metric, [SFM] fails to capture local spectral characteristics", motivando la combinazione con l'Unpredictability Measure per stime di tonalità più accurate.

La **sensibilità ai parametri FFT** è significativa: finestre più lunghe forniscono migliore risoluzione frequenziale (essenziale per segnali a banda stretta) ma peggiore risoluzione temporale, mentre finestre corte producono spettri artificialmente più piatti che sovrastimano la SFM. La soluzione proposta da Taghipour et al. con la PSFM — DFT di lunghezze diverse per diverse regioni frequenziali — replica la risoluzione variabile del sistema uditivo ma aggiunge complessità computazionale.

Infine, il confronto tra implementazioni full-spectrum (come in Lerch) e per sotto-bande (come in MPEG-7 e Peeters) rivela un trade-off fondamentale: la **SFM full-spectrum** è semplice e produce un singolo scalare, ma media informazioni di bande con carattere tonale/rumoroso diverso; la **SFM per sotto-bande** è percettivamente più rilevante e permette decisioni di codifica per banda, ma produce un vettore di valori e richiede la definizione di confini di banda appropriati.

---

## Conclusione

La Spectral Flatness Measure è un descrittore audio dalla formulazione matematica elegante — un semplice rapporto tra medie — ma dalle implicazioni profonde: è simultaneamente una misura geometrica della distribuzione spettrale, un indicatore percettivo di tonalità, e un concetto information-theorico equivalente alla dual total correlation. La sua debolezza strutturale più critica — il collasso a zero per un singolo bin nullo — è stata affrontata con soluzioni che vanno dall'aggiunta di epsilon (librosa) alla sostituzione con misure basate su entropia di Shannon (Madhu, 2009), ma nessuna è pienamente soddisfacente: le implementazioni attuali producono risultati divergenti sugli stessi segnali silenziosi (librosa → 1.0, Essentia → 0.0), un'incoerenza che chi lavora con pipeline multi-libreria deve gestire esplicitamente. La comprensione del funzionamento interno di questo descrittore — inclusa la scelta tra spettro di potenza e ampiezza, la definizione delle bande, e la strategia di gestione dei bin nulli — è essenziale per qualsiasi applicazione che ne faccia uso critico.