# Tabella descrittori per segnale (limite 10 kHz) — ARCHIVIATA

> **Nota (2026-04-13):** Questa tabella e' stata superata da `tabella-segnali.md`, aggiornata con i valori del corpus float32 e la pipeline attuale (soglia relativa -60 dB, flatness su bin attive, TPR con filtro a mediana). I valori qui sotto appartengono a una versione precedente del codice e non corrispondono all'analisi corrente. Conservata a fini storici.

Configurazione originale: FFT 8192, Hann, overlap 50%, SR 96000, analisi limitata a 0-10000 Hz

### Segnali base

| Segnale | Centroid (Hz) | Spread (Hz) | Flatness | Flux | Irregularity | TPR |
|---|---|---|---|---|---|---|
| Sinusoide 440 Hz | 439.7 | 11.9 | 0.2788 | 0.0063 | 28.6 | 0.5066 |
| Noise bianco | 4956.0 | 2866.2 | 0.9285 | 1.3013 | 2657.0 | 0.4034 |
| Impulsi 100 Hz | 0.0 | 0.0 | 0.0000 | 0.0000 | 0.0 | 0.5881 |

### Tanh (drive statico)

| Segnale | Centroid (Hz) | Spread (Hz) | Flatness | Flux | Irregularity | TPR |
|---|---|---|---|---|---|---|
| Tanh drive 1 | 475.4 | 174.3 | 0.2770 | 0.0075 | 50.8 | 0.5075 |
| Tanh drive 5 | 915.0 | 868.3 | 0.2942 | 0.0122 | 167.9 | 0.5108 |
| Tanh drive 20 | 1857.1 | 2090.5 | 0.3931 | 0.0426 | 273.7 | 0.5152 |

### Noise filtrato bandpass

| Segnale | Centroid (Hz) | Spread (Hz) | Flatness | Flux | Irregularity | TPR |
|---|---|---|---|---|---|---|
| Noise BP Q=500 | 2476.4 | 2057.4 | 0.7128 | 1.6960 | 2197.0 | 0.4189 |
| Noise BP Q=200 | 1803.3 | 1413.5 | 0.6511 | 1.2629 | 1641.7 | 0.4288 |
| Noise BP Q=50 | 1279.8 | 672.5 | 0.5703 | 0.7779 | 899.3 | 0.4491 |

### FM (indice statico)

| Segnale | Centroid (Hz) | Spread (Hz) | Flatness | Flux | Irregularity | TPR |
|---|---|---|---|---|---|---|
| FM indice 0.5 | 543.6 | 320.6 | 0.3608 | 0.0124 | 123.6 | 0.5188 |
| FM indice 3 | 1421.9 | 863.5 | 0.4416 | 0.0192 | 320.9 | 0.6059 |
| FM indice 10 | 4281.9 | 2236.1 | 0.5529 | 0.0197 | 701.0 | 0.6076 |

### Mix sinusoide/noise

| Segnale | Centroid (Hz) | Spread (Hz) | Flatness | Flux | Irregularity | TPR |
|---|---|---|---|---|---|---|
| Sin 100% | 436.1 | 11.4 | 0.2752 | 0.0157 | 28.4 | 0.5042 |
| Sin 75% + Noise 25% | 683.7 | 1175.6 | 0.2014 | 0.0468 | 232.0 | 0.5022 |
| Sin 50% + Noise 50% | 3654.3 | 3171.8 | 0.7398 | 0.7005 | 2656.6 | 0.4662 |
| Sin 25% + Noise 75% | 4594.3 | 3002.0 | 0.8910 | 1.0789 | 3098.1 | 0.3819 |
| Noise 100% | 4993.5 | 2882.3 | 0.9368 | 1.3074 | 2718.5 | 0.4071 |

### Inviluppi dinamici

| Segnale | Centroid (Hz) | Spread (Hz) | Flatness | Flux | Irregularity | TPR |
|---|---|---|---|---|---|---|
| Sin crescendo | 439.8 | 11.0 | 0.4837 | 0.0133 | 26.7 | 0.5047 |
| Sin diminuendo | 436.3 | 9.6 | 0.4807 | 0.0069 | 26.5 | 0.5075 |
| Sin cresc-dim | 436.3 | 9.6 | 0.4760 | 0.0071 | 26.6 | 0.5059 |
| Noise crescendo | 4020.2 | 2258.0 | 0.7805 | 0.6156 | 1884.3 | 0.4030 |
| Noise diminuendo | 4045.6 | 2228.5 | 0.7790 | 0.6146 | 1862.5 | 0.4034 |
| Noise cresc-dim | 3973.4 | 2278.8 | 0.8040 | 0.6132 | 1886.6 | 0.4032 |

### Bin esatto vs fuori bin

