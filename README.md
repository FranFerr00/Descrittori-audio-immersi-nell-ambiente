# Descrittori audio: misura relativa e controllo a nodi

Materiale supplementare anonimo dell'articolo (codice di analisi, script delle
figure, dati derivati ed external Pure Data). Studio su 16 descrittori audio
messi alla prova fuori dalle condizioni ideali per cui erano pensati: a
distanza, in ambiente, attraverso una catena di ripresa. La proposta è leggerli
in modo relativo, come posizione fra due suoni di riferimento tarati nello
stesso ambiente.

## Struttura

- `paper/` — sorgente LaTeX dell'articolo, script delle figure (`plot_*.py`) e figure
- `scripts/` — script di analisi
- `esplorazioni/` — analisi esplorative (PCA, traiettorie, controllo a nodi)
- `analisi/` — dati derivati (CSV) letti dagli script delle figure
- `esperimento_distanza/` — codice dell'esperimento a otto microfoni
- `pd-externals/`, `test-pd/` — external Pure Data e patch di test
- `diario/` — schede dei singoli descrittori
- `cataloghi/` — schede di risultati per strumento

## Riprodurre le figure

Dalla cartella `paper/`:

    python3 plot_scostamento.py
    python3 plot_controllo_nodi.py
    # ...e gli altri plot_*.py

Gli audio grezzi e i PDF bibliografici di terzi non sono inclusi.
