# Tonality Coefficient

## Definizione

Mappatura della Spectral Flatness (SFM) in dB su una scala lineare [0, 1] interpretabile come "tonalita'". E' una funzione di compressione che trasforma SFM (intrinsecamente concentrata vicino a 0 sui segnali tonali) in un coefficiente piu' leggibile.

tonality = min( SFM_dB / -60, 1 )

dove SFM_dB = 10 * log10(SFM).

- Tonality = 0 → SFM = 1 (spettro perfettamente piatto, rumore)
- Tonality = 1 → SFM ≤ -60 dB (spettro estremamente tonale, una sola componente domina)
- Valori intermedi mappano linearmente la SFM in dB sulla scala [0, 1]

## Range e significato dei valori estremi

Range: **[0, 1]**, adimensionale. Il valore 1 e' un "clipping" applicato a tutte le SFM ≤ -60 dB, quindi tutto cio' che e' "molto tonale" satura sullo stesso valore.

- **Tonality = 0** (minimo): SFM = 1, spettro perfettamente piatto. Caso ideale: rumore bianco. Sul corpus il noise bianco da' SFM ≈ 0.85 → SFM_dB ≈ -0.7 dB → tonality ≈ 0.012 (molto vicino a 0).
- **Tonality = 1** (massimo, clip): SFM ≤ -60 dB, spettro estremamente tonale. Caso ideale: sinusoide pura, dove SFM crolla nei dintorni di 0.001 → SFM_dB ≈ -30 dB → tonality ≈ 0.5. Per arrivare a 1 ci vuole una SFM di 1e-6 o meno, valore raro nei segnali reali.

Sul corpus, valori tipici:
- **0.0 - 0.05** → noise puro
- **0.05 - 0.20** → noise filtrato, mix sin+noise
- **0.20 - 0.50** → segnali armonici (tanh, FM, doppie sinusoidi)
- **0.50 - 1.00** → sinusoidi molto tonali

Il tonality coefficient e' una **trasformazione monotona** della SFM: contiene esattamente la stessa informazione, presentata su una scala piu' leggibile (lineare invece che log) e clippata in alto. Non aggiunge informazione rispetto alla SFM, ma e' piu' comodo per visualizzazioni e confronti percettivi.

## Riferimenti

- **Peeters (2004)** p.20, sez. 9.1: definisce la tonality come `min(SFM_dB / -60, 1)`.
- **MPEG-7**: usa la stessa formula per la `AudioSpectrumFlatness` mappata.

## Implementazione

Funzione `tonality_coefficient` in `ambiente/tests/analisi.py`. Riceve in input la SFM gia' calcolata.

```python
def tonality_coefficient(flatness):
    sfm_db = 10.0 * np.log10(flatness + 1e-19)
    return min(sfm_db / -60.0, 1.0)
```

## Relazione con altri descrittori

- E' una funzione **monotona** della SFM (informazione equivalente, presentazione diversa)
- Concettualmente sovrapponibile al **TPR** (entrambi sul range [0, 1] con interpretazione "tonalita'") ma calcolati in modo molto diverso: la tonality e' una trasformazione della SFM (uniformita' globale dello spettro), il TPR conta l'energia dei picchi prominenti
- Sui segnali del corpus, tonality e TPR danno risultati coerenti in direzione ma diversi in scala
