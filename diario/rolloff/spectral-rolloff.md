# Spectral Rolloff

## Definizione

Frequenza al di sotto della quale e' contenuta una percentuale fissata dell'energia spettrale totale (di solito 85% o 95%).

rolloff = min{ f_c : somma_{k <= c}(|X(k)|) >= p * somma_k(|X(k)|) }

dove `p` e' la percentuale (0.85 nel progetto).

- Valore basso = energia concentrata nelle basse frequenze
- Valore alto = energia distribuita anche in alta frequenza

E' una versione "robusta" del centroide: non e' influenzato dai picchi isolati ad alta frequenza, perche' si basa sulla cumulata.

## Range e significato dei valori estremi

Range: **[0 Hz, max_freq]**, in Hz, dove `max_freq` e' il limite di analisi (10 kHz nel progetto).

- **Rolloff → 0 Hz** (minimo): l'85% dell'energia e' tutta concentrata sulle prime bin. Caso ideale: una sub a frequenza molto bassa. Sul corpus i valori piu' bassi si trovano sulle sinusoidi gravi (sin a 100 Hz → rolloff ≈ 100 Hz).
- **Rolloff → max_freq** (massimo): l'85% dell'energia e' distribuito su quasi tutta la banda. Caso ideale: noise bianco perfettamente uniforme su [0, 10 kHz] da' rolloff = 0.85 × 10000 = 8500 Hz. Sul corpus il noise bianco da' valori prossimi a questo.

Sul corpus, valori tipici:
- **100 - 500 Hz** → sinusoidi gravi
- **500 - 3000 Hz** → segnali armonici medi
- **3000 - 8500 Hz** → segnali rumorosi o larghi

Il rolloff e' invariante per scala. Rispetto al centroide e' meno sensibile alla coda dello spettro: se aggiungi una bin isolata a 9000 Hz a una sinusoide a 440 Hz, il centroide schizza in alto, il rolloff resta basso (perche' quella bin contribuisce poco all'energia totale).

## Riferimenti

- **Peeters (2004)** p.20, sez. 9.2: introduce il rolloff (frequenza di taglio della cumulata).
- **Lerch (2023)** p.46-48, sez. 3.5.3: definizione e implementazione, varia la percentuale.

## Implementazione

Funzione `spectral_rolloff` in `ambiente/tests/analisi.py`:

```python
def spectral_rolloff(mag_th, freqs, percentile=0.85):
    cumsum = np.cumsum(mag_th)
    idx = np.searchsorted(cumsum, percentile * total)
    return freqs[idx]
```

Calcolato sulle bin sopra soglia relativa -60 dB. Percentile fissato a 0.85.

## Relazione con altri descrittori

- E' una versione "robusta" del centroide (insensibile a picchi isolati ad alta frequenza)
- Spesso correlato al centroide ma su segnali con coda spettrale lunga puo' divergere significativamente
