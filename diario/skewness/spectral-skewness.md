# Spectral Skewness

## Definizione

Terzo momento centrale standardizzato della distribuzione spettrale (asimmetria). Misura quanto lo spettro e' sbilanciato a destra o a sinistra del centroide.

skewness = somma( ((f(k) - centroide) / spread)^3 * |X(k)| ) / somma( |X(k)| )

- Skewness = 0 → spettro simmetrico attorno al centroide
- Skewness > 0 → coda lunga verso le alte frequenze (la maggior parte dell'energia e' al di sotto del centroide)
- Skewness < 0 → coda lunga verso le basse frequenze (la maggior parte dell'energia e' al di sopra del centroide)

## Range e significato dei valori estremi

Range: **(-∞, +∞)**, adimensionale (le distanze dal centroide sono normalizzate sullo spread). Per distribuzioni "normali" (gaussiane) il valore e' 0; per distribuzioni a coda asimmetrica puo' raggiungere valori dell'ordine di alcune unita'.

- **Skewness ≈ 0**: spettro simmetrico. Caso ideale: noise bianco perfettamente uniforme. Sul corpus il noise bianco da' valori vicini a 0 (≈ ±0.1).
- **Skewness ≫ 0** (positivo): la maggior parte dell'energia e' "compressa" sotto il centroide, con una coda che si estende verso l'alto. Caso ideale: segnale armonico con fondamentale forte e poche armoniche piu' deboli (la fondamentale tiene basso il centro di massa, le armoniche allungano la coda a destra). Sul corpus tipicamente +1 ÷ +5.
- **Skewness ≪ 0** (negativo): la maggior parte dell'energia e' sopra il centroide, con una coda verso il basso. Caso ideale: segnale passa-alto con energia in alta e qualche residuo grave. Sul corpus si vede meno di frequente.

Sul corpus, valori tipici:
- **|skewness| < 0.5** → spettro abbastanza simmetrico (noise larghi)
- **0.5 < |skewness| < 3** → segnali asimmetrici "normali" (tanh, FM, sinusoidi con armoniche)
- **|skewness| > 3** → forte asimmetria, energia molto sbilanciata

E' il terzo momento, quindi sensibile ai punti lontani dal centroide. Una bin isolata in una coda fa esplodere il valore. Dipende criticamente dal calcolo corretto di centroide e spread (se uno dei due e' impreciso, la skewness e' inaffidabile).

## Riferimenti

- **Peeters (2004)** p.14, sez. 6.1.3: terzo momento della distribuzione spettrale.
- **Lerch (2023)** p.46, sez. 3.5.2 (insieme a centroid e spread come "moments" della distribuzione spettrale).

## Implementazione

Funzione `spectral_skewness` in `ambiente/tests/analisi.py`. Riceve in input il centroide e lo spread gia' calcolati.

## Relazione con altri descrittori

- Dipende da centroide e spread (li usa entrambi come riferimento)
- Insieme a centroide, spread e kurtosis forma la famiglia dei "momenti spettrali" che descrivono la distribuzione spettrale come fosse una distribuzione di probabilita'
- Skewness e kurtosis insieme caratterizzano la forma "fine" della distribuzione oltre il valore medio (centroide) e la dispersione (spread)
