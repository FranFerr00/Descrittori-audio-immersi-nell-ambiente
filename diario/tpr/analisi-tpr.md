# Analisi del TPR sul corpus di test

Parametri di analisi: FFT 8192, hop 4096 (50% overlap), finestra Hann,
soglia relativa -60 dB dal picco del frame, SR 96 kHz, max_freq 10 kHz.
Formula: TPR_dB = 10*log10(E_tonale/E_rumore), regola MPEG-1 7 dB, lobo ±1 bin.

Tutti i valori sono medie sui frame validi del campione (gate escluso).
Per i campioni strumentali: gate --gate-dbfs -65 --gate-rel-db -30.

## Comportamento sui segnali sintetici

### Test cardine: sinusoide vs noise

| Segnale               | TPR media | std  | n_peaks |
|-----------------------|-----------|------|---------|
| 01_sinusoide_440      | +18.1 dB  | 0.0  | 7.1     |
| 17_noise100 (bianco)  |  -6.7 dB  | 1.0  | 30.2    |

Rapporto segnale/rumore del descrittore: 24.8 dB di distanza, netta e
stabile. La sinusoide ha pochi picchi (7: la fondamentale piu' i lobi
della Hann riportati in piu' bin); il noise ha 30 picchi classificati
tonali per fluttuazione statistica, ma il loro contributo e' piccolo
rispetto al fondo.

Sul noise la std e' 1.0 dB: il descrittore fluttua perche' ogni frame
ha una realizzazione diversa del rumore. Sulla sinusoide la std e'
praticamente 0: segnale periodico, ogni frame e' identico.

### Miscele sin + noise

| Proporzione noise     | TPR media | n_peaks |
|-----------------------|-----------|---------|
| 0 % (sin pura)        | +18.1 dB  | 7.1     |
| 25%                   | +16.4 dB  | 31.5    |
| 50%                   | +10.8 dB  | 31.5    |
| 75%                   | +2.4 dB   | 31.0    |
| 100% (noise puro)     |  -6.7 dB  | 30.2    |

Curva monotona e quasi lineare in dB: ogni 25% di noise in piu' toglie
circa 6 dB al TPR. La n_peaks salta subito da 7 a 31 al primo 25% di
noise: basta un piccolo fondo rumoroso a generare molti nuovi picchi
che passano la soglia MPEG-1. Il TPR integra l'informazione meglio di
n_peaks da solo: con 31 picchi sia al 25% che al 100%, n_peaks non
distingue i due estremi, il TPR li separa di 23 dB.

### Tanh e saturazione

| Drive                 | TPR media | n_peaks |
|-----------------------|-----------|---------|
| tanh drive = 1        | +18.1 dB  | 11.6    |
| tanh drive = 5        | +18.3 dB  | 11.0    |
| tanh drive = 20       | +18.6 dB  | 11.0    |

La saturazione tanh aggiunge armoniche ma tutte superano la soglia 7 dB
(sono armoniche regolari, non noise). Il TPR sale di soli 0.5 dB da
drive 1 a drive 20. La n_peaks scende da 11.6 a 11.0: i picchi
armonici emergono chiaramente ma in numero simile, il drive alto
concentra l'energia su poche armoniche basse invece di distribuirla.

**Osservazione chiave:** la tanh non distingue la ricchezza timbrica.
Segnale drive=1 (quasi una sinusoide) e drive=20 (saturazione piena,
molto diverso al suono) danno TPR quasi identici. Per distinguere
i livelli di drive serve il centroide (che si sposta in alto col drive)
o n_peaks in relazione alla frequenza fondamentale.

### FM (modulazione di frequenza)

| Indice FM             | TPR media | n_peaks |
|-----------------------|-----------|---------|
| idx = 0.5             | +18.6 dB  | 15.6    |
| idx = 3               | +23.1 dB  | 29.2    |
| idx = 10              | +23.9 dB  | 30.0    |

A differenza della tanh, la FM mostra un salto netto da idx 0.5 a idx 3:
+4.5 dB e il doppio dei picchi. A indice alto le bande laterali FM sono
molte e forti; ognuna supera la soglia 7 dB e contribuisce all'energia
tonale. Il risultato e' che un segnale FM a alto indice ha TPR piu'
alto di una sinusoide pura (+23.9 vs +18.1). E' un comportamento opposto
all'intuizione "piu' e' complesso meno e' tonale": l'FM a alto indice
e' percettivamente piu' brillante e metallica, e il TPR lo registra
come piu' ricco di energia tonale (non come piu' rumoroso).

