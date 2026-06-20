# Spectral Centroid

## Definizione

Baricentro dello spettro: media pesata delle frequenze, dove i pesi sono le magnitudini.

centroide = somma( f(k) * |X(k)| ) / somma( |X(k)| )

Correlato percettivamente alla *brillantezza* o *sharpness* del timbro (Krimphoff et al. 1994, Grey 1977). E' una delle tre dimensioni percettive principali del timbro, insieme al tempo di attacco e alla struttura fine spettrale.

## Range e significato dei valori estremi

Range: **[0 Hz, max_freq]**, dove `max_freq` e' il limite superiore di analisi (10 kHz nel progetto). Espresso in Hz, si interpreta direttamente come "frequenza media" pesata dall'ampiezza.

- **Centroide → 0 Hz** (minimo): tutta l'energia e' concentrata sulla bin DC o sulle prime bin. Sul corpus non si raggiunge mai esattamente 0; il valore piu' basso e' la sinusoide a 100 Hz (≈ 440 Hz, vedi nota sotto) e il piano del clarinetto contrabbasso (207 Hz).
- **Centroide → max_freq** (massimo): tutta l'energia e' concentrata vicino al limite di banda. Sul corpus il **noise bianco** raggiunge ≈ 5000 Hz, esattamente a meta' del range come ci si aspetta da una distribuzione uniforme su [0, 10 kHz]. Un noise filtrato passa-alto si avvicinerebbe al massimo.

Sul corpus, valori tipici:
- **100 - 500 Hz** → sinusoidi gravi, fondamentali pure, strumenti in piano
- **500 - 2000 Hz** → segnali armonici medi (tanh, FM a basso indice, strumenti in mf/f)
- **2000 - 5000 Hz** → segnali ricchi di armoniche, noise filtrato, FM ad alto indice
- **~5000 Hz** → noise bianco, treno di impulsi (distribuzione uniforme su tutta la banda)

**Proprieta' fondamentali:**

1. *Invariante per scala di ampiezza.* Raddoppiare il segnale non cambia il centroide: moltiplicare tutti i |X(k)| per una costante non cambia il rapporto somma(f*|X|)/somma(|X|). Verificato sul corpus con la scalatura -30 dB in float: colonna sintetico e colonna -30 dB identiche su tutti i 45 segnali.

2. *Non invariante per trasposizione.* Suonare la stessa nota un'ottava sopra raddoppia il centroide anche se il timbro e' identico. Schubert e Wolfe (2006) hanno dimostrato che la brillantezza percepita dipende dal centroide assoluto, non dal centroide normalizzato per F0: suonare piu' acuto rende percettivamente piu' brillante, anche a parita' di struttura armonica.

