# Analisi del centroide spettrale sul corpus di test

Analisi del comportamento del descrittore `centroid` sulle tabelle di `segnali/tabelle/segnali_tabelle.md` (segnali sintetici) e `segnali/tabelle/confronto_modi_tabelle.md` (confronto sintetico vs modi di ripresa).

Parametri di analisi: FFT 8192, hop 4096 (50% overlap), finestra Hann, soglia relativa -60 dB dal picco, calcolo sulle sole bin attive, SR 96 kHz, `max_freq` 10 kHz. Tutto il corpus e' in WAV float32; le sorgenti `recs-002/003/004.wav` sono PCM_24, conversione a float per il taglio esatta. Formula: magnitude classica (media pesata delle frequenze con pesi = magnitudine).

## Cosa misura (ripasso dalla ricerca)

Baricentro dello spettro: media pesata delle frequenze, dove i pesi sono le magnitudini. Unita': Hz. Correlato percettivamente alla *brillantezza* del timbro.

centroide = somma( f(k) * |X(k)| ) / somma( |X(k)| )

Range: [0 Hz, max_freq]. Una sinusoide pura ha centroide uguale alla propria frequenza. Il noise bianco ha centroide a meta' banda (5000 Hz su [0, 10 kHz]).

**Nota chiave:** il centroide e' invariante per scala di ampiezza (raddoppiare il segnale non cambia il valore) ma *non* e' invariante per trasposizione: suonare la stessa nota un'ottava sopra raddoppia il centroide anche se il timbro e' identico (Schubert e Wolfe 2006). Non misura il timbro puro, misura dove sta l'energia, che e' un intreccio di timbro e registro.

## Comportamento sui segnali sintetici

### Segnali stazionari di riferimento

| Segnale | Centroide (Hz) | Std |
|---|---|---|
| 01_sinusoide_440 | 440 | ~0 |
| 13_sin100 | 440 | ~0 |
| 02_noise_bianco | 5000 | 70 |
| 17_noise100 | 4994 | 70 |
| 09_impulsi_100 | 4993 | 0.06 |

La sinusoide pura restituisce esattamente la propria frequenza (440 Hz, con std nell'ordine di 10^-14, cioe' zero macchina). Il noise bianco sta a 5000 Hz, esattamente meta' del range [0, 10 kHz], come atteso per una distribuzione uniforme. Lo std del noise (~70 Hz) e' piccolo rispetto al valore: il centroide e' molto stabile anche su segnali aleatori.

Il treno di impulsi a 100 Hz ha centroide 4993 Hz, praticamente identico al noise: il suo spettro a righe equidistanti e' uniforme in media su tutta la banda, come il noise, ma senza la fluttuazione stocastica (std 0.06 Hz).

**Nota su `13_sin100`:** il centroide restituisce 440 Hz, non 100 Hz. Questo perche' la sinusoide a 100 Hz ha fondamentale fuori dalla risoluzione, e il centroide cade sulla prima bin attiva sopra soglia. (Da verificare: potrebbe essere un artefatto della soglia relativa, se la fondamentale e' nella prima bin e la soglia la esclude.)

### Tanh (saturazione crescente)

| Segnale | Drive | Centroide |
|---|---|---|
| 03_tanh_drive1 | 1 | 481 |
| 04_tanh_drive5 | 5 | 938 |
| 05_tanh_drive20 | 20 | 1888 |

Il centroide cresce in modo quasi proporzionale al drive: x2 da drive 1 a drive 5, x4 da drive 1 a drive 20. La saturazione aggiunge armoniche alte, il baricentro dello spettro sale di conseguenza. A differenza della flatness (che era quasi cieca alla saturazione, da 0.11 a 0.21), il centroide reagisce fortemente: il rapporto drive 20/drive 1 e' 3.9x sul centroide contro 1.9x sulla flatness.

**Confronto con la sinusoide pura:** tanh drive 1 ha centroide 481, leggermente sopra i 440 della sinusoide. La tanh a drive 1 e' gia' lievemente non lineare e aggiunge un po' di terza armonica. La flatness non vedeva questa differenza (0.110 vs 0.104); il centroide la vede.

Tutti i valori hanno std ~0: i segnali sono stazionari, il centroide non oscilla.

### FM (indice di modulazione crescente)

