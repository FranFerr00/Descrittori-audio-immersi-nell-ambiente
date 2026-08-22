# Studio: ridisegno del controllo nello spazio a n dimensioni

> **Stato** (2026-06-26). §8 riferimenti completi; §4 e §6 scritte in prosa e
> verificate su dati veri (prototipi in `esplorazioni/`); sezioni 1, 3, 5,
> 6-bis arricchite con i risultati che cambiano una scelta. Restano da scrivere
> in prosa §2 (già con la lettura M&W), §3, §5 e da derivare il design (§7).

Nota di ricerca per ripensare, su basi matematiche solide, come *interfantasia*
usa i 16 descrittori per guidare il proprio comportamento dal vivo. Erede
diretta di [dispensa-mapping-ancore.md](dispensa-mapping-ancore.md): lì il
controllo a due ancore con segno (prototipo `prova_ancore.py`), qui la versione
generale e più sofisticata. La soluzione attuale nel patch (`interfantasia/
ambiente/ancore/`, `bicomb/`) è stata messa giù in fretta: questo studio serve a
rifarla bene.

**Filosofia (scelta 2026-06-26):** si tengono in campo *sia* i metodi
interpretabili e tarati a mano *sia* i metodi che apprendono parametri dai dati.
Per ogni tecnica si dice sempre dove cade e quanto costa in trasparenza e in
ri-taratura dal vivo. (Nota: è una posizione più avventurosa di quella difesa
nel paper CIM 2026, lecita perché qui il contesto è l'opera, non il discorso
accademico.)

---

## 1. Il problema, posto bene

*Da risolvere qui:* cos'è oggi il controllo in interfantasia, perché era
affrettato, cosa vuol dire concretamente "farlo funzionare meglio".

- Lo stream: da ogni frame, un vettore `x(t)` a 16 dimensioni (un punto che si
  muove). Richiamare l'immagine già fissata in [dispensa-mapping-ancore.md](dispensa-mapping-ancore.md) §2.
- Cosa c'è ora nel patch: `ancore/` (ancora.pd, catalogo.pd, suoni.pd,
  piu/meno.pd), `bicomb/` (mappatura collocazione/grana/forma/dinamica), `desc/`
  (estrazione + integratori). Descrivere onestamente il meccanismo attuale.
- Cosa non va: soglie e distanze ad hoc, scatti, jitter, taratura fragile.
- Criteri di "meglio": continuità del comportamento, stabilità nel tempo,
  leggibilità per chi suona, difendibilità della scelta. (Definirli come metri
  di giudizio per le sezioni seguenti.)
- **Cornice estetica:** il sistema è *ecosistemico* nel senso di Di Scipio
  (accoppiamento sistema↔ambiente, il segnale come interfaccia). Questo non è
  decorazione: spiega perché la "firma del luogo" è una variabile vera del
  problema e ritorna come vincolo in §3 (metrica robusta all'ambiente) e §5
  (la PCA rischia di catturare la stanza invece del gesto). Vedi Di Scipio
  2003, §8.

**Cosa chiediamo davvero ai 16 (coordinate, non semantica).** Una messa a fuoco
che cambia il modo di giudicare tutto il resto. I 16 sono tutti descrittori di
*basso livello* (low-level nella tassonomia di Sturm & Roads 2023, §8: statistiche
dello spettro, senza modello acustico), mentre ciò che vorrei guidare (un
comportamento riconoscibile, "questo suono è come quel nodo") vive a livello alto.
Ma non sto chiedendo ai numeri di *descrivere* la qualità alta: non devono nominare
nota, strumento o timbro. Li uso come **sistema di coordinate**, e la semantica alta
la porta dentro il **nodo**, scelto in calibrazione con l'orecchio (i nodi sono
suoni). Il livello alto non sta *nei* descrittori, sta nella *scelta* dei nodi, che
impongono un senso allo spazio dal di fuori.

Ne segue il vero requisito sui 16, molto più debole della completezza semantica:
l'**adeguatezza topologica**. Basta che nodi percettivamente diversi cadano in
regioni separabili e che suoni simili restino vicini. È un metro di giudizio per le
sezioni seguenti, perché dove lo spazio low-level *tradisce* la percezione il
controllo si incrina, ed è esattamente ciò che ho già toccato altrove. In §4.4 il
mix `sin75_noise25` non cade sulla retta fra i nodi (l'interpolazione percettiva non
coincide con quella geometrica nei descrittori); è la "specificity" di Sturm & Roads
(§8): una grande differenza nei numeri può non corrispondere a una differenza
all'orecchio, e due suoni diversi possono perfino collidere nello stesso punto. Tutta
la §3 (pesare, sbiancare, apprendere la metrica) e la §5 (riduzione) sono il
tentativo di *piegare* lo spazio low-level perché somigli di più a quello percettivo;
McAdams e il Timbre Toolbox (§8) misurano proprio quanto questo allineamento regge
(in parte).

Non è un difetto da nascondere, anzi è coerente con la cornice ecosistemica: un
sistema sound-driven non deve *capire* il suono (classificarlo), deve accoppiarsi in
modo continuo e stabile. I descrittori low-level sono adatti proprio perché
model-free, veloci e sempre definiti: il senso emerge dall'accoppiamento, non da
un'etichetta. I nodi danno il minimo aggancio percettivo necessario senza chiedere al
sistema di nominare nulla.

