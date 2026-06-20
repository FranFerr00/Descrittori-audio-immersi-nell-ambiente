# Peer review — CIM 2026

**Titolo:** *Descrittori audio per il live electronics: misura relativa e controllo a nodi in ambiente*
**Tipo:** articolo (double-blind)
**Reviewer:** revisione simulata in qualità di revisore del Colloquio di Informatica Musicale

---

## 0. Raccomandazione sintetica

**Accettazione con revisioni maggiori** (*accept with major revisions*).

Lavoro originale, ben scritto, radicato in una pratica compositiva reale e pienamente nel
dominio del CIM. L'idea centrale — il controllo relativo e bipolare a nodi che fa elidere la
firma dell'ambiente — è elegante e potenzialmente utile alla comunità. **Il limite che oggi
tiene il lavoro sotto la soglia del "minor" è uno solo, ma sostanziale: il contributo che dà il
titolo all'articolo (il controllo a nodi) è validato in modo molto più debole di quanto sia
diagnosticato il problema.** Le tre prove dimostrano con cura che i descrittori sono
contestuali; la soluzione, invece, è verificata solo sui sintetici, con un'unica coppia di nodi
e lungo l'asse più facile da conservare, e mai dentro *interfantasia*. Se l'autore colma o
delimita con onestà questo scarto, il lavoro diventa una solida accettazione.

| Criterio | Valutazione (1–5) | Nota |
|---|---|---|
| Rilevanza per il CIM | 5 | Centratissimo: ecosistemico, live electronics, descrittori |
| Originalità | 4 | La diagnosi è in parte nota; il valore è nella sintesi e nel controllo a nodi |
| Rigore / validazione | 2–3 | Diagnosi solida; soluzione sotto-validata |
| Chiarezza espositiva | 4 | Scrittura viva ed efficace, qualche densità tecnica |
| Riproducibilità | 4 | Pipeline deterministica, codice promesso pubblico, dettagli buoni |

---

## 1. Riassunto del contributo (come l'ho inteso)

Nel live electronics ecosistemico di *interfantasia* (alla Di Scipio) i parametri dei filtri sono
guidati da descrittori audio calcolati in tempo reale sul suono ripreso in sala. La mappatura
originale a cinque descrittori era debole perché il **valore assoluto** di un descrittore si
muove con la stanza, non con il gesto. Da qui la domanda: come usare dal vivo un insieme
chiuso di sedici descrittori, dato che il segnale arriva sempre attraverso un ambiente e una
catena?

L'autore raccoglie evidenza su tre prove di realismo crescente:

1. **Segnali sintetici** (45 suoni): invarianza di scala dimostrata in forma chiusa, ma deriva
   sotto ripresa; tassonomia di robustezza in tre fasce.
2. **Strumenti acustici** (clarinetto contrabbasso, timpano aumentato): *quale* descrittore
   segue il gesto dipende dallo strumento (la forma per il clarinetto, l'irregularity per il
   timpano sostenuto).
3. **Esperimento di distanza** (8 microfoni omni, 1–8 m): la catena "firma" la misura —
   assorbimento dell'aria, onda stazionaria della fondamentale del clarinetto, direttività,
   attenuazione ~1/√r.

La soluzione (Sez. 5): un controllo **relativo e bipolare a nodi**,
`v = (d⁻ − d⁺)/(d⁻ + d⁺) ∈ [−1, 1]`, che legge la posizione del suono fra due prototipi nello
spazio dei descrittori. Se i nodi sono ripresi nello stesso ambiente dell'ingresso, la firma del
luogo entra in entrambi i termini e **si elide**.

---

## 2. Punti di forza (da preservare in revisione)

1. **Problema motivante eccellente.** Nasce da una pratica reale e da una tradizione precisa
   (ecosistemico). È esattamente il tipo di lavoro che il CIM premia.
2. **L'idea della cancellazione è il cuore concettuale ed è bella.** "Far pesare la catena
   ugualmente su entrambi i lati del confronto" è una mossa pulita ed elegante. Va messa
   ancora più in evidenza.
