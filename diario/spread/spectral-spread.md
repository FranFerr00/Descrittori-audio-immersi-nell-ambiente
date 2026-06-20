# Spectral Spread

## Definizione

Deviazione standard dello spettro attorno al centroide spettrale. Misura quanto l'energia e' concentrata o dispersa attorno al baricentro dello spettro.

v_SS = sqrt( somma( (k - centroide)^2 * |X(k)| ) / somma( |X(k)| ) )

- Valore basso = energia concentrata attorno al centroide (suono tonale, intonato)
- Valore alto = energia dispersa (suono rumoroso, a banda larga, transienti)

## Range e significato dei valori estremi

Range: **[0 Hz, max_freq/2]** circa. E' una deviazione standard espressa in Hz, quindi non puo' superare meta' della banda di analisi (per un noise uniforme su [0, 10 kHz] vale ≈ 2890 Hz, cioe' 10000/√12).

- **Spread → 0 Hz** (minimo): tutta l'energia e' su una sola bin (o su bin contigue tutte alla stessa frequenza). Caso ideale: sinusoide pura allineata a un bin esatto. Sul corpus la sinusoide a 440 Hz da' spread ≈ 30 Hz (non zero perche' la finestra Hann sparge l'energia su 3-5 bin).
- **Spread → max_freq/√12** (massimo pratico): energia distribuita uniformemente su tutta la banda di analisi. Caso ideale: noise bianco sopra soglia su tutto [0, 10 kHz]. Sul corpus il noise bianco da' spread ≈ 2890 Hz. Valori piu' alti si ottengono solo se l'energia e' concentrata ai due estremi della banda (caso teorico).

Sul corpus, valori tipici:
- **30 - 200 Hz** → sinusoidi pure, segnali tonali
- **200 - 1500 Hz** → tanh, FM, segnali armonici complessi
- **1500 - 3000 Hz** → noise larghi, bandpass larghi

Lo spread dipende dal centroide (e' calcolato attorno ad esso): se il centroide e' a 5000 Hz e l'energia spazia da 0 a 10000, lo spread e' grande; se il centroide e' a 100 Hz e l'energia spazia da 0 a 200, lo spread e' piccolo.

## Riferimenti

- **Peeters (2004)** p.13, sez. 6.1.2: definita come varianza della distribuzione spettrale (2o momento centrale). sigma^2 = integrale di (x - mu)^2 * p(x).
- **Lerch (2023)** p.45-46, sez. 3.5.2: stessa definizione, nota che il calcolo deve essere coerente con il centroide (se centroide usa power spectrum, spread pure). Menziona anche versione MPEG-7 con scala logaritmica.
- **Krimphoff et al. (1995)**: lo spread spettrale non e' tra le dimensioni percettive principali identificate (centroide, attacco, struttura fine).

## Implementazione

Patch: `ambiente/descrittori/abstract/spread.pd`
- Usa il centroide come riferimento
- Calcola la varianza pesata delle frequenze
- Output filtrato con lop~

## Relazione con altri descrittori

- Dipende dal centroide (lo usa come punto di riferimento)
- Correlato inversamente alla flatness? No: la flatness misura uniformita', lo spread misura dispersione attorno al centro. Uno spettro piatto ha sia flatness alta che spread alto. Uno spettro con due picchi lontani ha spread alto ma flatness bassa.

## Test

Da fare: stessi segnali degli altri descrittori.
