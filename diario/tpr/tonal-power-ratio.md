# Tonal Power Ratio (TPR)

## Definizione

Il TPR misura quanto dell'energia spettrale e' concentrata in picchi
isolati (componenti tonali) rispetto al fondo continuo (componente
rumorosa).

Nella formulazione base di Lerch:

    TPR = E_tonale / E_totale

dove E_tonale e' la somma della potenza nelle bin classificate come
"tonali" e E_totale e' la potenza totale dello spettro.

Nella formulazione usata in questo progetto (vedi sezione Implementazione):

    TPR_dB = 10 * log10( E_tonale / E_rumore )

dove E_rumore = E_totale - E_tonale.

## Classificazione dei picchi tonali

Un picco e' classificato come tonale se soddisfa due condizioni:

1. **Massimo locale**: |X(k)|^2 >= |X(k-1)|^2 e |X(k)|^2 >= |X(k+1)|^2
   (con distanza minima fra picchi di 3 bin)

2. **Regola MPEG-1 (7 dB)**: il picco supera entrambi i vicini a ±2 bin
   di almeno 7 dB in potenza (fattore ~5 lineare):

       P(k) / P(k-2) >= 5   e   P(k) / P(k+2) >= 5

La regola 7 dB deriva dal modello psicoacustico MPEG-1 per
distinguere componenti tonali da rumore nel calcolo dell'effetto di
mascheramento. La sua applicazione al TPR riduce drasticamente i
falsi positivi: nei frame di noise bianco, la probabilita' che un
massimo locale superi il vicino a ±2 bin di 7 dB e' bassa, percio'
pochi bin passano il test e E_tonale resta piccolo.

## Energia del lobo

Per ogni picco tonale si somma la potenza del lobo ±lobe_width bin
(default: 1, cioe' il bin centrale piu' i due adiacenti):

    E_lobo(k) = sum( P(k-1), P(k), P(k+1) )

Se due picchi sono vicini, le loro regioni si sovrappongono. Non e'
implementata de-duplicazione; in pratica la distanza minima di 3 bin
fra picchi limita la sovrapposizione al singolo bin di confine.

## Range e significato dei valori

**Formula lineare [0, 1]** (Lerch): il rapporto E_tonale/E_totale
e' bounded. Sul corpus dei segnali strumentali il range pratico era
0.76-1.00, insufficiente come segnale di controllo perche' comprimeva
tutto il corpus tonale nell'ultimo quarto della scala.

**Formula logaritmica dB** (implementata): scala non bounded.
Valori tipici osservati:

| Intervallo        | Carattere               |
|-------------------|-------------------------|
| < -10 dB          | prevalentemente rumoroso |
| -10 ... 0 dB      | zona di transizione      |
| 0 ... +15 dB      | parzialmente tonale      |
| > +20 dB          | fortemente tonale        |

Il descrittore e' invariante per scala di ampiezza: moltiplicare lo
spettro per una costante non cambia il rapporto E_tonale/E_rumore.

## Descrittore complementare: n_peaks

Con ogni calcolo si produce anche `n_peaks`: il numero di picchi che
hanno superato la regola 7 dB. I due descrittori sono complementari:

- TPR alto + n_peaks = 1 → sinusoide pura (tutta l'energia in un picco)
- TPR alto + n_peaks > 10 → segnale ricco di armoniche
- TPR basso + n_peaks > 20 → noise con molti minimi locali (nessuno
  tonale, ma qualcuno supera il 7 dB per fluttuazione)
- TPR < 0 + n_peaks basso → segnale con pochi picchi deboli su fondo alto

## Varianti nella letteratura

La formula base E_tonale/E_totale e' la piu' diffusa (Lerch, Peeters).
Alcune implementazioni usano la magnitudine al posto della potenza:

    TPR_mag = sum(|X(k)|) per k tonale / sum(|X(k)|) totale

Altre applicano una soglia assoluta invece della regola 7 dB (es.
bin che superano la media dello spettro di N deviazioni standard).
La regola MPEG-1 a 7 dB in potenza e' la piu' motivata fisicamente
per segnali audio a larga banda.

## Parametri dell'implementazione

| Parametro        | Valore | Effetto                                        |
|------------------|--------|------------------------------------------------|
| FFT size         | 8192   | Risoluzione 11.7 Hz a SR 96 kHz               |
| Distanza minima  | 3 bin  | Evita doppi conteggi su lobi adiacenti         |
| Soglia MPEG-1    | 7 dB   | Classifica picco come tonale                   |
| Riferimento 7 dB | ±2 bin | Picchi di rumore in banda adiacente            |
| Lobo integr.     | ±1 bin | Energia inclusa per picco tonale               |
| Formula output   | dB     | 10*log10(E_ton/E_rui), range pratico ~-90..+85 |

## Limiti noti

**Anomalia bin esatto.** Quando una sinusoide e' perfettamente
allineata a un bin FFT, il leakage della finestra Hann e' minimo:
quasi tutta l'energia sta nel lobo ±1. La potenza rumorosa
(E_totale - E_tonale) scende a valori di epsilon, e il rapporto
tonal/noise → ∞. Sul corpus sintetico digitale il valore sale
a +85 dB. Questo e' un caso limite del calcolo, non una proprieta'
del segnale: scompare appena il segnale passa attraverso una catena
acustica (mezzo bin di disallineamento basta).

**Noise a banda stretta.** I segnali noise filtrati con Q stretto
danno TPR leggermente piu' basso del noise bianco (-9 dB vs -7 dB).
Il motivo e' paradossale: un filtro stretto crea una distribuzione
di energia piu' uniforme dentro la banda, cosi' nessun bin supera
facilmente i vicini di 7 dB. Il noise bianco, con distribuzione
piu' irregolare, ha invece qualche picco "fortunato" che supera la
soglia, dando un E_tonale leggermente piu' alto.

**Impulsi e segnali percussivi.** Un treno di impulsi a 100 Hz ha
praticamente tutto lo spettro fino a 10 kHz riempito di armoniche
regolari, tutte altrettanto tonali. Il TPR sale a +17 dB con 99
picchi: altissimo n_peaks ma TPR inferiore a una sinusoide pura
(+18 dB con 7 picchi) perche' con molti picchi l'energia per lobo
e' piu' frammentata e il fondo residuo aumenta.

## Riferimenti

- **Lerch (2023)** pp. 60-61, sez. 3.5.11
- **ISO MPEG-1 Audio** Part 3, Annex C — Psychoacoustic Model 1
  (classificazione tonale/rumore a 7 dB per il calcolo del mascheramento)
