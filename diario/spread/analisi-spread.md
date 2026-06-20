# Analisi dello spectral spread sul corpus di test

Parametri di analisi: FFT 8192, hop 4096 (50% overlap), finestra Hann,
soglia relativa -60 dB dal picco del frame, SR 96 kHz, max_freq 10 kHz.
Formula: deviazione standard ponderata in Hz attorno al centroide,
`spread = sqrt(sum(p_k * (f_k - centroid)^2))` con `p_k` normalizzata
sui bin attivi. Per i campioni strumentali: gate `--gate-dbfs -65
--gate-rel-db -30`. Tutti i valori sono mediane sui frame validi del
campione.

## Comportamento sui segnali sintetici

### Test cardine: sinusoide vs noise

| Segnale             | Spread mediano | std   |
|---------------------|----------------|-------|
| 01_sinusoide_440    | 11.5 Hz        | 0.00  |
| 13_sin100           | 11.5 Hz        | 0.00  |
| 02_noise_bianco     | 2887 Hz        | 35.0  |
| 17_noise100         | 2889 Hz        | 28.2  |

Separazione di oltre due ordini di grandezza fra picco isolato e
distribuzione larga. Per la sinusoide il valore residuo (~11.5 Hz) e'
la larghezza del lobo principale della finestra Hann attorno alla
fondamentale: con sole bin attive nel lobo, la deviazione standard
ponderata e' geometricamente determinata dalla forma della finestra
e non dipende dalla frequenza (sin440 e sin100 danno lo stesso
valore). Per il noise lo spread tende all'rms della distribuzione
uniforme su [0, 10 kHz], ~2.9 kHz.

**Speculare a flatness/slope sul caso bin-esatto** (vedi sotto):
sullo spettro stretto lo spread *diminuisce* (dipende dalla
quantizzazione FFT), mentre flatness e slope si comportano in modo
opposto.

### Tanh e saturazione

| Drive               | Spread mediano | std  |
|---------------------|----------------|------|
| 03_tanh_drive1      | 194 Hz         | 0.00 |
| 04_tanh_drive5      | 923 Hz         | 0.00 |
| 05_tanh_drive20     | 2123 Hz        | 0.00 |

Gradiente monotono pulito su un fattore 11 (drive 1 → drive 20).
La saturazione aggiunge armonici sempre piu' alti, allargando la
distribuzione spettrale attorno al centroide. Std praticamente 0
(segnale periodico stabile). Lo spread cresce in modo coerente col
centroide ma con un tasso diverso: rapporto spread/centroide circa
costante a 0.95-0.98 a tutti i drive, perche' la distribuzione
armonica e' approssimativamente auto-simile.

### FM (modulazione di frequenza)

| Indice              | Spread mediano | std  |
|---------------------|----------------|------|
| 10_fm_idx05         | 333 Hz         | 0.00 |
| 11_fm_idx3          | 881 Hz         | 0.03 |
| 12_fm_idx10         | 2255 Hz        | 0.03 |

Gradiente analogo alla tanh. A indice 10 lo spread e' praticamente
identico al drive 20 della tanh: a parita' di "complessita' percettiva
massima" (~2.2 kHz) i due metodi convergono allo stesso allargamento
spettrale.

### Noise bandpass

| Filtro              | Spread mediano | std  |
|---------------------|----------------|------|
| 06_noise_bp_q500    | 2433 Hz        | 31.6 |
| 07_noise_bp_q200    | 2298 Hz        | 42.8 |
| 08_noise_bp_q50     | 2108 Hz        | 62.2 |

Trend monotono: piu' largo il filtro (Q basso), piu' piccolo lo
spread. Sembra controintuitivo ma e' coerente col centroide: il
filtro largo abbassa il baricentro spettrale e, con esso, lo spread
calcolato attorno a quel baricentro piu' basso. Lo spread non legge
la *larghezza di banda* del filtro: legge la dispersione dell'energia
attorno al centroide, e quel centroide si sposta. La std cresce con
il filtro piu' largo (62 vs 32) per la maggiore variabilita'
frame-per-frame del rumore filtrato.