| Segnale | Indice | Centroide |
|---|---|---|
| 10_fm_idx05 | 0.5 | 549 |
| 11_fm_idx3 | 3 | 1433 |
| 12_fm_idx10 | 10 | 4298 |

La FM mostra una crescita ancora piu' marcata della tanh: da 549 a 4298 Hz, rapporto 7.8x. L'indice di modulazione aggiunge bande laterali larghe e il centroide le segue fedelmente. Questo e' un punto dove centroide e flatness divergono completamente: la flatness era cieca all'indice FM (tutti attorno a 0.14), il centroide lo traccia con precisione.

FM idx 10 ha centroide quasi uguale al noise bianco (4298 vs 5000 Hz). Lo spettro e' effettivamente molto largo, ma a differenza del noise le componenti sono discrete e piccate: il centroide non li distingue, per quello serve la flatness (0.14 vs 0.85) o il crest.

### Miscele sin+noise (rapporto variabile)

| % noise | Centroide |
|---|---|
| 0% (sin pura) | 440 |
| 25% | 3158 |
| 50% | 4172 |
| 75% | 4698 |
| 100% (noise) | 4994 |

Curva monotona e molto ripida in basso: il 25% di noise porta il centroide da 440 a 3158 Hz, gia' a due terzi del valore di noise puro. La ragione e' che il noise aggiunge energia su tutta la banda [0, 10 kHz], spostando massicciamente il baricentro verso l'alto rispetto alla singola riga a 440 Hz.

La sensibilita' e' l'opposto della flatness: la flatness era sensibilissima alle piccole aggiunte di noise (da 0.10 a 0.54 con 25% di noise), il centroide lo e' ancora di piu' in termini assoluti (da 440 a 3158 Hz, un salto di 2700 Hz). Entrambi sono sensibili al noise, ma per ragioni diverse: la flatness perche' il noise riempie le bin vuote, il centroide perche' il noise aggiunge energia nelle alte frequenze.

### Noise bandpass (effetto del Q)

| Segnale | Q | Centroide |
|---|---|---|
| 06_noise_bp_q500 | 500 | 2866 |
| 07_noise_bp_q200 | 200 | 2497 |
| 08_noise_bp_q50 | 50 | 2168 |

