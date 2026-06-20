#
# Pipeline dell'esperimento di distanza (LEAP) — prova principale del paper (§5).
#
# Codifica i passi finora lanciati a mano sugli script di questa cartella. Parte dai
# wav multicanale gia' divisi per sorgente (8 canali = 8 distanze, 1->8 m) e genera i
# dati e i grafici che alimentano il report e la §5 del paper.
#
# Catena:
#   1. analizza_divisi.py  -> analisi per-canale dei 16 descrittori (la fondazione)
#   2. calibrazione_rms.py -> verifica dell'allineamento dei gain (RMS sul grappolo)
#   3. attenuazione_distanza.py -> attenuazione del rumore vs distanza
#   4. centroidi_riepilogo.py   -> centroidi_medie.csv + grafici (onda stazionaria, heatmap)
#   5. profili_famiglie.py      -> medie per canale dei 16 descrittori, grafici diagnostici
#   6. confronto_banda.py       -> centroide del rumore 10 kHz vs banda piena (assorbimento aria)
#
# Banda primaria = banda piena (48 kHz = Nyquist dei 96 kHz), la stessa del corpus e
# del paper; il 10 kHz serve solo al confronto di banda (passo 6).
#
# Uso:
#   make            # dati a banda piena + confronto di banda
#   make dati       # solo i dati/grafici a banda piena (no 10 kHz)
#   make confronto  # confronto 10 kHz vs banda piena (rigenera anche il 10 kHz)
#   make report     # compila report-distanza-leap.pdf
#   make clean      # rimuove le sentinelle (non i dati)
#
# I dati a banda piena esistono gia' nel repo (analisi/distanza-banda-piena/): un
# `make` li rigenera solo se cambiano gli script o i wav di input. Rieseguire la
# fondazione (analizza_divisi) e' pesante: 25 file x 8 canali di analisi.
#

PYTHON   := python

# sorgente: wav divisi per sorgente, 8 canali = 8 distanze (vedi README dell'esperimento)
REC_DIR  := 2026-06-13-FRAFER-TEST-DISTANZA-GIUSTO
DIVISI   := $(REC_DIR)/divisi
WAVS     := $(wildcard $(DIVISI)/*.wav)

# uscite (relative a questa cartella, cioe' sotto la radice del repo)
OUT      := ../analisi/distanza-banda-piena
OUT10    := ../analisi/distanza
BAND     := 48000

STAMP    := .stamps

.PHONY: all dati banda-10k calibrazione attenuazione centroidi profili confronto report clean

all: dati confronto

dati: calibrazione attenuazione centroidi profili

$(STAMP):
	mkdir -p $(STAMP)

# --- 1. analisi per-canale (fondazione, banda piena) ---
$(STAMP)/divisi-48k: analizza_divisi.py $(WAVS) | $(STAMP)
	$(PYTHON) analizza_divisi.py $(DIVISI) $(OUT) --max-freq $(BAND)
	@touch $@

# --- 1bis. stessa analisi a 10 kHz (solo per il confronto di banda) ---
$(STAMP)/divisi-10k: analizza_divisi.py $(WAVS) | $(STAMP)
	$(PYTHON) analizza_divisi.py $(DIVISI) $(OUT10) --max-freq 10000
	@touch $@

banda-10k: $(STAMP)/divisi-10k

# --- 2. calibrazione gain (RMS, indipendente dalla banda) ---
calibrazione: $(OUT)/calibrazione_rms.csv
$(OUT)/calibrazione_rms.csv: calibrazione_rms.py $(DIVISI)/NOISE_1mt.wav
	$(PYTHON) calibrazione_rms.py $(DIVISI)/NOISE_1mt.wav --out-dir $(OUT)

# --- 3. attenuazione del rumore vs distanza (RMS, indipendente dalla banda) ---
attenuazione: $(OUT)/attenuazione_distanza.csv
$(OUT)/attenuazione_distanza.csv: attenuazione_distanza.py \
		$(DIVISI)/NOISE_oriz_1-9mt.wav $(DIVISI)/NOISE_vert_1-9mt.wav
	$(PYTHON) attenuazione_distanza.py \
		$(DIVISI)/NOISE_oriz_1-9mt.wav $(DIVISI)/NOISE_vert_1-9mt.wav --out-dir $(OUT)

# --- 4. centroidi medie + grafici (onda stazionaria, heatmap) ---
centroidi: $(OUT)/centroidi_medie.csv
$(OUT)/centroidi_medie.csv: centroidi_riepilogo.py $(STAMP)/divisi-48k
	$(PYTHON) centroidi_riepilogo.py $(OUT)

# centroidi a 10 kHz: servono al confronto di banda
$(OUT10)/centroidi_medie.csv: centroidi_riepilogo.py $(STAMP)/divisi-10k
	$(PYTHON) centroidi_riepilogo.py $(OUT10)

# --- 5. profili per canale dei 16 descrittori (grafici diagnostici) ---
profili: $(STAMP)/profili
$(STAMP)/profili: profili_famiglie.py $(STAMP)/divisi-48k | $(STAMP)
	$(PYTHON) profili_famiglie.py $(OUT)
	@touch $@

# --- 6. confronto di banda: il tetto a 10 kHz nasconde l'assorbimento dell'aria ---
confronto: $(OUT)/centroidi_medie.csv $(OUT10)/centroidi_medie.csv
	$(PYTHON) confronto_banda.py $(OUT10) $(OUT)

# --- report LaTeX dell'esperimento ---
report: report-distanza-leap.pdf
report-distanza-leap.pdf: report-distanza-leap.tex
	pdflatex -interaction=nonstopmode report-distanza-leap.tex

clean:
	rm -rf $(STAMP)
