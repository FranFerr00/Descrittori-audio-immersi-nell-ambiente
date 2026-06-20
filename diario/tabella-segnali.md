# Tabella descrittori per segnale

Configurazione: FFT 8192, Hann, overlap 50%, SR 96000, limite 10 kHz (`--max-freq 10000`)

Valori medi per segnale. Generata da `segnali/tabelle/segnali_sommario.csv` (aggiornata 2026-04-13).

| Segnale | Centroid (Hz) | Spread (Hz) | Flatness | Flux | Irregularity | TPR |
|---|---|---|---|---|---|---|
| Sinusoide 440 Hz | 440.1 | 11.5 | 0.1036 | 0.0000 | 28.7 | 0.9995 |
| Noise bianco | 4999.9 | 2890.1 | 0.8462 | 1.0675 | 471.9 | 0.7579 |
| Tanh drive 1 | 481.2 | 194.1 | 0.1104 | 0.0000 | 67.6 | 0.9995 |
| Tanh drive 5 | 938.1 | 922.9 | 0.1546 | 0.0000 | 202.7 | 0.9996 |
| Tanh drive 20 | 1888.4 | 2122.6 | 0.2100 | 0.0000 | 276.2 | 0.9875 |
| Noise BP Q=500 | 2865.6 | 2433.3 | 0.5731 | 1.5421 | 484.9 | 0.9990 |
| Noise BP Q=200 | 2497.3 | 2294.2 | 0.4807 | 1.2113 | 503.0 | 0.9986 |
| Noise BP Q=50 | 2168.3 | 2108.9 | 0.3934 | 0.8452 | 648.7 | 0.9893 |
| Impulsi 100 Hz | 4993.0 | 2896.7 | 0.1789 | 0.0003 | 1184.1 | 0.4579 |
| FM indice 0.5 | 548.9 | 333.3 | 0.1500 | 0.0001 | 158.6 | 0.9996 |
| FM indice 3 | 1433.0 | 880.6 | 0.1357 | 0.0004 | 384.0 | 0.9998 |
| FM indice 10 | 4297.5 | 2255.4 | 0.1423 | 0.0003 | 722.4 | 0.9484 |
| Sin 100% | 440.1 | 11.5 | 0.1036 | 0.0000 | 28.7 | 0.9995 |
| Sin 75% + Noise 25% | 3157.8 | 3161.1 | 0.5434 | 0.2751 | 957.9 | 0.9974 |
| Sin 50% + Noise 50% | 4171.6 | 3148.9 | 0.7134 | 0.5340 | 536.4 | 0.9829 |
| Sin 25% + Noise 75% | 4698.4 | 3007.9 | 0.8025 | 0.8022 | 484.4 | 0.8962 |
| Noise 100% | 4994.3 | 2888.7 | 0.8458 | 1.0610 | 475.3 | 0.7558 |
| Sin crescendo | 440.2 | 12.9 | 0.1030 | 0.0036 | 27.1 | 0.9995 |
| Sin diminuendo | 440.1 | 12.6 | 0.1031 | 0.0036 | 27.2 | 0.9995 |
| Sin cresc-dim | 440.2 | 14.0 | 0.1025 | 0.0071 | 27.7 | 0.9995 |
| Noise crescendo | 4986.1 | 2881.8 | 0.8456 | 0.5282 | 475.0 | 0.7561 |
| Noise diminuendo | 5000.3 | 2890.3 | 0.8443 | 0.5363 | 478.1 | 0.7579 |
| Noise cresc-dim | 4995.7 | 2887.3 | 0.8451 | 0.5419 | 474.9 | 0.7575 |
| Bin esatto (40) | 468.8 | 8.3 | 0.9450 | 0.0000 | 29.0 | 1.0000 |
| Fuori bin (40.5) | 474.6 | 11.6 | 0.1045 | 0.0000 | 28.7 | 0.9995 |
| Bin esatto (80) | 937.5 | 8.3 | 0.9450 | 0.0000 | 29.0 | 1.0000 |
| Fuori bin (80.5) | 943.4 | 11.6 | 0.1045 | 0.0000 | 28.7 | 0.9995 |
| Gliss lento 200-2000 | 1098.5 | 11.6 | 0.1185 | 0.2523 | 28.9 | 0.9996 |
| Gliss veloce 200-2000 | 1095.8 | 16.6 | 0.1565 | 0.6391 | 28.7 | 0.9928 |
| Gliss lento 2000-200 | 1101.5 | 11.6 | 0.1187 | 0.2524 | 28.9 | 0.9996 |
| Gliss micro 440-460 | 450.0 | 10.2 | 0.1113 | 0.0031 | 28.9 | 0.9998 |
| 2 sin: 200 + 4000 Hz | 2134.1 | 1899.7 | 0.0953 | 0.0000 | 55.1 | 0.9999 |
| 2 sin: 400 + 1000 Hz | 703.3 | 300.2 | 0.0966 | 0.0000 | 55.1 | 0.9998 |
| 2 sin: 100 + 8000 Hz | 4038.5 | 3950.1 | 0.0966 | 0.0003 | 53.0 | 0.9996 |
| 2 sin: 200 cresc + 4000 dim | 2127.9 | 1501.2 | 0.1094 | 0.0044 | 54.0 | 0.9999 |
| 2 sin: 200 dim + 4000 cresc | 2117.4 | 1501.2 | 0.1092 | 0.0044 | 54.0 | 0.9999 |
| 2 sin: convergono 1000 | 1548.3 | 976.5 | 0.1149 | 0.1838 | 54.4 | 0.9992 |
| 2 sin: divergono da 1000 | 1546.5 | 973.3 | 0.1152 | 0.1836 | 54.2 | 0.9996 |
| 2 sin: convergono unisono | 400.0 | 52.1 | 0.1196 | 0.0216 | 41.1 | 0.9921 |
| Tanh drive cresc 1-20 | 1362.8 | 1479.5 | 0.1790 | 0.0040 | 236.0 | 0.9996 |
| Tanh drive decresc 20-1 | 1365.1 | 1482.6 | 0.1792 | 0.0040 | 236.3 | 0.9996 |
| FM indice cresc 0.5-10 | 2355.3 | 1324.7 | 0.1349 | 0.0390 | 501.0 | 0.9998 |
| FM indice decresc 10-0.5 | 2361.5 | 1327.9 | 0.1348 | 0.0390 | 502.1 | 0.9998 |
| Tanh drive cresc veloce | 1363.2 | 1481.2 | 0.1790 | 0.0127 | 236.7 | 0.9996 |
| FM indice cresc veloce | 2346.9 | 1322.7 | 0.1351 | 0.1245 | 501.1 | 0.9998 |

