# Spectral Kurtosis

## Definizione

Quarto momento centrale standardizzato della distribuzione spettrale, meno 3 (excess kurtosis). Misura quanto lo spettro e' "appuntito" o "appiattito" rispetto a una distribuzione normale.

kurtosis = somma( ((f(k) - centroide) / spread)^4 * |X(k)| ) / somma( |X(k)| ) - 3

La sottrazione di 3 e' la convenzione "excess kurtosis": una distribuzione gaussiana ha kurtosis = 0, una distribuzione piu' appuntita ha kurtosis > 0, una piu' piatta ha kurtosis < 0.

- Kurtosis ≈ 0 → distribuzione "normale" (noise gaussiano)
- Kurtosis ≫ 0 → distribuzione molto appuntita, picco stretto, code lunghe (segnale tonale, energia concentrata su poche bin)
- Kurtosis < 0 → distribuzione piatta, plateau (rumore uniforme, banda larga)

## Range e significato dei valori estremi

Range: **[-2, +∞)**, adimensionale. Il limite inferiore teorico e' -2 (distribuzione bimodale Bernoulli), in pratica difficilmente si scende sotto -1.5.

- **Kurtosis ≈ -1.2**: distribuzione uniforme (rettangolare). Caso ideale: noise bianco perfettamente uniforme su una banda. Sul corpus il noise bianco da' valori intorno a -1 ÷ -1.2.
- **Kurtosis ≈ 0**: distribuzione gaussiana. Caso ideale: rumore filtrato passa-banda con inviluppo a campana.
- **Kurtosis ≫ 0**: distribuzione molto piccata. Caso ideale: sinusoide pura, dove l'energia e' tutta su poche bin del lobo Hann (picco strettissimo, code lunghe). Sul corpus le sinusoidi pure danno valori molto alti (decine, centinaia, anche migliaia a seconda della larghezza del lobo).

Sul corpus, valori tipici:
- **-1.2 ÷ -0.5** → noise larghi, distribuzioni quasi uniformi
- **-0.5 ÷ +2** → segnali misti, noise filtrati, FM larghi
- **> 5** → segnali tonali (sinusoidi, tanh, FM stretti) con picchi netti

E' il quarto momento, quindi ipersensibile alle code: una bin isolata lontana dal centroide alza la kurtosis in modo enorme. E' il descrittore "piu' fragile" della famiglia dei momenti, da leggere sempre insieme a skewness e spread.

## Riferimenti

- **Peeters (2004)** p.14, sez. 6.1.3: quarto momento della distribuzione spettrale.
- **Lerch (2023)** p.46, sez. 3.5.2 (con centroid, spread, skewness).

## Implementazione

Funzione `spectral_kurtosis` in `ambiente/tests/analisi.py`. Sottrae 3 al risultato per ottenere la versione "excess".

## Relazione con altri descrittori

- Dipende da centroide e spread (li usa come riferimento)
- Forma la famiglia dei momenti spettrali insieme a centroide (1°), spread (2°), skewness (3°)
- Sul corpus, la kurtosis e' tipicamente correlata in modo inverso alla flatness: spettri appuntiti (kurtosis alta) sono anche tonali (flatness bassa). Ma kurtosis e' molto piu' "esplosiva" in termini numerici e meno robusta
