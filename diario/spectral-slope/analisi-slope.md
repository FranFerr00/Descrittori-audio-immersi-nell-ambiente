# Analisi dello spectral slope sul corpus di test

Parametri di analisi: FFT 8192, hop 4096 (50% overlap), finestra Hann,
soglia relativa -60 dB dal picco del frame, SR 96 kHz, max_freq 10 kHz.
Formula: regressione dB/ottava (asse X = log2(Hz), asse Y = 20·log10(|X|)).
Per i campioni strumentali: gate --gate-dbfs -65 --gate-rel-db -30.
Tutti i valori sono mediane sui frame validi del campione.

## Comportamento sui segnali sintetici

### Test cardine: sinusoide vs noise

| Segnale             | Slope mediana | std  |
|---------------------|---------------|------|
| 01_sinusoide_440    | +7.19 dB/ott  | 0.01 |
| 13_sin100           | +7.19 dB/ott  | 0.01 |
| 02_noise_bianco     | +0.01 dB/ott  | 0.17 |
| 17_noise100         | -0.01 dB/ott  | 0.17 |

Separazione di 7.2 dB tra sinusoide e noise. Il valore positivo della sinusoide
non indica uno spettro che cresce: e' una conseguenza geometrica della regressione
su un picco stretto. Le sole bin attive sono quelle del lobo principale della
finestra Hann attorno alla fondamentale; su questo insieme il lobo e' asimmetrico
su scala logaritmica (la salita copre piu' ottave della discesa), e la
regressione risulta positiva. Il valore +7.19 e' lo stesso per sin440 e sin100:
dipende dalla forma del lobo, non dalla frequenza.

Il noise e' piatto su scala log-log: slope ~0 con fluttuazioni (std 0.17) dovute
alla natura casuale del rumore. La std ~0 della sinusoide conferma la stabilita'
frame-per-frame del segnale periodico.

**Comportamento speculare alla flatness:** la flatness da' sinusoide ~0.10 e
noise ~0.85; lo slope da' sinusoide ~+7 e noise ~0. I due descrittori si
complementano: la flatness misura l'uniformita' spettrale, lo slope misura
l'inclinazione complessiva.

### Tanh e saturazione

| Drive               | Slope mediana | std  |
|---------------------|---------------|------|
| 03_tanh_drive1      | -4.72 dB/ott  | 0.00 |
| 04_tanh_drive5      | -2.80 dB/ott  | 0.00 |
| 05_tanh_drive20     | -0.55 dB/ott  | 0.00 |

Gradiente monotono pulitissimo: da -4.72 a -0.55, std praticamente 0
(segnale periodico, ogni frame e' identico). E' il gradiente piu' regolare
dell'intero corpus sintetico. La tanh a basso drive ha fondamentale forte e
armoniche deboli che decadono rapidamente → slope negativo. All'aumentare del
drive la saturazione avvicina lo spettro al noise → slope verso 0.

### FM (modulazione di frequenza)

| Indice              | Slope mediana | std  |
|---------------------|---------------|------|
| 10_fm_idx05         | -2.23 dB/ott  | 0.01 |
| 11_fm_idx3          | -1.20 dB/ott  | 0.22 |
| 12_fm_idx10         | -0.13 dB/ott  | 0.03 |

Gradiente coerente con la tanh. La std di idx=3 (0.22) e' piu' alta: a indice
intermedio le bande laterali hanno ampiezza confrontabile, generando fluttuazioni
frame-per-frame. A drive=5 la tanh e' gia' a -2.80, mentre FM idx=3 e' a -1.20:
la saturazione tanh produce un decadimento armonico piu' ripido dell'FM a
pari complessita' percettiva.

### Noise bandpass

| Filtro              | Slope mediana | std  |
|---------------------|---------------|------|
| 06_noise_bp_q500    | -2.94 dB/ott  | 0.18 |
| 07_noise_bp_q200    | -3.34 dB/ott  | 0.22 |
| 08_noise_bp_q50     | -3.81 dB/ott  | 0.29 |

Tutti i valori sono negativi. Il trend e' contro-intuitivo: il filtro stretto
(Q=500) da' slope meno negativo del filtro largo (Q=50). Il filtro piu' largo
copre una banda piu' ampia verso le basse frequenze, abbassando il baricentro
complessivo e rendendo lo spettro piu' inclinato.

### Miscele sinusoide/noise

| Segnale             | Slope mediana | std  |
|---------------------|---------------|------|
| 01_sinusoide_440    | +7.19 dB/ott  | 0.01 |
| 14_sin75_noise25    | -0.40 dB/ott  | 0.14 |
| 15_sin50_noise50    | -0.26 dB/ott  | 0.17 |
| 16_sin25_noise75    | -0.19 dB/ott  | 0.17 |
| 17_noise100         | -0.01 dB/ott  | 0.17 |

Il 25% di noise fa crollare lo slope da +7.19 a -0.40. Non c'e' una curva
graduale come nel TPR: la transizione e' quasi un gradino. Appena il noise
e' presente, le sue centinaia di bin attive dominano la regressione e il
picco della sinusoide (una bin su ~900) diventa trascurabile. Il risultato e'
una forma a V rovesciata: sinusoide pura (+7.19) → mix (-0.4 ÷ -0.2) →
noise puro (-0.01). Per misurare la proporzione di noise il TPR e' il
descrittore adatto.

### Impulsi

| Segnale             | Slope mediana | std  |
|---------------------|---------------|------|
| 09_impulsi_100      | +0.14 dB/ott  | 0.03 |

Le 99 armoniche equispaziate del treno di impulsi danno un risultato +0.14,
quasi identico al noise. Lo slope non distingue impulsi da rumore.

### Inviluppi dinamici (crescendo/diminuendo)

| Segnale             | Slope mediana | std  | min    |
|---------------------|---------------|------|--------|
| 18_sin_crescendo    | +7.18 dB/ott  | 2.30 | -12.06 |
| 19_sin_diminuendo   | +7.18 dB/ott  | 2.37 | -12.48 |
| 21_noise_crescendo  | +0.03 dB/ott  | 0.15 |  -0.41 |
| 22_noise_diminuendo | -0.01 dB/ott  | 0.17 |  -0.49 |

La sinusoide in crescendo ha mediana identica alla sinusoide stabile (+7.18),
ma std 2.30 e minimo -12. I frame a bassa ampiezza hanno poche bin attive;
la regressione su pochi punti e' instabile. Il noise dinamico e' stabile
(std ~0.17 come il noise statico): molte bin attive rendono la regressione
robusta.

### Bin esatto vs fuori bin

| Segnale             | Slope mediana | std  |
|---------------------|---------------|------|
| 24_bin_esatto_40    | +0.70 dB/ott  | 0.00 |
| 25_fuori_bin_40     | +5.30 dB/ott  | 0.01 |
| 26_bin_esatto_80    | +0.70 dB/ott  | 0.00 |
| 27_fuori_bin_80     | +5.31 dB/ott  | 0.00 |

Con un solo bin attivo la regressione da' +0.70 invece di ~+7. Comportamento
opposto alla flatness (che sul bin-esatto schizza a 0.945): lo slope viene
abbassato dalla mancanza di punti, la flatness viene alzata dalla convergenza
GM/AM. I due descrittori si comportano in modo speculare su questo caso limite.

### Glissandi

| Segnale                       | Slope mediana | std   |
|-------------------------------|---------------|-------|
| 28_gliss_lento_200_2000       | +5.76 dB/ott  | 25.80 |
| 29_gliss_veloce_200_2000      | +5.81 dB/ott  | 17.21 |
| 30_gliss_lento_2000_200       | +6.10 dB/ott  | 25.49 |
| 31_gliss_micro_440_460        | +6.54 dB/ott  | 34.90 |

La mediana e' positiva (come una sinusoide stabile) ma la std e' enorme (17-35)
con range che supera i ±100 dB/ott. Lo slope non e' un descrittore adatto ai
segnali a frequenza variabile. Il microgliss (440-460 Hz, range -137 ÷ +448)
e' il caso piu' estremo: su una variazione di soli 20 Hz la frequenza attraversa
ripetutamente la zona bin-esatto (risoluzione FFT ~11.7 Hz), generando frame
instabili.

### Due sinusoidi

| Segnale                | Slope mediana | std   |
|------------------------|---------------|-------|
| 32_2sin_200_4000       | -0.11 dB/ott  | 0.00  |
| 33_2sin_400_1000       | +0.92 dB/ott  | 0.00  |
| 34_2sin_100_8000       | +0.06 dB/ott  | 0.28  |
| 39_2sin_convergono_un. | +2.27 dB/ott  | 16.15 |

Slope vicino a 0 quando le due componenti sono distribuite simmetricamente
(200+4000 → -0.11, 100+8000 → +0.06). Quando entrambe sono nella zona bassa
(400+1000 → +0.92) la mancanza di energia in alta frequenza sposta la regressione
verso positivo. Lo slope misura l'asimmetria della distribuzione energetica,
non il numero di componenti.

### Timbro dinamico (drive/indice variabile)

| Segnale                  | Slope mediana | std  |
|--------------------------|---------------|------|
| 40_tanh_drive_cresc      | -1.51 dB/ott  | 1.13 |
| 41_tanh_drive_decresc    | -1.49 dB/ott  | 1.11 |
| 42_fm_idx_cresc          | -1.02 dB/ott  | 0.66 |
| 43_fm_idx_decresc        | -1.04 dB/ott  | 0.67 |

Mediane intermedie tra i valori estremi statici. La std cattura l'ampiezza
del gesto (tanh std 1.13, FM std 0.66). La velocita' del cambiamento non
altera la mediana.

## Comportamento sotto ripresa microfonica

| Sorgente                | Slope mediana | std  |
|-------------------------|---------------|------|
| test_segnali (sint.)    | -0.01 dB/ott  | 8.85 |
| test_segnali -30 dB     | -0.01 dB/ott  | 8.85 |
| recs-002 (1 m)          | -3.26 dB/ott  | 2.29 |
| recs-003 (2 m sporco)   | -3.67 dB/ott  | 2.09 |
| recs-004 (2 m pulito)   | -3.98 dB/ott  | 2.20 |

**Invarianza per scala verificata:** test_segnali e -30 dB sono identici al
centesimo. La regressione dB/ottava e' invariante per scalatura del segnale.

**Effetto microfono:** le recs danno tutte valori negativi (-3.3 ÷ -4.0).
La risposta dell'altoparlante e della stanza ha rolloff in alta: lo spettro
risultante e' sistematicamente inclinato verso il basso → slope negativo stabile.
La distanza ha un effetto leggibile: -3.26 a 1 m, -3.7/-4.0 a 2 m. Ambiente
sporco e pulito differiscono di soli 0.31 dB. La std scende da 8.85 (sintetico
eterogeneo) a 2.1-2.3 (recs, profilo piu' omogeneo).

## Corpus strumentale

### Clarinetto contrabbasso

| id  | gesto         | Slope mediana |
|-----|---------------|---------------|
| 001 | piano 1       | -6.47 dB/ott  |
| 002 | piano 2       | -7.04 dB/ott  |
| 003 | mezzoforte    | -4.62 dB/ott  |
| 004 | forte         | -4.38 dB/ott  |
| 005 | crescendo 1   | -4.62 dB/ott  |
| 006 | crescendo 2   | -5.24 dB/ott  |
| 007 | diminuendo    | -5.24 dB/ott  |
| 010 | cresc-dim     | -5.89 dB/ott  |
| 013 | dim-cresc     | -4.84 dB/ott  |

Gradiente dinamico leggibile sui tenuti fissi: piano scuro (p2: -7.04), forte
brillante (f: -4.38), differenza di 2.7 dB. Il forte eccita armoniche piu'
alte, distribuendo piu' energia in frequenza e avvicinando lo slope a 0.
Gradiente meno marcato di centroid e ZCR ma stabile e nella direzione attesa.

### Timpano

| id  | gesto                 | Slope mediana |
|-----|-----------------------|---------------|
| 004 | piano                 | -2.30 dB/ott  |
| 005 | mezzoforte            | -1.43 dB/ott  |
| 006 | forte 1               | -2.62 dB/ott  |
| 007 | forte 2               | -2.29 dB/ott  |
| 008 | mezzoforte 2 (spec.)  | -6.36 dB/ott  |

Nessun gradiente dinamico leggibile sui tenuti: p, mf, f1, f2 si raggruppano
tra -1.4 e -2.6 senza direzione stabile (< 1 dB tra piano e forte). Il timpano
tenuto e' dominato dalla fondamentale a tutte le dinamiche e l'architettura
spettrale non cambia con la dinamica. Il campione 008 (-6.36) e' un gesto
speciale con profilo spettrale diverso dai tenuti ordinari.

## Sintesi

**Cosa lo slope fa bene:**

1. Misura la saturazione tanh con gradiente pulitissimo (-4.72 → -0.55, std ≈ 0)
2. Traccia l'indice FM (-2.23 → -0.13), con distinzione graduale
3. Legge la brillantezza del clarinettocb: piano scuro (-7) → forte brillante (-4.4)
4. Misura la colorazione di altoparlante e stanza nelle recs (-3.3 ÷ -4.0)
5. E' invariante per scala di ampiezza

**Cosa lo slope non fa:**

1. Non quantifica la proporzione noise in una miscela (25% di noise distrugge
   il segnale della sinusoide — per questo serve il TPR)
2. Non distingue impulsi da noise (entrambi ~0)
3. Non discrimina la dinamica del timpano (< 1 dB tra p e f)
4. Non e' affidabile su glissandi (std 17-35) o a bassa ampiezza (crescendo,
   bin-esatto)

**Valori di riferimento:**

| Tipo di segnale                               | Slope tipico       |
|-----------------------------------------------|--------------------|
| Picco stretto isolato (sinusoide)             | +5 ÷ +8 dB/ott     |
| Segnale armonico ricco (tanh basso, cbcl pp)  | -7 ÷ -4 dB/ott     |
| FM o tanh a indice/drive intermedio           | -3 ÷ -1 dB/ott     |
| Spettro quasi piatto (noise, tanh saturo)     | -0.5 ÷ +0.5 dB/ott |
| Colorazione acustica stanza + altoparlante    | -4 ÷ -3 dB/ott     |
