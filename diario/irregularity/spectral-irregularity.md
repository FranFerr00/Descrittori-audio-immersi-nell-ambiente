# Spectral Irregularity

## Definizione

Misura la "frastagliatura" dello spettro: quanto bin adiacenti differiscono tra loro in ampiezza.

irregularity = somma( |log(S[k]) - log(S[k+1])| )

- Valore basso = spettro liscio (inviluppo spettrale regolare)
- Valore alto = spettro frastagliato (bin adiacenti con ampiezze molto diverse)

## Range e significato dei valori estremi

Range: **[0, +∞)**. E' la somma cumulativa dei salti logaritmici tra bin adiacenti, quindi cresce con il numero di bin. Sotto soglia le bin vengono sostituite con un epsilon piccolo, quindi i grandi salti "attiva → inattiva" pesano molto sul totale.

- **Irregularity = 0** (minimo): tutte le bin adiacenti hanno lo stesso modulo logaritmico. Caso ideale: spettro perfettamente piatto attivo su tutta la banda. Sul corpus il **noise bianco** ha i valori piu' bassi (≈ 50-100): le bin adiacenti differiscono pochissimo perche' lo spettro e' approssimativamente uniforme.
- **Irregularity → ∞** (nessun limite superiore): grandi salti tra bin attive e bin sotto soglia (epsilon). Caso ideale: una sinusoide pura, dove poche bin del lobo Hann sono molto sopra la massa di bin sotto soglia: ogni transizione "attiva ↔ silenzio" e' un salto enorme nel logaritmo. Sul corpus la sinusoide pura raggiunge valori dell'ordine di 10000-30000.

Sul corpus, valori tipici:
- **50 - 200** → noise larghi (bin adiacenti simili)
- **500 - 5000** → segnali armonici complessi (tanh, FM, mix)
- **5000 - 30000** → sinusoidi pure, segnali tonali con poche bin attive

L'irregolarita' e' **l'opposto** della flatness sul versante "frastagliato vs liscio": valori alti = pochi picchi su silenzio (tonale), valori bassi = spettro pieno (rumoroso). Anch'essa NON e' invariante per scala in modo perfetto, perche' la soglia relativa determina quali bin entrano nel calcolo.

## Riferimenti

- **Park (2004)**: riferimento principale per la nostra implementazione.
- **Peeters (2004)**: non ha "irregularity" come descrittore. Ha la "Harmonic Spectral Deviation" (p.17, sez. 7.1.4) che e' simile ma lavora sulle armoniche, non sullo spettro grezzo: misura la deviazione dei picchi armonici dall'inviluppo spettrale.
- **Lerch (2023)**: non include spectral irregularity.
- **Krimphoff et al. (1994)**: citato da Peeters nella bibliografia, lavoro originale sulla caratterizzazione del timbro con analisi acustica e quantificazione psicofisica. L'irregolarita' spettrale e' tra i parametri analizzati.

## Implementazione

Patch: `ambiente/descrittori/abstract/irregularity.pd`
- Usa logaritmo delle bin (arraylog)
- Calcola differenza assoluta tra bin consecutive (arraysubnext)
- Somma le differenze

## Relazione con altri descrittori

- Diversa dalla flatness: la flatness misura quanto lo spettro e' uniforme globalmente, l'irregolarita' misura quanto e' frastagliato localmente. Uno spettro con molti picchi ravvicinati di altezza simile ha irregolarita' alta ma potrebbe avere flatness alta.
- Diversa dallo spread: lo spread misura dispersione attorno al centroide, non la regolarita' bin-per-bin.
- Per segnali tonali (poche armoniche su fondo silenzioso): irregolarita' alta (grandi salti tra bin con e senza energia).
- Per noise: irregolarita' bassa (bin adiacenti con ampiezze simili).

## Test

Da fare: stessi segnali degli altri descrittori. Ipotesi: potrebbe essere il descrittore che distingue la sinusoide pura dalla sinusoide con tanh~ (piu' armoniche = piu' transizioni brusca/silenzio nello spettro).
