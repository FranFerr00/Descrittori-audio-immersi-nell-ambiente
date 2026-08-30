#
# Pipeline test segnali
#
# Genera:
#   1. test_segnali.wav da Csound
#   2. taglio in 45 segmenti + analisi (analisi/sintetici/NN_*/)
#   3. versione scalata a -30 dB (test_segnali_-30db.wav) + taglio+analisi
#   4. taglio recs-002..004 + analisi (analisi/recs-00N/NN_*/)
#   5. analisi dei cataloghi di gesti strumentali
#      (segnali/francesco/<nome>/samples/*.wav → analisi/<nome>/analisi/NNN/)
#   6. tabelle riassuntive (analisi/tabelle/)
#
# Uso:
#   make               # genera tutto
#   make wav           # solo Csound
#   make segnali       # solo taglio+analisi sintetici
#   make segnali-30db  # scala a -30 dB e taglia+analizza
#   make recs          # solo taglio+analisi registrazioni microfono
#   make cataloghi     # analisi di tutti i cataloghi strumentali
#   make nuovi         # descrittori in test (entropy + contrast, desc_nuovi/)
#   make zscore        # normalizza per-sample i CSV in *_zscore.csv
#   make zscore-plot   # PNG per CSV: 4 subplot (famiglie), descrittori in σ
#   make tabelle       # solo tabelle
#   make clean         # rimuove tutto il generato
#   make clean-tabelle # rimuove solo le tabelle
#   make clean-nuovi   # rimuove desc_nuovi/
#   make clean-zscore  # rimuove i CSV *_zscore.csv e i PNG *_zscore.png
#
# Per aggiungere un nuovo catalogo: crearlo in segnali/francesco/<nome>/
# con sottocartella samples/NNN.wav, poi aggiungere il nome alla variabile
# CATALOGHI qui sotto.
#

PYTHON    := python
CSOUND    := csound
SEG_DIR   := segnali
OUT_DIR   := analisi
# Banda d'analisi: banda piena = Nyquist dei 96 kHz. Allineata a §5/LEAP e al paper
# (prima era 10000; il tetto a 10 kHz nascondeva l'assorbimento dell'aria negli acuti).
BAND      := 48000
CSD       := $(SEG_DIR)/test_segnali.csd
WAV       := $(SEG_DIR)/test_segnali.wav
WAV_30    := $(SEG_DIR)/test_segnali_-30db.wav
RECS      := $(SEG_DIR)/recs-002.wav $(SEG_DIR)/recs-003.wav $(SEG_DIR)/recs-004.wav
TABELLE   := $(OUT_DIR)/tabelle

# cataloghi di gesti strumentali (segnali/francesco/<nome>/samples/*.wav)
CAT_DIR   := $(SEG_DIR)/francesco
CATALOGHI := clarinettocb timpano

# id "ufficiali" per ciascun catalogo: solo questi vengono inclusi nei
# grafici aggregati (vedi docs/schede/<nome>.md per la descrizione).
CLARINETTOCB_OFF := 001,002,003,004,005,006,007,010,013
TIMPANO_OFF      := 004,005,006,007,008,015,016,018,023,025

# file sentinella: servono a make per capire cosa e' gia' aggiornato
STAMP_DIR := $(OUT_DIR)/.stamps
STAMP_SEGNALI := $(STAMP_DIR)/segnali
STAMP_30DB    := $(STAMP_DIR)/segnali-30db
STAMP_RECS    := $(STAMP_DIR)/recs
STAMP_CATALOGHI  := $(foreach c,$(CATALOGHI),$(STAMP_DIR)/cat-$(c))
STAMP_TEMPORALI  := $(foreach c,$(CATALOGHI),$(STAMP_DIR)/temp-$(c))
STAMP_NUOVI      := $(STAMP_DIR)/nuovi-sintetici \
                    $(foreach c,$(CATALOGHI),$(STAMP_DIR)/nuovi-$(c))

