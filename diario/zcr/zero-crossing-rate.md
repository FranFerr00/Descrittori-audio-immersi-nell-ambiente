# Zero Crossing Rate (ZCR)

## Definizione

Numero di volte che il segnale attraversa lo zero per unita' di campioni, calcolato sul frame nel dominio del tempo.

ZCR = (numero di cambi di segno in [x(0)..x(N-1)]) / (N - 1)

- Valore basso = il segnale attraversa raramente lo zero (segnale grave o tonale a bassa frequenza)
- Valore alto = molti attraversamenti (segnale acuto o rumoroso ad alta frequenza)

E' uno dei descrittori piu' antichi del riconoscimento vocale: distingue grossolanamente "voiced" (toni gravi, basso ZCR) da "unvoiced" (consonanti rumorose, alto ZCR).

## Range e significato dei valori estremi

Range: **[0, 1]**, adimensionale (frazione dei campioni in cui avviene un cambio di segno).

- **ZCR = 0** (minimo): il segnale non cambia mai segno nel frame. Caso ideale: una componente DC (offset costante) o una sinusoide a frequenza molto bassa rispetto alla durata del frame. Sul corpus, frame con ZCR vicino a 0 corrispondono a sinusoidi gravi (es. sin a 100 Hz da' ZCR ≈ 0.002 a SR 96 kHz).
- **ZCR = 1** (massimo): il segnale cambia segno a ogni campione. Caso ideale: un'onda quadra alternata campione per campione (segnale a Nyquist, frequenza SR/2). Sul corpus i valori massimi si trovano sui noise bianchi (≈ 0.5: in media il segnale cambia segno la meta' delle volte).

Una sinusoide pura a frequenza f, campionata a SR, ha ZCR = 2*f/SR (due attraversamenti per ciclo). Quindi:
- sin 100 Hz a SR 96 kHz → ZCR ≈ 0.0021
- sin 1000 Hz → ZCR ≈ 0.021
- sin 10 kHz → ZCR ≈ 0.21

Questa relazione rende lo ZCR una stima rozza della frequenza dominante per segnali quasi-sinusoidali. Sui segnali rumorosi non c'e' una relazione semplice e il valore tende a stabilizzarsi attorno a 0.5 (statistica di un processo bianco).

Sul corpus, valori tipici:
- **< 0.01** → sinusoidi gravi
- **0.01 - 0.1** → segnali armonici medi (tanh, FM)
- **0.1 - 0.5** → noise filtrati larghi, segnali rumorosi

Lo ZCR e' invariante per scala di ampiezza (cambia il segno, non il valore assoluto).

## Riferimenti

- **Peeters (2004)** p.10, sez. 5.2: descrittore temporale standard.
- **Lerch (2023)** p.42, sez. 3.4.1: definizione classica e usi tipici (voicing, pitch tracking grossolano).

## Implementazione

Funzione `zero_crossing_rate` in `ambiente/tests/analisi.py`. Calcolata sul frame raw nel dominio del tempo (NON sul frame finestrato), conta i cambi di segno e divide per N-1.

```python
def zero_crossing_rate(frame):
    signs = np.sign(frame)
    crossings = np.sum(np.abs(np.diff(signs)) > 0)
    return crossings / (len(frame) - 1)
```

## Relazione con altri descrittori

- E' uno dei pochi descrittori del progetto **temporali** (lavora sul segnale nel tempo, non sullo spettro). L'altro e' `max_autocorrelation`
- Per segnali quasi-sinusoidali e' correlato al **centroide** (entrambi proxy della frequenza dominante), ma calcolati in domini diversi
- Su segnali rumorosi diverge dal centroide: il noise bianco ha ZCR ≈ 0.5 stabile mentre il centroide dipende dalla forma spettrale (5000 Hz su [0, 10 kHz])
- Storicamente usato in alternativa ai descrittori spettrali quando il costo della FFT era proibitivo
