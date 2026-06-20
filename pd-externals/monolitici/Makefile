# Makefile per descrittori monolitici
# Layout:
#   src/NOME.c                sorgenti tutti insieme
#   NOME/NOME-help.pd         help e patch di esempio del singolo descrittore
#   NOME/NOME.pd_linux        external compilato (output)

CC = gcc
CFLAGS = -DPD -O2 -fPIC -Wall
PDINCLUDE = /usr/include/pd

UNAME := $(shell uname -s)

ifeq ($(UNAME),Linux)
    LDFLAGS = -shared -lm
    EXT = pd_linux
endif

ifeq ($(UNAME),Darwin)
    LDFLAGS = -bundle -undefined dynamic_lookup -lm
    EXT = pd_darwin
endif

OBJECTS = centroid spread rolloff slope obsir_std flatness irregularity flux \
          crest skewness kurtosis entropy tonality tpr zcr zscore matrice \
          selettore scatto ancore ema

EXTERNALS = $(foreach obj,$(OBJECTS),$(obj)/$(obj).$(EXT))

all: $(EXTERNALS)

# Regola generata per ogni descrittore: NOME/NOME.pd_linux ← src/NOME.c
define build_rule
$(1)/$(1).$(EXT): src/$(1).c
	@mkdir -p $(1)
	$(CC) $(CFLAGS) -I$(PDINCLUDE) $(LDFLAGS) -o $$@ $$<
	@echo "Compilato: $$@"
endef
$(foreach obj,$(OBJECTS),$(eval $(call build_rule,$(obj))))

clean:
	rm -f */*.$(EXT)
	@echo "Pulito!"

install: all
	mkdir -p ~/Documents/Pd/externals
	cp $(EXTERNALS) ~/Documents/Pd/externals/
	@for obj in $(OBJECTS); do \
		if [ -f $$obj/$$obj-help.pd ]; then \
			cp $$obj/$$obj-help.pd ~/Documents/Pd/externals/; \
		fi; \
	done
	@echo "Installati tutti i monolitici (con help) in ~/Documents/Pd/externals/"

help:
	@echo "Comandi disponibili:"
	@echo "  make          - compila tutti i monolitici"
	@echo "  make clean    - rimuove i file compilati"
	@echo "  make install  - installa tutti in Pd"
	@echo ""
	@echo "Oggetti da compilare:"
	@echo "  $(OBJECTS)"
