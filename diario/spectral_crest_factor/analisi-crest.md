# Analisi del crest factor sul corpus di test

Analisi del comportamento del descrittore `crest` (Spectral Crest Factor, SCF) sulle tabelle di `segnali/tabelle/segnali_tabelle.md` e `segnali/tabelle/confronto_modi_tabelle.md`.

Parametri di analisi: FFT 8192, hop 4096 (50% overlap), finestra Hann, soglia relativa -60 dB dal picco, calcolo sulle sole bin attive, SR 96 kHz, `max_freq` 10 kHz. Implementazione: `max(mag_th) / mean(mag_th)` calcolato solo sulle bin sopra soglia (formulazione di Peeters: il valore minimo e' 1, non c'e' limite superiore teorico).

## Cosa misura (ripasso dalla ricerca)

Rapporto tra il bin piu' alto dello spettro e la media aritmetica dello spettro stesso. Misura la "peakiness", quanto il picco massimo domina sulla distribuzione complessiva.

- **SCF alto** → una componente domina nettamente (segnale tonale con fondamentale forte, filtro stretto, picco isolato su pavimento)
- **SCF basso (~1-3)** → energia distribuita uniformemente (rumore, banda larga)

E' concettualmente l'inverso della SFM, ma non e' il suo reciproco: la SFM usa la media geometrica sull'intera distribuzione, lo SCF guarda solo al massimo. Due spettri con lo stesso massimo e la stessa media ma forme diverse danno SCF identico e SFM diverse.

**Sensibile al singolo outlier:** poiche' dipende solo dal valore massimo, una singola bin anomala (artefatto FFT, interferenza) puo' alzare l'SCF in modo arbitrario. Lerch e Peeters lo segnalano come la principale debolezza del descrittore.

## Comportamento sui segnali sintetici

### Famiglia noise/tonale (test cardine, ma con un esito controintuitivo)

| Segnale | Crest |
|---|---|
| 02_noise_bianco | **3.0** |
| 17_noise100 | 3.0 |
| 01_sinusoide_440 | **5.8** |
| 13_sin100 | 5.8 |

Il rapporto noise/sinusoide e' solo **circa 1:2**, sorprendentemente compresso. Il motivo e' che il calcolo e' limitato alle bin sopra soglia, e una sinusoide pura attiva pochissime bin del lobo principale della Hann, tutte di valore confrontabile fra loro. Il max e' alto in assoluto, ma la media calcolata su quelle stesse poche bin altrettanto. Il rapporto resta modesto.

Il noise bianco ha invece centinaia di bin tutte di livello simile, quindi max ≈ mean e il rapporto sta vicino a 1, con leggera variabilita' frame per frame.

**Lezione:** la coppia "sin pura vs noise bianco" non e' il caso d'uso ideale del crest factor con soglia relativa. Lo SCF non e' progettato per quello.

### Miscele sin+noise (14, 15, 16)

| % noise | Crest |
|---|---|
| 0% (sin) | 5.8 |
| 25% noise | **138.7** |
| 50% noise | 66.0 |
| 75% noise | 25.1 |
| 100% noise | 3.0 |

Massimo a 25% noise, decrescente dopo. E' il caso d'uso vero del crest factor: una sinusoide forte che emerge da un pavimento di rumore. Il rumore non aggiunge un picco rivale ma riempie tutte le bin sotto la soglia con valori bassi, **abbassando drasticamente la media** mentre il max della sinusoide resta dov'era. Il rapporto esplode.

A 100% noise (nessun picco) il rapporto torna basso (3.0). A 0% noise (sin pura) il valore e' moderato perche' la soglia relativa esclude il pavimento di rumore numerico, lasciando solo il lobo Hann. **Il crest e' massimo nel "mezzo"**: e' un descrittore di *contrasto*, non di tonalita'.

### Noise bandpass (effetto del Q)

| Segnale | Q | Crest |
|---|---|---|
| 06_noise_bp_q500 | 500 | 11.1 |
| 07_noise_bp_q200 | 200 | 19.5 |
| 08_noise_bp_q50 | 50 | **41.2** |

Crescita ripida col restringersi del filtro: il bandpass concentra l'energia in una banda stretta che produce un picco netto sopra il fondo (residuo del noise filtrato sulle frequenze fuori banda, ma sotto soglia o quasi). Q=50 da' un picco quasi 4 volte piu' marcato di Q=500. Il crest reagisce molto al restringimento di banda perche' la sua dinamica non e' compressa fra 0 e 1.

### Tanh e FM (test di robustezza timbrica)

| Segnale | Drive/Idx | Crest |
|---|---|---|
| 03_tanh_drive1 | 1 | 8.3 |
| 04_tanh_drive5 | 5 | 12.9 |
| 05_tanh_drive20 | 20 | **14.0** |
| 10_fm_idx05 | 0.5 | 10.5 |
| 11_fm_idx3 | 3 | 9.2 |
| 12_fm_idx10 | 10 | 8.4 |

**Tanh:** crescita monotona col drive (8.3 → 14.0, quasi raddoppia). La fondamentale resta dominante e cresce in livello relativo rispetto alle armoniche, che sono presenti ma piu' deboli. Coerente con la descrizione del materiale di ricerca ("la fondamentale cresce di livello rispetto alle armoniche sempre piu' deboli").

**FM:** decrescita monotona con l'indice (10.5 → 9.2 → 8.4). E' l'opposto della tanh: la portante perde dominanza man mano che l'energia si sposta sulle bande laterali, sempre piu' larghe e sempre piu' equiparate alla portante. Il descrittore distingue chiaramente le due famiglie di sintesi sintetica:
- distorsione armonica → crest cresce
- modulazione di frequenza → crest cala

### Bin esatto / fuori bin (di nuovo il limite numerico)

| Segnale | Crest |
|---|---|
| 24_bin_esatto_40 | **1.50** |
| 25_fuori_bin_40 | 5.6 |
| 26_bin_esatto_80 | **1.50** |
| 27_fuori_bin_80 | 5.6 |

Sul bin esatto il crest e' 1.50, quasi al minimo teorico (1.0). Con la sinusoide allineata al bin restano attive solo 2-3 bin, tutte molto simili in modulo (la Hann produce un lobo molto piccato). Max e mean su 2-3 valori vicini danno un rapporto vicino a 1.

Mezzo bin di disallineamento basta a riportare il valore a 5.6 (uguale alla sinusoide normale a 440 Hz, perche' anche 440 Hz non cade su un bin esatto: 440 / (96000/8192) ≈ 37.55, mezzo bin fuori).

**Verifica float32:** il valore patologico 1.50 sopravvive intatto alla scalatura -30 dB in float (`test_segnali_-30db` da' lo stesso 1.50). E' una proprieta' del calcolo, non un effetto di formato. La condizione "pochissime bin attive tutte simili" e' fragile: appena lo spettro contiene piu' di una manciata di componenti (per leakage o per ripresa acustica) il valore esce dal limite.

### Segnali dinamici (crescendo/diminuendo)

| Segnale | Min | Max | Media | Std |
|---|---|---|---|---|
| 18_sin_crescendo | 5.74 | 8.49 | 5.82 | 0.28 |
| 19_sin_diminuendo | 5.74 | 7.86 | 5.82 | 0.24 |
| 21_noise_crescendo | 2.56 | 3.88 | 3.09 | 0.27 |
| 22_noise_diminuendo | 2.55 | 3.92 | 3.04 | 0.28 |

Sui crescendi/diminuendi sintetici il crest e' **stabile**: la media si discosta poco dal valore "a regime" di sin (5.79) e noise (3.0). Le piccole oscillazioni del sin (max 8.49) corrispondono ai frame ad ampiezza bassa, in cui il numero di bin sopra soglia cambia frame per frame mentre il max resta dominante. Guardare al singolo picco rende il crest poco sensibile a queste fluttuazioni di soglia.

### Glissandi e microglissandi

| Segnale | Min | Max | Media | Std |
|---|---|---|---|---|
| 28_gliss_lento_200_2000 | 4.94 | 6.00 | 5.45 | 0.34 |
| 29_gliss_veloce_200_2000 | 4.81 | 5.28 | 5.05 | 0.12 |
| 31_gliss_micro_440_460 | **1.50** | 6.22 | 5.12 | 1.03 |

Il gliss veloce ha media leggermente piu' bassa del lento (5.05 vs 5.45). Lo smearing spettrale del movimento rapido aggiunge bin attive intorno alla frequenza istantanea, abbassando il rapporto max/mean.

Il microgliss 440-460 Hz mostra **min 1.50**: la frequenza istantanea passa periodicamente sopra un bin esatto e collassa nel limite numerico (vedi sezione bin esatto).

### Doppie sinusoidi (32-39)

Tutte fra 4.7 e 6.5. Aggiungere una seconda sinusoide cambia poco: il max resta uno dei due picchi (di solito quello a livello piu' alto del lobo Hann), la mean si alza di pochissimo perche' la seconda sinusoide aggiunge solo altre 2-3 bin attive. Il crest e' quasi insensibile al numero di componenti tonali.

I valori di gliss "convergono/divergono" (37-39) sono leggermente piu' bassi (4.7-5.5) perche' nei frame in cui le due frequenze sono vicine si crea interferenza che spalma l'energia.

## Comportamento sotto ripresa microfonica

I cinque modi confrontati: `sintetico`, `test_segnali_-30db` (scalatura in float, sostituisce il vecchio `recs-001`), `recs-002` (1 m), `recs-003` (2 m sporco), `recs-004` (2 m pulito).

### Caso 1: il noise *guadagna* crest sotto microfono

| Segnale | sintetico | -30 dB | recs-002 | recs-003 | recs-004 |
|---|---|---|---|---|---|
| 02_noise_bianco | 3.0 | 3.0 | **34.3** | 18.1 | **50.3** |
| 17_noise100 | 3.0 | 3.0 | 31.4 | 17.4 | 27.3 |
| 06_noise_bp_q500 | 11.1 | 11.1 | 22.9 | 19.8 | 26.8 |
| 07_noise_bp_q200 | 19.5 | 19.5 | 30.9 | 29.5 | 26.6 |
| 08_noise_bp_q50 | 41.2 | 41.2 | 40.2 | 38.2 | 37.6 |

Il noise bianco passa da 3 a 34-50 (10x-15x). Le risonanze della stanza creano picchi locali nello spettro del noise: il crest, sensibile al singolo outlier, li cattura in pieno. Il valore esprime la colorazione spettrale del luogo di ripresa, ma con varianza elevata fra recs-002, recs-003, recs-004 (rispettivamente 34, 18, 50 sul noise bianco): il numero preciso dipende da quale bin specifica risuona di piu', che cambia con la posizione del microfono.

Il noise bp Q=50, gia' alto di base (41.2), si stabilizza sotto microfono (37-40): il segnale era gia' dominato dal picco filtrato, l'ambiente non puo' aggiungerne uno piu' alto.

`-30 dB` coincide perfettamente col sintetico per tutti i rumori → invarianza per scala confermata anche per il crest (proprieta' garantita dalla definizione).

### Caso 2: le sinusoidi pure *guadagnano molto* crest sotto microfono

| Segnale | sintetico | -30 dB | recs-002 | recs-003 | recs-004 |
|---|---|---|---|---|---|
| 01_sinusoide_440 | 5.8 | 5.8 | 27.4 | **65.6** | 50.4 |
| 13_sin100 | 5.8 | 5.8 | 31.1 | 37.7 | **53.7** |
| 18_sin_crescendo | 5.8 | 5.8 | 21.6 | 67.7 | 40.9 |

La sinusoide passa da 5.8 a 50-65 sotto microfono (10x). Stesso meccanismo del caso "miscele sin+noise": il picco della sinusoide resta intatto, ma il rumore ambientale e il riverbero aggiungono molte bin di basso livello che abbassano la media. Il rapporto esplode.

A 1 m l'effetto e' moderato (~25), a 2 m e' massimo (~50-65). E' coerente: piu' lontano il microfono, piu' rumore ambientale relativo.

`-30 dB` invariato (5.8) come ci si aspetta in float.

### Caso 3: il bin esatto crolla solo sotto microfono

| Segnale | sintetico | -30 dB | recs-002 | recs-003 | recs-004 |
|---|---|---|---|---|---|
| 24_bin_esatto_40 | **1.50** | **1.50** | 19.4 | 28.2 | 18.4 |
| 26_bin_esatto_80 | **1.50** | **1.50** | 13.9 | 23.3 | 17.7 |

Il valore patologico 1.50 sopravvive alla scalatura in float, e crolla **solo** sotto microfono. La microfonazione aggiunge le bin che mancavano per uscire dalla condizione patologica. I valori 18-28 sono coerenti con il crest di una sinusoide normale microfonata (vedi caso 2: 27-65). Il bin esatto, sotto microfono, non e' piu' distinguibile dal "fuori bin": entrambi sono solo "una sinusoide ripresa".

### Caso 4: FM con alto indice resta indistinguibile dalla portante sotto microfono

| Segnale | sintetico | -30 dB | recs-002 | recs-003 | recs-004 |
|---|---|---|---|---|---|
| 10_fm_idx05 | 10.5 | 10.5 | 18.1 | 21.8 | 23.0 |
| 11_fm_idx3 | 9.2 | 9.2 | 18.1 | 17.9 | 22.2 |
| 12_fm_idx10 | 8.4 | 8.4 | 18.0 | 25.0 | 32.5 |

Sul sintetico il crest distingueva i tre indici (10.5 → 9.2 → 8.4). Sotto microfono i valori si avvicinano: a recs-002 sono praticamente uguali (18.0-18.1). A recs-003 l'idx 10 risale (25.0), a recs-004 ancora (32.5). Il microfono comprime e poi inverte la distinzione fatta sul sintetico: il pavimento di rumore ambientale abbassa la mean uniformemente per tutti gli indici, e l'idx 10 (che ha bande laterali larghe) finisce per avere un picco isolato relativamente piu' netto rispetto alla mean abbassata.

**FM e tanh restano distinguibili sotto microfono** ma con margini stretti: tanh drive 20 sotto recs-* sta a 19-22, FM idx 10 sotto recs-* sta a 18-32. Le distribuzioni si sovrappongono.

### Caso 5: alta varianza fra modi, bassa significativita' del singolo numero

Il crest dei segnali microfonati varia molto fra recs-002, recs-003, recs-004 (es. sin 440: 27, 65, 50; noise bianco: 34, 18, 50). Non c'e' un trend monotono con la distanza, e la posizione del microfono cambia il valore in modo non prevedibile. E' la conseguenza diretta della sensibilita' al singolo outlier: la posizione del picco di magnitudine spettrale dipende dalla specifica risonanza che capita di catturare, e cambia ad ogni configurazione.

**Per il confronto fra prese microfoniche il singolo numero non e' affidabile**: il crest dice "c'e' un picco" ma non dice dove, e il valore preciso e' rumore di posizione.

## Sintesi delle proprieta' emerse

**Cosa il crest fa bene:**

1. **Distorsione armonica (tanh):** crescita monotona col drive (8.3 → 14.0).
2. **Filtraggio bandpass:** crescita ripida col restringersi del Q (11 → 41).
3. **Mix sin+noise:** riconosce il "picco su pavimento" e lo amplifica (max 138 a 25% noise). E' il caso d'uso *naturale* del descrittore.
4. **Indice FM:** decrescita monotona con l'indice (10.5 → 8.4). Primo descrittore visto finora che reagisce all'indice FM su segnale sintetico.
5. **Colorazione del luogo di ripresa:** sotto microfono il noise bianco passa da 3 a 34-50, indicando le risonanze.
6. **Invarianza per scala:** verificata sul `-30 dB` in float.

**Cosa il crest non fa:**

1. **Non distingue noise da tono in modo netto** col calcolo a soglia relativa (3 vs 5.8 = solo 2x).
2. **Non conta i parziali:** sin, 2sin, tanh drive 20 stanno tutti fra 5 e 14.
3. **E' instabile fra prese microfoniche diverse:** sensibile al singolo outlier, dipende dalla posizione del microfono.
4. **Non e' affidabile su segnali con pochi bin attivi:** bin esatto da' 1.50 (limite inferiore).

**Casi limite emersi:**

1. **Bin esatto:** crest = 1.50, vicino al limite inferiore teorico (1.0). Il calcolo su pochissime bin attive tutte simili in modulo collassa il rapporto max/mean. Sopravvive alla scalatura in float, sparisce solo sotto microfono (vedi caso 3 piu' sopra).
2. **Gliss veloce:** crest scende leggermente (5.45 → 5.05) perche' lo smearing spettrale aggiunge bin laterali. Il movimento spettrale lo legge come "meno picco netto".
3. **Mix sin+noise al 25%:** crest = 138, valore enorme sproporzionato rispetto agli altri segnali. Da considerare quando si normalizzano feature per il confronto.

Il confronto sistematico col resto della famiglia "distribuzione" (flatness, skewness, kurtosis, tonality) sara' fatto in un foglio a parte una volta analizzati tutti i descrittori della famiglia.
