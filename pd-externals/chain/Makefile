# Makefile per array operations

# Compilatore
CC = gcc

# Flags
CFLAGS = -DPD -O2 -fPIC -Wall

# Percorso include Pd
PDINCLUDE = /usr/include/pd

# Sistema operativo
UNAME := $(shell uname -s)

# Linux
ifeq ($(UNAME),Linux)
    LDFLAGS = -shared -lm
    EXT = pd_linux
endif

# macOS
ifeq ($(UNAME),Darwin)
    LDFLAGS = -bundle -undefined dynamic_lookup -lm
    EXT = pd_darwin
endif

# Lista di tutti gli oggetti da compilare
OBJECTS = arraysum arraysub arraymol arraydiv arraylog arraysubscalar arraysubnext_noabs arrayabs arraydelta arraycounter arraymolscalar arraymax arraycumsum arraysubnext arraysubnext2

# Lista dei file compilati
EXTERNALS = $(addsuffix .$(EXT), $(OBJECTS))

# Compila tutti
all: $(EXTERNALS)

# Regola generica per compilare ogni oggetto
%.$(EXT): %.c
	$(CC) $(CFLAGS) -I$(PDINCLUDE) $(LDFLAGS) -o $@ $<
	@echo "Compilato: $@"

# Pulisci
clean:
	rm -f *.$(EXT)
	@echo "Pulito!"

# Installa tutti
install: all
	mkdir -p ~/Documents/Pd/externals
	cp $(EXTERNALS) ~/Documents/Pd/externals/
	@echo "Installati tutti gli oggetti in ~/Documents/Pd/externals/"

# Help
help:
	@echo "Comandi disponibili:"
	@echo "  make          - compila tutti gli oggetti"
	@echo "  make clean    - rimuove i file compilati"
	@echo "  make install  - installa tutti in Pd"
	@echo ""
	@echo "Oggetti da compilare:"
	@echo "  $(OBJECTS)"