### Miscele sinusoide/noise

| Segnale             | Spread mediano | std  |
|---------------------|----------------|------|
| 01_sinusoide_440    |   11.5 Hz      |  0.0 |
| 14_sin75_noise25    | 3164 Hz        | 31.3 |
| 15_sin50_noise50    | 3149 Hz        | 28.9 |
| 16_sin25_noise75    | 3007 Hz        | 29.6 |
| 17_noise100         | 2889 Hz        | 28.2 |

Anche qui transizione a gradino: il 25% di noise porta lo spread da
11 Hz a 3164 Hz. Curiosita': i mix con piu' sinusoide (sin75) danno
spread *maggiore* del noise puro (3164 vs 2889). La presenza di una
componente concentrata a 440 Hz, lontana dal centroide del noise,
introduce uno scarto quadratico grande che spinge lo spread verso
l'alto. Lo spread non e' monotono nella proporzione di noise: un mix
puo' essere "piu' largo" del noise puro perche' contiene una coda
isolata.

### Impulsi

| Segnale             | Spread mediano | std  |
|---------------------|----------------|------|
| 09_impulsi_100      | 2897 Hz        | 0.02 |

Treno di impulsi: spread quasi identico al noise bianco. Le 99
armoniche equispaziate distribuiscono l'energia in modo simile a
una distribuzione piatta. Lo spread non distingue impulsi da noise.

### Inviluppi dinamici (crescendo/diminuendo)

| Segnale             | Spread mediano | std    |
|---------------------|----------------|--------|
| 18_sin_crescendo    |   11.5 Hz      | 11.7   |
| 19_sin_diminuendo   |   11.5 Hz      |  8.8   |
| 21_noise_crescendo  | 2883 Hz        | 31.9   |
| 22_noise_diminuendo | 2891 Hz        | 31.1   |

La sinusoide in crescendo ha mediana identica alla statica (11.5)
ma std confrontabile col valore stesso: i frame a bassa ampiezza
hanno poche bin attive e lo spread si allontana dal valore di
regime. Sul noise dinamico lo spread e' invece stabile (std come
nel noise statico): molte bin attive rendono il calcolo robusto.

### Bin esatto vs fuori bin

| Segnale             | Spread mediano | std  |
|---------------------|----------------|------|
| 24_bin_esatto_40    | 8.29 Hz        | 0.00 |
| 25_fuori_bin_40     | 11.56 Hz       | 0.00 |
| 26_bin_esatto_80    | 8.29 Hz        | 0.00 |
| 27_fuori_bin_80     | 11.56 Hz       | 0.00 |

Sul bin esatto lo spread crolla a 8.3 Hz: una sola bin attiva (la
fondamentale colpisce un centro di bin e i lobi laterali della Hann
cadono sotto la soglia). Fuori bin lo spread sale a 11.6 Hz perche'
si attivano le bin adiacenti del lobo. Il valore non dipende dalla
frequenza (40 Hz e 80 Hz danno gli stessi numeri): e' fissato dalla
risoluzione FFT (~11.7 Hz a SR 96 kHz, FFT 8192) e dalla forma
della finestra. Comportamento speculare a flatness (che sul bin
esatto schizza a 0.945 perche' GM/AM convergono su un solo punto).

### Glissandi

| Segnale                       | Spread mediano | std  |
|-------------------------------|----------------|------|
| 28_gliss_lento_200_2000       | 11.7 Hz        | 0.51 |
| 29_gliss_veloce_200_2000      | 16.7 Hz        | 0.11 |
| 30_gliss_lento_2000_200       | 11.7 Hz        | 0.51 |
| 31_gliss_micro_440_460        | 10.3 Hz        | 1.06 |

Il glissando veloce ha spread leggermente piu' grande (16.7 vs
11.7): la frequenza in movimento durante il frame "spalma" l'energia
su piu' bin adiacenti. Sui glissandi lenti l'effetto e' trascurabile
perche' la frequenza si muove poco entro la finestra di analisi.
Lo spread non e' un descrittore adatto a distinguere glissandi:
risponde solo all'effetto di sbavatura intra-frame.

