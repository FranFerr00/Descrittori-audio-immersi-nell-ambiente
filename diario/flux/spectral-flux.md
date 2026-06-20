# Spectral Flux

## Definizione

Misura la quantita' di cambiamento spettrale tra frame consecutivi. E' la differenza media tra lo spettro corrente e quello precedente.

v_SF = sqrt( somma( (|X(k,n)| - |X(k,n-1)|)^2 ) / (K/2 + 1) )

- Valore basso = spettro stabile (nota tenuta, suono stazionario)
- Valore alto = spettro che cambia rapidamente (transienti, attacchi, cambi di nota)

Lerch nota che e' legato alla sensazione di *roughness* (Zwicker e Fastl).

## Range e significato dei valori estremi

Range: **[0, +∞)**. Il valore dipende dalla scala di ampiezza del segnale (NON e' invariante per scala): un segnale a -30 dB ha flux numericamente piu' basso dello stesso segnale a 0 dB. Il valore va sempre letto in relazione al livello del segnale o normalizzato.

- **Flux = 0** (minimo): lo spettro non cambia tra un frame e il successivo. Caso ideale: una sinusoide perfettamente stazionaria, fra due frame consecutivi del lobo Hann allineato. Sul corpus i valori piu' bassi si trovano nel cuore della sinusoide pura sostenuta (≈ 0.001-0.01).
- **Flux → ∞** (nessun limite superiore): lo spettro cambia drasticamente da un frame all'altro. I valori piu' alti si osservano sui **transienti** (attacco di un impulso, transizione fra due segmenti del corpus, glissandi veloci). Sul corpus i picchi di flux raggiungono valori dell'ordine di 100-500 a seconda della scala di ampiezza.

Sul corpus, valori tipici (sintetico, scala nominale):
- **< 0.01** → segnale stazionario (sinusoide tenuta, noise stazionario)
- **0.01 - 1** → variazioni interne lente (modulazione lenta, glissando lento)
- **1 - 50** → variazioni rapide, micro-modulazioni
- **> 50** → transienti, salti, attacchi

Il flux e' l'unico descrittore del progetto che richiede memoria del frame precedente: il primo frame ha flux = 0 per definizione.

## Varianti

- **Half-Wave Rectification (HWR)**: considera solo gli incrementi di energia (utile per onset detection)
- **Flux logaritmico**: usa log2(|X(k,n)| / |X(k,n-1)|), indipendente dalla scala di ampiezza
- **Distanza generalizzata**: beta = 1 (Manhattan) o beta = 2 (euclidea)

## Riferimenti

- **Peeters (2004)** p.15, sez. 6.2.1: la chiama "spectral variation", calcolata come 1 - cross-correlazione normalizzata tra spettri consecutivi. Formulazione diversa ma concetto equivalente.
- **Lerch (2023)** p.55-57, sez. 3.5.8: differenza euclidea tra spettri consecutivi, con varianti (HWR, log, deviazione standard).

## Implementazione

Patch: `ambiente/descrittori/abstract/flux.pd`
- Memorizza spettro precedente in array `spectrumpr`
- Calcola differenza assoluta con spettro corrente
- Somma le differenze

## Nota

Il flux e' diverso dagli altri descrittori: non descrive la *forma* dello spettro in un istante, ma il *cambiamento* tra istanti. E' un descrittore temporale calcolato nel dominio della frequenza.

## Test

Da fare: stessi segnali degli altri descrittori. In particolare interessante con segnali stazionari vs segnali che cambiano nel tempo.
