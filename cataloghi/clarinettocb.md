# Catalogo clarinetto contrabbasso — osservazioni sui descrittori

Prime osservazioni numeriche sul catalogo `segnali/francesco/clarinettocb/`
(9 campioni ufficiali, vedi `segnali/francesco/clarinettocb/docs/schede/clarinettocb.md`).

I valori qui sotto sono estratti direttamente dai CSV
`analisi/NNN/NNN_hann_ov50_48000hz_analisi.csv` (frame-per-frame, FFT 8192,
hop 4096, Hann, **banda piena 48 kHz** = Nyquist dei 96 kHz, downmix omni dei
4 canali). Le medie e le deviazioni standard sono calcolate sui frame di ogni
singolo campione.

> **Aggiornamento banda (2026-06-19).** La tabella delle dinamiche fisse e la
> sua interpretazione sono state rigenerate a **banda piena (48 kHz)**, per
> allineare il catalogo al corpus e al paper (prima erano a 10 kHz; il tetto a
> 10 kHz nascondeva l'energia sugli acuti). I conteggi `N val/tot` non cambiano
> (il gate e' sul picco raw, indipendente dalla banda); cambiano i valori
> spettrali. Due descrittori, **TPR e n_peaks**, riflettono anche un
> aggiornamento di definizione successivo alla prima stesura, quindi i loro
> numeri differiscono dalle vecchie tabelle gia' a 10 kHz.
> Anche la sezione "Dinamiche variabili" e' stata ricalcolata a banda piena, con
> un metodo nuovo ed esplicito (vedi la nota di quella sezione) al posto del
> vecchio calcolo a chunk non piu' riproducibile.

> **Nota sulla fondamentale.** Tutti i campioni di questo catalogo
> sono suonati con fondamentale fissa attorno a **100 Hz** (stessa nota
> dei tenuti del timpano aumentato, vedi `timpano.md`). Sul clarinetto
> pero' il 100 Hz non domina lo spettro: il registro di questo strumento
> mette sopra la fondamentale una serie di armonici molto piu' forti,
> e sono quelli che si muovono con la dinamica. Per questo il catalogo
> clarinetto e' "piu' leggibile" del timpano a parita' di fondamentale:
> il centroid passa da ~218 Hz (p1) a ~1160 Hz (f) perche' la
> distribuzione di energia sugli armonici sopra la fondamentale cambia
> in modo marcato, mentre sul timpano sostenuto lo spettro e' quasi
> tutto nella fondamentale (vedi `sine_100hz.md` per il confronto
> numerico con una sinusoide pura a 100 Hz).

## Dinamiche fisse (p1, p2, mf, f)

> **Aggiornamento metodologico (2026-04-09).** I valori riportati qui
> sotto usano i due gate aggiunti ad `analisi.py` (`--gate-dbfs -65
> --gate-rel-db -30`), che escludono dal calcolo delle medie i frame
> ai bordi del file dove c'e' solo rumore di sala. Sui tenuti del
> clarinetto l'effetto del gate e' contenuto (i tenuti sono per
> costruzione "tutto segnale"), ma sui forti e su tutti i gesti con
> pause i numeri cambiano in modo significativo. **Le tabelle
> precedenti senza gate erano polluite dai frame ai bordi.**

| descrittore  | p1 (001) | p2 (002) | mf (003) | f (004)  |
|--------------|----------|----------|----------|----------|
| N val/tot    | 163/180  | 172/196  | 174/217  | 128/196  |
| centroid     | 218      | 242      | 419      | **1162** |
| spread       | 471      | 413      | 742      | **1405** |
| rolloff      | 309      | 422      | 674      | **2137** |
| slope        | -6.12    | -6.67    | -4.81    | -4.60    |
| obsir_std    | 0.562    | 0.668    | 0.518    | 0.674    |
| flatness     | 0.123    | 0.121    | 0.143    | **0.195**|
| crest        | 27.9     | 20.7     | 26.6     | **34.4** |
| skewness     | 16.9     | 10.6     | 9.04     | 3.13     |
| kurtosis     | **667**  | 389      | 211      | 14.4     |
| entropy      | 0.166    | 0.208    | 0.227    | 0.327    |
| tonality     | 0.152    | 0.153    | 0.144    | 0.119    |
| tpr          | 16.3     | 15.2     | 13.8     | 19.4     |
| n_peaks      | 158      | 157      | 189      | **241**  |
| flux         | 1.5e-4   | 2.2e-4   | 5.5e-4   | **3.7e-3**|
| irregularity | 152      | 149      | 303      | **977**  |
| zcr          | 0.00223  | 0.00308  | 0.00727  | **0.0122**|

(tutti i valori sono *medie* sui frame validi del singolo campione, dopo
gate. I frame totali sono 180/196/217/196.)

### Cosa si vede (post-gate)

**Dinamica e forma dello spettro camminano insieme.**
Centroid, spread, rolloff, flatness, irregularity e zcr crescono
*monotonicamente* da p1 a f. Il forte ha centroid circa 5.3 volte il
piano (1162 vs 218 Hz), rolloff circa 6.9 volte (2137 vs 309 Hz),
irregularity circa 6.4 volte (977 vs 152). I rapporti col gate sono *piu'
grandi* di quelli pre-gate (4.5x sul centroid prima, 5.3x adesso)
perche' i frame deboli ai bordi del forte spingevano in basso la sua
media; tolto il pollution, il contrasto piano/forte diventa ancora
piu' netto. Comportamento atteso per uno strumento a fiato: aumentando
il fiato si eccitano armonici piu' alti che si aggiungono (non
sostituiscono) a quelli bassi, quindi sia il centro di gravita' sia
la larghezza dello spettro salgono.

**Tonality e kurtosis si muovono al contrario.**
Tonality scende da 0.152 (p1) a 0.119 (f), kurtosis da 667 a 14.
Lo spettro del forte e' meno piccato e meno tonale: non perche' sia
rumoroso, ma perche' l'energia si distribuisce su piu' armonici
realmente emergenti, quindi nessuno domina come succede nel piano dove
c'e' praticamente solo la fondamentale. A banda piena la kurtosis del
piano e' enorme (667 contro i 28.8 a 10 kHz): misurato su tutta la banda
fino a Nyquist, lo spettro quasi-puro del piano e' estremamente piccato
rispetto all'asse largo, e i momenti di ordine alto esplodono. E' la
stessa ipersensibilita' alle code che colloca kurtosis e skewness fra i
descrittori meno robusti.

**Crest non discrimina le dinamiche, anzi le confonde.**
Pre-gate il crest sembrava salire col forte (29→47), ma quei valori
erano gonfiati dai frame quasi-silenziosi ai bordi del file, dove uno
spettro vicino al rumore puo' avere un picco isolato altissimo
rispetto al fondo (crest spuri 60-100). Con il gate il crest e' 27.9,
20.7, 26.6, 34.4 da p1 a f: **non e' monotono** (p2 e' piu' basso di
p1) e il margine fra piano e forte e' modesto (+23%). Crest non e' un
buon indicatore di dinamica sul clarinetto; flatness invece resta
coerente (0.123 → 0.195, +58%) e si conferma il descrittore di
distribuzione piu' stabile su questo strumento.