.PHONY: all sync-supplementare wav segnali segnali-30db recs cataloghi temporali tabelle desc nuovi zscore zscore-plot clean clean-tabelle clean-wav clean-segnali clean-segnali-30db clean-recs clean-cataloghi clean-temporali clean-desc clean-nuovi clean-zscore

all: tabelle

# Aggiorna il repo pubblico del materiale supplementare (citato in bibliografia)
sync-supplementare:
	bash scripts/sync_supplementare.sh

# --- analisi singolo descrittore (test rapido) ---
# Uso: make desc ONLY=tpr,n_peaks
# Output: desc/<ONLY>/
desc:
ifndef ONLY
	$(error Specifica il descrittore con ONLY=nome, es: make desc ONLY=tpr,n_peaks)
endif
	$(PYTHON) scripts/analisi.py $(WAV) --only $(ONLY) --max-freq $(BAND)
	@if [ -f $(WAV_30) ]; then \
		$(PYTHON) scripts/analisi.py $(WAV_30) --only $(ONLY) --max-freq $(BAND); \
	fi
	@for f in $(RECS); do \
		if [ -f $$f ]; then \
			$(PYTHON) scripts/analisi.py $$f --only $(ONLY) --max-freq $(BAND) \
				--gate-dbfs -65 --gate-rel-db -30; \
		fi; \
	done
	@for c in $(CATALOGHI); do \
		for f in $(CAT_DIR)/$$c/samples/*.wav; do \
			[ -f "$$f" ] && $(PYTHON) scripts/analisi.py "$$f" --only $(ONLY) \
				--max-freq $(BAND) --gate-dbfs -65 --gate-rel-db -30; \
		done; \
	done

$(STAMP_DIR):
	mkdir -p $(STAMP_DIR)

# --- Csound ---
wav: $(WAV)

$(WAV): $(CSD)
	cd $(SEG_DIR) && $(CSOUND) test_segnali.csd

# --- taglio + analisi sintetici ---
segnali: $(STAMP_SEGNALI)

$(STAMP_SEGNALI): $(WAV) scripts/taglia_segnali.py scripts/analisi.py scripts/temporali.py scripts/aggrega_grafici.py | $(STAMP_DIR)
	$(PYTHON) scripts/taglia_segnali.py $(WAV) --max-freq $(BAND)
	$(PYTHON) scripts/aggrega_grafici.py $(OUT_DIR)/sintetici
	@touch $@

# --- versione -30 dB: scala il wav e taglia con segmenti completi ---
$(WAV_30): $(WAV)
	$(PYTHON) -c "import soundfile as sf; d,sr=sf.read('$(WAV)'); sf.write('$(WAV_30)', d*10**(-30/20), sr, subtype='FLOAT')"

segnali-30db: $(STAMP_30DB)

$(STAMP_30DB): $(WAV_30) scripts/taglia_segnali.py scripts/analisi.py scripts/temporali.py scripts/aggrega_grafici.py | $(STAMP_DIR)
	$(PYTHON) scripts/taglia_segnali.py $(WAV_30) --subdir --max-freq $(BAND)
	$(PYTHON) scripts/aggrega_grafici.py $(OUT_DIR)/test_segnali_-30db
	@touch $@

# --- taglio + analisi registrazioni microfono ---
recs: $(STAMP_RECS)

$(STAMP_RECS): $(wildcard $(RECS)) scripts/taglia_segnali.py scripts/analisi.py scripts/temporali.py scripts/aggrega_grafici.py | $(STAMP_DIR)
	@for f in $(RECS); do \
		if [ -f $$f ]; then \
			echo ">>> $$f"; \
			$(PYTHON) scripts/taglia_segnali.py $$f --recs --max-freq $(BAND) --gate-dbfs -65 --gate-rel-db -30; \
			base=$$(basename $$f .wav); \
			$(PYTHON) scripts/aggrega_grafici.py $(OUT_DIR)/$$base; \
		else \
			echo "!! manca $$f (saltato)"; \
		fi; \
	done
	@touch $@

# --- cataloghi di gesti strumentali ---
# I WAV multicanale dei campioni vengono automaticamente ridotti a mono (omni)
# tramite media dei canali in scripts/analisi.py (load_audio).
# Il grafico aggregato include solo i campioni ufficiali (vedi *_OFF sopra).
cataloghi: $(STAMP_CATALOGHI)

$(STAMP_DIR)/cat-clarinettocb: scripts/analizza_catalogo.py scripts/analisi.py scripts/aggrega_grafici.py $(wildcard $(CAT_DIR)/clarinettocb/samples/*.wav) | $(STAMP_DIR)
	$(PYTHON) scripts/analizza_catalogo.py $(CAT_DIR)/clarinettocb --max-freq $(BAND) --output-root $(OUT_DIR)/clarinettocb
	$(PYTHON) scripts/aggrega_grafici.py $(OUT_DIR)/clarinettocb/analisi --prefix clarinettocb --only $(CLARINETTOCB_OFF)
	@touch $@

$(STAMP_DIR)/cat-timpano: scripts/analizza_catalogo.py scripts/analisi.py scripts/aggrega_grafici.py $(wildcard $(CAT_DIR)/timpano/samples/*.wav) | $(STAMP_DIR)
	$(PYTHON) scripts/analizza_catalogo.py $(CAT_DIR)/timpano --max-freq $(BAND) --output-root $(OUT_DIR)/timpano
	$(PYTHON) scripts/aggrega_grafici.py $(OUT_DIR)/timpano/analisi --prefix timpano --only $(TIMPANO_OFF)
	@touch $@

# --- descrittori temporali dei cataloghi strumentali ---
# sintetici e recs vengono analizzati automaticamente da scripts/taglia_segnali.py
temporali: $(STAMP_TEMPORALI)

$(STAMP_DIR)/temp-clarinettocb: scripts/temporali.py $(wildcard $(CAT_DIR)/clarinettocb/samples/*.wav) | $(STAMP_DIR)
	$(PYTHON) scripts/temporali.py $(CAT_DIR)/clarinettocb/samples/ \
		--output-dir $(OUT_DIR)/clarinettocb/temporali \
		--gate-dbfs -65 --gate-rel-db -30 --no-plot
	@touch $@

$(STAMP_DIR)/temp-timpano: scripts/temporali.py $(wildcard $(CAT_DIR)/timpano/samples/*.wav) | $(STAMP_DIR)
	$(PYTHON) scripts/temporali.py $(CAT_DIR)/timpano/samples/ \
		--output-dir $(OUT_DIR)/timpano/temporali \
		--gate-dbfs -65 --gate-rel-db -30 --no-plot
	@touch $@

# --- descrittori in test (entropy + contrast) ---
# NOTA: scripts/analisi_nuovi.py e' provvisorio. Serve a validare due descrittori
# extra sul corpus prima di un eventuale ingresso nei 16 ufficiali.
nuovi: $(STAMP_NUOVI)

$(STAMP_DIR)/nuovi-sintetici: scripts/analisi_nuovi.py $(wildcard $(OUT_DIR)/sintetici/*/*.wav) | $(STAMP_DIR)
	@for d in $(OUT_DIR)/sintetici/*/; do \
		name=$$(basename $$d); \
		wav=$$d$$name.wav; \
		if [ -f $$wav ]; then \
			$(PYTHON) scripts/analisi_nuovi.py $$wav --max-freq $(BAND) \
				--output-dir desc_nuovi/sintetici/$$name; \
		fi; \
	done
	@touch $@

$(STAMP_DIR)/nuovi-clarinettocb: scripts/analisi_nuovi.py $(wildcard $(CAT_DIR)/clarinettocb/samples/*.wav) | $(STAMP_DIR)
	@for f in $(CAT_DIR)/clarinettocb/samples/*.wav; do \
		n=$$(basename $$f .wav); \
		$(PYTHON) scripts/analisi_nuovi.py $$f --max-freq $(BAND) \
			--gate-dbfs -65 --gate-rel-db -30 \
			--output-dir desc_nuovi/clarinettocb/$$n; \
	done
	@touch $@

$(STAMP_DIR)/nuovi-timpano: scripts/analisi_nuovi.py $(wildcard $(CAT_DIR)/timpano/samples/*.wav) | $(STAMP_DIR)
	@for f in $(CAT_DIR)/timpano/samples/*.wav; do \
		n=$$(basename $$f .wav); \
		$(PYTHON) scripts/analisi_nuovi.py $$f --max-freq $(BAND) \
			--gate-dbfs -65 --gate-rel-db -30 \
			--output-dir desc_nuovi/timpano/$$n; \
	done
	@touch $@

# --- z-score per-sample ---
# Post-processing: legge i CSV *_analisi.csv esistenti e scrive accanto
# un *_zscore.csv con media/std calcolate sui frame non-gated del singolo
# sample. Non dipende da stamp: agisce su qualsiasi CSV trovi in $(OUT_DIR).
zscore:
	$(PYTHON) scripts/zscore.py $(OUT_DIR)

# plot dei descrittori z-scored, un PNG per CSV. Da lanciare dopo `make zscore`.
zscore-plot:
	$(PYTHON) scripts/plot_zscore.py $(OUT_DIR)

# --- tabelle (dipendono dai tre stamp) ---
tabelle: $(STAMP_SEGNALI) $(STAMP_30DB) $(STAMP_RECS)
	DESC_BAND=$(BAND) $(PYTHON) scripts/tabelle_descrittori.py

# --- clean ---
clean: clean-tabelle clean-segnali clean-segnali-30db clean-recs clean-cataloghi clean-temporali clean-wav clean-desc clean-nuovi
	rm -rf $(STAMP_DIR)
	@echo "Pulito."

clean-nuovi:
	rm -rf desc_nuovi
	rm -f  $(STAMP_NUOVI)

clean-zscore:
	find $(OUT_DIR) -name "*_zscore.csv" -delete 2>/dev/null || true
	find $(OUT_DIR) -name "*_zscore.png" -delete 2>/dev/null || true

clean-desc:
	rm -rf desc

clean-wav:
	rm -f $(WAV)

clean-tabelle:
	rm -rf $(TABELLE)

# rimuove la cartella dei segmenti sintetici e i grafici aggregati
clean-segnali:
	rm -rf $(OUT_DIR)/sintetici
	rm -f  $(STAMP_SEGNALI)

# rimuove il wav -30 dB e la sua cartella di segmenti
clean-segnali-30db:
	rm -f  $(WAV_30)
	rm -rf $(OUT_DIR)/test_segnali_-30db
	rm -f  $(STAMP_30DB)

# rimuove le cartelle analisi/recs-00N/ (conserva i .wav sorgente in segnali/)
clean-recs:
	rm -rf $(OUT_DIR)/recs-002 $(OUT_DIR)/recs-003 $(OUT_DIR)/recs-004
	rm -f  $(STAMP_RECS)

# rimuove le cartelle analisi/ dei cataloghi (conserva catalog.json, samples/, docs/)
clean-cataloghi:
	@for c in $(CATALOGHI); do \
		echo ">>> clean $$c"; \
		rm -rf $(OUT_DIR)/$$c/analisi; \
	done
	rm -f $(STAMP_CATALOGHI)

# rimuove le cartelle temporali/ dei cataloghi
clean-temporali:
	@for c in $(CATALOGHI); do \
		echo ">>> clean temporali $$c"; \
		rm -rf $(OUT_DIR)/$$c/temporali; \
	done
	rm -f $(STAMP_TEMPORALI)