### Due sinusoidi

| Segnale                | Spread mediano | std    |
|------------------------|----------------|--------|
| 32_2sin_200_4000       | 1900 Hz        |   0.00 |
| 33_2sin_400_1000       |  300 Hz        |   0.00 |
| 34_2sin_100_8000       | 3950 Hz        |   0.03 |
| 39_2sin_convergono_un. |   51 Hz        |  27.1  |

Due sinusoidi danno spread esattamente uguale alla *meta' della
distanza* fra le due (200+4000 → 1900, distanza 3800; 400+1000 →
300 = (1000-400)/2; 100+8000 → 3950, distanza 7900). Risultato
analitico: spread = |f1-f2|/2 quando le due componenti hanno energia
uguale. Lo spread misura geometricamente la dispersione, non il
numero di componenti ne' la loro distribuzione. Il caso convergente
all'unisono ha spread 51 Hz con std 27 (le due componenti si
fondono progressivamente).

### Timbro dinamico (drive/indice variabile)

| Segnale                  | Spread mediano | std  |
|--------------------------|----------------|------|
| 40_tanh_drive_cresc      | 1668 Hz        | 564  |
| 41_tanh_drive_decresc    | 1671 Hz        | 562  |
| 42_fm_idx_cresc          | 1322 Hz        | 543  |
| 43_fm_idx_decresc        | 1324 Hz        | 543  |

Mediane intermedie fra i valori statici (drive 1: 194; drive 20:
2123). La std (~560 Hz) cattura l'ampiezza del gesto. Non c'e'
asimmetria fra crescente e decrescente: lo spread e' invariante
per inversione temporale, come ogni descrittore basato su statistiche
di frame.

## Comportamento sotto ripresa microfonica

| Sorgente                | Sin440 (med) | Noise100 (med) |
|-------------------------|--------------|----------------|
| sintetici               |   11.5 Hz    | 2889 Hz        |
| test_segnali -30 dB     |   11.5 Hz    | 2889 Hz        |
| recs-002 (1 m)          |  193 Hz      | 3016 Hz        |
| recs-003 (2 m sporco)   |  936 Hz      | 2980 Hz        |
| recs-004 (2 m pulito)   |  725 Hz      | 3005 Hz        |

**Invarianza per scala verificata:** test_segnali e -30 dB sono
identici al centesimo di Hz. La definizione e' invariante per
scalatura del segnale.

**Effetto microfono sul caso sinusoide:** dal sintetico (11.5 Hz)
alle recs lo spread esplode (193 ÷ 936 Hz). La risposta della
stanza, le risonanze e il riverbero introducono energia spettrale
attorno alla fondamentale che originariamente non c'era; lo spread
e' molto sensibile a queste code laterali perche' lo scarto
quadratico amplifica i contributi lontani dal centroide. Sul noise
l'effetto e' minimo (+3-5%): la distribuzione era gia' larga.
**Il caso piu' interessante e' il microfono in stanza viva (recs-003,
936 Hz)** che rende il segnale di una sinusoide indistinguibile da
una sintesi armonica complessa, sotto il profilo dello spread.

## Corpus strumentale

### Clarinetto contrabbasso

| id  | gesto         | Spread mediano |
|-----|---------------|----------------|
| 001 | piano 1       |  247 Hz        |
| 002 | piano 2       |  222 Hz        |
| 003 | mezzoforte    |  565 Hz        |
| 004 | forte         | **1187 Hz**    |
| 005 | crescendo 1   |  679 Hz        |
| 006 | crescendo 2   |  283 Hz        |
| 007 | diminuendo    |  417 Hz        |
| 010 | cresc-dim     |  241 Hz        |
| 013 | dim-cresc     |  330 Hz        |

