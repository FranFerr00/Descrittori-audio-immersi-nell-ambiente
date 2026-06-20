# Spectral OBSIR-std

## Definizione

OBSIR (Octave-Band Signal Intensity Ratio) e' la differenza in scala
logaritmica fra le energie di due bande ottavali consecutive. Il
descrittore qui usato e' la **deviazione standard** delle OBSIR
calcolate sulle 6 bande, che riassume in un solo numero quanto il
decadimento spettrale e' *non uniforme* fra ottave.

Bande ottavali (edge in Hz):

```
[200, 400, 800, 1600, 3200, 6400, 10000]
```

Da 6 bande si ottengono 5 differenze. Per ogni banda i si calcola
l'energia totale come somma del power spectrum nelle bin che cadono
nell'intervallo:

E_i = somma_{k : edges[i] <= freq[k] < edges[i+1]} |X(k)|^2

Poi log-energia:

logE_i = log10(E_i + epsilon)

OBSIR (5 valori, una per coppia di bande consecutive):

OBSIR_i = logE_{i+1} - logE_i

E infine il descrittore scalare:

obsir_std = std(OBSIR)

## Range e significato dei valori estremi

Range: **[0, +∞)**, adimensionale (e' una std di rapporti log10).

- **obsir_std ≈ 0**: il decadimento spettrale e' uniforme fra bande
  (tutte le ottave perdono energia con lo stesso rapporto). E' il
  caso teorico di uno spettro a legge di potenza pura.
- **obsir_std grande**: alcune bande "saltano" (energia molto diversa
  rispetto alle adiacenti). Tipico di spettri con risonanze localizzate
  o buchi marcati.

Sul corpus i primi valori misurati danno:

- clarinetto contrabbasso, dinamica piano (001): obsir_std=0.568, slope=-6.47
- clarinetto contrabbasso, dinamica forte (004): obsir_std=0.672, slope=-4.38
- timpano, tenuto piano (003): obsir_std=0.397, slope=-4.86
- timpano, tenuto forte (006): obsir_std=0.520, slope=-2.62

Cresce con la dinamica come lo slope, ma su una scala diversa e con
informazione complementare (la non-uniformita', non la pendenza media).

## Riferimenti

- **Essid, Richard, David (2006)** "Musical Instrument Recognition by
  pairwise classification strategies", IEEE Transactions on Audio,
  Speech and Language Processing 14(4). Introduce OBSI/OBSIR come
  feature per il riconoscimento strumenti.

## Implementazione

Funzione `spectral_obsir_std(mag, freqs)` in `analisi.py`. Costanti
modulo: `OBSI_EDGES = [200.0, 400.0, 800.0, 1600.0, 3200.0, 6400.0, 10000.0]`.

```python
def spectral_obsir_std(mag, freqs, edges=OBSI_EDGES):
    power = mag ** 2
    log_E = np.empty(len(edges) - 1)
    for i in range(len(edges) - 1):
        band = power[(freqs >= edges[i]) & (freqs < edges[i + 1])]
        log_E[i] = np.log10(np.sum(band) + EPSILON)
    if len(log_E) < 2:
        return 0.0
    obsir = np.diff(log_E)
    return float(np.std(obsir))
```

Nota: usa la magnitudine piena `mag` (non `mag_th`), per evitare che
la soglia relativa azzeri intere bande e renda log_E = log10(epsilon)
in modo artificiale.

## Relazione con altri descrittori

- **Slope**: stesso obiettivo di leggere il decadimento spettrale, ma
  lo slope e' la pendenza media (quanto in totale lo spettro scende),
  obsir_std e' la *varianza* del decadimento (quanto i singoli salti
  fra ottave sono diversi fra loro). I due possono essere alti
  contemporaneamente (decadimento ripido e irregolare) o muoversi
  indipendentemente (decadimento ripido ma uniforme = slope alto,
  obsir_std basso).
- **Decrease**: era il descrittore precedente in questo slot, rimosso
  per ridondanza con lo slope (Timbre Toolbox 2011, Peeters et al.,
  JASA 130(5)). OBSIR-std e' stato scelto per coprire l'aspetto
  ortogonale (varianza fra ottave) che decrease non quantificava.

## Comportamento sul corpus

Valori medi sui frame non-gated, dal corpus rigenerato il 19/04.

**Sintetici, casi limite:**

- noise bianco: 0.14 (5 bande con energia simile, std bassa)
- sinusoide 440 Hz pura: 4.3 (la banda 200-400 ha *tutta*
  l'energia, le altre quasi nulla, salti enormi fra ottave)
- 2 sinusoidi 200+4000 Hz: 8.4 (il caso peggiore: due bande
  cariche, le altre vuote, std massima sul corpus)

**Sintetici, gradiente:**

- tanh drive 1 → 5 → 20: 3.4 → 2.3 → 2.0 (con piu' drive le
  armoniche riempiono piu' bande, std cala)
- FM idx 0.5 → 3 → 10: 3.0 → 2.8 → 0.75 (lo stesso effetto, piu'
  netto: a indice 10 lo spettro e' ben distribuito)
- mix sin+noise 75/25 → 50/50 → 25/75: 2.1 → 1.6 → 0.98 (la
  componente noise riempie le bande alte e abbassa la std)
- noise BP Q=500 → Q=50: 0.75 → 1.3 (banda stretta = piu'
  energia in una sola ottava, std cresce)

**Cataloghi strumentali:**

- clarinetto contrabbasso, p1 → p2 → mf → f: 0.56 → 0.67 → 0.52
  → 0.67. Non monotono, ma il forte ha sempre la std piu' alta
  fra le quattro dinamiche di tenuto.
- timpano, tenuto piano vs forte: 0.40 vs 0.59. Cresce con la
  dinamica come lo slope, ma su una scala diversa (lo slope
  passa da -4.86 a -2.62, l'obsir_std da 0.40 a 0.59).

**Letture incrociate:**

- Range operativo strumenti: 0.4-0.7. Range sintetici: 0.14-8.4
  (i sintetici esplorano gli estremi, gli strumenti reali stanno
  tutti in una banda stretta intermedia).
- I sintetici con due picchi netti (sinusoide pura, 2 sin) hanno
  obsir_std molto alto perche' alcune bande ottavali restano
  vuote. Sui suoni strumentali, dove anche lo spettro armonico
  e' "sporcato" da rumore di soffio/scoccatura/ambiente, il
  valore resta sotto 1.
