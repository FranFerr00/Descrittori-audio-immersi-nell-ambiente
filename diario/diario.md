# Diario di test

> Indice principale spostato in [README.md](../README.md).


## Voci per giorno

### [2026-03-30](2026-03-30.md)

- Spectral flatness in ambiente acustico
- Studio dei riferimenti (Peeters, Lerch, Krimphoff)
- Creazione schede descrittori

### [2026-04-02](2026-04-02.md)

- Script Python analisi offline e segnali di test Csound
- Tabella descrittori per segnale
- Limite di frequenza nell'analisi
- Segnali a timbro dinamico (tanh e FM)
- Flux lag (distanza tra frame)

### [2026-04-03](2026-04-03.md)

- Riscrittura TPR con prominence e conteggio picchi
- Ampliamento a 16 descrittori
- Script taglia_segnali.py e cartelle per segnale
- Dispensa LaTeX descrittori
- Registrazioni in ambiente acustico

### [2026-04-04](2026-04-04.md)

- Resoconto trasversale per descrittore (soglia relativa)
- Resoconto trasversale per segnale (soglia relativa -60 dB)

### [2026-04-07](2026-04-07.md)

- Tabelle per descrittore su tutti i segnali e modi di ripresa

### [2026-04-10](2026-04-10.md)

- Varianti del centroide spettrale (scheda `centroid/spectral_centroid_varianti.md`)
- Verifica numerica magnitude vs power vs MPEG-7 log sul clarinetto
- Scelta motivata della magnitude classica come default di `analisi.py`

### [2026-04-08](2026-04-08.md)

- Pipeline test segnali con Makefile e file sentinella
- Analisi del file intero rimossa, nuovo `aggrega_grafici.py`
- `-30 dB` (scalatura in float) sostituisce il vecchio `recs-001`
- Bug `--recs` vs nuovo `--subdir` in `taglia_segnali.py`
- `tabelle_descrittori.py` generalizzato ai modi
- Verifica dati: `-30db` ora coincide col sintetico (vecchio `recs-001` era artefatto 16-bit)
- Riscrittura `flatness/analisi-flatness.md`: `bin_esatto` 0.945 e' un limite numerico, non un artefatto di quantizzazione
- Riorganizzazione del diario per descrittore (cartelle `diario/flatness/`, `diario/spectral_crest_factor/`)
- Analisi del crest factor (`spectral_crest_factor/analisi-crest.md`): primo descrittore che reagisce all'indice FM su sintetico, ma collassa col bin esatto come la flatness

### [2026-04-13](2026-04-13.md)

- Scheda e analisi del centroide spettrale (`centroid/analisi-centroid.md`, `spectral-centroid.md`)
- Secondo descrittore con documentazione completa dopo la flatness

### [2026-04-15](2026-04-15.md)

- Riorganizzazione repository: output in `analisi/` separato dai sorgenti audio
- `temporali.py` con grafici per categoria e integrazione nella pipeline Makefile
- `README.md` per GitLab ricavato dal diario
- TPR: tre fix (regola MPEG-1 7 dB, lobo ±1 bin, scala dB tonal/noise)
- Flag `--only` in `analisi.py` e target `make desc ONLY=xxx`
- Output `--only` in sottocartelle per catalogo e campione
- Schede TPR in `diario/tpr/` (scheda estesa + analisi corpus)

### [2026-04-17](2026-04-17.md)

