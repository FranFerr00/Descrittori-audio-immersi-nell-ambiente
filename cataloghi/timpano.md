# Catalogo timpano — osservazioni sui descrittori

Prime osservazioni numeriche sul catalogo `segnali/francesco/timpano/`
(10 campioni ufficiali, vedi `segnali/francesco/timpano/docs/schede/timpano.md`).

> **Attenzione:** questo non e' un timpano tradizionale ma un **timpano
> aumentato elettromagneticamente**. In questo catalogo la pelle non
> viene mai colpita: viene eccitata per **induzione elettromagnetica**,
> cioe' tenuta in risonanza da un campo magnetico pilotato. Di
> conseguenza **non c'e' nessun transiente percussivo da bacchetta**:
> tutto il sample, dai primi millisecondi in poi, e' un tono sostenuto
> attivo. Quelli che nei CSV appaiono come "attacchi" con centroid alto
> e flux forte non sono colpi meccanici ma **inviluppi d'attacco del
> tono sostenuto** (il circuito che si "accende" e porta la pelle in
> regime), oppure transitori inarmonici della fase di attivazione del
> campo. In questo catalogo lo strumento e' quindi concettualmente piu'
> simile a un oscillatore/fiato sostenuto che a una percussione.
>
> I gesti impulsivi (colpi di bacchetta/mallet vero e proprio) saranno
> oggetto di un **catalogo successivo**, ancora da registrare, in cui
> il timpano verra' colpito normalmente. La pipeline e i 16 descrittori
> resteranno gli stessi: cambiera' solo la lettura, perche' un colpo
> reale produce un vero transiente percussivo seguito da un decadimento
> fisico, non da un regime sostenuto attivo.

I valori qui sotto sono estratti direttamente dai CSV
`analisi/NNN/NNN_hann_ov50_48000hz_analisi.csv` (frame-per-frame, FFT 8192,
hop 4096, Hann, **banda piena 48 kHz** = Nyquist dei 96 kHz, downmix omni dei
4 canali). Le medie e le deviazioni standard sono calcolate sui frame di ogni
singolo campione.