3. **Mestiere sperimentale notevole.** La fila di 8 microfoni, la doppia ripresa
   orizzontale/verticale per separare propagazione e direttività del microfono, la
   calibrazione RMS con deviazione di 0,17 dB: è progettazione sperimentale matura.
4. **Onestà sui limiti.** Invarianza del puro livello sul timpano sostenuto, fragilità di
   kurtosis/skewness, validazione limitata, dubbio aperto sull'onda stazionaria: tutto
   dichiarato. È credibilità.
5. **Riproducibilità.** Pipeline Python deterministica, external in C verificata contro di essa,
   z-score "congelato", codice promesso pubblico.
6. **Sotto-risultati genuinamente interessanti** in sé: l'onda stazionaria letta sul centroide,
   il "caso limite del bin esatto" che la realtà acustica paradossalmente guarisce, la kurtosis
   che "dorme sui cluster e scatta sul Do" come spia dell'interazione campana/luogo/microfono.

---

## 3. Criticità maggiori (da affrontare per l'accettazione)

### 3.1 La validazione del contributo principale è troppo debole per le sue rivendicazioni
È il punto su cui il lavoro verrà giudicato. Circa sei pagine su dieci (Sez. 3–4) stabiliscono
con cura che i descrittori sono contestuali; ma il controllo a nodi — ciò che dà il titolo
all'articolo — è validato (Sez. 5, Fig. 7) **solo sui 45 sintetici, con un'unica coppia di nodi
(sinusoide/rumore), e per ammissione dell'autore stesso lungo "l'asse di massima varianza
del corpus, il più facile da conservare".** Non c'è validazione:
- sugli **strumenti acustici** (eppure il corpus c'è già);
- su **assi più sottili** (cioè coppie di nodi meno separate, che sono il caso d'uso realistico);
- **dentro *interfantasia***, né con un ascolto, né con un criterio musicale o percettivo.

Conseguenza: la frase chiave ("il controllo regge") è **asserita più che dimostrata** nel
regime che conta. Servono almeno una di queste mosse:
- **(preferibile)** estendere l'esperimento di Fig. 7 agli strumenti acustici e ad almeno una
  seconda coppia di nodi su un asse "sottile", riportando come degrada la tenuta;
- **(minimo)** ridimensionare esplicitamente la portata della validazione nell'abstract e in
  Sez. 5, dichiarando che si tratta di una *prova di principio* sul caso più favorevole, e
  spostando il resto fra i lavori futuri in modo netto.

### 3.2 "LEAP" è usato ma mai definito
A pagina 9: *"È la traduzione, sul controllo, di ciò che il **LEAP** ha mostrato sulla misura..."*.
Il termine non compare definito da nessuna parte (probabile residuo di anonimizzazione o di
una rinominazione di sezione/esperimento). Un revisore lo segnala come errore. Da sciogliere
o sostituire (immagino si riferisca all'esperimento di distanza in laboratorio).

### 3.3 Tensione concettuale fra "descrittori interpretabili" e controllo a distanza euclidea
La Sez. 2 fonda l'intera scelta metodologica sull'**interpretabilità**: *"solo un descrittore con
un nome mi lascia dire perché un valore cambia"*. Ma il controllo a nodi **collassa i sedici
descrittori in una distanza euclidea** in z-score: al livello del controllo l'interpretabilità —
*quale* descrittore si è mosso e *perché* — si perde. Non è necessariamente un difetto, ma è
una tensione che il revisore noterà e che va affrontata di petto: l'interpretabilità serve in fase
di **analisi e taratura** (scelta dei nodi, diagnosi con Mahalanobis) mentre il controllo runtime
è volutamente sintetico? Se è così, dirlo. Inoltre: la distanza euclidea pesa tutti i sedici
descrittori allo stesso modo, inclusi quelli della "fascia bassa" (crest, skewness, kurtosis, n.
picchi) che il lavoro stesso dichiara inaffidabili sotto catena — perché allora restano nel
calcolo della distanza? Questa scelta va giustificata (o i descrittori vanno pesati).

### 3.4 Generalità: una sola sala, un solo setup
L'esperimento di distanza, pur ben fatto, è condotto in **un solo ambiente**. Affermazioni
come "la catena è coautrice della misura" sono corrette ma vanno calibrate: ciò che si mostra
è *un* caso, ricco e leggibile. L'onda stazionaria e i numeri dell'assorbimento dell'aria sono di
fatto aneddotici (un locale, una geometria). Suggerisco di esplicitare ovunque che i fenomeni
sono *illustrativi del meccanismo*, non misure generali, e di spostare il peso argomentativo
sul **principio** (la cancellazione) piuttosto che sui valori numerici specifici.

### 3.5 Lo z-score "congelato": come vive dal vivo?
La normalizzazione usa media e deviazione calcolate una volta "sull'intero corpus". Ma:
- *quale* corpus (sintetici? strumenti? unione)? Va detto, perché cambia i numeri.
- soprattutto, **dal vivo non esiste un corpus**: come si fissa lo z-score in performance?
  Questo è il ponte fra l'analisi offline e l'uso real-time che il titolo promette, e oggi è un
  buco pratico. Anche solo un paragrafo che spieghi la procedura live (taratura preliminare in
  sala? corpus di riferimento precaricato?) rafforzerebbe molto la tesi del "tempo reale".

---

## 4. Criticità minori

- **Bilanciamento.** Diagnosi (Sez. 3–4) molto sviluppata, cura (Sez. 5) compressa.
  Considerare di accorciare alcune letture descrittore-per-descrittore della linea di base per
  dare respiro alla soluzione e alla sua validazione.
- **Novità della diagnosi.** Che le feature dipendano dalla catena di ripresa è in parte noto in
  MIR/acustica. Conviene dichiararlo e posizionare la novità dove davvero sta: nella
  *caratterizzazione sistematica di un set chiuso interpretabile nel contesto live* e nel
  *controllo a nodi*. Così si previene l'obiezione "questo si sapeva già".
- **Lavori correlati un po' magri (Sez. 2).** Mancano riferimenti su: robustezza delle feature
  timbriche all'ambiente/riverbero; spazi di interpolazione/preset e assi anchored (il controllo
  a nodi ha parenti — interpolatori di preset, assi tipo Fisher/LDA, similarità ancorata) che
  andrebbero almeno citati per collocare il contributo. La cornice ecosistemica di Di Scipio è
  evocata ma poco sviluppata concettualmente.
- **Perché "sedici" e perché "chiuso"?** Il vincolo dell'insieme chiuso è centrale nella tesi ma
  motivato debolmente. Se è un vincolo architetturale/real-time di *interfantasia*, dirlo
  esplicitamente; altrimenti il numero appare arbitrario, tanto più che durante il lavoro alcune
  voci sono state sostituite (spectral decrease → OBSIR-std; max autocorrelazione → entropia).
- **Mahalanobis/sbiancamento (Sez. 5).** Passaggio denso e difficile da seguire. La conclusione
  ("usare z-score; tenere lo sbiancamento come diagnostica in taratura") è chiara, ma il
  perché va sbrogliato. Rischia di confondere il lettore proprio nel punto culminante.
- **Statistica.** Mancano numerosità dei frame, eventuali intervalli/dispersioni, e n è piccolo
  (9 clarinetto, 10 timpano). Le correlazioni di Tab. 5 sono descrittive: dichiararlo.
- **Anonimato (double-blind).** *interfantasia* è nominata ripetutamente ed è verosimilmente
  un brano identificabile dell'autore: possibile criticità di anonimato. Valutare un fraseggio più
  neutro ("un brano per live electronics ecosistemico") o verificare le regole del CIM.
- **Abstract solo in inglese**, corpo in italiano. Verificare i requisiti CIM (spesso si gradisce
  anche un abstract italiano). Formattazione.

---

## 5. Note puntuali (per sezione / figura)

- **Abstract.** Forte e ben scritto. Inserire una mezza frase che delimiti la validazione ("a
  proof of principle on synthetic signals") per non sovra-promettere.
- **Tab. 1 (formule).** Verificare il rendering tipografico: in alcune copie le formule risultano
  spezzate/illeggibili. Controllare la versione finale del PDF.
- **Fig. 1.** Buona mappa; l'avvertenza ("misura quanto un descrittore si sposta, non quanto
  resta utile") è preziosa — tenerla.
- **Tab. 2 / dz.** La distinzione "non è uno scarto da correggere, ma la misura di quanto il
  contesto entra nel segnale" è ottima. Chiarire la metrica (distanza euclidea in z-score sui
  frame validi comuni) anche nel corpo, non solo in didascalia.
- **Fig. 4.** Molto densa: decine di numeri sovrapposti, di fatto illeggibili a stampa. Considerare
  di mostrare medie ± dispersione per configurazione, o spostare il dettaglio in appendice e
  tenere a testo solo la lettura sintetica ("a colpo d'occhio il centroide si sposta col microfono").
- **Fig. 5 (onda stazionaria).** Risultato bello e convincente proprio perché orizzontale e
  verticale coincidono. La spiegazione nodo/ventre è chiara.
- **Sez. 3.3, "1/√r".** Internamente coerente (−8,6 dB su 3 raddoppi ≈ −2,9 dB/raddoppio;
  fonometro 96/93/90/87 dBA). Precisare che è il comportamento del **campo riverberante**
  (la −3 dB/raddoppio vs −6 in campo libero), così "1/√r" non suona informale.
- **Tab. 6 (kurtosis sul Do).** Bel sotto-risultato. Specificare che è un singolo evento (una nota,
  una campana) — illustrativo, non statistico.
- **Eq. (1) / Fig. 6.** Chiare. Aggiungere il comportamento ai bordi e il caso di nodi coincidenti
  o non raggiungibili (l'autore già accenna alla "raggiungibilità": formalizzarlo).

---

## 6. Domande agli autori

1. Come si fissa lo z-score "congelato" **in performance**, dove non esiste un corpus?
2. La distanza euclidea pesa anche i descrittori di fascia bassa che dichiarate inaffidabili:
   perché non escluderli o ripesarli nel controllo?
3. Avete una qualunque evidenza della tenuta del controllo a nodi **su strumenti acustici** o
   **dentro interfantasia**, anche solo qualitativa/d'ascolto? Anche un esempio audio aiuterebbe.
4. Cos'è "LEAP"?
5. L'onda stazionaria: avete dati per dire se è modo della stanza o dipende dalla sorgente?
   (Già indicato come futuro — c'è anche solo un indizio?)

---

## 7. Come mettere a fuoco il lavoro (visto che non è concluso)

In ordine di ritorno sull'investimento per superare la revisione:

1. **Chiudere lo scarto diagnosi/cura.** È *la* mossa. Anche un solo esperimento aggiuntivo —
   Fig. 7 ripetuta sugli strumenti acustici e con una seconda coppia di nodi su un asse sottile —
   trasforma il giudizio. Se non c'è tempo, ridimensionare le rivendicazioni con chiarezza
   chirurgica (abstract + Sez. 5 + conclusioni).
2. **Una frase, una tesi.** Decidere se l'articolo è "i descrittori sono contestuali" (diagnosi) o
   "ecco un controllo che cancella il contesto" (cura) e ribilanciare il testo verso la seconda,
   che è il vero contributo. Oggi il titolo promette la cura ma il corpo pesa sulla diagnosi.
3. **Risolvere il ponte real-time.** Un paragrafo sulla taratura dello z-score dal vivo dà
   sostanza alla parola "tempo reale".
4. **Sciogliere la tensione interpretabilità ↔ distanza euclidea**, e ripulire il passaggio
   Mahalanobis.
5. **Igiene da double-blind**: LEAP, *interfantasia*, riferimenti.

Se 1–3 vengono affrontati, secondo me il lavoro passa da "revisioni maggiori" a una buona
accettazione: l'idea è valida e il mestiere c'è.

---

*Revisione costruttiva: l'obiettivo è aiutare a portare a fuoco un lavoro che ha un'idea forte e
una base sperimentale seria.*