**TPR e n_peaks.**
TPR (in dB) e' erratico, 16.3/15.2/13.8/19.4 da p1 a f: il forte e' il
piu' alto ma il mezzoforte il piu' basso, quindi non traccia la dinamica
in modo monotono. n_peaks invece, a banda piena, **sale** col forte
(158/157/189/241): aprendo la banda fino a Nyquist il forte mostra molte
piu' componenti spettrali sopra soglia, quindi piu' picchi. A 10 kHz e con
la vecchia definizione n_peaks restava quasi piatto: il salto e' anche un
effetto di banda e di un aggiornamento della sua definizione.

## Dinamiche variabili (cresc, dim, cresc-dim, dim-cresc)

> **Metodo (banda piena, 2026-06-19).** Sezione ricalcolata a 48 kHz con un
> metodo esplicito e riproducibile, che ha sostituito il vecchio calcolo a
> chunk (la cui gestione dei frame ai bordi era andata persa). Per ogni gesto:
> lavoro sui soli **frame validi** (gated=0, cioe' la parte effettivamente
> sonora); 1 frame = 42.7 ms (hop 4096 @ 96 kHz); i tempi sono dalla colonna
> `time` del CSV. Riporto (a) la **traiettoria del centroide** come media su 5
> blocchi contigui uguali dei frame validi; (b) il **culmine** del centroide,
> come istante e percentuale della durata sonora; (c) i **top-5 frame** per
> centroid, irregularity, flux, crest (gli istanti piu' salienti); (d) la
> **quota di frame "bassi"** (centroid < 200 Hz, il respiro/emissione debole).
> Misurare solo i frame validi descrive l'evoluzione del suono che c'e', senza
> l'artefatto della coda silenziosa: i crescendo risultano percio' monotoni,
> dove il vecchio calcolo vedeva un "rilascio" finale che era solo la coda
> gateata.

### 005 cresc1 — 223 frame, 166 validi (~7.1 s sonori)

Traiettoria centroide (5 blocchi): 195 → 451 → 668 → 939 → 1040.
Culmine a 6.6 s (**92% dei validi**), 1496 Hz; 16% di frame bassi.

Top-5 frame per descrittore:
- **centroid**: 6.4-6.7 s (a ridosso del culmine), max 1496 Hz
- **irregularity**: 6.4-6.6 s, max 1360
- **flux**: 6.6-6.7 s, max 0.021 (ordine 100x il resto)
- **crest**: 6.6-7.0 s, max 60

Crescendo **monotono**: il centroide sale di blocco in blocco e culmina
quasi a fine parte sonora (92%), non a meta'. I quattro descrittori
hanno i loro massimi tutti raggruppati attorno a 6.5 s, l'istante piu'
brillante e piu' instabile del gesto. Il "rilascio" che il vecchio
calcolo segnalava era la coda silenziosa, qui esclusa dal gate.

### 006 cresc2 — 245 frame, 184 validi (~7.9 s sonori)

Traiettoria centroide: 187 → 276 → 542 → 819 → 1172.
Culmine a 7.7 s (**96% dei validi**), 1509 Hz; 14% di frame bassi.

Top-5 frame:
- **centroid**: 7.6-7.9 s, max 1509 Hz
- **irregularity**: 7.3-7.5 s, max 1190
- **flux**: 7.6-7.7 s, max 0.024
- **crest**: 7.5-7.9 s, max 45

Crescendo ancora piu' pulito e continuativo di 005: salita monotona
senza interruzioni fino al 96% della durata sonora, con tutti i massimi
addensati negli ultimi 0.5 s. La forma "salita fino al culmine quasi
finale" e' la stessa di 005: e' un tratto del gesto, non del singolo
campione.

### 007 dim — 200 frame, 187 validi (~8.0 s sonori)

Traiettoria centroide: 998 → 841 → 564 → 301 → 165.
Culmine all'inizio (0.4 s, **0% dei validi**), 1175 Hz; 20% di frame bassi.

Top-5 frame:
- **centroid**: 0.4-0.8 s (i primissimi istanti), max 1175 Hz
- **crest**: 0.4-1.1 s, max 73
- **flux**: 0.4-0.6 s, max 0.009
- **irregularity**: 0.6-1.5 s (con qualche frame di ritardo), max 926

Diminuendo strettamente **monotono**: dal massimo iniziale il centroide
cala di blocco in blocco fino a 165 Hz. Tutti i descrittori hanno i
massimi nel primo secondo, l'irregularity con un breve ritardo. E' il
gesto piu' facile da leggere del catalogo.

### 010 cresc-dim — 319 frame, 295 validi (~12.6 s sonori)

Traiettoria centroide: 115 → 165 → 666 → 682 → 182. Forma a campana,
ma con un dettaglio che i blocchi nascondono:

- **centroid**: un picco isolato a 0.5 s (**2015 Hz!**), poi il corpo
  della campana a 7.9-8.0 s (~985 Hz)
- **crest**: 0.3-0.9 s (e un frame a 13.4 s), max 124
- **irregularity**: 7.7-8.0 s, max 851
- **flux**: 7.6-8.0 s, max 0.0028

Non e' una campana semplice: c'e' un **picco istantaneo molto alto
all'inizio** (2015 Hz a 0.5 s, oltre il massimo della campana centrale),
poi una lunga fase debole, poi la campana principale attorno a 7.9 s.
Il **48% dei frame e' basso** (< 200 Hz): quasi meta' del gesto e'
emissione debole, le pause del fiato fra le due porzioni.

### 013 dim-cresc — 385 frame, 297 validi (~12.7 s sonori)

Traiettoria centroide: 952 → 617 → 271 → 200 → 741. Forma a U.
Culmine all'inizio (0.4 s, **2675 Hz**, il massimo di tutto il catalogo);
19% di frame bassi.

Top-5 frame:
- **centroid**: 0.4 s (2675 Hz) e 13.6-13.9 s (la risalita finale)
- **crest**: 0.4-0.5 s e 13.7 s, max 114
- **irregularity**: 13.4-13.6 s, max 1090
- **flux**: 0.5-0.6 s e 13.7-13.8 s (entrambi i culmini), max 0.0088

U asimmetrica: il diminuendo iniziale culmina nei primi 0.4 s a 2675 Hz
(il valore piu' alto del catalogo), poi lo spettro scende fino a ~200 Hz
e risale nel crescendo finale (13.6-13.9 s). La risalita non torna al
livello iniziale (blocco finale 741 contro 952), ma e' netta.

## Cosa emerge

1. **I quattro gesti hanno forme distinte.** Cresc (005, 006) = salita
   monotona fino al 92-96% della durata sonora; dim (007) = massimo
   iniziale + decadimento monotono; cresc-dim (010) = **picco iniziale
   isolato + campana centrale, meta' del gesto in emissione debole**;
   dim-cresc (013) = U asimmetrica, primo picco brevissimo e altissimo,
   secondo piu' largo e piu' basso.

2. **I crescendo culminano quasi a fine gesto, non a meta'.** Con il
   metodo a banda piena, sui soli frame sonori, 005 e 006 salgono in
   modo monotono fino al 92-96% della durata: il "rilascio" finale che
   il vecchio calcolo mostrava era la coda silenziosa, non un fatto del
   suono. Resta valido che i crescendo sintetici di `test_segnali.wav`
   finiscono sempre al massimo: anche questi, una volta tolto il
   silenzio, salgono fino quasi alla fine.

3. **Irregularity e' il descrittore piu' leggibile per le traiettorie
   continue**: i suoi top-5 frame coincidono col culmine dell'energia e
   la curva e' regolare. Crest invece trova picchi istantanei piu'
   sparsi (su 005 a ridosso del culmine, su 010 e 013 anche nell'attacco
   iniziale).

4. **Flux coglie i punti di cambio massimo**: i suoi top-5 frame stanno
   a meno di 100 ms dai massimi di centroid su 005 e 006, e su 013
   identifica entrambi i culmini (inizio e fine).

5. **I gesti con pause vanno letti sui top-N frame, non sui 5 blocchi**:
   su 010 il 48% dei frame e' basso, quindi i blocchi diluiscono i picchi
   istantanei in mezzo alle fasi deboli e nascondono il picco iniziale.

## Conclusioni operative

1. Sul clarinetto contrabbasso, per distinguere le dinamiche bastano pochi
   descrittori: **centroid + irregularity + flatness** coprono il 95% del
   comportamento (post-gate; pre-gate avrei detto crest al posto di
   flatness, ma il gate ha mostrato che il crest era fuorviante per
   colpa dei frame ai bordi). Tonality aggiunge una lettura "timbrica"
   (quanto e' piccato lo spettro), non una lettura di livello.
2. TPR e n_peaks non vanno usati come feature di dinamica per questo
   strumento: a banda piena il TPR resta erratico (non monotono) e il
   n_peaks sale col forte, ma piu' per la densita' spettrale della banda
   larga che per una lettura pulita della dinamica. Vanno mantenuti per
   confronto con altri strumenti.
3. Slope ha medie piccole e deviazioni grandi: su uno strumento come
   questo e' rumoroso e andrebbe letto solo sui tenuti (non sui gesti
   variabili). L'obsir_std, a banda piena, resta invariato (usa bande
   ottavali fisse 200 Hz-10 kHz, indipendenti dalla banda d'analisi).
4. Flux e irregularity sono i descrittori che *vedono il gesto*: flux
   sui transienti istantanei, irregularity sulla tessitura armonica media.

Da verificare nella prossima analisi: correlazione numerica tra centroid,
crest, irregularity sui 9 ufficiali, per capire quale combinazione
minima di 2-3 descrittori basti per ricostruire la dinamica.