### Noise bandpass

| Q del filtro          | TPR media | n_peaks |
|-----------------------|-----------|---------|
| Q = 500 (stretto)     |  -6.8 dB  | 30.5    |
| Q = 200               |  -8.6 dB  | 28.5    |
| Q = 50 (largo)        |  -9.4 dB  | 29.2    |

Il noise bandpass da' TPR negativo indipendentemente dal Q. Contro
l'intuizione, il Q stretto da' TPR leggermente piu' alto (-6.8 vs
-9.4): dentro la banda stretta la distribuzione e' ancora irregolare
e qualche picco passa la soglia. Con Q piu' largo la distribuzione
intra-banda e' piu' uniforme e nessun bin emerge facilmente di 7 dB
dai vicini. In ogni caso i valori sono tutti sotto -6 dB, quindi la
distinzione da qualunque segnale tonale (+18 dB) e' netta (25 dB).

### Impulsi e treno di impulsi

| Segnale               | TPR media | n_peaks |
|-----------------------|-----------|---------|
| 09_impulsi_100 Hz     | +17.0 dB  | 99.0    |

Un treno di impulsi a 100 Hz ha armoniche regolari ogni 100 Hz fino a
10 kHz: 99 armoniche nei 9900 Hz del range. Tutte superano la soglia 7
dB. Il TPR (+17 dB) e' leggermente inferiore alla sinusoide pura
(+18.1 dB) perche' l'energia e' distribuita su molti lobi, non
concentrata; ma l'ordine preserva la distinzione dal noise.

### Glissandi

| Segnale                     | TPR media | std   | n_peaks |
|-----------------------------|-----------|-------|---------|
| gliss lento 200-2000 Hz     | +19.8 dB  | 2.2   | 14.3    |
| gliss veloce 200-2000 Hz    |  +8.0 dB  | 16.6  | 13.2    |
| microgliss 440-460 Hz       | +28.7 dB  | 9.2   | 12.3    |

Il gliss lento mantiene un TPR alto (simile alla sinusoide). Il gliss
veloce crolla a +8 dB con std altissima (16.6): quando la frequenza si
muove rapidamente, lo smearing spettrale sposta l'energia fuori dal
bin principale, il picco perde localizzazione e a volte non supera la
soglia 7 dB. La std alta indica che il descrittore varia molto
frame-per-frame durante il gliss veloce: in alcuni frame la frequenza
e' centrata su un bin (picco alto, supera 7 dB) e in altri e' a meta'
bin (due picchi simili, nessuno supera il vicino di 7 dB).

Il microgliss 440-460 ha TPR alto (+28.7 dB): in 20 Hz di variazione
la frequenza non si allontana mai abbastanza dal bin di partenza da
perdere la localizzazione. La std 9.2 indica variazione residua.

### Anomalia bin esatto

| Segnale               | TPR media | n_peaks |
|-----------------------|-----------|---------|
| sin bin esatto 40 Hz  | **+85.7 dB** | 29.0 |
| sin fuori bin 40 Hz   | +16.9 dB  | 8.3     |