## Osservazioni

**Flatness:**
- Noise bianco ~0.85, sinusoide ~0.10, FM ~0.14
- La tanh aggiunge armoniche ma sposta la flatness solo da 0.10 a 0.21 (drive 20): l'aggiunta di componenti armoniche regolari non basta a rendere lo spettro "piatto"
- Il mix sin/noise ha una transizione graduale: 0.10 (sin pura) → 0.54 (75%) → 0.71 (50%) → 0.80 (25%) → 0.85 (noise puro)
- Bin esatto da' flatness 0.945 (poche bin tutte simili → GM/AM → 1, caso limite); fuori bin da' 0.104 (distribuzione irregolare nel lobo)
- Gli inviluppi non alterano la flatness della sinusoide (0.103 sia statica che crescendo/diminuendo)
- Calcolata solo sulle bin attive (sopra soglia relativa -60 dB dal picco del frame)

**Spread:**
- Migliore indicatore della distanza tra componenti: 11.5 Hz per sinusoide sola, 1900 Hz per 200+4000 Hz, 3950 Hz per 100+8000 Hz
- Cattura bene la ricchezza armonica della tanh (194 → 923 → 2123 Hz)
- Segue la convergenza di due sinusoidi

**Flux:**
- Quasi zero per segnali stazionari
- Alto per noise (~1.07), proporzionale alla banda nel range 0-10 kHz
- Il glissando veloce da' flux piu' alto del lento (0.64 vs 0.25)

**Irregularity:**
- Noise ~472-649, sinusoide ~29, due sinusoidi ~55
- Impulsi al massimo (1184): picchi isolati ogni frame creano transizioni brusche
- Proporzionale al numero di transizioni brusche nello spettro

**TPR:**
- Quasi sempre vicino a 1.0 per segnali tonali (sinusoidi, tanh, FM, glissandi, 2 sinusoidi)
- Noise bianco: ~0.76; noise BP: 0.99-1.00 (i picchi del noise filtrato vengono catturati)
- Impulsi: 0.46 (il lobo dei picchi non domina il totale dell'energia distribuita)
- Mix sin+noise: scende gradualmente da 1.0 a 0.76 all'aumentare del noise
- Bin esatto: 1.0 esatto (un solo lobo cattura tutta l'energia)
