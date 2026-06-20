# Spectral Entropy

## Definizione

Entropia di Shannon dello spettro di potenza normalizzato. Misura quanto
l'energia e' distribuita uniformemente fra le bin: bassa per spettri a
pochi picchi, alta per spettri piatti (rumore).

Sia |X(k)|^2 lo spettro di potenza alla bin k. Si normalizza in
distribuzione di probabilita':

p(k) = |X(k)|^2 / somma_j |X(j)|^2

L'entropia di Shannon e':

H = - somma_k p(k) * log2(p(k))

e si normalizza per il logaritmo del numero totale di bin (non solo
quelle con energia non nulla):

entropy = H / log2(N_totale)

In questo modo entropy e' compresa in [0, 1] indipendentemente dalla
risoluzione spettrale: 0 = una sola bin attiva (sinusoide pura), 1 =
distribuzione uniforme su tutte le bin (noise bianco).

## Range e significato dei valori estremi

Range: **[0, 1]**, adimensionale.

- **entropy ≈ 0**: una bin domina lo spettro. Caso ideale: sinusoide
  pura allineata col bin esatto. Sul corpus la sinusoide bin-esatto da'
  ~0.13 (non zero perche' la finestra Hann sparge un po' di energia
  sulle bin vicine).
- **entropy ≈ 0.5**: spettro con piu' picchi marcati. Sul corpus i
  segnali armonici complessi (FM con indice alto, tanh con drive alto)
  stanno qui (~0.4-0.6).
- **entropy ≈ 1**: spettro piatto. Caso ideale: noise bianco. Sul
  corpus il noise bianco da' ~0.94.

## Riferimenti

- **Shen, Hung, Lee (1998)** "Robust Endpoint Detection of Speech
  Signal Based on Spectral Entropy", introduzione del concetto in
  ambito speech processing.
- **Misra, Ikbal, Bourlard, Hermansky (2004)** "Spectral entropy based
  feature for robust ASR", IEEE ICASSP. Fa la normalizzazione per
  log2(N) e mostra robustezza al rumore.

## Implementazione

Funzione `spectral_entropy(mag_th)` in `analisi.py`. Lavora sulla
magnitudine post-soglia (mag_th), che e' gia' la rappresentazione
post-gating delle bin sotto la soglia relativa.

```python
def spectral_entropy(mag_th):
    n_total = len(mag_th)
    if n_total < 2:
        return 0.0
    power = mag_th ** 2
    total = np.sum(power)
    if total == 0:
        return 0.0
    p = power[power > 0] / total
    H = -np.sum(p * np.log2(p))
    return H / np.log2(n_total)
```

La somma -p log2 p considera solo le bin con p > 0 (per evitare
log2(0) = -inf), ma la normalizzazione usa **N_totale** (tutte le bin
del frame, anche quelle a zero). Questa scelta garantisce che il
descrittore sia confrontabile fra frame con diverso numero di bin
attive: se un frame avesse log2(N_attive) come denominatore, due
frame con poche bin attive ma distribuite diversamente potrebbero
dare entropy molto diverse, mentre con log2(N_totale) il valore
riflette davvero "quanto e' rumoroso" lo spettro.

## Relazione con altri descrittori

- **Flatness**: entropy e flatness misurano entrambi quanto lo
  spettro e' "piatto", ma flatness e' la media geometrica/aritmetica
  delle ampiezze (sensibile al pavimento) mentre entropy e' una somma
  pesata sulla distribuzione di probabilita' (insensibile a uno scaling
  globale). Sul corpus la flatness satura a 0.99 sul noise bianco e a
  0.945 sul bin-esatto, l'entropy invece da' 0.94 e 0.13: piu'
  separazione.
- **Crest factor**: simile alla flatness, satura su segnali a un solo
  picco. L'entropy dilata la zona di mezzo (segnali armonici complessi
  fra 0.2 e 0.6), che e' quella interessante per discriminare gesti
  strumentali.
- Nessuna ridondanza con la famiglia Forma (centroid/spread/rolloff/
  slope/obsir_std), che misurano *dove* sta l'energia, non *come* e'
  distribuita.

## Comportamento sul corpus

Valori medi sui frame non-gated, dal corpus rigenerato il 19/04.

**Sintetici, casi limite:**

- sinusoide 440 Hz pura: 0.13 (dominata da una bin)
- noise bianco: 0.94 (vicino al massimo teorico)
- gliss 200→2000 Hz lento: 0.14 (sempre una sola componente)

**Sintetici, gradiente continuo:**

- FM con indice di modulazione 0.5 → 3 → 10: 0.20 → 0.42 → 0.55
- tanh con drive 1 → 5 → 20: 0.13 → 0.18 → 0.22 (il tanh
  satura prima e l'entropia non cresce molto)
- mix sinusoide+noise 75/25 → 50/50 → 25/75: 0.14 → 0.23 → 0.58
  (la transizione "diventa rumoroso" si vede chiaramente)
- noise band-pass Q=500 → Q=50: 0.73 → 0.46 (piu' la banda e'
  stretta, piu' l'entropia scende verso il regime sinusoidale)

**Cataloghi strumentali:**

- clarinetto contrabbasso, p1 → p2 → mf → f: 0.20 → 0.26 → 0.28 →
  0.40. Cresce monotonicamente con la dinamica (lo spettro si
  popola di parziali e diventa piu' rumoroso).
- timpano, tenuto piano vs forte: 0.15 vs 0.13. *Non* cresce con
  la dinamica: il timpano e' sempre dominato da pochi modi (il
  forte ha leggermente meno entropia perche' i modi principali
  emergono ancora piu' netti sul rumore di fondo).

**Letture incrociate:**

- L'entropy e' ortogonale al centroid: due segnali con stesso
  centroid possono avere entropia molto diversa (FM idx 10 e
  tanh d.20 hanno centroid 4283 e 1876 ma entropia 0.55 e 0.22:
  il primo ha lo spettro distribuito su molte componenti, il
  secondo ha un picco su poche armoniche basse).
- Conferma il ruolo discriminante fra "tonale" e "rumoroso":
  i sintetici tonali stanno tutti sotto 0.25, i rumorosi sopra
  0.45. Gli strumenti reali stanno nel mezzo (0.13-0.40), che e'
  la zona piu' interessante per l'analisi gestuale.