Mezzo bin di disallineamento fa crollare il TPR da +85 a +17 dB.
Il caso bin-esatto e' un limite numerico del calcolo: quando tutta
l'energia sta nel lobo Hann ristrettissimo del bin, E_rumore scende
a epsilon e il rapporto E_ton/E_rui → infinito. Sul segnale digitale
puro il valore non e' significativo come descrittore; scompare alla
prima catena acustica (analogia con l'artefatto 0.945 della flatness
per lo stesso caso).

### Doppie sinusoidi

| Segnale               | TPR media | n_peaks |
|-----------------------|-----------|---------|
| 2sin 200+4000 Hz      | +24.7 dB  | 2.6     |

Due sinusoidi danno TPR piu' alto (+24.7) della sinusoide singola
(+18.1): due lobi tonali separati sommano piu' E_tonale con poco fondo.
La n_peaks e' 2.6 (vicino a 2): il TPR distingue "1 vs 2 componenti"
che la flatness e il centroide non distinguono.

## Comportamento sotto ripresa microfonica

I valori qui sono estratti dall'analisi full-file (non per-segmento):
ciascun file contiene 45 segmenti concatenati, quindi le medie
mescolano tipi di segnale diversi.

| Sorgente              | TPR media | std   | n_peaks |
|-----------------------|-----------|-------|---------|
| test_segnali (sint.)  | +15.4 dB  | 19.4  | 21.2    |
| test_segnali -30 dB   | +15.3 dB  | 19.6  | 21.8    |
| recs-002 (1 m)        | +10.3 dB  | 13.0  | 35.5    |
| recs-003 (2 m sporco) |  +9.0 dB  | 12.7  | 36.0    |
| recs-004 (2 m pulito) |  +9.0 dB  | 13.0  | 35.9    |

