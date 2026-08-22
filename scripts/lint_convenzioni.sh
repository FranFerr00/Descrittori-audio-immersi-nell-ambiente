#!/usr/bin/env bash
# Verifica le convenzioni di scrittura del progetto sul corpo del paper.
# Uso: lint_convenzioni.sh [file.tex]   (default: la camera-ready)
# Esce con codice != 0 se trova violazioni.
set -u
FILE="${1:-$(dirname "$0")/../paper/articolo-cim2026-camera-ready.tex}"
[ -f "$FILE" ] || { echo "File non trovato: $FILE" >&2; exit 2; }
fail=0

check() {  # descrizione  pattern(grep -E, case-insensitive)
  local desc="$1" pat="$2"
  local hits
  hits=$(grep -nEi "$pat" "$FILE" | grep -v '^\s*[0-9]*:%' || true)
  if [ -n "$hits" ]; then
    echo "VIOLAZIONE: $desc"
    echo "$hits"
    echo
    fail=1
  fi
}

check "trattino lungo (em-dash o ---)" '—|---'
check "termine vietato: performer/esecutore/esecuzione" '\b(performer|esecutor[ei]|esecuzion[ei])\b'
check "anglicismo: pattern/framework" '\b(pattern|framework)\b'
check "spazio dei suoni / sound space" 'spazio dei suoni|sound space'
check "spazio acustico (usare 'spazio dei descrittori' o 'luogo')" 'spazio acustico'
check "'audio' come sostantivo (deve essere aggettivo: 'segnale/descrittori audio')" "l'audio|lo audio|gli audio"
check "framing vietato: molto riverberato" 'molto riverberat'
# Doppio cieco: il nome dell'autore non deve comparire. Dal 2026-06-11 il nome
# del brano (interfantasia) si può scrivere. Il controllo non vale sulla
# camera-ready, dove autore e affiliazione sono in chiaro per definizione.
case "$FILE" in
  *camera-ready*) ;;
  *) check "anonimizzazione: nome dell'autore nel testo" '\bFrancesco\b' ;;
esac

if [ "$fail" -eq 0 ]; then
  echo "Lint OK: nessuna violazione."
fi
exit "$fail"
