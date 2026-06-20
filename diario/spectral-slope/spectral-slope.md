# Spectral Slope

Parametri di analisi: FFT 8192, hop 4096 (50% overlap), finestra Hann,
soglia relativa -60 dB dal picco del frame, SR 96 kHz, max_freq 10 kHz.
Formula: regressione dB/ottava (asse X = log2(Hz), asse Y = 20·log10(|X|)).
Per i campioni strumentali: gate --gate-dbfs -65 --gate-rel-db -30.

## Cosa misura

Pendenza della retta di regressione dello spettro in funzione della frequenza.
Misura quanto lo spettro "scende" dalle basse alle alte frequenze: un descrittore
di inclinazione globale, distinto dal centroide (posizione del baricentro) e
dalla flatness (uniformita' della distribuzione).

La formula classica (Lerch 2023, Peeters 2004) usa asse X in Hz e asse Y
in ampiezza lineare:

    slope = Σ (f(k) - f̄) · (|X(k)| - |X̄|) / Σ (f(k) - f̄)²

Questa formulazione produce valori ~10⁻⁸ su qualsiasi segnale perche' il
denominatore Σ(f - f̄)² vale ~10¹⁰ Hz² e dipende solo da FFT size e
frequenza di campionamento, non dal contenuto del segnale. openSMILE documenta
il problema con il flag `oldSlopeScale` (comportamento legacy, corretto da
luglio 2013, da disabilitare nei nuovi progetti).

**Formula implementata: regressione dB/ottava.** Soluzione adottata da
openSMILE/GeMAPS e validata da Kazazis, Depalle e McAdams (2022,
*Frontiers in Psychology*) su esperimenti psicofisici di percezione dello
slope:

    f_ott(k) = log₂( f(k) )
    s_dB(k)  = 20 · log₁₀( |X(k)| )

    slope = Σ (f_ott(k) - f̄_ott) · (s_dB(k) - s̄_dB) / Σ (f_ott(k) - f̄_ott)²

Il risultato e' in dB/ottava: quanti dB varia mediamente l'ampiezza ogni
volta che la frequenza raddoppia. E' la stessa unita' usata per la pendenza
dei filtri (filtro del primo ordine = -6 dB/ottava).

**Proprieta':**

- Invariante per scala di ampiezza: scalare tutti i |X(k)| per una costante
  non cambia la regressione su valori in dB (verificato sul corpus -30 dB).
- Non invariante per trasposizione: la stessa armonia suonata a diverse
  ottave puo' dare slope diverso.
- Range utile sul corpus: circa -20 ÷ +10 dB/ottava.

**Relazione con gli altri descrittori di forma:** lo slope e' concettualmente
vicino al decrease (Peeters 2004), che pesa le basse frequenze con un fattore
1/(k-1); il decrease e' piu' sensibile alle componenti gravi, lo slope tratta
tutte le ottave con pari peso. La flatness misura l'uniformita' (quanto lo
spettro assomiglia al noise), lo slope misura la direzione (se l'energia
prevale in basso o in alto): i due descrittori sono ortogonali per design ma
convergono nei segnali saturi (entrambi si avvicinano ai valori del noise).

## Comportamento sui segnali sintetici

### Test cardine: sinusoide vs noise

| Segnale          | Slope mediana | std  |
|------------------|---------------|------|
| sinusoide 440 Hz | +7.19 dB/ott  | 0.01 |
| sinusoide 100 Hz | +7.19 dB/ott  | 0.01 |
| noise bianco     | +0.01 dB/ott  | 0.17 |

Separazione di 7.2 dB. Il valore positivo della sinusoide non indica uno
spettro che cresce: e' una conseguenza geometrica della regressione su un
picco stretto. Le sole bin attive sono quelle del lobo Hann attorno alla
fondamentale; su scala logaritmica il lobo e' asimmetrico (la salita copre
piu' ottave della discesa) e la regressione risulta positiva. Il valore +7.19
e' identico per sin440 e sin100: dipende dalla forma del lobo, non dalla
frequenza.

Il noise e' piatto su scala log-log (slope ~0). La std 0.17 e' la fluttuazione
stocastica del rumore; quella della sinusoide e' 0.01 (segnale periodico,
ogni frame identico).

