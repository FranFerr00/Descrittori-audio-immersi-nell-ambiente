# Struttura del paper CIM 2026 e confronto con le fonti

> Stato 2026-06-18. Riflette il paper dopo il riorientamento sulla catena
> elettroacustica (branch `paper-cim2026-catena`). Confronto con i quattro
> documenti di laboratorio: `prompt_esperimento.md`, il report del LEAP
> (`esperimento_distanza/report-distanza-leap.tex`, non esiste un
> `report_esperimento.md`), `diario/diario.md`, `diario/percorso.md`.

---

## 1. Tesi e obiettivo del paper

**Tesi unica:** i descrittori non misurano la sorgente, ma la sorgente *come la
consegna la catena elettroacustica* (ambiente, distanza, aria, microfono,
conversione). Il centroide, invariante al guadagno, è la sonda che lo dimostra.

**Obiettivo OSSERVATIVO**, non selettivo: vedere *cosa restituiscono* i
descrittori al crescere del realismo, non quali tenere. Set chiuso e intero.

---

## 2. Schema a capitoli e sottocapitoli (stato attuale)

| # | Sezione | Sotto-blocchi | Obiettivo |
|---|---------|---------------|-----------|
| — | Abstract (EN) | — | Domanda + centroide-sonda + tre prove + lezione dal vivo |
| §1 | Origine: i descrittori e il comportamento inatteso | — | Motivare la domanda da un fatto concreto in *interfantasia* |
| §2 | Lavori correlati | — | Collocare fra data-driven e descrittori interpretabili; agganciare la robustezza |
| §3 | Il banco di prova | corpus · pipeline/gate/z-score · **centroide-nucleo** · tabella 16 descrittori · **nota di riproducibilità** (codice pubblico, deterministico, external C) | Attrezzare la misura |
| §4 | Linea di base: dal sintetico allo strumento acustico | **§4a Segnali sintetici** (invarianza di scala, firma del luogo, deriva, tassonomia robustezza, bin esatto) · **§4b Strumenti acustici** (clarinetto=forma vs timpano=irregularity) | Lo "zero" della deformazione + come i descrittori seguono il gesto |
| §5 | La prova principale: i descrittori alla prova della distanza ⭐ | apparato (+ **foto** grappolo microfoni) · 3 osservazioni (assorbimento aria, onda stazionaria, attenuazione 1/√r) · **altri descrittori** (tabella onda nodo/ventre + tabella kurtosis del Do/campana) · **direttività e soprano vs CCB** · **note matematiche** | La catena al lavoro in modo sistematico (prova centrale) |
| §6 | Sintesi: cosa resta della sorgente, cosa porta la sala | le 3 letture (ancorata alla sorgente / firma della sala / poco informativa) + tabella | Tirare le fila sull'asse sorgente/sala (non una classifica) |
| §7 | Discussione | criteri · **proposta nodi (una riga)** · limiti (timpano, momenti, punto aperto LEAP) · gioco inverso | Lezione, proposta futura, limiti |

**Arco:** §1 domanda → §2 colloca → §3 attrezza → **§4→§5 salgono per realismo
crescente** → §6 sintetizza → §7 chiude. 7 sezioni (la vecchia §Codice è stata
assorbita in §3).

---

## 3. Confronto con le fonti

### 3.1 `prompt_esperimento.md` → confluisce in §5 (anonimizzato)

È il brief con cui è stato commissionato l'esperimento di distanza. Tutto il suo
contenuto fattuale è in §5, ma **anonimizzato** per il doppio cieco:

| prompt_esperimento.md | nel paper §5 |
|---|---|
| LEAP, Laboratorio ElettroAcustico Permanente di Roma | "un laboratorio di elettroacustica" |
| LineAudio OM1, Audient ASP880, Yamaha HS8, PETALONIO | "microfoni omnidirezionali", "preamplificatore multicanale", marche/nomi rimossi |
| 8 mic a passo 1 m (1→8 m), doppia ripresa orizz/vert | apparato di §5 (identico) |
| calibrazione gain a RMS uguale, 96 dBA@1 m | dev.std 0,17 dB; fonometro 96/93/90/87 dBA |
| centroide come analisi centrale (matematica ripresa dagli altri) | filo conduttore di §5 + §3 centroide-nucleo |
| attenuazione teorica 1/√2 al raddoppio (mic 1,2,4,8) | terza osservazione (1/√r vs campo libero) |
| direttività mic = fenomeno di alta frequenza (doppia angolazione) | direttività del microfono in chiusura di §5 |
| "particolarità che non voglio dichiarare per non influenzare" | = l'onda stazionaria, svelata e spiegata in §5 |

