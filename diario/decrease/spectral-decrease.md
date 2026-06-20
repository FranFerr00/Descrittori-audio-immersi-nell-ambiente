# Spectral Decrease

## Definizione

Misura quanto lo spettro decresce a partire dalla prima bin. E' una somma pesata degli scarti tra ciascuna bin e la prima, normalizzata sul totale.

decrease = ( somma_{k=1..N}( (|X(k)| - |X(0)|) / k ) ) / somma_{k=1..N}( |X(k)| )

Il peso 1/k da' piu' importanza alle bin vicine alla fondamentale (k piccoli) e attenua il contributo delle bin alte. E' pensato per quantificare in modo percettivamente plausibile il decadimento delle armoniche.

- Decrease negativo = spettro che decresce (caso normale, energia maggiore sulle prime bin)
- Decrease ≈ 0 = spettro piatto
- Decrease positivo = spettro che cresce (energia maggiore sulle bin alte)

## Range e significato dei valori estremi

Range: **(-∞, +∞)**, adimensionale. La normalizzazione per la somma totale dello spettro lo rende invariante per scala di ampiezza, ma il valore dipende dalla forma dello spettro e dal range di bin considerato.

- **Decrease ≪ 0** (molto negativo): la prima bin domina ampiamente sulle successive. Caso ideale: una sinusoide grave (fondamentale a bassa frequenza, niente armoniche). Sul corpus i valori piu' negativi si trovano sulle sinusoidi pure gravi.
- **Decrease ≈ 0**: spettro mediamente piatto. Caso ideale: noise bianco. Sul corpus il noise bianco da' valori vicini a 0 (lievemente positivi o negativi a seconda della finestra).
- **Decrease > 0**: la prima bin e' piu' bassa delle bin successive. Caso ideale: segnale con energia concentrata in alta frequenza, o sinusoide il cui fondamentale e' al di fuori della prima bin (caso quasi sempre).

Sul corpus i valori sono numericamente piccoli (tipicamente -0.1 ÷ +0.05): la normalizzazione tiene il segnale compresso. Va letto come segno + ordine di grandezza piu' che come valore assoluto.

## Riferimenti

- **Peeters (2004)** p.14, sez. 6.1.5: introduce il decrease come alternativa percettivamente piu' robusta dello slope.
- **Lerch (2023)** p.49, sez. 3.5.5: stessa formulazione.

## Implementazione

Funzione `spectral_decrease` in `ambiente/tests/analisi.py`. La sommatoria parte da k=1 (la prima bin e' il riferimento, non si confronta con se stessa).

## Relazione con altri descrittori

- Stessa famiglia dello slope (entrambi misurano la pendenza globale dello spettro), ma il decrease e' invariante per scala mentre lo slope no
- Peeters lo presenta come l'alternativa "percettiva" allo slope: il peso 1/k privilegia le bin gravi, dove l'orecchio e' piu' sensibile al decadimento armonico
