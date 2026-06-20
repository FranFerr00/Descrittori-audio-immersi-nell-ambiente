# Maximum of Autocorrelation Function (ACF max)

## Definizione

Valore massimo assoluto dell'autocorrelazione del segnale, escludendo il lobo principale (lag ~ 0).

v_Ta = max |r_xx(eta, n)|  per eta_start <= eta <= K-1

- Valore tra 0 e 1
- Alto = segnale periodico
- Basso = segnale non periodico

## Range e significato dei valori estremi

Range teorico: **[-1, 1]**, in pratica **[0, 1]** sui segnali del corpus. L'autocorrelazione e' normalizzata dividendo per il valore al lag 0 (`acf[0]`, energia del segnale), quindi il valore e' un coefficiente di correlazione. L'implementazione del progetto cerca il massimo (non il modulo del massimo) escludendo i primi due lag.

- **ACF max = 1** (massimo): a un certo lag il segnale coincide perfettamente con se stesso. Caso ideale: una **sinusoide pura**, che ha autocorrelazione massima a ogni multiplo del periodo. Sul corpus le sinusoidi danno valori vicini a 1 (≈ 0.99). Anche i segnali armonici molto periodici (tanh con drive basso, FM con indice basso) danno valori alti.
- **ACF max = 0** (minimo pratico): nessun lag produce correlazione apprezzabile. Caso ideale: **noise bianco**, totalmente decorrelato da se stesso a ogni lag > 0. Sul corpus il noise bianco da' valori prossimi a 0 (≈ 0.01-0.05). Valori negativi sono teoricamente possibili (anti-correlazione) ma non emergono sul corpus perche' cerchiamo il massimo, non il minimo.

Sul corpus, valori tipici:
- **0.0 - 0.1** → noise puro, segnali aperiodici
- **0.1 - 0.6** → segnali parzialmente periodici (mix sin+noise, noise bandpass stretto)
- **0.6 - 1.0** → segnali periodici (sinusoidi, armonici)

A differenza degli altri descrittori del progetto, lavora **nel dominio del tempo** sul frame finestrato (anche se l'implementazione usa la FFT per efficienza tramite il teorema di Wiener-Khinchin). Misura periodicita' temporale, non struttura spettrale.

## Riferimenti

- **Lerch (2023)** p.62-63, sez. 3.5.12: definizione, strategie per escludere il lobo principale (minimum lag, minimum magnitude threshold, first local minimum).

## Note

- Lavora nel dominio del tempo, non della frequenza
- Misura periodicita', non struttura spettrale
- Funziona meglio con segnali monofonici o con poche frequenze fondamentali

## Implementazione

Da implementare.

## Test

Da fare: stessi segnali usati per flatness e TPR.