**Invarianza per scala:** sintetico e -30 dB differiscono di soli 0.04 dB
(verifica: il rapporto E_ton/E_rui non dipende dall'ampiezza).

**Effetto microfonazione:** il TPR scende di ~5 dB passando da sintetico
a 1 metro, e di ~1 dB ulteriore a 2 metri. La colorazione acustica
dell'altoparlante e il riverbero della stanza aggiungono componenti
diffuse che alzano il fondo rumoroso, abbassando il rapporto. La n_peaks
sale da 21 a 36: il microfono introduce picchi aggiuntivi dal rumore
ambientale e dall'accordatura acustica della stanza, ma questi picchi
sono rumorosi e contribuiscono poco all'E_tonale.

## Corpus strumentale

### Clarinetto contrabbasso

Campioni ufficiali (9). Fondamentale ~100 Hz.

| id  | gesto             | TPR media | n_peaks |
|-----|-------------------|-----------|---------|
| 001 | piano 1           | +14.8 dB  | 35.8    |
| 002 | piano 2           | +13.4 dB  | 35.1    |
| 003 | mezzoforte        | +11.1 dB  | 51.4    |
| 004 | forte             | +12.7 dB  | 56.8    |
| 005 | crescendo 1       | +13.2 dB  | 55.6    |
| 006 | crescendo 2       | +14.0 dB  | 49.5    |
| 007 | diminuendo        | +15.6 dB  | 62.3    |
| 010 | cresc-dim         | +14.3 dB  | 49.4    |
| 013 | dim-cresc         | +13.5 dB  | 51.7    |

**Risultato principale:** il TPR non discrimina le dinamiche del
clarinetto. I valori si raggruppano attorno a +13-15 dB con variazione
di soli 4.5 dB tra il minimo (003 mf: +11.1) e il massimo (007 dim:
+15.6). Il clarinetto e' uniformemente tonale a tutte le dinamiche:
piano e forte hanno entrambi uno spettro a righe dominato da armoniche
che superano la soglia 7 dB.

**La n_peaks porta piu' informazione:** varia da 35 (piano) a 62
(diminuendo). Il forte spinge energia nelle armoniche alte, aumentando
il numero di picchi che superano la soglia, ma non cambia il rapporto
tonal/noise perche' anche il fondo cresce. Per discriminare la dinamica
del clarinetto sono piu' adatti il centroide (+5.5x da p1 a f) e l'ZCR.

Nota: la vecchia formula lineare dava 0.989-1.000, un range ancora piu'
inutile. La formula dB porta il margine da 0.011 a 4.5 dB, ancora
insufficiente come segnale di controllo ma almeno leggibile.

### Timpano

Campioni ufficiali (10). Fondamentale: timpano aumentato.

| id  | gesto                    | TPR media | n_peaks |
|-----|--------------------------|-----------|---------|
| 004 | piano                    | +24.1 dB  | 36.3    |
| 005 | mezzoforte               | +21.8 dB  | 45.1    |
| 006 | forte 1                  | +17.6 dB  | 63.3    |
| 007 | forte 2                  | +19.3 dB  | 66.0    |
| 008 | mezzoforte 2             |  -6.1 dB  | 11.9    |
| 015 | crescendo                | +18.9 dB  | 50.9    |
| 016 | diminuendo               | +25.4 dB  | 69.5    |
| 018 | dim-cresc lungo          | +23.2 dB  | 60.5    |
| 023 | dim-cresc corto          | +23.5 dB  | 64.5    |
| 025 | cresc-dim                | +25.4 dB  | 76.5    |

**Risultato principale:** il TPR discrimina le dinamiche del timpano
meglio che sul clarinetto, ma in senso inverso: il piano (+24.1 dB) e'
piu' tonale del forte (+17-19 dB). Questo e' fisicamente corretto: il
timpano piano ha un attacco breve e una risonanza lunga e pura, mentre
il forte ha un attacco percussivo energico (rumoroso) che alza il fondo.
Il gate `--gate-dbfs -65 --gate-rel-db -30` non elimina completamente
l'attacco forte nei frame validi.

**Campione 008 (mf 2): -6.1 dB.** Negativo: il segnale ha piu' fondo
rumoroso che energia tonale. Non e' un errore, e' un gesto peculiare
(probabilmente un colpo smorzato o una tecnica estesa); il gate potrebbe
non escludere il rumore correttamente per questo tipo di attacco.

**Gradiente piano-forte:** -6 dB da +24.1 a +18.3 dB. Modesto ma
leggibile. La n_peaks segue la tendenza opposta: piano 36, forte 63.
Combinare TPR e n_peaks permette di separare dinamiche e tecniche:
piano = TPR alto + n_peaks basso; forte = TPR medio + n_peaks alto.

## Sintesi

**Cosa il TPR fa bene:**

1. Separa segnali tonali da rumorosi con ~25 dB di distanza (stabile)
2. Quantifica la proporzione di noise nelle miscele sin+noise (curva
   monotona, ~6 dB per ogni 25% di noise)
3. Distingue FM a basso indice da alto indice (+4.5 dB, opposto alla
   tanh): e' sensibile alla distribuzione delle bande laterali
4. Individua le fasi percussive vs risonanti del timpano
5. E' invariante per scala di ampiezza

**Cosa il TPR non fa:**

1. Non discrimina la ricchezza timbrica della tanh (drive 1 e 20
   differiscono di soli 0.5 dB)
2. Non distingue la dinamica del clarinetto (tutti in un range di 4.5 dB)
3. Non e' affidabile per sinusoidi allineate ai bin FFT (+85 dB anomalo)
4. Da solo non basta a identificare il tipo di gesto strumentale:
   serve combinarlo con n_peaks, centroid o ZCR

**Integrazione matriciale:** il TPR lavora bene come secondo asse di
una matrice descrittori. Con la flatness separa quattro zone: tonale
puro (TPR alto, flatness bassa), ricco di noise (TPR basso, flatness
alta), ibrido rumoroso (entrambi intermedi), FM/armonico denso (TPR
alto, flatness non bassa). Con il centroide separa la collocazione
frequenziale da quella energetica.