Conseguenza operativa che ritorna in §7 (calibrazione): i **nodi vanno scelti tra
suoni separabili nei 16 dim**. Se due nodi percettivamente distinti collidono nello
spazio dei descrittori, nessuna σ né metrica li salva. Rimedi in ordine di costo:
(a) scegliere nodi separabili (gratis); (b) aggiungere una dimensione mid-level che
rompa la degenerazione, la f0 dello slot sperimentale (`analisi_nuovi.py`), che è il
salto low→mid di Roads; (c) apprendere una metrica che allinei lo spazio alla
percezione (§3).

## 2. La cornice unificante: controllo per interpolazione tra nodi

*Da risolvere qui:* enunciare l'idea che tiene insieme tutto il resto.

- L'idea: si definisce il *comportamento desiderato ai nodi*; a runtime si
  calcolano dei **pesi** sui nodi a partire dalla posizione di `x(t)` e si
  **fonde** il comportamento. Distanza, riduzione e mappatura diventano scelte
  *dentro* questa cornice, non problemi separati.
- Perché unifica i "quattro lati" (metrica / riduzione / pesi / architettura).
- Inquadramento nella letteratura: modelli geometrici di Momeni & Wessel,
  "Metasurface" di Bencina, navigazione di spazi descrittori (Schwarz/CataRT).
  → §8.

**Lettura di Momeni & Wessel (sparring 2026-06-26, scheda in §Letture).**
Esito netto: di M&W si tiene **solo la matematica dell'interpolazione** (una
gaussiana per nodo con ampiezza e σ proprie, pesi normalizzati = partizione
dell'unità, con estrapolazione oltre il perimetro), **non il modello di
controllo**. Il loro spazio è un piano 2D *astratto*: gli assi non misurano
nulla, i punti li dispone a mano l'orecchio del compositore, e in tempo reale a
muovere il cursore è una **mano** (mouse/joystick/tavoletta). Non c'è segnale
d'ingresso: la posizione è un gesto empirico, senza relazione col suono.

> **Perno della cornice:** *interfantasia = M&W in cui il mouse è guidato dal
> suono.* Stessa legge di fusione, ma il cursore è il vettore dei 16 descrittori
> misurato frame per frame, non una mano.

**Presa di posizione (utente, 2026-06-26):** il controllo gestuale alla M&W è
*esattamente ciò da cui ci si vuole distaccare* — l'aspetto ludico, la posizione
senza relazione effettiva col segnale, non interessa. Il controllo resta
**sound-driven** (ecosistemico, Di Scipio): la posizione deve *significare*, e
significa solo se la decide il suono. Niente ibridi con controller di correzione.
Conseguenza: i problemi propri del cursore-suono (jitter → §6 filtro 1€; zone
vuote → CataRT §8; metrica vera in 16 dim → §3) sono il vero oggetto del
ridisegno. Parente stretto da studiare: Schwarz/CataRT, non M&W.
(Vedi memoria progetto: controllo sound-driven.)

## 3. La metrica: come si misura "vicino"

*Da risolvere qui:* quale distanza nello spazio dei descrittori, e cosa si
guadagna salendo di sofisticazione.

- Euclidea sui grezzi → perché no (la decidono centroide e rolloff). Richiamo a
  [dispensa-mapping-ancore.md](dispensa-mapping-ancore.md) §3.
- z-score congelato (dove siamo): ogni asse stesso peso.
- Mahalanobis / sbiancamento (covarianza): tiene conto della correlazione tra
  descrittori. Già esplorato (`prova_ancore.py --sbianca`, vedi
  schema-sbiancamento.png). **Avvertenza dalla ricerca (decisione che cambia):**
  lo sbiancamento pieno equivale a euclidea dopo `Σ⁻¹ᐟ²`, e *amplifica le
  direzioni a bassa varianza* — che nei descrittori audio sono spesso rumore di
  misura (Gavish et al. 2019, §8). Quindi lo **z-score diagonale congelato è
  probabilmente più robusto** del Mahalanobis pieno. Se serve la covarianza, va
  regolarizzata (shrinkage Ledoit-Wolf). Peeters (§8) rincara: i descrittori
  collassano in ~10 classi indipendenti → la `Σ` è mal condizionata.
  *Benchmark che decide:* se la varianza inter-ambiente sui descrittori a bassa
  energia supera quella del gesto, escludere il whitening pieno.
- Metriche apprese (metric learning, LMNN/NCA/ITML): stimano una metrica di
  Mahalanobis dai dati ma restano lineari/spiegabili. Costo: vogliono coppie
  etichettate, rischio overfitting con pochi dati, e fragilità se l'ambiente a
  runtime diverge dal training (concreto nel tuo caso). Solo con annotazioni di
  "gesti" coerenti tra ambienti. → §8.
- → riferimenti §8.

## 4. I pesi e l'interpolazione: da distanze a fusione

Questo è il salto di sofisticazione più grosso per il live: come si passa da
"quanto è lontano il suono da ogni nodo" a "quanto ciascun nodo decide il
comportamento, adesso". Le formule che seguono le ho provate sui descrittori veri
del corpus `recs-003`; gli script e le figure stanno in `esplorazioni/`
(`controllo_nodi_un_nodo.py`, `controllo_nodi_gaussiane.py`,
`confronto_bipolare_pulito.py`, `gaussiana_2d_correlazione.py`).

### 4.1 Il meccanismo in tre passi

Ad ogni frame il suono è un punto `x` nello spazio dei descrittori (in z-score).
Ci sono `N` nodi, ciascuno in una posizione `c_i` e con associato un comportamento
`b_i` (i parametri da mandare a bicomb/zone). Tre passi:

1. **Peso grezzo** (quanto il suono somiglia a ogni nodo), una gaussiana centrata
   sul nodo:

       w_i(x) = exp( − ‖x − c_i‖² / (2 σ²) )

   Vale 1 quando il suono è sul nodo, e cala dolcemente allontanandosi.

2. **Normalizzazione** (la partizione dell'unità):

       ŵ_i(x) = w_i(x) / Σ_j w_j(x)         con   Σ_i ŵ_i = 1

   I pesi diventano *quote*: frazioni di una torta, "quanta parte del comando la
   fa il nodo i". È lo stesso passo del `/lookup` di Momeni & Wessel (§2).

3. **Fusione** (media pesata dei comportamenti):

       y(x) = Σ_i ŵ_i(x) · b_i

Sul nodo si fa il suo comportamento; tra due nodi, la loro miscela. In statistica
questa è la **regressione kernel di Nadaraya–Watson** (in musica: interpolazione
di Shepard); con una `Σ` per nodo diventa la **GMM/GMR** di Françoise (§8). Tre
nomi diversi per la stessa formula.

### 4.2 Un nodo solo: il peso è una presenza

Con un nodo solo non c'è gara da spartire: il peso (grezzo, non normalizzato) è
semplicemente un **misuratore di vicinanza fra 0 e 1**, un gate morbido. Sul nodo
vale 1, lontano svanisce a 0. Misurando la distanza in unità di `σ`:

    distanza 0 → 1.00 ;  1σ → 0.61 ;  2σ → 0.14 ;  3σ → 0.01

Da qui la lettura intuitiva di `σ`: **la distanza alla quale il nodo è ancora
"presente al 61%".** Il prototipo `controllo_nodi_un_nodo.py` lo mostra sullo
sweep tonale→rumore: il nodo "rumoroso" è spento sul tono puro (distanza ~10,
peso ~0) e quasi pieno sul rumore (distanza ~1.3, peso ~0.87).

### 4.3 La σ: la manopola di durezza che il bipolare non ha

`σ` è il raggio della campana, e regola la **durezza delle transizioni tra nodi**.
I casi limite:

    σ → 0   ⇒ vince solo il nodo più vicino (a scatti, come le soglie attuali)
    σ → ∞   ⇒ tutti i nodi pesano uguale (1/N): sistema sordo, immobile

Il *tetto utile* di `σ` non è un numero assoluto: è dettato da **quanto sono
distanti i nodi**. Misurato sul corpus, i tre nodi-prova distano 5.4–10.7 (in z,
16 dim); oltre `σ ≈` la coppia più vicina (~5) i due nodi si fondono e perdono
identità. Regola del pollice: **σ ≈ (distanza dal nodo vicino) / 2 ÷ /3**. Sul
corpus `σ=2.5` era il compromesso buono e `σ=5` già "morbido al limite", coerente
con una distanza minima tra nodi di 5.4.

Conseguenze per il ridisegno: (a) `σ` va scelta **nelle unità della metrica** —
se si cambia la metrica (§3) va ritarata: `σ` e metrica sono legate; (b) se i nodi
stanno a distanze molto diverse, una `σ` unica è scomoda (troppo larga per la
coppia vicina, stretta per quella lontana): argomento concreto per una **σ per
nodo**.

### 4.4 Due o più nodi: la gara, e le zone vuote

Con due o più nodi le presenze 0..1 entrano in **gara**: la normalizzazione le
trasforma in quote che sommano a 1. È qui che nasce un problema che il singolo
nodo non ha. Quando il suono finisce **lontano da tutti i nodi**, tutte le `w_i`
sono ≈ 0 e la normalizzazione fa `0/0`: numericamente esplode e i pesi diventano
arbitrari. Momeni & Wessel non lo vivono (con la mano non si va nel vuoto); il
controllo sound-driven sì, perché è il suono a portarci lì (è il problema delle
**zone vuote** di CataRT, §8, in versione gaussiana).

Il prototipo `controllo_nodi_gaussiane.py` lo rende visibile sullo sweep
tonale→rumore: la "copertura" (somma dei pesi grezzi) crolla nel mezzo
(0.05–0.29) rispetto agli estremi (0.81–1.02). E mostra una sorpresa istruttiva:
il mix `sin75_noise25` **non** sta sulla retta fra i due nodi puri, anzi è
dominato da un terzo nodo (armonico): in 16 dimensioni le miscele percettive non
sono medie geometriche, lo spazio è curvo. Questa è la non-convessità che rende
il *posizionamento dei nodi* un problema serio.

Servono quindi due valvole per il caso vuoto: una **soglia di distanza assoluta**
(se lontano da tutti, non innescare: il gate, ma sui nodi) oppure un **nodo di
riposo** implicito (un peso di fondo costante `ε` che assorbe il vuoto e riporta a
un comportamento neutro). Si lega a §7 (cosa fa il sistema "fuori da ogni nodo").

### 4.5 Confronto col metodo attuale (bipolare)

Il controllo bipolare di [dispensa-mapping-ancore.md](dispensa-mapping-ancore.md),
`v = (d⁻ − d⁺)/(d⁻ + d⁺)`, è un **caso particolare** del gaussiano. Ridotto a due
nodi e a un valore con segno, il gaussiano dà `tanh((d⁻²−d⁺²)/4σ²)`: lo stesso
segnale del bipolare passato in una `tanh` con `σ` come pendenza. Il confronto sui
dati (`confronto_bipolare_pulito.py`) conferma che il bipolare quasi coincide col
gaussiano a `σ` grande (morbido): il metodo attuale non è sbagliato, è il
gaussiano *con la manopola bloccata su "morbido"*. Sbloccandola si ottiene un
intervallo di comportamenti, dal morbido di ora al deciso, che prima non c'era.

Il gaussiano aggiunge tre cose che il bipolare non possiede: la **manopola σ**
(durezza regolabile); la **consapevolezza delle zone vuote** (vedi subito sotto);
e l'**estensione a N nodi** (il bipolare è inchiodato a due per costruzione).

Sulla seconda vale la pena essere precisi, perché è facile sbagliarla (l'avevo
sbagliata io stesso). Nel vuoto il bipolare **non** esplode e non inventa un valore
saturo: essendo un rapporto di distanze va a `v ≈ 0` in modo grazioso (a distanza
`R` da entrambi i nodi vale `|v| ≤ L/2R → 0`, con `L` la loro separazione). Il
problema è un altro, più sottile: quel `v ≈ 0` è **indistinguibile dal punto
d'equilibrio** fra i due nodi, che vale anch'esso `v = 0`. Il bipolare, essendo
*scale-free*, butta via la distanza assoluta, quindi non sa di essere nel vuoto:
conflate "sono nella fusione equilibrata dei due suoni" con "sono lontano da tutto".
Anzi: `v = 0` esatto non è solo il midpoint ma tutta la **bisettrice** fra i due
nodi, e nel vuoto `|v|` *diminuisce* con la distanza (un punto a 1 unità dal midpoint
dà `|v| ≈ 0.2`, uno perso a 1000 dà `|v| ≈ 0.004`): il `|v|` più piccolo è il vuoto
profondo, non il centro, quindi la grandezza di `v` non è un rivelatore di vuoto.
La **copertura** (la somma dei pesi grezzi, prima di normalizzare) invece distingue
i casi: ≈0 nel vuoto, moderata fra i nodi, alta sul nodo
(`controllo_nodi_gaussiane.py`: 0.05–0.29 nel mezzo contro 0.81–1.02 sugli estremi).
È il segnale che il rapporto del bipolare distrugge. Ne seguono due cose: l'esplosione
`0/0` è un problema della gaussiana *normalizzata* (§4.4), non del bipolare; e
correggere il vuoto serve solo se il punto d'equilibrio deve fare qualcosa di
specifico, altrimenti `v ≈ 0` = neutro è già un default sicuro. Le valvole per il
caso vuoto stanno in §4.4 (gate sui nodi, o nodo di riposo).

C'è però un pregio del bipolare che si scopre solo guardandolo da qui, e che non
va perso. Il bipolare **non ha una σ**: è un rapporto di distanze, quindi è
*scale-free*. Se si allontanano i nodi del doppio, `v` non cambia — la forma della
transizione resta identica rispetto alla posizione fra i due nodi. Ha cioè una
**σ effettiva che si auto-adatta alla distanza tra i nodi**, mentre la σ del
gaussiano è assoluta e va ritarata sulla spaziatura. Ne segue una lettura precisa
del sistema attuale: non si stava "impostando σ=5", si stava prendendo *qualunque
morbidezza dettava la geometria*, che su questo corpus (nodi a distanza 5–11)
cadeva vicino a σ=5. Una conseguenza, non una scelta.

Il bipolare quindi *perdeva* la manopola (morbidezza non regolabile) ma *aveva*
l'auto-scaling (nessuna ritaratura se si spostano le ancore). Il gaussiano con σ
fissa dà la manopola e toglie l'auto-scaling. La via che tiene **entrambi i
pregi** è la **σ per nodo legata alla distanza dal vicino** (es.
`σ_i ≈ distanza-dal-nodo-più-vicino / 2`, cfr. §4.3): riottiene l'auto-scaling del
bipolare e conserva il controllo fine. In una riga: il ridisegno trasforma il
"morbido per caso" del bipolare in un "morbido per scelta", possibilmente
auto-tarato sui nodi.

### 4.6 Dalla sfera alla forma: isotropo, σ per asse, Σ pieno

Finora `σ` è un numero solo, uguale in tutte le 16 direzioni: la campana è una
**sfera**. (In z-score le scale sono già pareggiate, ma la sfera resta cieca alla
*correlazione* tra descrittori.) C'è una scala di raffinatezza:

1. **σ unica (sfera).** Tutte le direzioni uguali.
2. **σ_k per descrittore (ellissoide diritto).** Ogni asse il suo raggio: un
   descrittore rumoroso/poco utile pesa meno, uno discriminante di più. Non
   risolve però la correlazione: due descrittori correlati (centroide e rolloff,
   r=0.91 sul corpus) restano contati due volte.
3. **Σ pieno (ellissoide *inclinato*, Mahalanobis).** I termini fuori diagonale
   ruotano l'ellisse per allinearla alla nuvola: la brillantezza ridondante viene
   contata **una volta sola**. È, esattamente, il `--sbianca` già in
   `prova_ancore.py`.

Il prototipo 2D `gaussiana_2d_correlazione.py` lo dimostra su centroide×rolloff:
due punti alla stessa distanza euclidea dal nodo (2.20), uno *lungo* la nuvola e
uno *di traverso*, hanno Mahalanobis **1.59** e **7.33**. Il cerchio isotropo li
pesa uguali; l'ellisse vede l'evento raro (di traverso) come molto più lontano —
che è ciò che si vuole.

Il prezzo è quello già fissato in §3: lo sbiancamento **gonfia le direzioni
magre** (il punto di traverso passa da 2.2 a 7.3, ×3), ottimo se sono informazione
ma disastroso se sono rumore di misura (Gavish et al., §8). Da qui la scala dal
più robusto al più rischioso: **sfera (σ) → ellissoide globale con shrinkage →
ellissoide per nodo (GMM)**, e in alternativa la **riduzione** (PCA/famiglie, §5)
che butta via le direzioni magre invece di gonfiarle. Una `Σ` propria di ogni
nodo, stimata dai dati, è la GMM di Françoise (§8): la più potente e la più
affamata di dati.

**Sintesi operativa della sezione.** Il controllo a nodi è *una gaussiana per
nodo nello spazio dei descrittori, pesi normalizzati, comportamento interpolato*.
La sofisticazione sta tutta in due scelte: **la forma della gaussiana** (sfera →
Σ globale → Σ per nodo) e **la gestione delle zone vuote**. Il metodo attuale
(bipolare) è il gradino più basso di entrambe.

## 5. La riduzione dimensionale: 16 → poche dimensioni di controllo

*Da risolvere qui:* conviene ridurre lo spazio? Quando aiuta il controllo e
quando lo danneggia.

- PCA (autobase della covarianza); le famiglie già usate (Forma / Distribuzione
  / Tonalità / Dinamica, vedi memoria progetto due-schemi-famiglie). Peeters (§8)
  dà l'argomento empirico: ~10 classi indipendenti dentro i 16, c'è ridondanza
  riducibile.
- **Trappola specifica del tuo caso ecosistemico:** la PCA può catturare la
  *firma del luogo* invece del gesto (se la varianza dell'ambiente domina). Da
  usare **solo congelata sul corpus, mai adattiva a runtime**. *Soglia che
  decide:* se i primi 2-3 PC spiegano meno varianza inter-gesto che
  inter-ambiente, non ridurre. (Bevilacqua, MnM, §8: PCA via SVD in real-time.)
- Mappe auto-organizzanti (SOM/Kohonen): Fasciani & Wyse (§8) hanno un caso
  quasi identico al tuo (voce/strumento → controllo), tutto nello spazio dei
  descrittori; training offline, lookup runtime economico.
- UMAP/t-SNE, autoencoder: visti, ma instabili nel tempo / non interpretabili →
  orizzonte (§6-bis), non nucleo.
- Tensione: interpretabilità e stabilità temporale vs compressione. Una
  riduzione che salta a scatti dal vivo è peggio del problema che risolve.
- → riferimenti §8.

## 6. La dinamica temporale: `x(t)` è una traiettoria

Il punto `x(t)` non è fermo: si muove e trema. Va stabilizzato senza spegnerlo,
cioè togliendo il jitter da fermo senza introdurre ritardo (lag) sui movimenti
veri. Prototipo: `esplorazioni/filtro_uno_euro.py`, sul corpus `recs-003` a
rate ~23 Hz (un frame ~43 ms).

**Atteso vs trovato (un risultato che cambia la raccomandazione).** Mi aspettavo
che il **filtro 1€** (Casiez et al. 2012, §8) fosse la vittoria immediata:
passa-basso a taglio adattivo alla velocità, liscio da fermo e pronto in
movimento, due parametri, e — secondo gli autori — meno lag di Kalman. Sui
descrittori **non** mantiene quel vantaggio, e ho capito perché. L'1€ presume
che il rumore sia *piccolo e lento* (vero per una mano su un controller); il
rumore dei descrittori è invece **spiky**: un picco singolo è indistinguibile,
al primo frame, da un movimento vero. Per non farsi ingannare dai picchi bisogna
lisciare moltissimo la stima di velocità (`dcutoff` basso), ma così l'1€ diventa
lento a reagire ai salti veri e **collassa su un passa-basso fisso** (EMA): a
pari pulizia ha lo stesso lag (5 frame ≈ 213 ms).

**La cura giusta per i picchi è la robustezza agli outlier, non la velocità.** Un
**filtro mediano** li ignora per costruzione. Misurato sui dati (jitter sul
plateau stabile; lag alla risposta a gradino):

    metodo            jitter   lag al salto
    grezzo            0.136    0 frame
    EMA (a=0.12)      0.019    5 frame  (~213 ms)
    1€ (tunato)       0.017    5 frame  (~213 ms)
    mediano5 + EMA    0.029    2 frame  (~85 ms)   <- meglio

Mediano(5) seguito da un EMA leggero dà pulizia paragonabile con **meno della
metà del lag**. Per i descrittori il mediano batte sia l'EMA sia l'1€.

**Indicazioni per il ridisegno.** (a) La prima difesa contro il jitter dei
descrittori è un **mediano breve causale** (finestra 3–5), poi un'EMA leggera —
non l'1€. Attenzione: l'EMA è un integratore *leaky* (passa-basso, con ingresso
costante si assesta sul valore), mentre l'`integrator_wrap` già nel patch è un
integratore *puro* con wrap (con ingresso costante rampa e gira): accumula la
*deriva*, **non liscia**. Sono ruoli opposti, non intercambiabili: lo smoother va
aggiunto, non recuperato dagli integratori esistenti. (b) Il filtro
di **Kalman** resta sovradimensionato (più parametri e assunzioni, e non risolve
i picchi meglio del mediano). (c) La **velocità/derivata** del punto, una volta
ripulita dai picchi, può diventare un segnale di controllo a sé (la deriva). (d)
La lisciatura va fatta **prima** del calcolo dei pesi: si liscia `x(t)`, non i
pesi, così le valvole delle zone vuote (§4.4) lavorano su un punto già pulito.
→ riferimenti §8.

## 6-bis. Orizzonte neurale (paradigma alternativo)

*Da risolvere qui:* conoscere cosa fa la scuola neurale 2020-2025, e dire con
chiarezza perché resta *fuori* dal nucleo del ridisegno.

- Il punto critico, unico e dirimente: questi modelli **navigano un proprio
  spazio latente appreso, non i tuoi 16 descrittori**. Sostituirebbero l'oggetto
  del controllo invece di migliorarlo.
- RAVE (Caillon & Esling 2021, §8): VAE per sintesi waveform real-time, gira in
  Pd via `nn~`; latente nativo a 128 dim, ridotto via PCA (es. a 12). Inferenza
  <200 ms su laptop ma training ~3 settimane di GPU. Per *generare* timbri, non
  per il tuo controllo.
- Timbre-VAE percettivo (Esling et al. 2018, §8): latente regolarizzato sui
  timbre spaces percettivi. Ibrido interessante, ma resta latente appreso.
- DDSP (Engel et al. 2020, §8): il più vicino al tuo mondo (parametri DSP
  interpretabili come layer finale); utile come *ispirazione* per sintesi
  differenziabile, ma il controllo passa comunque da una rete.
- Conclusione operativa: se mai servisse *generare* timbri nuovi, valutare DDSP
  (ibrido interpretabile) prima di RAVE, e tenerlo **fuori dal loop di controllo
  principale**.

## 7. Atterraggio in Pd / Faust

*Da risolvere qui:* di tutto quanto sopra, cosa è davvero realizzabile nel patch
e come. Ponte verso il documento di design successivo.

- Cosa si calcola per frame, cosa si congela in calibrazione.
- Dove vive ciascun pezzo: estrazione (`desc/`), metrica+pesi (nuovo?), fusione
  → bicomb/zone.
- Cosa è già pronto (arrayop2, integratori) e cosa va scritto.
- Lista dei candidati realizzabili, ordinati per rapporto resa/sforzo.

## 8. Riferimenti

Dalla ricerca bibliografica del 2026-06-26 (artefatto grezzo:
[compass_artifact_wf-ef1a7833.md](compass_artifact_wf-ef1a7833-fbdc-4e2e-824d-9ea09da60341_text_markdown.md)).
Caveat sulle fonti: alcuni numeri di pagina sono discordanti tra fonti
secondarie, e le cifre latenza/GPU dei modelli neurali vanno riprodotte sul
proprio hardware. Lerch 2023 non verificato.

### Cornice / controllo per interpolazione
- **Momeni & Wessel (2003)**, "Characterizing and Controlling Musical Material
  Intuitively with Geometric Models", NIME 2003, pp. 54–61. DOI 10.5281/zenodo.1176535.
  *L'antenato diretto del controllo a nodi: poli = "punti", v = posizione relativa.*
- **Bencina (2005)**, "The Metasurface — Applying Natural Neighbour Interpolation
  to Two-to-Many Mapping", NIME 2005, pp. 101–104. DOI 10.5281/zenodo.1176701.
  *Fusione many-to-many con partizione dell'unità (natural neighbour/Voronoi).*
- **Schwarz, Beller, Verbrugghe & Britton (2006)**, "Real-Time Corpus-Based
  Concatenative Synthesis with CataRT", DAFx-06, pp. 279–282. HAL hal-01161358.
  *Opera ESATTAMENTE sullo spazio dei descrittori, distanza euclidea pesata;
  attenzione alla distribuzione non uniforme del corpus (cluster densi / vuoti).*
- **Sturm & Roads (2023)**, "Concatenative Synthesis", cap. 23 di *The Computer
  Music Tutorial*, 2ª ed., MIT Press. *Tassonomia dei descrittori in low / mid /
  high level (i nostri 16 sono tutti low-level); la "specificity": i descrittori
  low-level sono vicini ai campioni, non al contenuto percepito (grande differenza
  nei numeri ≠ grande differenza all'orecchio). CataRT come navigazione del
  descriptor space con il target spostato da mouse, controller o suono. Distingue
  la concatenativa (sceglie un grano dal corpus, è sampling) dalla nostra fusione
  di comportamenti.*
- **Van Nort, Wanderley & Depalle (2014)**, "Mapping Control Structures for Sound
  Synthesis: Functional and Topological Perspectives", CMJ 38(3): 6–22.
  DOI 10.1162/COMJ_a_00253.
- **Spain & Polfreman (2001)**, "Interpolator…", Organised Sound 6(2): 147–151;
  più Marier (NIME 2012, Intersecting N-Spheres), Gibson & Polfreman (2019/2020):
  *confronto sperimentale tra leggi di interpolazione.*

### Inquadramento (timbre spaces, descrittori)
- **McAdams et al. (1995)**, "Perceptual scaling of synthesized musical timbres",
  Psychological Research 58(3): 177–192. DOI 10.1007/BF00419633.
- **Peeters et al. (2011)**, "The Timbre Toolbox", JASA 130(5): 2902–2916.
  DOI 10.1121/1.3642604. *I 16 collassano in ~10 classi indipendenti → giustifica
  PCA e sconsiglia il Mahalanobis pieno.*
- **Lerch (2023)**, *An Introduction to Audio Content Analysis*, 2ª ed., Wiley/IEEE
  *(da verificare)*.

### Metriche e distanza
- **Gavish, Talmon, Su & Wu (2019)**, "Optimal Recovery of Mahalanobis Distance in
  High Dimension", arXiv:1904.09204. *Il whitening pieno amplifica le direzioni a
  bassa varianza (rumore); propone uno shrinker ottimale.*
- Shrinkage **Ledoit-Wolf** per stima regolarizzata di Σ.
- **Metric learning:** Kulis (2012); Bellet, Habrard & Sebban, arXiv:1306.6709;
  LMNN (Weinberger & Saul, JMLR 2009), NCA (Goldberger 2004), ITML (Davis 2007).

### Riduzione dimensionale
- PCA congelata sul corpus; **Bevilacqua, Müller & Schnell (2005)**, "MnM: a
  Max/MSP mapping toolbox", NIME 2005 (mapping lineari via SVD, Kernel-PCA).
- **Fasciani & Wyse (2013/2018)**, SOM per controllo vocale; CMJ 42(1): 37–59,
  DOI 10.1162/comj_a_00450. *Caso quasi identico al tuo.*

### Pesi / appartenenza morbida
- **Françoise, Schnell, Borghesi & Bevilacqua (2014)**, "Probabilistic Models for
  Designing Motion and Sound Relationships", NIME 2014 (#482), DOI 10.5281/zenodo.1178764;
  **Françoise & Bevilacqua (2018)**, "Motion-Sound Mapping through Interaction",
  ACM TiiS 8(2):16, DOI 10.1145/3211826; tesi Françoise (2015, HAL tel-01161965).
  *GMM/GMR: ogni nodo = gaussiana, peso = responsabilità a posteriori. Libreria
  XMM (mubu.gmm/gmr/hmm/hmr).*
- **Goudeseune (2002)**, "Interpolated mappings for musical instruments",
  Organised Sound (simplicial interpolation). RBF, softmax, coordinate baricentriche.

### Dinamica temporale
- **Casiez, Roussel & Vogel (2012)**, "1€ Filter", ACM CHI 2012, pp. 2527–2530.
  DOI 10.1145/2207676.2208639. *Due parametri (f_Cmin, β), meno lag di Kalman.*
  LaViola (double exponential smoothing) come compromesso; Kalman come alternativa.

### Mapping gesto→suono (esplicito vs appreso)
- **Hunt & Wanderley (2002)**, "Mapping performer parameters to synthesis engines",
  Organised Sound 7(2): 97–108; Hunt, Wanderley & Paradis (2003), JNMR 32(4): 429–440.
- **Fiebrink & Cook (2010)**, "The Wekinator", ISMIR 2010; Fiebrink (2011, PhD).
  *Interactive machine learning per apprendere il mapping nodi→parametri da esempi.*

### Orizzonte neurale (paradigma alternativo, §6-bis)
- **Caillon & Esling (2021)**, "RAVE", arXiv:2111.05011 (gira in Pd via `nn~`).
- **Esling, Chemla-Romeu-Santos & Bitton (2018)**, "…Perceptually-regularized
  Variational Timbre Spaces", ISMIR 2018, pp. 175–181 (e DAFx-18, arXiv:1805.08501);
  FlowSynth (IJCAI 2020); "Interpretable timbre synthesis…VAE", arXiv:2307.10283.
- **Engel, Hantrakul, Gu & Roberts (2020)**, "DDSP", ICLR 2020, arXiv:2001.04643.

### Cornice estetica (ecosistemico)
- **Di Scipio (2003)**, "'Sound is the interface': from interactive to ecosystemic
  signal processing", Organised Sound 8(3): 269–277. DOI 10.1017/S1355771803000244;
  Solomos/Meric (2014), Contemporary Music Review 33(1).

---

## Letture (schede)

Schede di lettura mirate, una per tappa del percorso di studio (vedi rosa dei 5,
§8). Si compilano *prima* di leggere, per non disperdersi, e si annotano dopo.

### Tappa 1 — Momeni & Wessel (2003)

> Ali Momeni & David Wessel, "Characterizing and Controlling Musical Material
> Intuitively with Geometric Models", NIME-03, Montréal, pp. 54–61.
> DOI 10.5281/zenodo.1176535. PDF locale: `docs/momeni_interpolation-spaces.pdf`.

**Perché:** riconoscere che il controllo a nodi è un caso particolare del loro
modello geometrico, e prenderne cornice e vocabolario. Non è una tecnica da
imparare, è la cornice da cui cade il resto.

**Le 3 idee da cercare:**
1. I "punti" come prototipi in uno spazio a bassa dimensione, disposti a mano →
   i tuoi nodi scelti in calibrazione. Come li scelgono e dispongono?
2. L'interpolazione pesata per distanza: a ogni punto un insieme di parametri, la
   posizione corrente genera parametri come media pesata (peso tipo gaussiano che
   cala con la distanza) → cuore della §4.
3. La bidirezionalità "caratterizzare ↔ controllare": lo stesso spazio dice dove
   sei e guida il suono → la tua coppia analisi/controllo.

**Domande al testo (rispetto al nostro caso):**
- La funzione peso: che forma ha, come ne tarano la larghezza? → la "durezza"
  (temperatura softmax / raggio RBF). Annotare la formula esatta.
- I pesi sommano a 1? Come normalizzano? → partizione dell'unità, chiave
  dell'appartenenza morbida.
- Quante dimensioni usano e come ci arrivano? (vedi avvertenza sotto)
- Il punto che si muove: lisciano la traiettoria? Come? → §6.
- Cosa dichiarano come limite (troppi punti, punti vicini, zone vuote)?

**⚠️ Differenza da non perdere:** loro costruiscono uno spazio di controllo
*astratto a 2D*, separato dalle feature; noi no — i nodi vivono *dentro* lo
spazio dei 16 descrittori, che è già lo spazio. È una semplificazione (niente
mappa verso un piano) ma anche un rischio: il loro 2D è povero e ben distribuito
per costruzione, il nostro a 16 dim è ricco, correlato e con zone vuote (il
problema che CataRT segnala, §8). Leggere M&W per la *legge di interpolazione*,
non per la *scelta dello spazio*.

**Da estrarre:** la formula del peso → semina §4; il vocabolario (punti/
prototipi, interpolazione) → allineare con [dispensa-mapping-ancore.md](dispensa-mapping-ancore.md);
l'avvertenza sulla differenza di spazio → §2.

### Tappa 2 — Schwarz / CataRT (2006)

> Diemo Schwarz, Grégory Beller, Bruno Verbrugghe & Sam Britton, "Real-Time
> Corpus-Based Concatenative Synthesis with CataRT", DAFx-06, Montréal,
> pp. 279–282. HAL hal-01161358. PDF locale: `docs/schwarz_catart_dafx2006.pdf`
> *(da scaricare)*.

**Perché:** è il tuo parente stretto. È il primo in cui a guidare il cursore c'è
un **suono** descritto da descrittori, esattamente come interfantasia. Da M&W hai
preso la legge di fusione; da CataRT prendi i problemi *veri* di chi naviga uno
spazio di descrittori con un segnale: la distanza come legge di controllo e,
soprattutto, le **zone vuote**.

**Le 3 idee da cercare:**
1. Il **corpus** di unità (grani), ciascuna con i suoi descrittori → punti nello
   spazio. Come è costruito, cosa è un'unità.
2. Il **target cost = distanza euclidea pesata** dal target nello spazio dei
   descrittori, e la selezione delle unità più vicine (k-NN, con un po' di caso).
   → è la tua legge di distanza ai nodi.
3. La **distribuzione non uniforme** del corpus (cluster densi, vaste zone
   vuote) e cosa succede quando il target cade nel vuoto. → il problema di *dove
   mettere i nodi* e *cosa fare quando il suono è lontano da tutti*.

**Domande al testo (rispetto al nostro caso):**
- Come pesano gli assi nella distanza (i pesi della "weighted Euclidean")? Da
  cosa li ricavano? → si lega alla tua metrica (§3): z-score vs Mahalanobis.
- Esiste una **modalità audio-driven** (l'audio in ingresso fissa il target)?
  Se sì è *letteralmente* il tuo paradigma: annotare come la realizzano.
- Lo spazio di navigazione è i descrittori pieni o una **proiezione 2D**? Come
  scelgono le due dimensioni mostrate? → §5 riduzione.
- Cosa fanno con le **zone vuote**: rifiutano? forzano l'unità più vicina? →
  decide la tua strategia di posizionamento nodi e di comportamento "fuori zona".
- C'è continuità tra unità successive (concatenation cost) o solo target? → tocca
  la tua §6 (dinamica temporale, evitare gli scatti).

**⚠️ Differenza da non perdere:** CataRT, dato il target, **seleziona un grano
esistente** dal corpus (risintesi granulare). Tu no: dato il punto, **fondi i
comportamenti dei nodi** (sintesi/processamento). Stessa geometria (distanza nel
descriptor space), *carico* diverso (loro scelgono un campione, tu interpoli
parametri). Quindi: prendi la loro *teoria della distanza e delle zone vuote*,
non il loro *motore granulare*.

**Da estrarre:** la formula della weighted Euclidean e l'origine dei pesi →
§3; la modalità audio-driven (se c'è) → conferma del paradigma in §2; la
strategia per le zone vuote → §4 e §7 (comportamento "fuori da ogni nodo").

### Tappa 3 — Bencina, Metasurface (2005)
*(scheda da compilare prima della lettura)*

## Prossimi passi

1. ~~Lanciare la ricerca bibliografica e versare i risultati in §8.~~ *(fatto
   2026-06-26)*
2. Leggere la rosa dei 5 (Momeni & Wessel, Schwarz/CataRT, Bencina, Peeters,
   1€ Filter) e scrivere in prosa le sezioni 2→6 scegliendo, dentro la cornice
   §2, le tecniche concrete.
3. Prototipi numerici in `esplorazioni/`, da provare sui corpus reali:
   - ~~**N nodi con gaussiane** (partizione dell'unità), σ come durezza,
     confronto col bipolare, isotropo vs anisotropo.~~ *(fatto 2026-06-26,
     vedi §4 e `controllo_nodi_*.py`)*
   - ~~**1€ Filter** sui 16 descrittori.~~ *(fatto 2026-06-26, `filtro_uno_euro.py`):
     esito diverso dall'atteso — sul rumore spiky dei descrittori l'1€ collassa
     su un EMA; meglio **mediano breve + EMA leggera** (metà del lag). Vedi §6.*
   - **Controprova Mahalanobis vs z-score diagonale** con shrinkage Ledoit-Wolf
     e il benchmark inter-ambiente vs inter-gesto (§3).
   - **PCA congelata** con la verifica "gesto vs stanza" (§5) prima di adottarla.
   - **GMR** (ogni nodo = gaussiana con Σ) per l'appartenenza morbida.
4. Da §7 derivare il documento di design del nuovo controllo per il patch
   *interfantasia*.