### 3.2 Report del LEAP (`report-distanza-leap.tex`) → compresso e anonimizzato in §5

Report di laboratorio **autonomo** (11 sezioni, italiano, non anonimo). §5 ne è la
versione breve e cieca per il paper.

| Report (sezioni) | nel paper |
|---|---|
| Scopo · Apparato e metodo · Pipeline d'analisi · Calibrazione | apparato di §5 (1 paragrafo) |
| Il rumore sulla distanza | osservazione 1 (assorbimento aria) + `figura_leap_centroide_rumore` |
| Il centroide sugli strumenti | osservazione 2 (onda stazionaria) + `figura_leap_onda_ccb` |
| Comportamento dei descrittori | distribuito tra §5 e §6 |
| Discussione · Conclusioni | §5 chiusura + §7 (punto aperto onda stazionaria) |
| Note matematiche (invariante di scala, 1/r, assorbimento aria) | richiami brevi in §5; la dimostrazione di scala vive in §4 |

Il report resta il documento esteso e firmato; il paper ne prende i risultati, li
anonimizza e li integra con la linea di base (§4) e la sintesi (§6).

### 3.3 `diario/diario.md` → fonte di formule e analisi, copre molto più del paper

Indice delle voci giornaliere + schede dei 16 descrittori. Il paper attinge a:
- **schede `diario/<descrittore>/`** per formule e valori attesi (§3, §4);
- analisi del corpus (flatness/bin esatto, crest, centroide, TPR) → §4;
- voci 2026-06-13/16 (LEAP) → §5.

Restano **fuori dal paper** (lavoro di laboratorio, non articolo): tutta la parte
real-time (monolitici Pd 23–28 apr), la mappatura matrice/bicomb (mag), gli
external `[ancore]`/`[ema]`/`[matrice]`. Sono nel diario e in `docs/STATO_PROGETTO.md`.

### 3.4 `diario/percorso.md` → il percorso completo; il paper ne è una fetta osservativa

`percorso.md` racconta 9 fasi, dalla flatness (30 mar) al LEAP (16 giu), con tre
svolte (a mattoni→monolitico; matrice/bicomb→ancore; sbiancamento come spia). Il
paper **non ripercorre il percorso**: ne isola l'asse osservativo e lascia cadere
l'arco strumentale/real-time e il metodo a nodi.

| Fase di percorso.md | Nel paper attuale |
|---|---|
| 1 Ascoltare prima di calcolare · 2 Pipeline e 16 descrittori · 3 Potatura | confluite in §3 + §4 (la potatura è accennata in §4b, non è più un fine) |
| 4 External Pd (monolitici) · 5 Mappatura matrice/bicomb | **fuori dal paper** |
| 6 Ancore e distanza (la "svolta") | **declassato**: una riga di proposta in §7 |
| 7 Deriva sintetico→ripreso | §4a (Tabella deriva, firma del luogo) |
| 9 Esperimento distanza al LEAP | **§5, prova principale** |

> ⚠️ `percorso.md` §8 descrive una versione **superata** del paper ("potatura del
> set", "ancore e distanza" come sezione, titolo "condizione ecosistemica", il
> mini-esperimento di validazione nodi). Va aggiornata: il paper oggi è
> osservativo sulla catena, i nodi sono solo una proposta, il mini-esperimento è
> stato rimosso (prosa salva in `paper/archivio/articolo-cim2026-pre-catena.tex`).

---

## 4. In sintesi: cosa il paper tiene e cosa lascia fuori

**Tiene** (asse osservativo): studio dei descrittori → linea di base sintetici e
strumenti → esperimento di distanza (prova principale) → sintesi sorgente/sala.

**Lascia fuori** (resta nel laboratorio/diario): external Pure Data e tempo reale,
mappatura matrice/bicomb, **metodo a nodi e distanza** (ridotto a una riga di
proposta), sbiancamento di Mahalanobis, mini-esperimento di validazione dei nodi.

La differenza chiave rispetto a `percorso.md`: il *percorso* è il racconto di tutto
il lavoro; il *paper* è una tesi sola, dimostrata bene, su un solo asse.