3. *Robusto al bin esatto.* A differenza della flatness (che genera un valore patologico 0.945 quando la sinusoide e' allineata a un bin FFT), il centroide non mostra artefatti: bin esatto e fuori bin differiscono di meno di 6 Hz su 470, una differenza trascurabile.

4. *Stabile sui segnali deboli.* Crescendo e diminuendo di sinusoide pura non spostano il centroide (oscillazione < 9 Hz attorno a 440 Hz), mentre la flatness scendeva a 0.067 per instabilita' numerica nei frame a bassa ampiezza.

## Varianti della formula

La formula del centroide non e' unica. In letteratura e nei software MIR esistono almeno **sette varianti** documentate (vedi [`centroid/spectral_centroid_varianti.md`](centroid/spectral_centroid_varianti.md) per la trattazione completa):

1. **Magnitude classica** (la nostra): pesi = |X(k)|. Peeters 2004, librosa, Meyda, Essentia.
2. **Power spectrum**: pesi = |X(k)|^2. Enfatizza i picchi. Lerch 2023, MATLAB, MPEG-7 base.
3. **MPEG-7 logaritmica**: power spectrum + scala log (ottave vs 1 kHz). Percettivamente piu' uniforme.
4. **Sharpness di Zwicker**: loudness specifica + scala Bark + ponderazione g(z). Gold standard percettivo.
5. **Subband centroids**: un centroide per sotto-banda. Produce un vettore.
6. **Harmonic centroid**: solo sulle armoniche, richiede F0 detection.
7. **Log-magnitude**: pesi = log|X(k)|. Enfatizza le componenti deboli.

La verifica numerica sul clarinetto contrabbasso (diario 2026-04-10) ha mostrato che magnitude, power e MPEG-7 log danno valori molto diversi sullo stesso campione (rispettivamente 1133, 481, 323 Hz sul forte), ma **preservano l'ordine** delle dinamiche p1 < p2 < mf < f. I rapporti cambiano (5.5x, 4.0x, 3.0x) ma le osservazioni qualitative restano valide con qualunque scelta.

**Scelta per il progetto:** magnitude classica, per tre motivi: (1) escursione utile piu' grande sul corpus reale (5.5x piano/forte contro 3.0x della MPEG-7 log), (2) confrontabilita' diretta con la letteratura MIR dominante, (3) il gate `-65/-30` risolve il problema per cui la power spectrum sarebbe stata preferibile (pulizia dalle componenti deboli nei frame silenziosi).

La formula va dichiarata esplicitamente ogni volta che si cita un valore numerico di centroide: due pipeline che usano formule diverse possono differire di un fattore 3-5 sullo stesso segnale.

## Riferimenti

- **Peeters (2004)** p.13, sez. 6.1.1: baricentro dello spettro interpretato come distribuzione. Corrisponde a mpeg7:AudioSpectrumCentroid.
- **Lerch (2023)** p.43-44, sez. 3.5.1: stessa definizione. Nota variante con power spectrum e variante MPEG-7 con scala logaritmica.
- **Krimphoff et al. (1994)**: il centroide e' una delle tre dimensioni percettive principali del timbro (insieme a tempo di attacco e struttura fine spettrale).
- **Grey (1977)**: lavoro pionieristico, il centroide emerge come dimensione percettiva dominante nello scaling multidimensionale dei timbri.
- **Schubert e Wolfe (2006)**: la brillantezza percepita dipende dal centroide assoluto, non dal centroide normalizzato per F0.
- **Marui e Martens (2006)**: la sharpness puo' essere predetta dalla combinazione di centroide e spread.
- **Saitis et al. (2022)**: scale psicofisiche per centroide, spread e skewness.
- **Zwicker e Fastl (1999)**: modello di sharpness (centroide percettivo su scala Bark con ponderazione).

Software: librosa (magnitude, Hz), MATLAB `spectralCentroid` (power, Hz), Essentia `Centroid` (generico), openSMILE `cSpectral` (opzioni log/power/sharpness).

Standard: ISO/IEC 15938-4:2002 (MPEG-7 AudioSpectrumCentroid), DIN 45692:2009 (sharpness di Zwicker).

## Implementazione

Patch: `ambiente/descrittori/abstract/centroid.pd`
- Usa array di frequenze (`freqs`) e spettro di magnitudine
- Media pesata: somma(freq * mag) / somma(mag)
- Usato come riferimento dallo spread (che misura la dispersione attorno al centroide)

Pipeline di analisi: `analisi.py`
- FFT 8192, SR 96000 (risoluzione ~11.7 Hz per bin)
- Soglia relativa -60 dB dal picco del frame
- Gate `-65/-30` per escludere frame silenziosi ai bordi
- Calcolo sulle sole bin attive sopra soglia
- max_freq 10 kHz

## Relazione con altri descrittori

- **Spread**: misura la dispersione attorno al centroide (momento centrale del secondo ordine). Il centroide e' il punto di riferimento; lo spread dice quanto lo spettro e' largo attorno a quel punto.
- **Flatness**: complementare. Il centroide vede *dove* sta l'energia (frequenza del baricentro), la flatness vede *come* e' distribuita (uniforme o piccata). Insieme coprono due dimensioni ortogonali. La flatness distingue noise da tono (8x), il centroide traccia la ricchezza armonica e la dinamica strumentale (dove la flatness e' quasi cieca).
- **Rolloff**: correlato ma non identico. Il rolloff (85%) e' la frequenza sotto cui sta l'85% dell'energia; il centroide e' la media pesata. Su spettri simmetrici coincidono quasi, su spettri asimmetrici divergono.
- **Slope e decrease**: tutti descrittori di "forma" dello spettro. Lo slope misura la pendenza globale, il decrease la velocita' di decadimento dalle basse alle alte; il centroide riassume la posizione del centro di gravita'.

Nella zona RM del sistema interfantasia, il centroide dei 4 microfoni controlla la frequenza dell'oscillatore per la ring modulation.

## Test

### Corpus sintetico e modi di ripresa

Vedi [`centroid/analisi-centroid.md`](centroid/analisi-centroid.md) per il resoconto completo sui 45 segnali sintetici e le 5 condizioni di ripresa.

Risultati principali:

- **Sinusoide pura:** centroide = frequenza della sinusoide (440 Hz, errore < 1 Hz, std ~0)
- **Noise bianco:** 5000 Hz, meta' banda esatta (std 70 Hz)
- **Tanh drive 1→20:** da 481 a 1888 Hz (3.9x), traccia la ricchezza armonica della saturazione
- **FM idx 0.5→10:** da 549 a 4298 Hz (7.8x), la flatness era cieca a questa variazione
- **Miscele sin+noise:** curva monotona ripida, il 25% di noise sposta da 440 a 3158 Hz
- **Sotto microfono:** il noise cala da 5000 a ~3300 Hz (colorazione acustica dell'altoparlante e della stanza); i segnali tonali restano stabili o salgono leggermente per il rumore ambientale
- **Invarianza per scala:** confermata (colonna -30 dB identica al sintetico)
- **Bin esatto:** nessun artefatto

### Corpus strumentale (clarinetto contrabbasso)

Vedi [`centroid/analisi-centroid.md`](centroid/analisi-centroid.md) e `cataloghi/clarinettocb.md`.

- Dinamiche fisse: crescita monotona 207 Hz (p1) → 1133 Hz (f), rapporto 5.5x
- Gesti: il centroide traccia la traiettoria energetica (culmine a ~70% nei crescendo, decadimento monotono nei diminuendo)
- Varianti della formula: magnitude, power, MPEG-7 log danno numeri diversi ma preservano l'ordine

## Sviluppi

- [x] Analisi completa sui 45 segnali sintetici e 5 modi di ripresa
- [x] Confronto numerico tra varianti della formula (magnitude, power, MPEG-7 log)
- [x] Scelta motivata della formula per il progetto (magnitude classica)
- [x] Verifica sul corpus strumentale (clarinetto contrabbasso, 9 campioni)
- [ ] Foglio di famiglia "Forma" (con spread, rolloff, slope, decrease)