> **Aggiornamento banda (2026-06-19).** La tabella delle dinamiche fisse e la
> sua interpretazione sono state rigenerate a **banda piena (48 kHz)**, per
> allineare il catalogo al corpus e al paper. I conteggi `N val/tot` non cambiano
> (il gate e' sul picco raw, indipendente dalla banda). Due cose da tenere
> presenti a banda piena: lo **spread del piano** ha media gonfiata (102 Hz) da
> pochi frame d'attacco a banda larga, ma la mediana resta ferma (~17 Hz), in
> linea con gli altri tenuti; **TPR** riflette anche un aggiornamento di
> definizione (ora in dB, non piu' una frazione ~1). Anche la sezione
> "Dinamiche variabili" e' stata ricalcolata a banda piena con un metodo
> nuovo ed esplicito (vedi la nota di quella sezione).

> **Aggiornamento metodologico (2026-04-09).** I valori riportati qui
> sotto usano i due gate aggiunti ad `analisi.py`: `--gate-dbfs -65`
> (hard floor sul rumore digitale) e `--gate-rel-db -30` (skip dei
> frame con peak piu' di 30 dB sotto il peak globale del file). Senza
> gate i frame ai bordi del file (rumore di sala durante l'attacco e
> il rilascio del circuito di induzione) entravano nelle medie con
> centroid e spread arbitrari, gonfiando in modo sostanziale i numeri
> del regime sostenuto. Le tabelle precedenti che davano per il
> timpano spread tipici di 127-310 Hz erano dominate da quei frame
> spuri: i valori reali del regime sono molto piu' bassi e molto piu'
> vicini a quelli di una sinusoide pura a 100 Hz. **La direzione dei
> trend dinamici e' rimasta la stessa, ma le magnitudini si sono
> ridimensionate parecchio.**

## Dinamiche fisse (p, mf, f1, f2, mf2)

| descrittore  | p (004) | mf (005) | f1 (006) | f2 (007) | mf2 (008)* |
|--------------|---------|----------|----------|----------|------------|
| N val/tot    | 161/180 | 151/185  | 175/229  | 152/185  | 19/45      |
| centroid     | 98      | 99       | **109**  | 103      | 919        |
| spread†      | 102     | 34       | **52**   | 43       | 2853       |
| rolloff      | 106     | 107      | **121**  | 107      | 1704       |
| slope        | -2.98   | -2.08    | -2.84    | -2.41    | -4.37      |
| obsir_std    | 0.411   | 0.664    | 0.589    | 0.596    | 0.228      |
| flatness     | 0.098   | 0.088    | 0.097    | 0.096    | 0.152      |
| crest        | 9.87    | 10.1     | **11.3** | 10.5     | 64.0       |
| skewness     | 5.67    | 5.41     | 6.15     | 5.63     | 12.8       |
| kurtosis     | 155     | 62       | 56       | 46       | 231        |
| entropy      | 0.107   | 0.106    | 0.106    | 0.106    | 0.190      |
| tonality     | 0.170   | 0.177    | 0.170    | 0.170    | 0.145      |
| tpr          | 26.9    | 26.7     | 23.0     | 23.5     | -14        |
| flux         | 3.4e-4  | 6.3e-4   | 9.5e-4   | 9.6e-4   | 5.3e-4     |
| irregularity | 39      | 50       | **74**   | 70       | 256        |
| zcr          | 0.00202 | 0.00200  | 0.00203  | 0.00203  | 0.00544    |

\* 008 mf2 e' un caso anomalo, vedi sotto. Anche con gate restano solo 19 frame su 45.

† Spread del piano (004): la **media** e' 102 Hz, gonfiata a banda piena da pochi
frame d'attacco a banda larga; la **mediana** e' 17 Hz, in linea col baseline degli
altri tenuti (mediane 17/27/36/37 da p a f2). Lo spread resta quindi fermo come prima.

### Il centroid quasi non si muove con la dinamica

Sul timpano **centroid, spread e rolloff sono praticamente fermi al
baseline della fondamentale (~100 Hz, ~30 Hz mediano, ~107 Hz) per tutte
le dinamiche**. Il centroid va da 98 a 109, una variazione del 10% su
valori bassissimi, difficilmente significativa. Lo spread, a banda piena,
ha media gonfiata sul piano (102 Hz) dai frame d'attacco a banda larga,
ma la sua **mediana** resta ferma (17→37 Hz da p a f2): il frame tipico
non si muove. Il comportamento e' molto diverso dal clarinetto, dove la
dinamica si riflette sui descrittori di forma con fattori 5-7x.

**Perche':** questo timpano in regime sostenuto e' di fatto
indistinguibile da una sinusoide pura a 100 Hz su quasi tutti i
descrittori (vedi `sine_100hz.md`). I valori dei tenuti puliti
(centroid ~98-110, spread mediano ~17-37, rolloff ~106-121) sono
praticamente sovrapposti a quelli di un riferimento sinusoidale a 100 Hz.
Lo strumento aumentato in regime non aggiunge contenuto
armonico nuovo al variare della dinamica, quindi la "forma" dello spettro
non si muove. Il clarinetto invece ha molti parziali attivi e una
dinamica piu' forte ne attiva di piu', spostando il centro di gravita'.

### Quali descrittori vedono la dinamica, allora?

**Irregularity (e marginalmente crest).** Crescono con la dinamica sui
tenuti, anche se con margini molto piu' piccoli di quanto credevamo
prima del gate:

| | p (004) | mf (005) | f1 (006) | f2 (007) |
|---|---|---|---|---|
| crest        | 9.87 | 10.1 | **11.3** | 10.5 |
| irregularity | 39   | 50   | **74**   | 70   |
| flux         | 3.4e-4 | 6.3e-4 | 9.5e-4 | 9.6e-4 |

Il salto fra piano e forte1 e' di +90% sull'irregularity (39→74), un
margine reale ma molto piu' piccolo del +90% che riportavamo prima del
gate (53→102, su numeri spuri 50% piu' alti del vero). Crest si muove
solo del 15% (9.8→11.3), al limite del rumore statistico. Il flux
quasi triplica (3.4e-4 → 9.5e-4), seguendo la stessa traiettoria, perche'
con il segnale piu' forte aumentano anche le piccole differenze
istantanee fra frame consecutivi.

**Conseguenza per il mapping:** sul timpano in regime sostenuto la
dinamica si legge **quasi solo dall'irregularity** (e in subordine dal
flux), e con un margine molto piu' stretto di quanto sembrava. Crest e
gli altri descrittori di distribuzione restano sostanzialmente fermi.
Questo e' l'opposto del clarinetto, dove la dinamica spinge in
modo evidente i descrittori di forma.

### 008 mf2 e' un outlier da verificare

008 ha solo 45 frame totali (circa 2 secondi contro i 7-10 s degli altri)
e con il gate ne sopravvivono solo **19**. Anche dopo la pulizia i
numeri restano completamente fuori scala rispetto al resto del catalogo:
- centroid 919 Hz (vs 98-109 degli altri tenuti puliti),
- spread 2853 (vs media 34-102),
- crest 64 (vs 9.9-11.3),
- TPR -14 dB (il piu' basso del catalogo, l'unico negativo),
- zcr 0.0054 (~2.7x gli altri).

Numericamente si comporta piu' come un rumore colorato che come un
tono sostenuto del timpano. Possibili spiegazioni: file tagliato male,
attivazione del circuito anomala (pelle che non entra in regime), o una
prova diversa finita nel catalogo per sbaglio. **Da riascoltare prima
di considerarlo dato.**

## Dinamiche variabili (cresc, dim, cresc-dim, dim-cresc)

> **Metodo (banda piena, 2026-06-19).** Sezione ricalcolata a 48 kHz con un
> metodo esplicito (lo stesso del clarinetto), al posto del vecchio calcolo non
> piu' riproducibile: solo **frame validi** (gated=0); 1 frame = 42.7 ms; tempi
> dalla colonna `time`. Riporto per ogni gesto la **quota di frame "in regime"**
> (centroid < 150 Hz), i **top-5 frame** per centroid/irregularity/flux/crest e
> la **traiettoria dell'irregularity** su 5 blocchi. Nota: alcuni campioni
> risultano oggi piu' "tutto-regime" di quanto descrivessero le vecchie note
> (es. 015 non ha piu' un picco brillante finale: i sample sono stati ritagliati
> dopo la prima stesura), e i numeri qui sotto riflettono i CSV attuali.

**Tabella delle medie sui gesti, post-gate (`-65 dBFS, rel -30 dB`):**

| sample              | n val/tot | centroid | spread (m/med) | rolloff | crest | irregularity | flux   |
|---------------------|-----------|----------|----------------|---------|-------|--------------|--------|
| 015 cresc           | 257/354   | 101      | 36/40          | 105     | 9.9   | 63           | 6.3e-4 |
| 016 dim             | 333/344   | 113      | 58/38          | 122     | 9.9   | 64           | 5.4e-4 |
| 018 dim-cresc lungo | 300/336   | 104      | 40/35          | 113     | 10.0  | 58           | 1.0e-3 |
| 023 dim-cresc corto | 519/576   | 106      | 48/40          | 111     | 10.0  | 64           | 5.7e-4 |
| 025 cresc-dim       | 634/651   | 102      | 36/40          | 105     | 10.0  | 64           | 3.2e-4 |

**Le medie sono praticamente identiche fra tutti i gesti, e identiche
ai tenuti puliti.** Centroid 101-113, spread mediano 35-40, irregularity
58-64. Visti dalla statistica aggregata, i cinque gesti variabili sono
cinque tenuti. La variazione dinamica c'e' ma sulle medie globali sparisce
per due ragioni: (a) in regime sostenuto la dinamica e' principalmente
*ampiezza*, e i descrittori spettrali sono in larga parte invarianti per
scala; (b) i gesti sono lunghi e in parte simmetrici, quindi porzioni piu'
forti e piu' deboli si compensano nella media.

**C'e' pero' un descrittore che traccia l'inviluppo dinamico anche quando
il centroide resta piatto: l'irregularity.** La sua traiettoria su 5
blocchi segue il nome del gesto: 016 dim scende (104 → 69 → 69 → 47 → 32),
015 cresc sale (33 → 66 → 76 → 76 → 64), 025 cresc-dim sale e poi scende
(57 → 69 → 79 → 71 → 46). E' l'unico descrittore non invariante per scala
che cala/cresce davvero col livello, perche' quando l'ampiezza scende il
rumore di fondo emerge e la struttura dei picchi perde definizione.

L'altra informazione utile sta nei **frame di inviluppo d'attacco**, i
pochi istanti in cui il circuito di induzione porta la pelle in regime
(centroid alto, flux molto alto). Sotto, i due gruppi di campioni: quelli
che contengono l'attacco e quelli tagliati a regime gia' stabilito.

**Gruppo A — campioni con l'inviluppo d'attacco (016, 018, 023).**
Iniziano con il transitorio di attivazione del circuito: pochi frame a
centroid alto e flux molto alto, poi regime sostenuto per tutto il resto.

- **016 dim** (344 frame, ~14.7 s, 98% in regime): attacco nei primi
  ~0.4 s (centroid max 2219 Hz, crest 77, irregularity 815, flux 0.019),
  poi regime. Il "dim" si legge solo dall'irregularity, che cala in modo
  continuo (104 → 32 sui cinque blocchi); tutti gli altri descrittori
  spettrali restano al baseline del regime.
- **018 dim-cresc lungo** (336 frame, ~14.3 s, 99% in regime): l'attacco
  piu' brusco del catalogo (flux max **0.047** a ~0.4 s, centroid 865),
  poi ~11 s di regime stabile e un evento debolissimo attorno a 11.7 s.
  Il "dim-cresc" quasi non si legge: i descrittori spettrali vedono
  soprattutto l'attivazione iniziale.
- **023 dim-cresc corto** (576 frame, ~24.6 s, 99% in regime): attacco a
  inizio sample (centroid 1070, flux 0.012 a ~0.6 s) e un secondo evento
  attorno a 13.4 s. Il nome si riferisce all'andamento del gesto, non
  alla durata del segmento (e' il piu' lungo).

**Gruppo B — campioni tagliati a regime gia' stabilito (015, 025).**
Non contengono l'inviluppo d'attacco: l'attivazione del circuito e'
avvenuta prima dell'inizio del segmento. Qui non c'e' nessun transitorio
brillante, solo variazioni di livello applicate al tono sostenuto.

- **015 cresc** (354 frame, ~15.1 s, **100% in regime**): centroide max
  107 Hz su tutto il sample, nessun frame brillante; flux max 0.005, un
  ordine di grandezza sotto gli attacchi del gruppo A. Il crescendo si
  legge **solo** dall'irregularity, che sale (33 → 76 sui blocchi).
- **025 cresc-dim** (651 frame, ~27.8 s, **100% in regime**): il caso
  limite piu' duro. Centroide max **129 Hz** su 651 frame, flux max
  0.0015 (quasi due ordini sotto gli attacchi); centroid, rolloff, crest,
  tonality tutti costanti al baseline. Solo l'irregularity traccia il
  cresc-dim (57 → 79 → 46). **E' un gesto che i descrittori di forma non
  leggono affatto**: lo spettro del tono sostenuto e' gia' povero
  (fondamentale e pochi parziali), e una variazione di sola ampiezza non
  vi aggiunge contenuto; l'unico appiglio e' l'irregularity, non
  normalizzata per scala, che segue il livello.

## Cosa emerge

Dato che il timpano e' elettromagneticamente aumentato, la lettura va
riformulata rispetto a quella iniziale:

1. **Due regimi numericamente distinti.** I sample del timpano
   aumentato hanno tipicamente:
   - **inviluppo d'attacco del circuito** (primi 0.1-0.5 s se il
     sample inizia dall'attivazione): largabanda inarmonica, centroid
     alto, crest e irregularity alti, flux molto alto. E' il
     transitorio con cui il circuito porta la pelle in regime, non un
     colpo meccanico;
   - **regime sostenuto** (tutto il resto del sample, fino a decine di
     secondi): quasi-stazionario, centroid attorno a 100 Hz, rolloff
     ~105 Hz, tonality ~0.17, zcr ~0.002, crest ~10. Numericamente
     indistinguibile da una sinusoide pura a 100 Hz su quasi tutti i
     descrittori (vedi `sine_100hz.md`). E' il tono sostenuto attivo
     mantenuto dall'induzione.
   Alcuni sample (015, 025) sono stati tagliati a regime gia' stabilito
   e non contengono l'inviluppo d'attacco iniziale.

2. **I descrittori spettrali sono molto poco sensibili alle variazioni
   dinamiche del regime sostenuto.** Su 025 cresc-dim il centroid non
   supera mai 129 Hz su 651 frame: se una dinamica cresc-dim e' stata
   applicata durante il sostenuto, lo spettro non la sente. Questo
   perche' in regime sostenuto il contenuto spettrale e' gia' molto
   povero (fondamentale + pochi parziali, tutti entro il primo bin di
   rolloff), e una variazione di livello non aggiunge contenuto nuovo.

3. **L'irregularity e' l'unico descrittore spettrale che traccia
   l'inviluppo dinamico del regime sostenuto.** La sua traiettoria su 5
   blocchi segue il gesto: scende su 016 dim (104 → 32), sale su 015 cresc
   (33 → 76), sale e poi scende su 025 cresc-dim (57 → 79 → 46). Succede
   perche' l'irregularity e' sensibile alla struttura locale dei picchi,
   che guadagna o perde definizione al variare dell'ampiezza complessiva.

4. **Sul timpano aumentato in regime sostenuto la dinamica e' quasi
   solo ampiezza, e i descrittori spettrali tendono a ignorarla.**
   Per adesso non stiamo aggiungendo descrittori al set attuale, quindi
   la strada e' pensare **come leggere il livello implicito** dentro
   quelli esistenti: ad esempio l'irregularity (che non e' normalizzata
   per scala) scende effettivamente quando il livello cala, e puo'
   fare da indicatore indiretto. Resta il fatto che questo e' il caso
   limite piu' duro per la pipeline: se in futuro il corpus richiedera'
   davvero un descrittore di livello dedicato, si potra' valutare
   come cambiamento della roadmap descrittori.

5. **Sample da verificare ascoltando**:
   - **008 mf2** — troppo corto (45 frame) e spettralmente fuori scala;
   - **018 dim-cresc lungo** — il secondo inviluppo e' numericamente
     molto piu' piccolo del primo, difficile leggere il "dim-cresc";
   - **015, 025** — tagliati a regime gia' stabilito, il gesto
     dinamico e' solo sul livello e non viene visto dai descrittori
     spettrali attuali. Non sono rotti, sono semplicemente **fuori
     dalla portata della pipeline**.

## Conclusioni operative (aggiornate)

1. **Il descrittore che vede la dinamica dipende dallo strumento e dal
   regime.** Clarinetto = forma (centroid, spread, rolloff). Timpano
   aumentato in inviluppo d'attacco = distribuzione (crest,
   irregularity). Timpano aumentato in regime sostenuto = **solo
   irregularity** (l'unico non invariante per scala che scende
   davvero col livello); gli altri 15 restano saturi al baseline del
   tono sostenuto. Per adesso non aggiungiamo descrittori nuovi alla
   lista: il vincolo e' che qualunque descrittore usato lavori su
   tutti i segnali. Se in futuro un caso come questo dovesse richiedere
   davvero un descrittore di livello, lo si valutera' come
   cambiamento di roadmap e non come patch al volo.

2. **TPR e n_peaks non discriminano** neanche qui: a banda piena il TPR
   (ora in dB, non piu' una frazione ~1) resta attorno a 23-27 sui tenuti
   puliti, e il n_peaks non separa le dinamiche.

3. **Il baseline spettrale del regime sostenuto del timpano** (centroid
   ~100 Hz, rolloff 105 Hz, crest ~10, zcr 0.002, tonality 0.17) e'
   numericamente riconoscibile con una semplice soglia. Permette di
   segmentare automaticamente inviluppo d'attacco vs regime nelle
   registrazioni future.

4. **Il rolloff a 105 Hz in regime sostenuto non e' una saturazione
   numerica: e' il rolloff reale di un segnale quasi-sinusoidale a
   100 Hz.** Lo conferma il test sulla sinusoide pura a 100 Hz
   (vedi `sine_100hz.md`), che produce esattamente rolloff 105.47 Hz,
   identico al timpano in regime. La fondamentale dello strumento e'
   intorno a 100 Hz e il regime sostenuto contiene cosi' pochi
   parziali da essere indistinguibile numericamente da una sinusoide
   su *quasi tutti* i descrittori (tonality, zcr, slope, flatness,
   crest). Anche lo **spread** li separa di poco: 11.7 Hz (= 1 bin,
   limite di risoluzione) per la sinusoide contro una mediana di ~17 Hz
   per il timpano 004 in regime (la media, 102 Hz, e' gonfiata dai pochi
   frame d'attacco a banda larga). Il regime sostenuto e' quindi largo
   poco piu' di un bin: c'e' appena qualcosa oltre la fondamentale, ma
   cosi' poco da restare numericamente quasi indistinguibile da una
   sinusoide.

Da verificare nella prossima analisi: fino a che punto l'**irregularity
frame-per-frame** (non mediata sul sample) basta come proxy del livello
sul regime sostenuto del timpano, confrontando direttamente 025 cresc-dim
con i tenuti 004-007. Se emerge che la lettura del livello sul timpano
richiede davvero piu' di quanto i 16 descrittori attuali offrono, la
questione va portata come discussione di roadmap, non come patch al volo
(vedi `feedback_descrittori_chiusi.md`).
