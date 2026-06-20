# Analisi della flatness sul corpus di test

Analisi del comportamento del descrittore `flatness` sulle tabelle di `segnali/tabelle/segnali_tabelle.md` (segnali sintetici) e `segnali/tabelle/confronto_modi_tabelle.md` (confronto sintetico vs modi di ripresa).

Parametri di analisi: FFT 8192, hop 4096 (50% overlap), finestra Hann, soglia relativa -60 dB dal picco, calcolo sulle sole bin attive, SR 96 kHz, `max_freq` 10 kHz. Tutto il corpus e' in WAV float32 (sia il sintetico generato da Csound, sia i tagli prodotti da `taglia_segnali.py`); le sorgenti `recs-002/003/004.wav` sono PCM_24, ma la conversione a float per il taglio e' esatta.

## Cosa misura (ripasso dalla ricerca)

Media geometrica / media aritmetica dello spettro, limite [0,1]. Intuitivamente: quanto uniformemente l'energia e' distribuita sulle frequenze. 0 = tutta l'energia in un bin, 1 = energia uguale su tutti i bin.

**Nota chiave:** la flatness *non* misura la ricchezza timbrica ne' il numero di parziali. Misura solo l'uniformita' statistica dello spettro. Una sinusoide pura e una tanh satura hanno flatness simile perche' entrambe hanno "spettro a righe su fondo zero", solo con numero di righe diverso.

## Comportamento sui segnali sintetici

### Famiglia noise/tonale (il test cardine)

| Segnale | Flatness |
|---|---|
| 02_noise_bianco | **0.846** |
| 17_noise100 | 0.846 |
| 01_sinusoide_440 | **0.104** |
| 13_sin100 | 0.104 |

Il rapporto ~8x tra i due estremi e' netto e stabile (std < 0.01). Questo e' il test che la flatness passa meglio.

Il noise non e' 1.0 ma 0.85. L'articolo di ricerca sulla SFM lo spiegava: su un campione finito il noise bianco da' tipicamente 0.5-0.6 con parametri da libreria. Si arriva a 0.85 perche' (a) la soglia relativa -60 dB esclude le bin morte, (b) l'FFT 8192 ha piu' bin, riducendo la varianza della media geometrica.

### Miscele sin+noise (14, 15, 16 → 17)

| % noise | Flatness |
|---|---|
| 0% | 0.104 |
| 25% | 0.543 |
| 50% | 0.713 |
| 75% | 0.802 |
| 100% | 0.846 |

Curva monotona ma non lineare: il 25% di noise sposta gia' a meta' strada (0.10 → 0.54). La flatness e' molto sensibile alla presenza di rumore anche in piccola dose, perche' basta riempire le bin vuote per far crollare la distanza tra media geometrica e aritmetica. Oltre il 50% la curva si appiattisce. E' un comportamento coerente con l'uso nei codec: la flatness serve a decidere "c'e' componente noise o no?", non a misurarne la quantita' con precisione.

### Noise bandpass (effetto del Q)

| Segnale | Q | Flatness |
|---|---|---|
| 06_noise_bp_q500 | 500 | 0.573 |
| 07_noise_bp_q200 | 200 | 0.481 |
| 08_noise_bp_q50 | 50 | 0.393 |

Piu' il filtro e' largo, piu' la flatness sale. Riduzione di circa 0.09 per ogni dimezzamento del Q. Qui la flatness funziona bene come stima inversa della larghezza di banda di un segnale rumoroso. E' uno dei pochi casi in cui si puo' leggere un valore intermedio in modo quantitativo.

### Tanh e FM (test di robustezza timbrica)

| Segnale | Drive/Idx | Flatness |
|---|---|---|
| 03_tanh_drive1 | 1 | 0.110 |
| 04_tanh_drive5 | 5 | 0.155 |
| 05_tanh_drive20 | 20 | 0.210 |
| 10_fm_idx05 | 0.5 | 0.150 |
| 11_fm_idx3 | 3 | 0.136 |
| 12_fm_idx10 | 10 | 0.142 |

La tanh ha un piccolo ma leggibile aumento con il drive (+0.10 da drive 1 a drive 20). Attenzione: tanh drive 1 e' 0.110, quasi identica a sinusoide pura 0.104. E tanh drive 20, che e' chiaramente percepita come molto piu' ricca armonicamente di una sinusoide, e' ancora solo 0.210, ben lontana dal noise. La flatness non quantifica la densita' armonica: quello e' compito del TPR o del numero di picchi.