**Comportamento speculare alla flatness:** flatness da' sinusoide ~0.10 e
noise ~0.85; slope da' sinusoide ~+7 e noise ~0. I due descrittori si
complementano: la flatness misura l'uniformita' spettrale, lo slope misura
l'inclinazione.

### Tanh e FM: i gradienti piu' leggibili

| Segnale         | Slope mediana | std  |
|-----------------|---------------|------|
| tanh drive=1    | -4.72 dB/ott  | 0.00 |
| tanh drive=5    | -2.80 dB/ott  | 0.00 |
| tanh drive=20   | -0.55 dB/ott  | 0.00 |
| FM idx=0.5      | -2.23 dB/ott  | 0.01 |
| FM idx=3        | -1.20 dB/ott  | 0.22 |
| FM idx=10       | -0.13 dB/ott  | 0.03 |

La tanh mostra il gradiente piu' regolare dell'intero corpus sintetico:
monotono, std praticamente 0 su tutti e tre i valori (segnale periodico).
All'aumentare del drive la saturazione distribuisce energia piu' uniformemente
sulle armoniche alte → slope verso 0. La FM segue la stessa direzione con
range leggermente piu' ristretto.

Il parallelo tra le due famiglie e' significativo: a drive=5 la tanh e' a
-2.80, mentre FM idx=3 e' a -1.20. La saturazione tanh produce un decadimento
armonico piu' ripido dell'FM a pari complessita' percettiva.

### Miscele sinusoide/noise

| Segnale          | Slope mediana |
|------------------|---------------|
| sinusoide pura   | +7.19 dB/ott  |
| sin 75% + 25% n. | -0.40 dB/ott  |
| sin 50% + 50% n. | -0.26 dB/ott  |
| sin 25% + 75% n. | -0.19 dB/ott  |
| noise puro       | -0.01 dB/ott  |

Il 25% di noise fa crollare lo slope da +7.19 a -0.40: la transizione e'
quasi un gradino, non una curva graduale come nel TPR (~6 dB per ogni 25%
di noise). Appena il noise e' presente, le sue centinaia di bin attive
dominano la regressione e il picco della sinusoide (una bin su ~900) diventa
trascurabile. Lo slope non misura la proporzione di noise in una miscela.

### Casi limite

**Bin esatto:** una sinusoide perfettamente allineata a un bin FFT attiva
pochissime bin; la regressione da' +0.70 invece di ~+7. Comportamento opposto
alla flatness (che sul bin-esatto schizza a 0.945): i due descrittori si
comportano in modo speculare su questo caso limite.

**Glissandi:** la mediana e' positiva (come una sinusoide istantanea) ma la
std e' enorme (17-35 dB/ott) con range che supera i ±100. Lo slope non e'
adatto a segnali a frequenza variabile.

**Inviluppi dinamici:** la sinusoide in crescendo ha mediana stabile (+7.18)
ma std 2.30 e minimo -12: i frame a bassa ampiezza con poche bin attive
destabilizzano la regressione.

## Comportamento sotto ripresa microfonica

| Sorgente              | Slope mediana | std  |
|-----------------------|---------------|------|
| sintetico             | -0.01 dB/ott  | 8.85 |
| sintetico -30 dB      | -0.01 dB/ott  | 8.85 |
| recs-002 (1 m)        | -3.26 dB/ott  | 2.29 |
| recs-003 (2 m sporco) | -3.67 dB/ott  | 2.09 |
| recs-004 (2 m pulito) | -3.98 dB/ott  | 2.20 |

Sintetico e -30 dB sono identici: invarianza per scala confermata.