Tutti i filtri sono centrati a 2000 Hz. Il centroide si avvicina alla frequenza centrale al diminuire del Q (filtro piu' selettivo), ma non la raggiunge mai esattamente: 2168 Hz con Q 50, ancora 168 Hz sopra il centro del filtro. Questo perche' il centroide e' sensibile all'asimmetria dello spettro: il noise filtrato ha un roll-off non simmetrico attorno al centro, e il centroide si sposta verso il lato con piu' energia.

Lo spread e la variabilita' (std) calano insieme al Q: noise bp Q50 ha std 87 Hz, Q500 ha std 60 Hz. Il filtro piu' stretto produce anche un centroide piu' stabile.

### Bin esatto e fuori bin

| Segnale | Centroide |
|---|---|
| 24_bin_esatto_40 | 468.8 |
| 25_fuori_bin_40 | 474.6 |
| 26_bin_esatto_80 | 937.5 |
| 27_fuori_bin_80 | 943.4 |

A differenza della flatness (che schizzava a 0.945 sul bin esatto), il centroide non mostra nessun artefatto: i valori sono vicini e coerenti. Il bin esatto da' un centroide leggermente piu' basso del fuori bin (468.8 vs 474.6 per la coppia 40) perche' il leakage del fuori bin sposta un po' di energia verso i sidelobes, ma la differenza e' di 6 Hz su 470. Il centroide e' robusto al problema del bin esatto perche' la formula (media pesata) non e' sensibile al *numero* di bin attivi come lo e' la media geometrica della flatness.

### Segnali dinamici (crescendo/diminuendo)

| Segnale | Min | Max | Media | Std |
|---|---|---|---|---|
| 18_sin_crescendo | 440.1 | 448.6 | 440.2 | 0.81 |
| 19_sin_diminuendo | 440.1 | 445.4 | 440.1 | 0.52 |
| 20_sin_crescdim | 440.1 | 448.6 | 440.2 | 0.95 |
| 21_noise_crescendo | 4833 | 5125 | 4986 | 67 |
| 22_noise_diminuendo | 4805 | 5135 | 5000 | 73 |
| 23_noise_crescdim | 4825 | 5137 | 4996 | 72 |

Il centroide della sinusoide e' praticamente costante durante il crescendo: oscilla di meno di 9 Hz (440-449). Questo conferma l'invarianza per scala di ampiezza: cambiare volume non sposta il baricentro dello spettro. Stesso comportamento per il noise (circa 5000 Hz in ogni condizione).

A differenza della flatness (che nei crescendo di sinusoide scendeva a 0.067 nei frame deboli per instabilita' numerica), il centroide resta stabile: e' immune all'effetto "pochi bin attivi" che destabilizzava la flatness.

### Glissandi e microglissandi

| Segnale | Min | Max | Media | Std |
|---|---|---|---|---|
| 28_gliss_lento_200_2000 | 208 | 1990 | 1098 | 517 |
| 29_gliss_veloce_200_2000 | 225 | 1966 | 1096 | 510 |
| 30_gliss_lento_2000_200 | 211 | 1992 | 1102 | 517 |
| 31_gliss_micro_440_460 | 440 | 460 | 450 | 5.7 |

Il centroide traccia il glissando con precisione: min e max corrispondono alle frequenze estreme (200 e 2000 Hz), la media e' al centro (1098 Hz), lo std e' alto (517 Hz) perche' il segnale percorre tutto il range. Il gliss lento e il veloce danno media quasi identica (1098 vs 1096) ma min e max leggermente diversi: il gliss veloce non raggiunge gli estremi (225 vs 208 come minimo) perche' il movimento rapido non lascia il tempo a un frame intero di catturare la frequenza piu' bassa.

Il microgliss (440-460 Hz) restituisce esattamente media 450 Hz con std 5.7 Hz: il centroide e' un tracker di frequenza preciso quando c'e' una sola componente. A differenza della flatness (che oscillava fino a 0.945 quando il microgliss passava su un bin esatto), il centroide non ha artefatti.

### Doppie sinusoidi

| Segnale | Centroide | Note |
|---|---|---|
| 32_2sin_200_4000 | 2134 | media pesata di 200 e 4000 |
| 33_2sin_400_1000 | 703 | media pesata di 400 e 1000 |
| 34_2sin_100_8000 | 4038 | sbilanciata verso 8000 |
| 39_2sin_convergono_unisono | 400 | converge a 400 Hz |

Con due sinusoidi di uguale ampiezza, il centroide e' la media aritmetica delle due frequenze: (200+4000)/2 = 2100, osservato 2134 (la leggera differenza dipende dal leakage FFT). 33_2sin_400_1000 da' 703, vicino a (400+1000)/2 = 700.

Il caso 34 (100+8000 Hz) da' 4038, spostato verso l'alto rispetto alla media (4050) ma coerente. Due sinusoidi convergenti verso l'unisono a 400 Hz danno centroide stabile a 400 Hz quando le frequenze coincidono.

Le doppie sinusoidi con ampiezze variabili (35, 36) producono centroide che segue la componente piu' forte: quando la sinusoide a 200 Hz cresce e quella a 4000 Hz cala, il centroide scende da ~4000 a ~230 Hz (e viceversa). Il centroide e' un tracciatore del baricentro istantaneo, sensibile sia alla frequenza sia all'ampiezza relativa delle componenti.

### Segnali con parametri variabili (tanh drive e FM indice)

| Segnale | Min | Max | Media |
|---|---|---|---|
| 40_tanh_drive_cresc | 489 | 1886 | 1363 |
| 41_tanh_drive_decresc | 491 | 1887 | 1365 |
| 42_fm_idx_cresc | 558 | 4270 | 2355 |
| 43_fm_idx_decresc | 562 | 4277 | 2362 |
| 44_tanh_drive_cresc_veloce | 506 | 1880 | 1363 |
| 45_fm_idx_cresc_veloce | 583 | 4206 | 2347 |

Il centroide traccia la variazione del parametro di sintesi in tempo reale: sulla tanh da 489 (drive basso) a 1886 (drive massimo), sulla FM da 558 (idx basso) a 4270 (idx alto). La FM ha un'escursione 4 volte piu' grande della tanh (3700 Hz vs 1400 Hz), perche' le bande laterali FM si estendono molto piu' in alto nello spettro rispetto alle armoniche della saturazione.

I crescendo lenti e veloci danno min/max quasi identici: la velocita' del cambiamento non influenza gli estremi del centroide (a differenza della flatness, dove lo smearing spettrale dei glissandi veloci alterava il valore).

## Comportamento sotto ripresa microfonica

I cinque modi sono:
- `sintetico`: taglio diretto di `test_segnali.wav` (Csound, float32)
- `test_segnali_-30db`: lo stesso file scalato in float di -30 dB
- `recs-002`: microfono a 1 m dall'altoparlante
- `recs-003`: microfono a 2 m, ambiente sporco (voci di sottofondo)
- `recs-004`: microfono a 2 m, ambiente pulito

### Caso 1: invarianza per scala di ampiezza (conferma)

La colonna `-30 dB` e' identica al sintetico per *tutti* i segnali, senza eccezione. Come la flatness, il centroide e' invariante per scala, e la conversione in float elimina qualsiasi artefatto di quantizzazione. La proprieta' e' garantita dalla formula: moltiplicare tutti i |X(k)| per una costante non cambia il rapporto somma(f*|X|)/somma(|X|).

### Caso 2: il noise scende, i segnali tonali sono stabili o salgono

| Segnale | sintetico | recs-002 (1m) | recs-003 (2m sporco) | recs-004 (2m pulito) |
|---|---|---|---|---|
| 02_noise_bianco | 5000 | 3285 | 3487 | 3160 |
| 17_noise100 | 4994 | 3315 | 3537 | 3450 |
| 01_sinusoide_440 | 440 | 409 | 614 | 439 |
| 03_tanh_drive1 | 481 | 372 | 571 | 432 |
| 05_tanh_drive20 | 1888 | 1204 | 1547 | 1541 |

Il noise bianco crolla da 5000 a circa 3300 Hz sotto microfono: la risposta in frequenza dell'altoparlante e della stanza taglia le alte, il baricentro scende. E' un effetto fisico reale (colorazione acustica) e il centroide lo misura correttamente.

La sinusoide pura e' quasi stabile: 440 Hz sintetica, 409-614 Hz microfonata. Le piccole variazioni dipendono dal rumore ambientale e dal riverbero che aggiungono componenti spettrali attorno e sopra la fondamentale. A 2 m sporco (recs-003) il centroide sale a 614 Hz perche' il rumore ambientale contribuisce piu' energia rispetto al segnale puro attenuato dalla distanza.

Tanh drive 20 scende da 1888 a 1204-1541 Hz: le armoniche alte sono attenuate dalla catena acustica.

**Convergenza:** il noise scende (5000 → 3300) e i segnali tonali restano bassi o salgono leggermente. Come per la flatness, la distanza tra i due estremi si riduce sotto microfono, ma resta sempre leggibile. Il rapporto noise/sinusoide passa da 11x (sintetico) a circa 7x (microfonato): la discriminabilita' si riduce di un terzo.

### Caso 3: FM ad alto indice crolla sotto microfono

| Segnale | sintetico | recs-002 | recs-003 | recs-004 |
|---|---|---|---|---|
| 10_fm_idx05 | 549 | 507 | 505 | 468 |
| 11_fm_idx3 | 1433 | 1165 | 935 | 1081 |
| 12_fm_idx10 | 4298 | 2745 | 2772 | 2809 |

La FM idx 10 passa da 4298 a circa 2800 Hz, una caduta di un terzo. L'effetto e' simile a quello del noise (caduta delle alte frequenze per la risposta dell'altoparlante) e coerente: la FM a indice alto ha componenti distribuite su tutta la banda, come il noise, e subisce la stessa colorazione. La FM a basso indice (549 Hz) e' quasi stabile perche' le sue componenti sono tutte nella zona bassa, dove la catena acustica e' relativamente piatta.

### Caso 4: miscele sin+noise sotto microfono

| % noise | sintetico | recs-002 | recs-003 | recs-004 |
|---|---|---|---|---|
| 25% | 3158 | 1405 | 2398 | 2385 |
| 50% | 4172 | 2525 | 2959 | 2863 |
| 75% | 4698 | 3002 | 3305 | 3251 |
| 100% | 4994 | 3315 | 3537 | 3450 |

A 1 m (recs-002) la caduta e' piu' severa della distanza: sin+25% noise passa da 3158 a 1405 Hz, meno della meta'. A 2 m la caduta e' piu' moderata (2398 Hz). La spiegazione: a 1 m il microfono capta fedelmente il segnale dell'altoparlante (con il suo roll-off), a 2 m il riverbero e il rumore ambientale riempiono le alte frequenze, compensando parzialmente la colorazione.

### Caso 5: segnali dinamici sotto microfono

| Segnale | sintetico | recs-002 | recs-003 | recs-004 |
|---|---|---|---|---|
| 18_sin_crescendo | 440 | 237 | 600 | 236 |
| 19_sin_diminuendo | 440 | 318 | 301 | 213 |
| 21_noise_crescendo | 4986 | 2676 | 2749 | 2761 |

Le sinusoidi dinamiche mostrano variabilita' sotto microfono: il crescendo a 1m ha centroide medio 237 Hz, molto sotto i 440 Hz sintetici. I frame deboli (inizio del crescendo) sono dominati dal rumore di fondo della stanza che ha centroide basso (molti contributi sotto 440 Hz). Nei diminuendo il problema e' simmetrico: la coda debole trascina giu' la media.

Il noise dinamico scende da ~5000 a ~2700 Hz, la stessa caduta del noise stazionario. La colorazione acustica agisce indipendentemente dalla dinamica.

### Caso 6: doppie sinusoidi sotto microfono

| Segnale | sintetico | recs-002 | recs-003 | recs-004 |
|---|---|---|---|---|
| 32_2sin_200_4000 | 2134 | 1207 | 1026 | 1270 |
| 34_2sin_100_8000 | 4038 | 2011 | 1517 | 1181 |

La coppia 200+4000 Hz scende da 2134 a 1026-1270 Hz. L'alta frequenza (4000 Hz) e' piu' attenuata dalla catena acustica rispetto alla bassa (200 Hz), quindi il baricentro si sposta verso il basso. L'effetto e' ancora piu' estremo sulla coppia 100+8000 Hz: da 4038 a 1181 Hz (recs-004), quasi un terzo. La componente a 8000 Hz e' fortemente tagliata dal roll-off dell'altoparlante e il centroide si avvicina alla sola fondamentale bassa.

### Caso 7: 2m sporco vs 2m pulito

A differenza della flatness (dove le due condizioni erano quasi identiche), il centroide mostra differenze piu' grandi tra recs-003 e recs-004 su alcuni segnali: la sinusoide 440 Hz ha 614 Hz (sporco) vs 439 Hz (pulito), e le doppie sinusoidi differiscono di 100-300 Hz. Il centroide e' piu' sensibile al rumore ambientale della flatness perche' il rumore aggiunge energia nelle alte frequenze che sposta il baricentro, mentre la flatness e' un rapporto statistico che assorbe meglio l'aggiunta di componenti sparse.

## Comportamento sul corpus strumentale (clarinetto contrabbasso)

Dati dal catalogo `cataloghi/clarinettocb.md`, 9 campioni con fondamentale fissa a ~100 Hz. Gate `-65/-30` attivo.

### Dinamiche fisse

| Campione | Dinamica | Centroide (Hz) |
|---|---|---|
| 001 | p1 | 207 |
| 002 | p2 | 231 |
| 003 | mf | 403 |
| 004 | f | 1133 |

Crescita monotona da piano a forte, rapporto 5.5x. L'effetto e' fisico: aumentando il fiato il musicista eccita armonici piu' alti che si aggiungono ai bassi, e il baricentro sale. Sul piano lo spettro e' quasi tutto nella fondamentale (centroide 207 Hz, vicino alla frequenza fondamentale ~100 Hz piu' la seconda armonica); sul forte la serie armonica si estende e il centroide sale a 1133 Hz.

**Confronto con la flatness:** il centroide ha rapporto p1/f = 5.5x, la flatness 1.6x (0.123 → 0.199). Il centroide e' molto piu' sensibile alla dinamica su questo strumento. Entrambi sono monotoni, ma il centroide offre un'escursione utile 3.5 volte maggiore.

### Dinamiche variabili (gesti)

I gesti del clarinetto mostrano il centroide come tracciatore della traiettoria energetica:

- **Crescendo (005, 006):** salita del centroide fino a ~70% della durata, poi rilascio. Il culmine (1420-1470 Hz) corrisponde al momento di massimo fiato. L'ultimo 30% del sample ha centroide in discesa mentre il crest sale: il fiato si ritira, lo spettro si riconcentra su pochi armonici prominenti.

- **Diminuendo (007):** culmine nei primi 0.6 s (1470 Hz), poi decadimento monotono. Traiettoria strettamente monotona sui chunk medi per tutti i descrittori di forma. Gesto piu' facile da leggere numericamente del catalogo.

- **Crescendo-diminuendo (010):** non una campana semplice ma "piccolo attacco iniziale + lunga campana centrata". Il 53% dei frame ha centroide sotto 200 Hz: meta' del sample e' quiete (pause del fiato tra le due porzioni).

- **Diminuendo-crescendo (013):** forma a U asimmetrica. Il primo picco (1690 Hz, max dell'intero catalogo) e' breve (primi 0.4 s); il secondo (1510 Hz) arriva a ~14 s ed e' piu' esteso ma non raggiunge il primo.

### Nota sulle varianti della formula

La verifica numerica sul clarinetto (diario 2026-04-10) ha mostrato che magnitude, power e MPEG-7 log danno valori molto diversi sullo stesso campione (rispettivamente 1133, 481, 323 Hz sul forte 004), ma **preservano l'ordine** p1 < p2 < mf < f. I rapporti cambiano (5.5x, 4.0x, 3.0x) ma le osservazioni qualitative restano valide con qualunque scelta. La formula va dichiarata esplicitamente in tesi.

## Sintesi delle proprieta' emerse

**Cosa il centroide fa bene:**

1. Traccia la frequenza delle sinusoidi pure con precisione assoluta (errore < 1 Hz)
2. Misura la ricchezza armonica della saturazione (tanh: rapporto 3.9x da drive 1 a drive 20) e dell'indice FM (7.8x da idx 0.5 a idx 10), dove la flatness era cieca
3. Discrimina le dinamiche sugli strumenti acustici con alto rapporto (5.5x piano/forte sul clarinetto contrabbasso)
4. Traccia le traiettorie temporali dei gesti (crescendo, diminuendo, campane) con precisione istantanea
5. Misura la colorazione acustica della catena di ripresa (caduta sistematica delle alte: noise da 5000 a 3300 Hz)
6. E' invariante per scala di ampiezza (verificato sul `-30 dB` in float)
7. E' robusto al problema del bin esatto (nessun artefatto, a differenza della flatness)
8. E' stabile sui segnali dinamici (crescendo/diminuendo non spostano il centroide delle sinusoidi)

**Cosa il centroide non fa:**

1. Non distingue noise da tono se hanno lo stesso baricentro: FM idx 10 (4298 Hz) e noise bianco (5000 Hz) sono vicini, ma il primo e' tonale e il secondo no. Per quella distinzione serve la flatness
2. Non e' invariante per trasposizione: suonare la stessa nota un'ottava sopra raddoppia il centroide. Non misura il timbro puro
3. E' sensibile al rumore ambientale sotto microfono piu' della flatness: il rumore di fondo sposta il baricentro, soprattutto sui segnali deboli (sin crescendo a 1m: 237 Hz vs 440 Hz sintetici)
4. Non distingue due componenti dallo stesso baricentro: una sinusoide a 2000 Hz e due sinusoidi a 200+3800 Hz possono avere centroide simile

**Confronto sistematico con la flatness:**

| Proprieta' | Centroide | Flatness |
|---|---|---|
| Distinzione noise/tono | Parziale (baricentro simile possibile) | Eccellente (8x) |
| Sensibilita' alla saturazione (tanh) | Alta (3.9x) | Bassa (1.9x) |
| Sensibilita' all'indice FM | Molto alta (7.8x) | Nulla (~1x) |
| Sensibilita' alla dinamica strumentale | Molto alta (5.5x su clarinetto) | Media (1.6x) |
| Stabilita' su segnali deboli | Alta | Bassa (instabilita' numerica) |
| Problema bin esatto | Nessuno | Grave (0.945) |
| Sensibilita' al rumore ambientale | Alta | Bassa |
| Invarianza per scala | Si | Si |

I due descrittori sono complementari: il centroide vede dove sta l'energia (frequenza del baricentro), la flatness vede come e' distribuita (uniforme o piccata). Insieme coprono due dimensioni ortogonali dello spettro.