- Test entropy + contrast in `analisi_nuovi.py` sul corpus completo
- Decisione: **entropy entra nei 16 al posto di ACF** (contrast scartato)
- `analisi.py` aggiornato: entropy in categoria "distribuzione", chiave CSV `entropy`
- Decrease rimosso dai 16 (ridondante con slope, vedi `decrease/compass_artifact_*.md`)
- Sostituito da **OBSIR-std** (Essid/Richard/David 2006): std delle differenze log-energia tra bande ottavali consecutive
- Riorganizzazione famiglie 5+5+3+3 (tonality coefficient passa da Distribuzione a Tonalita')

### [2026-04-19](2026-04-19.md)

- `zscore.py` + `make zscore`: normalizzazione z-score per-sample dei CSV di analisi
- `plot_zscore.py` + `make zscore-plot`: PNG per ogni sample con 4 subplot (uno per famiglia), descrittori sovrapposti in σ
- Letture utili: confronto fra descrittori dentro lo stesso sample (forma del gesto), non fra sample diversi (per quello servono i valori grezzi o uno z-score globale)

### [2026-04-23](2026-04-23.md)

- Centroide monolitico in Pd (`centroid.c`): due passate, gate relativo, output diretto
- `arraymax.c` (riduzione array → float) e `arraycumsum.c` (per pipeline rolloff)
- Discrepanza catena vs monolitico su 100 Hz: fix con soglia adattiva `arraymax * 0.0316`

### [2026-04-28](2026-04-28.md)

- Monolitici `flatness`, `irregularity`, `flux` in `pd-externals/monolitici/`
- `flux` con buffer `prev` allocato in `calloc` + destructor + metodo `(reset)`
- Stato monolitici: 5/16 (centroid, spread, flatness, irregularity, flux)
- Chiusura del punto teorico catena vs monolitico (gating per frame)

### [2026-05-19](2026-05-19.md)

- Dispensa di mappatura descrittori -> bicomb: matrici di correlazione per famiglia
- Mappatura definitiva ai 5 ingressi del bicomb (2 continui, selettore, 2 trigger)
- Trigger FIR/IIR per famiglia implementati in `matrice_controlli.py`

### [2026-05-25](2026-05-25.md)

- Esterno generico `[matrice]` in Pd: porting di `matrice_controlli.py` (K inlet, uscite scalari configurabili, Jacobi simmetrico)
- Nucleo numerico in `matrice_core.h` + test standalone, verificato contro il Python
- Corrispondenza fra i due schemi di famiglie (studio vs mappatura al bicomb)

### [2026-05-26](2026-05-26.md)

- Banda di analisi del patch Pd allineata a 10 kHz come il Python (array `$0-spectrum` ridotto a 854 bin, nessun `.c` toccato)
- `[selettore]`: aggiunto l'argomento `finestra` (media mobile sugli ingressi)
- Profilo "lento" coerente nel patch di test (matrici a N=16/20, selettore dwell 1,5 s)

### [2026-05-31](2026-05-31.md)

- Controllo bipolare a ancore e distanza: un valore con segno (`v`) dalla distanza fra il suono e due ancore +1/-1, prototipo in `prova_ancore.py`
- Taratura z-score congelata e scelta degli assi (pochi ortogonali o sbiancamento): i 16 descrittori valgono circa 3,5 dimensioni, la brightness pesa il 50 percento
- Le quattro regole per posizionare le ancore (stesso mondo, raggiungibili, lontane fra loro, allineate al senso musicale)
- Prova su materiale reale (A Pierre di Nono): modo `--wav`, ancore da frame reali del brano, canali stereo come strumenti distinti, finestra centrale per la scelta
- Estensioni: piu' ancore per polo (minimo vs media), piu' parametri ognuno con la sua coppia +1/-1 (superficie di controllo a N dimensioni da un solo ingresso)

### [2026-06-01](2026-06-01.md)

- Dispensa del metodo a ancore e distanza (`dispensa-mapping-ancore.md`) con due schemi visivi
- Sbiancamento (Mahalanobis) della distanza: la brightness vale il 49,6 percento, dimensione effettiva 3,5; flag `--sbianca` in `prova_ancore.py`
- Catalogo frame per frame: l'ancora va presa nel cuore del suono (frame centrale), non come media del file
- Ogni strumento tarato sulle proprie ancore (l'asse del clarinetto non misura il timpano); scan dei soli campioni ufficiali (9 clarinetto, 10 timpano)
- Lo sbiancamento come spia: z-score e sbiancata coincidono se le ancore stanno su un asse vero, divergono se poggiano sulla brillantezza

### [2026-06-02](2026-06-02.md)

- Porting in Pure Data del controllo a ancore e distanza: external `[ancore]` (nucleo C `ancore_core.h` verificato contro `prova_ancore.py` a 5e-13), in sostituzione della mappatura matrice/bicomb
- Ordine dei 16 descrittori fisso (`DESCS`) come contratto dell'external; `media`/`dev` restano il righello del corpus, caricati da `loadbang`
- Ancore `+1`/`-1` come abstraction unica `ancora.pd` (`[ancora <polo> <k>]`, argomenti escapati `\$1 \$2`), selettore della sorgente che scatta subito (`0` dal vivo, indice dal catalogo)
- Architettura a send/receive con due bus locali (`$0-frame`, `$0-anc`): niente cavi lunghi
- Il messaggio `piu 0 ...` da `list prepend` piu' `list trim` (il primo elemento diventa selettore); monitoraggio col `[list]` davanti al listbox o `[print]`
- Multi-parametro `[ancore 5]`: cinque coppie +1/-1, dieci `[ancora]`, uscita lista di 5 `v` con `[unpack]`
- Catalogo a 64 suoni (45 sintetici, 9 clarinetto, 10 timpano sul frame centrale): motore impacchettato `suoni.pd` + pannello-elenco `catalogo.pd`, number box come selettore, generatore `genera_suoni_pd.py`
- Media recente come terza via di cattura: external `[ema]` (media mobile esponenziale con costante di tempo in secondi); selettore `-1`=media, `0`=frame, `1+`=catalogo
- Inciampi: `\$0`/`\$1` da escapare (anche nei message box), `;` e `,` nei commenti `#X text` spezzano il record, un `[r \$0-...]` in abstraction non vede il bus del padre

### [2026-06-13](2026-06-13.md)

- Registrazione al LEAP: i descrittori alla prova della distanza
- 8 microfoni LineAudio OM1 in fila (1-8 m, passo 1 m), HS8 come sorgente, doppia ripresa orizzontale/verticale
- Sorgenti: pink noise, clarinetto contrabbasso (Do grave e cluster), clarinetto soprano

### [2026-06-16](2026-06-16.md)

- Pipeline d'analisi del materiale e report di laboratorio (`report-distanza-leap.tex`)
- Calibrazione dei gain ottima (dev.std 0,17 dB); attenuazione del rumore −3 dB/raddoppio (1/√r), non i −6 dB del campo libero
- Banda piena contro tetto a 10 kHz: il tetto nascondeva l'assorbimento dell'aria (centroide del rumore in calo con la distanza)
- Onda del centroide sui CCB (onda stazionaria della fondamentale, nodo ~mic3, ventre ~mic5-6); punto aperto: modo della stanza o geometria sorgente-microfono

## Schede descrittori

### Forma dello spettro

- [Spectral Centroid](centroid/spectral-centroid.md) — [analisi sul corpus](centroid/analisi-centroid.md)
- [Spectral Spread](spread/spectral-spread.md)
- [Spectral Rolloff](rolloff/spectral-rolloff.md)
- [Spectral Slope](spectral-slope/spectral-slope.md) — [analisi sul corpus](spectral-slope/analisi-slope.md)
- [Spectral OBSIR-std](obsir/spectral-obsir.md) — da scrivere

### Distribuzione

- [Spectral Flatness](flatness/spectral-flatness.md) — [analisi sul corpus](flatness/analisi-flatness.md)
- [Spectral Crest Factor](spectral_crest_factor/spectral_crest_factor.md) — [analisi sul corpus](spectral_crest_factor/analisi-crest.md)
- [Spectral Skewness](skewness/spectral-skewness.md)
- [Spectral Kurtosis](kurtosis/spectral-kurtosis.md)
- [Spectral Entropy](entropy/spectral-entropy.md) — da scrivere

### Tonalita'

- [Tonal Power Ratio](tpr/tonal-power-ratio.md) — [analisi sul corpus](tpr/analisi-tpr.md) (copre `tpr` e `n_peaks`)
- [Tonality Coefficient](tonality/tonality-coefficient.md)

### Dinamica

- [Spectral Flux](flux/spectral-flux.md)
- [Spectral Irregularity](irregularity/spectral-irregularity.md)
- [Zero Crossing Rate](zcr/zero-crossing-rate.md)

## Cataloghi di gesti strumentali

- [Clarinetto contrabbasso](cataloghi/clarinettocb.md) — osservazioni numeriche sui 9 campioni ufficiali di dinamica
- [Timpano](cataloghi/timpano.md) — osservazioni numeriche sui 10 campioni ufficiali di dinamica
- [Sinusoide 100 Hz](cataloghi/sine_100hz.md) — riferimento numerico per la fondamentale comune a clarinetto e timpano

## Altro

- [Dispensa: mapping bipolare a ancore e distanza](dispensa-mapping-ancore.md) — come nasce il valore con segno `v` dalla distanza fra suono e due ancore +1/-1
- [Prossimi test](prossimi-test.md)
- [Tabella segnali di test](tabella-segnali-10khz.md)
- [Dispensa LaTeX descrittori](dispensa-descrittori.pdf)
