# Descrittori audio: misura relativa e controllo a nodi

Materiale supplementare dell'articolo **"Descrittori audio immersi nell'ambiente:
quale mappatura ricavarne"** (XXV CIM, Colloqui di Informatica Musicale, 2026),
di Francesco Ferracuti (LEAP - Laboratorio Elettroacustico Permanente).

Contiene il codice di analisi, gli script che generano le figure, i dati derivati
e le patch Pure Data di test. Lo studio mette alla prova 16 descrittori audio fuori
dalle condizioni ideali per cui erano pensati: a distanza, in ambiente, attraverso
una catena di ripresa. La proposta è leggerli in modo relativo, come posizione fra
due suoni di riferimento tarati nello stesso ambiente. I descrittori sono gli
stessi che guidano il live electronics di *interfantasia*.

## Struttura

- `paper/` — sorgente LaTeX dell'articolo, script delle figure (`plot_*.py`) e figure
- `scripts/` — script di analisi
- `esplorazioni/` — analisi esplorative (PCA, traiettorie, controllo a nodi)
- `analisi/` — dati derivati (CSV) letti dagli script delle figure
- `esperimento_distanza/` — codice dell'esperimento a otto microfoni
- `test-pd/` — patch Pure Data di test dei singoli descrittori
- `diario/` — schede dei singoli descrittori
- `cataloghi/` — schede di risultati per strumento

Gli external Pure Data dei descrittori non stanno qui: hanno una fonte unica nella
libreria **pd-descrittori**, <https://gitlab.com/francesco-ferracuti/pd-descrittori>
(sorgenti C, build con `make`).

## Riprodurre le figure

Dalla cartella `paper/`:

    python3 plot_scostamento.py
    python3 plot_controllo_nodi.py
    # ...e gli altri plot_*.py

Gli audio grezzi e i PDF bibliografici di terzi non sono inclusi.
