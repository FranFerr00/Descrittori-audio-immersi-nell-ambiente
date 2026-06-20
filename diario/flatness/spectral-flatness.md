# Spectral Flatness (SFM)

## Definizione

Rapporto tra media geometrica e media aritmetica dello spettro di magnitudine.

SFM = exp(1/N * somma(log(x))) / (1/N * somma(x))

## Range e significato dei valori estremi

Range teorico: **[0, 1]**.

- **SFM = 1** (massimo): media geometrica e aritmetica coincidono. Succede solo quando **tutte le bin attive hanno lo stesso modulo**, cioe' uno spettro perfettamente piatto. Il caso ideale e' il **rumore bianco** (sul corpus: noise bianco sintetico ≈ 0.85, mai 1.0 esatto perche' lo spettro istantaneo di un noise reale non e' mai perfettamente uniforme). Il caso patologico e' la sinusoide allineata a un bin esatto, dove restano attive 2-3 bin del lobo Hann tutte simili in modulo: il calcolo collassa a 0.945 anche se il segnale e' tonale (limite numerico, vedi `analisi-flatness.md`).
- **SFM = 0** (minimo): la media geometrica e' zero, ovvero **almeno una bin attiva ha modulo zero**. Con la soglia relativa -60 dB le bin sotto soglia vengono escluse dal calcolo, quindi nella pratica il valore non scende mai esattamente a 0; tende a 0 quando lo spettro e' fortemente concentrato su poche bin di valore molto diverso (caso tonale "pulito", una fondamentale forte e qualche armonica decrescente). Sul corpus i valori piu' bassi sono ≈ 0.10 (sinusoide pura microfonata) e ≈ 0.07 (frame transitori dei segnali dinamici).

Nella pratica, sul corpus dei test:
- **0.10 - 0.20** → segnale tonale (sinusoide pura, tanh, FM a basso indice)
- **0.20 - 0.50** → segnale parzialmente tonale (mix sin+noise, bandpass stretto)
- **0.50 - 0.85** → segnale rumoroso (noise filtrato, noise bianco)

Alto (~0.8-1) = spettro piatto, rumoroso. Basso (~0) = spettro non piatto, tonale.

## Riferimenti

- **Peeters (2004)** p.20, sez. 9.1: calcolo per bande (250-500, 500-1000, 1000-2000, 2000-4000 Hz). Introduce anche Spectral Crest Factor e conversione in Tonality.
- **Lerch (2023)** p.59-60, sez. 3.5.10: calcolo su intero spettro. Nota il problema delle bin a zero. Suggerisce smoothing con filtro MA e raccomandazione MPEG-7 (250 Hz - 16 kHz, 24 bande).
- **Park (2004)**: riferimento MPEG-7, base della nostra implementazione.

## Implementazione

Patch: `ambiente/descrittori/abstract/sfm.pd`
- FFT 8192, SR 96000 (risoluzione ~11.7 Hz per bin)
- Soglia a 0.01 in pfft.pd azzera bin sotto soglia
- Epsilon 1e-19 prima del log per evitare log(0)
- Calcolo su tutte le 4096 bin (intero spettro)

## Test

### 2026-03-30 — Segnali in ambiente acustico

**Setup:** segnali riprodotti da altoparlante, captati da microfono a distanze variabili.

**Risultati:**

| Segnale | Flatness | Note |
|---------|----------|------|
| Noise | ~0.8 | Costante al variare di distanza e ampiezza |
| Sinusoide pura | bassa | Come atteso |
| Sinusoide + tanh~ | bassa | Stessi valori della sinusoide pura |
| Noise + bandpass (Q largo) | ~0.7 | |
| Noise + bandpass (Q stretto) | scende ~0.1 per step | Graduale |

**Osservazioni:**
- Distanza e ampiezza non influenzano la flatness
- tanh~ aggiunge armoniche (picchi discreti) ma la flatness non cambia: misura uniformita dello spettro, non ricchezza di parziali
- Distingue bene: spettro continuo largo / continuo stretto / discreto
- Non distingue timbri armonici semplici da complessi

## Sviluppi

- [ ] Testare calcolo per bande separate (come Peeters/MPEG-7) invece che su intero spettro
- [ ] Testare miscela noise + sinusoide a rapporto variabile
- [ ] Testare noise con bandpass a Q misurati (1, 2, 5, 10, 20, 50)
- [ ] Testare con passa basso a frequenza di taglio decrescente
- [ ] Testare onda quadra / treno di impulsi
- [ ] Testare FM a indice di modulazione crescente