Gradiente dinamico molto leggibile sui tenuti: piano (~230 Hz),
mezzoforte (565), forte (1187): il forte e' 5 volte il piano. Lo
spread cammina con la dinamica come centroide e rolloff (vedi
catalogo `cataloghi/clarinettocb.md`), confermando che la
distribuzione spettrale del clarinetto contrabbasso si allarga
verso l'alto con l'aumento della pressione di soffio.

### Timpano

| id  | gesto                 | Spread mediano |
|-----|-----------------------|----------------|
| 003 | piano (tenuto)        | 18.5 Hz        |
| 004 | mezzoforte            | 16.4 Hz        |
| 005 | forte                 | 22.7 Hz        |
| 007 | mezzoforte 2          | 36.6 Hz        |
| 010 | crescendo             | 35.1 Hz        |
| 013 | tenuto p              | 38.4 Hz        |
| 015 | tenuto mf             | 32.1 Hz        |
| 020 | tenuto f              | 32.1 Hz        |
| 025 | gesto                 | 40.1 Hz        |

Tutti i valori sono fra 16 e 40 Hz: il timpano tenuto e' dominato
dalla fondamentale (~100 Hz) e lo spread risulta confrontabile
all'allargamento intrinseco della finestra (11.5 Hz) piu' un
piccolo contributo dei modi di membrana. **Nessun gradiente
dinamico leggibile**: p, mf e f stanno tutti sotto i 40 Hz, in
linea con quanto visto per slope (< 1 dB di differenza). Lo spread
non discrimina la dinamica del timpano per lo stesso motivo
strutturale: l'architettura spettrale dello strumento sostenuto
e' essenzialmente fissa.

I campioni 001, 002, 008, 022 hanno mediana 0.0: sono gesti con
attacchi/silenzi dove la maggioranza dei frame ha pochissime bin
attive e lo spread degenera (la mediana finisce su frame quasi
muti, mentre la std esplode).

## Sintesi

**Cosa lo spread fa bene:**

1. Separa nettamente segnali stretti da larghi (11 Hz vs 2900 Hz,
   piu' di due ordini di grandezza)
2. Misura la saturazione tanh con gradiente pulitissimo (194 → 2123 Hz)
3. Traccia l'indice FM (333 → 2255 Hz)
4. Legge la brillantezza del clarinettocb: piano (220) → forte (1187)
5. Per due componenti pure restituisce esattamente |f1-f2|/2
6. E' invariante per scala di ampiezza

**Cosa lo spread non fa:**

1. Non e' monotono nella proporzione noise/sinusoide (i mix possono
   avere spread maggiore del noise puro)
2. Non legge la larghezza del bandpass (Q 50/200/500 sono compressi)
3. Non distingue impulsi da noise (entrambi ~2900 Hz)
4. Non discrimina la dinamica del timpano (16-40 Hz a tutte le dinamiche)
5. E' molto sensibile alla colorazione di stanza/microfono sui segnali
   tonali (sinusoide passa da 11 a ~700-900 Hz nelle recs)

**Valori di riferimento:**

| Tipo di segnale                                | Spread tipico    |
|------------------------------------------------|------------------|
| Picco isolato (sinusoide, fuori bin)           |  11-12 Hz        |
| Picco isolato sul bin esatto                   |   8 Hz           |
| Tono stabile a fondamentale bassa (cbcl pp)    | 220-250 Hz       |
| Saturazione/FM intermedia                      | 300-1000 Hz      |
| Saturazione/FM forte (cbcl f, tanh20, fm10)    | 1100-2300 Hz     |
| Spettro largo (noise, impulsi)                 | 2800-3000 Hz     |
| Sinusoide ripresa in stanza viva               | 200-1000 Hz      |