L'FM e' quasi piatta (tutti attorno a 0.14). L'indice di modulazione cambia le bande laterali ma non sposta la flatness. Questo e' importante: un descrittore che distingue noise da tono ignora completamente la morfologia armonica.

### Bin esatto / fuori bin (limite numerico del calcolo)

| Segnale | Flatness |
|---|---|
| 24_bin_esatto_40 | **0.945** |
| 25_fuori_bin_40 | 0.104 |
| 26_bin_esatto_80 | **0.945** |
| 27_fuori_bin_80 | 0.104 |

Quando la frequenza del seno cade esattamente su un bin FFT la flatness schizza a 0.945, piu' alta del noise bianco stesso. Mezzo bin di disallineamento e' sufficiente a riportarla al valore "normale" 0.104.

**Spiegazione:** con soglia relativa -60 dB, se la sinusoide e' allineata al bin il leakage della Hann e' minimo e restano attivi pochissimi bin, tutti di valore confrontabile (il lobo principale della finestra e' molto piccato). Su questo insieme ridotto, media geometrica e aritmetica coincidono quasi del tutto e il rapporto GM/AM tende a 1. La flatness non sta misurando un'effettiva uniformita' spettrale: sta restituendo un **valore di limite** della propria formula su una distribuzione degenere (poche componenti, tutte simili). Mezzo bin di leakage in piu' aggiunge sidelobe asimmetriche e basta a romperla.

**Verifica.** L'ipotesi iniziale era che il valore 0.945 dipendesse dal rumore di quantizzazione del WAV 16-bit (e infatti sul vecchio `recs-001` precipitava a 0.266). Convertendo tutto il corpus a float32 e generando il nuovo `test_segnali_-30db` come scalatura esatta del sintetico, il valore resta **0.945** anche dopo -30 dB di guadagno. Conferma: e' una proprieta' geometrica del calcolo, non un effetto di formato. Il valore sopravvive alla scalatura ma collassa in presenza di microfono (vedi caso 3 sotto), perche' allora arrivano molti bin di rumore ambientale che rompono la condizione "poche bin attive".

**Implicazione per la taratura:** la flatness non e' affidabile quando meno di circa 5-10 bin sono attivi. Varrebbe la pena aggiungere una condizione minima (`if n_active < 10: return NaN`) oppure esporre `n_active` come descrittore separato per poter filtrare i valori dubbi. L'articolo di ricerca non lo menziona, e' venuto fuori dal corpus.

### Segnali dinamici (crescendo/diminuendo)

| Segnale | Min | Max | Media |
|---|---|---|---|
| 18_sin_crescendo | 0.067 | 0.104 | 0.103 |
| 19_sin_diminuendo | 0.071 | 0.104 | 0.103 |
| 20_sin_crescdim | 0.067 | 0.104 | 0.102 |
| 21_noise_crescendo | 0.819 | 0.864 | 0.846 |
| 22_noise_diminuendo | 0.823 | 0.864 | 0.844 |

Osservazione importante: il sin crescendo ha min 0.067, piu' basso del suo valore a regime 0.104. Questo significa che nei frame iniziali (ampiezza bassa) la flatness scende invece di salire. Intuitivamente ci si aspetterebbe l'opposto: ampiezza bassa → segnale sepolto nel noise numerico → flatness piu' alta.

La spiegazione sta nella soglia relativa: quando l'ampiezza del seno cresce lentamente, il picco cresce con lei, ma la soglia -60 dB e' sempre relativa a quel picco. Con pochissime bin attive (sin pulito) la flatness si avvicina al comportamento "bin esatto/fuori bin" descritto sopra. Il valore oscilla perche' il numero di bin sopra soglia cambia frame per frame in modo discreto.

Il noise dinamico invece resta stabile perche' ha sempre centinaia di bin attive e la statistica e' robusta.

**Lezione:** la flatness e' stabile solo su segnali ricchi (molti bin attivi). Sui segnali puri e deboli e' numericamente instabile, indipendentemente dall'ampiezza.

### Glissandi e microglissandi

| Segnale | Min | Max | Media | Std |
|---|---|---|---|---|
| 28_gliss_lento_200_2000 | 0.104 | 0.141 | 0.118 | 0.009 |
| 29_gliss_veloce_200_2000 | 0.145 | 0.169 | 0.157 | 0.008 |
| 31_gliss_micro_440_460 | 0.084 | **0.945** | 0.111 | 0.080 |

Il gliss veloce ha flatness media piu' alta del lento (0.157 vs 0.118), perche' il movimento rapido spalma energia su piu' bin nel frame (smearing spettrale): un descrittore stazionario "vede" un segnale piu' largo.

Il microgliss 440-460 mostra max 0.945 perche' in alcuni frame la frequenza passa esattamente su un bin FFT e scatta lo stesso limite numerico del bin esatto. Il movimento e' di soli 20 Hz, cioe' meno di 2 bin (risoluzione 11.7 Hz), quindi capita ripetutamente di passare in fase.

### Doppie sinusoidi (32-39)

Tutte nell'intervallo 0.089-0.204. Due sinusoidi danno flatness praticamente uguale a una sola. La flatness e' cieca al numero di componenti tonali, vede solo l'uniformita' globale.

## Comportamento sotto ripresa microfonica

I cinque "modi" sono:
- `sintetico`: il taglio diretto di `test_segnali.wav` (Csound, float32)
- `test_segnali_-30db`: lo stesso file scalato in float di -30 dB. Sostituisce il vecchio `recs-001` (che era WAV 16-bit attenuato e introduceva rumore di quantizzazione)
- `recs-002`: registrazione con microfono a 1 m dall'altoparlante (un altoparlante normale, non Stone)
- `recs-003`: microfono a 2 m, ambiente sporco (voci di sottofondo)
- `recs-004`: microfono a 2 m, ambiente pulito

### Caso 1: il noise perde flatness passando per il microfono

| Segnale | sintetico | -30 dB | recs-002 (1m) | recs-003 (2m sporco) | recs-004 (2m pulito) |
|---|---|---|---|---|---|
| 02_noise_bianco | 0.846 | 0.846 | 0.657 | 0.668 | 0.615 |
| 06_noise_bp_q500 | 0.573 | 0.573 | 0.314 | 0.310 | 0.309 |
| 07_noise_bp_q200 | 0.481 | 0.481 | 0.245 | 0.244 | 0.247 |
| 08_noise_bp_q50 | 0.393 | 0.393 | 0.204 | 0.204 | 0.207 |
| 17_noise100 | 0.846 | 0.846 | 0.662 | 0.675 | 0.661 |

Effetto molto evidente: la flatness del noise crolla di circa il 25-45% passando dal segnale puro al microfono. Il motivo e' fisico: l'altoparlante e la stanza hanno una risposta in frequenza non piatta, con risonanze e roll-off alle alte; il noise "bianco" captato e' in realta' noise colorato. La flatness sta correttamente misurando questa colorazione.

`test_segnali_-30db` e' **identico al sintetico** per tutti i rumori: e' la conferma empirica della **invarianza per scala** della flatness, proprieta' garantita dalla definizione (moltiplicare tutti i bin per una costante non cambia il rapporto GM/AM).

### Caso 2: le sinusoidi pure guadagnano flatness sotto microfono

| Segnale | sintetico | -30 dB | recs-002 | recs-003 | recs-004 |
|---|---|---|---|---|---|
| 01_sinusoide_440 | 0.104 | 0.104 | 0.113 | **0.187** | 0.154 |
| 13_sin100 | 0.104 | 0.104 | 0.161 | 0.121 | 0.165 |
| 18_sin_crescendo | 0.103 | 0.103 | 0.100 | 0.183 | 0.133 |

Effetto opposto: la sinusoide pura sale con la microfonazione, soprattutto a 2 metri. Il rumore ambientale e il riverbero aggiungono bin attive (fondo diffuso), lo spettro diventa meno concentrato. A 1 metro l'effetto e' debole, a 2 metri raddoppia.

La colonna `-30db` mostra di nuovo invarianza perfetta col sintetico (0.104). Nel vecchio corpus a 16-bit la sinusoide aveva 0.094 sotto `recs-001`: era l'unica vera anomalia attribuibile alla quantizzazione, ed e' sparita appena la scalatura e' stata fatta in float. La sinusoide pura ha pochissime bin attive, quindi era il caso piu' fragile al rumore di quantizzazione che si addensa sotto la soglia relativa.

**Convergenza:** noise da 0.846 → 0.66 e sinusoide da 0.10 → 0.18. La distanza tra "tonale" e "rumoroso" nella flatness si dimezza passando dalla sintesi al 2m. Resta pero' sempre distinguibile (0.66 >> 0.18).

### Caso 3: il bin esatto crolla solo con la ripresa microfonica

| Segnale | sintetico | -30 dB | recs-002 | recs-003 | recs-004 |
|---|---|---|---|---|---|
| 24_bin_esatto_40 | **0.945** | **0.945** | 0.104 | 0.121 | 0.095 |
| 26_bin_esatto_80 | **0.945** | **0.945** | 0.088 | 0.116 | 0.083 |

Il valore patologico 0.945 sopravvive intatto a -30 dB (era impossibile ottenerlo nel vecchio corpus a 16 bit), e collassa solo quando il segnale passa attraverso altoparlante e microfono. Letto al contrario: non basta abbassare l'ampiezza, serve aggiungere componenti spettrali. Il riverbero della stanza, la risposta non piatta dell'altoparlante e il rumore ambientale forniscono *abbastanza* bin attive per spostare la flatness fuori dal limite numerico, riportandola al valore tipico di una sinusoide pura microfonata (~0.10).

**Il bin_esatto e' quindi fragile in due sensi:**
1. Fragile al leakage FFT: mezzo bin di disallineamento (il caso "fuori bin") basta a riportare la flatness a 0.104.
2. Fragile a qualsiasi interazione acustica: appena lo spettro contiene piu' di una manciata di componenti, la condizione "poche bin attive tutte simili" si rompe.

Non e' una proprieta' del segnale ma del calcolo, e si manifesta solo su un seno digitale ideale generato in float64 e perfettamente allineato a un bin FFT. Non sopravvive nemmeno a una catena acustica banale.

### Caso 4: FM con alto indice aumenta flatness a distanza

| Segnale | sintetico | -30 dB | recs-002 | recs-003 | recs-004 |
|---|---|---|---|---|---|
| 10_fm_idx05 | 0.150 | 0.150 | 0.122 | 0.104 | 0.110 |
| 11_fm_idx3 | 0.136 | 0.136 | 0.133 | 0.157 | 0.162 |
| 12_fm_idx10 | 0.142 | 0.142 | 0.191 | **0.232** | 0.220 |

La FM a basso indice (bande laterali concentrate) si comporta come una sinusoide: scende leggermente a distanza. La FM a alto indice 10 (bande laterali larghe) sale da 0.142 a 0.232 con la microfonazione: le sue molte componenti interagiscono con il riverbero e il rumore come fosse un segnale semi-rumoroso. Solo a distanza la flatness distingue l'FM idx 10 dall'FM idx 0.5: sul segnale sintetico sono identiche, mentre nella ripresa reale l'indice alto emerge. Interessante inversione di significato tra analisi offline e analisi in ambiente.

### Caso 5: 2m sporco vs 2m pulito praticamente identici

Per quasi tutti i segnali, recs-003 (con voci di sottofondo) e recs-004 (pulito) danno valori molto vicini, differenze tipicamente < 0.03. Il rumore ambientale di fondo e' trascurabile rispetto alla modificazione imposta da altoparlante + aria. La flatness non riesce a usare quella differenza come segnale.

## Sintesi delle proprieta' emerse

**Cosa la flatness fa bene:**

1. Distingue noise da tono (8x di rapporto, stabile)
2. Misura larghezza di banda del noise filtrato (crescita lineare col Q)
3. Misura proporzione noise in una miscela (curva monotona, sensibile in basso)
4. Resiste alla saturazione (tanh) e alla FM: il descrittore non si confonde con la ricchezza armonica
5. Misura la colorazione spettrale imposta da altoparlante e stanza: e' una firma acustica del luogo di ripresa
6. Separa noise da tono anche dopo microfonazione (la distanza si riduce ma non si annulla)
7. E' invariante per scala di ampiezza (verificato sul `-30 dB` in float)

**Cosa la flatness non fa:**

1. Non conta i parziali (sin, 2sin, tanh drive 20 sono quasi indistinguibili)
2. Non misura la ricchezza timbrica in senso musicale
3. Non distingue indice FM sul segnale sintetico (funziona solo sotto ripresa)
4. Non e' affidabile su segnali con pochi bin attivi (bin esatto, sin a bassa ampiezza): diventa numericamente instabile

**Casi limite emersi:**

1. L'artefatto "bin-esatto" (flatness → 0.945) indica meno di circa 5 bin attivi. E' un limite del calcolo, non una proprieta' del segnale: sopravvive alla scalatura in float ma sparisce non appena interviene una catena acustica reale.
2. Sui crescendo/diminuendo di segnali tonali la flatness oscilla tra 0.067 e 0.104 senza significato musicale: e' rumore numerico della soglia relativa.
