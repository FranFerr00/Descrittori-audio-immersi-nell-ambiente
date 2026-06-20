## ricordario

### Aperte

- [ ] scrivere un md su come funziona il repository (la struttura è in `CLAUDE.md`, manca una guida estesa per chi non usa Claude)
- [ ] convertire le schede descrittori da .md a LaTeX per le formule (vedi `dispensa-descrittori.tex` come modello)

### Risolte

- [x] tpr, slope e decrease non stanno dando informazioni → decrease rimosso (sostituito da OBSIR-std, 2026-04-17); TPR riscritto con prominence (2026-04-03, fix 2026-04-15); slope riscritto a regressione dB/ottava (2026-04-15). Bilancio finale nella tassonomia di robustezza del paper
- [x] sostituire l'autocorrelation con la spectral entropy → fatto il 2026-04-17 (contrast provato e scartato)
- [x] aumentare il numero di descrittori (temporali e di ampiezza) → superato: il set dei 16 è chiuso per scelta; i candidati futuri si provano negli slot sperimentali (`analisi_nuovi.py`, `make nuovi`)
- [x] riordinare il repository → 2026-04-15 (riorganizzazione generale), 2026-06-09 (materiale del paper separato in `paper/`) e 2026-06-11 (script Python in `scripts/`, `src/` rinominata `tesi/`, wav e call CIM ricollocati; Makefile e script aggiornati ai nuovi percorsi)
- [x] valutare sistemi di normalizzazione: z-score → `zscore.py` + `make zscore` (2026-04-19), poi z-score congelato sul corpus e sbiancamento Mahalanobis (2026-06-01)