Le recs danno valori negativi (-3.3 ÷ -4.0): la risposta dell'altoparlante
e della stanza ha rolloff in alta frequenza, il che produce uno spettro
sistematicamente inclinato verso il basso. La distanza ha un effetto leggibile
(+0.4/+0.7 dB piu' negativo passando da 1 a 2 m); ambiente sporco e pulito
differiscono di soli 0.31 dB.

La std scende da 8.85 (sintetico: mescola segnali con slope molto diversi)
a 2.1-2.3 (recs: profilo spettrale piu' omogeneo).

## Corpus strumentale

### Clarinetto contrabbasso

| gesto      | Slope mediana |
|------------|---------------|
| piano 1    | -6.47 dB/ott  |
| piano 2    | -7.04 dB/ott  |
| mezzoforte | -4.62 dB/ott  |
| forte      | -4.38 dB/ott  |

Gradiente dinamico leggibile: piano scuro (p2: -7.04), forte brillante
(f: -4.38), differenza di 2.7 dB. Il forte eccita armoniche piu' alte,
avvicinando lo slope a 0. Il gradiente e' meno marcato del centroide
(rapporto 5.5x da p1 a f) ma stabile e nella direzione attesa. I gesti
dinamici (crescendo, diminuendo) si collocano nei valori intermedi in modo
coerente con il loro profilo di ampiezza.

### Timpano

| gesto      | Slope mediana |
|------------|---------------|
| piano      | -2.30 dB/ott  |
| mezzoforte | -1.43 dB/ott  |
| forte 1    | -2.62 dB/ott  |
| forte 2    | -2.29 dB/ott  |

Nessun gradiente dinamico leggibile: i quattro tenuti si raggruppano tra
-1.4 e -2.6 senza una direzione stabile (< 1 dB tra piano e forte). Il
timpano tenuto e' dominato dalla fondamentale a tutte le dinamiche e
l'architettura spettrale non cambia con la forza del colpo.

## Sintesi

**Cosa lo slope fa bene:**

1. Misura la saturazione tanh con il gradiente piu' pulito del corpus
   sintetico (-4.72 → -0.55, std ≈ 0)
2. Traccia l'indice FM (-2.23 → -0.13)
3. Legge la brillantezza del clarinettocb: piano scuro (-7) → forte
   brillante (-4.4)
4. Misura la colorazione di altoparlante e stanza nelle recs (-3.3 ÷ -4.0)
5. E' invariante per scala di ampiezza

**Cosa lo slope non fa:**

1. Non quantifica la proporzione noise in una miscela (collasso a gradino
   al 25% di noise; per questo serve il TPR)
2. Non distingue impulsi da noise
3. Non discrimina la dinamica del timpano
4. Non e' affidabile su glissandi o segnali a bassa ampiezza

**Valori di riferimento:**

| Tipo di segnale                              | Slope tipico       |
|----------------------------------------------|--------------------|
| Picco stretto isolato (sinusoide)            | +5 ÷ +8 dB/ott     |
| Segnale armonico ricco (tanh basso, cbcl pp) | -7 ÷ -4 dB/ott     |
| FM o tanh a indice/drive intermedio          | -3 ÷ -1 dB/ott     |
| Spettro quasi piatto (noise, tanh saturo)    | -0.5 ÷ +0.5 dB/ott |
| Colorazione acustica stanza + altoparlante   | -4 ÷ -3 dB/ott     |

## Riferimenti

- **Peeters (2004)** p. 13, sez. 6.1.4: formula lineare originale.
- **Lerch (2023)** p. 48, sez. 3.5.4: stessa definizione, nota la sensibilita'
  al range di frequenze.
- **openSMILE / GeMAPS**: sub-band log-power slopes; `oldSlopeScale = 0` per
  la versione corretta.
- **Kazazis, Depalle, McAdams (2022)** *Frontiers in Psychology*: esperimenti
  psicofisici su slope percettivo in dB/ottava.
