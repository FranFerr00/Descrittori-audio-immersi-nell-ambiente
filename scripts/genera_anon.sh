#!/usr/bin/env bash
# Rigenera la versione anonima del repo per la peer-review cieca (CIM).
#
# Cosa fa: copia in ../descrittori-anon SOLO le cartelle pubblicabili (allowlist),
# escludendo quanto identifica l'autore o è privato (tesi/, docs/, CLAUDE.md, tools/,
# template-cim/, prompt*, segnali/, e gli output rigenerabili desc/ risultati/).
# Il corpo del paper (paper/articolo-cim2026.tex) è già scritto in forma anonima:
# lo script lo verifica col lint esistente e si ferma se trova il nome dell'autore.
#
# NB: l'allowlist è volutamente una *whitelist* (non una blacklist): una cartella
# nuova non entra nell'anon finché non viene aggiunta qui a mano. È la scelta sicura
# per la cieca — meglio escludere per errore che far trapelare.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-$ROOT/../descrittori-anon}"

# Cartelle/file da includere nella versione anonima
INCLUDI=(analisi cataloghi diario esperimento_distanza esplorazioni Makefile \
         paper pd-externals README.md scripts test-pd)

echo "Rigenero la versione anonima in: $DEST"
rm -rf "$DEST"
mkdir -p "$DEST"

# Esporta SOLO i file tracciati da git dei path in allowlist: così restano fuori
# automaticamente i wav e gli output rigenerabili (gitignorati). Si parte da HEAD,
# quindi la versione anon riflette l'ultimo commit (non le modifiche non committate).
git -C "$ROOT" archive --format=tar HEAD -- "${INCLUDI[@]}" | tar -x -C "$DEST"

# Verifica anonimato del corpo del paper col lint esistente
echo "Verifico l'anonimato del paper col lint..."
( cd "$DEST" && bash scripts/lint_convenzioni.sh ) || {
  echo "ERRORE: il lint segnala il nome dell'autore nel paper anon ($DEST)." >&2
  echo "Correggere paper/articolo-cim2026.tex prima di inviare." >&2
  exit 1
}

# Avviso (non bloccante): il nome può comparire in file di contorno copiati
RESIDUI=$(grep -rliE "francesco|ferracuti" "$DEST" 2>/dev/null | sed "s#$DEST/##" || true)
if [ -n "$RESIDUI" ]; then
  echo
  echo "AVVISO: il nome dell'autore compare ancora in questi file di contorno"
  echo "(come nell'originale; rilevanti solo se invii anche questi file, non il solo PDF):"
  echo "$RESIDUI" | sed 's/^/  - /'
fi

echo
echo "Fatto. Versione anonima in: $DEST"