| Segnale | Centroid (Hz) | Spread (Hz) | Flatness | Flux | Irregularity | TPR |
|---|---|---|---|---|---|---|
| Bin esatto (40) | 465.4 | 9.9 | 0.9330 | 0.0154 | 28.8 | 0.6581 |
| Fuori bin (40.5) | 474.2 | 12.0 | 0.2805 | 0.0064 | 28.6 | 0.4776 |
| Bin esatto (80) | 936.9 | 10.5 | 0.9408 | 0.0107 | 28.9 | 0.6597 |
| Fuori bin (80.5) | 943.7 | 12.0 | 0.2796 | 0.0090 | 28.7 | 0.4784 |

### Glissandi

| Segnale | Centroid (Hz) | Spread (Hz) | Flatness | Flux | Irregularity | TPR |
|---|---|---|---|---|---|---|
| Gliss lento 200-2000 | 1107.6 | 11.5 | 0.3311 | 0.2546 | 28.9 | 0.5860 |
| Gliss veloce 200-2000 | 1130.8 | 17.9 | 0.3992 | 0.6476 | 28.6 | 0.4686 |
| Gliss lento 2000-200 | 1093.0 | 11.4 | 0.3337 | 0.2572 | 28.8 | 0.5846 |
| Gliss micro 440-460 | 448.1 | 10.0 | 0.3513 | 0.0103 | 28.8 | 0.6075 |

### Due sinusoidi

| Segnale | Centroid (Hz) | Spread (Hz) | Flatness | Flux | Irregularity | TPR |
|---|---|---|---|---|---|---|
| 2 sin: 200 + 4000 Hz | 2130.6 | 1899.8 | 0.4241 | 0.0061 | 55.0 | 0.6162 |
| 2 sin: 400 + 1000 Hz | 702.3 | 300.6 | 0.4073 | 0.0082 | 54.9 | 0.6084 |
| 2 sin: 100 + 8000 Hz | 4045.1 | 3950.0 | 0.4215 | 0.0072 | 54.7 | 0.5371 |
| 2 sin: 200 cresc + 4000 dim | 2101.1 | 1487.6 | 0.4067 | 0.0078 | 53.7 | 0.6182 |
| 2 sin: 200 dim + 4000 cresc | 2137.7 | 1488.1 | 0.4061 | 0.0080 | 53.7 | 0.6176 |
| 2 sin: convergono 1000 | 1543.1 | 969.9 | 0.4593 | 0.1842 | 54.5 | 0.5912 |
| 2 sin: divergono da 1000 | 1548.9 | 980.1 | 0.4606 | 0.1843 | 54.6 | 0.5909 |
| 2 sin: convergono unisono | 400.0 | 51.7 | 0.4631 | 0.0194 | 47.0 | 0.5980 |

### Timbro dinamico

| Segnale | Centroid (Hz) | Spread (Hz) | Flatness | Flux | Irregularity | TPR |
|---|---|---|---|---|---|---|
| Tanh drive cresc 1-20 | 1346.8 | 1447.6 | 0.3422 | 0.0111 | 225.2 | 0.5153 |
| Tanh drive decresc 20-1 | 1335.7 | 1430.8 | 0.3427 | 0.0069 | 223.0 | 0.5149 |
| FM indice cresc 0.5-10 | 2340.0 | 1302.0 | 0.4971 | 0.0578 | 440.8 | 0.5935 |
| FM indice decresc 10-0.5 | 2341.2 | 1303.4 | 0.4990 | 0.0436 | 442.1 | 0.5964 |

## Confronto con analisi a banda piena (0-48000 Hz)

| Segnale | Centroid piena | Centroid 10kHz | Flatness piena | Flatness 10kHz |
|---|---|---|---|---|
| Noise bianco | 23947 | 4956 | 0.94 | 0.93 |
| Sin 75% + Noise 25% | 5623 | 684 | 0.31 | 0.20 |
| Sin 50% + Noise 50% | 22201 | 3654 | 0.91 | 0.74 |
| Sin 25% + Noise 75% | 23552 | 4594 | 0.94 | 0.89 |
| Tanh drive 20 | 2274 | 1857 | 0.33 | 0.39 |
| Noise crescendo | 22775 | 4020 | 0.91 | 0.78 |

## Osservazioni

- Il centroide del noise scende da ~24000 a ~5000 Hz, piu' confrontabile con i segnali tonali
- La transizione nel mix sin/noise diventa piu' graduale: 0.20 -> 0.74 -> 0.89 -> 0.94 (prima: 0.31 -> 0.91 -> 0.94)
- Flux e irregularity del noise si riducono (~80%) per il minor numero di bin considerate
- I segnali tonali (sinusoidi, FM, tanh, glissandi) restano praticamente invariati: il loro contenuto era gia' sotto 10 kHz
- La tanh drive 20 mostra flatness leggermente piu' alta (0.39 vs 0.33): le armoniche sopra 10 kHz non diluiscono piu' il calcolo
- Il limite rende i descrittori piu' sensibili alla zona musicalmente rilevante
