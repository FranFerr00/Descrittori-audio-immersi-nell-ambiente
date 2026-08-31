#!/usr/bin/env bash
# Aggiorna il repo pubblico del materiale supplementare citato in bibliografia
# (@misc{reposupp} in paper/riferimenti.bib) con lo stato di questo repo.
#
# Sostituisce scripts/genera_anon.sh, che serviva alla peer-review cieca e non
# serve piu' da quando l'articolo e' accettato e il materiale non e' anonimo.
#
# REGOLA: aggiorna SOLO i file che il mirror gia' traccia, e non ne aggiunge
# nessuno da solo. Lo scope del mirror e' una scelta curata (niente log datati
# del diario, niente PDF a parte le figure, niente peer-review, niente audio):
# ricostruirlo da una allowlist di cartelle lo ha gia' fatto sbagliare. Cosi'
# invece un file nuovo qui non finisce online per distrazione: viene elencato
# in fondo come candidato, e lo si aggiunge a mano nel mirror una volta sola.
#
# Non committa e non pusha: mostra cosa cambia e lascia la decisione.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-/home/francesco/github/Descrittori-audio-immersi-nell-ambiente}"

[ -d "$DEST/.git" ] || { echo "ERRORE: $DEST non e' un clone git." >&2; exit 1; }

# Cartelle da cui puo' arrivare un candidato nuovo (il resto non si guarda
# nemmeno: tesi/, docs/, segnali/, CLAUDE.md, prompt*).
SORGENTI=(Makefile README.md analisi cataloghi diario esperimento_distanza \
          esplorazioni paper scripts test-pd)

# File che nel mirror sono deliberatamente diversi e non vanno sovrascritti:
# il suo README e' scritto per chi scarica il supplementare (struttura, come
# rigenerare le figure), non e' il README interno di questo repo.
NON_TOCCARE=(README.md)

aggiornati=0; mancanti=0
while IFS= read -r f; do
  skip=""
  for n in "${NON_TOCCARE[@]}"; do [ "$f" = "$n" ] && skip=1; done
  [ -n "$skip" ] && continue
  if [ -f "$ROOT/$f" ]; then
    cmp -s "$ROOT/$f" "$DEST/$f" || { cp "$ROOT/$f" "$DEST/$f"; aggiornati=$((aggiornati+1)); }
  else
    echo "ASSENTE QUI (resta nel mirror com'e'): $f"; mancanti=$((mancanti+1))
  fi
done < <(git -C "$DEST" ls-files)

echo
echo "File aggiornati: $aggiornati    non piu' presenti qui: $mancanti"
echo
git -C "$DEST" status -s

# Candidati: file tracciati qui, sotto le cartelle sorgente, che il mirror non ha.
echo
echo "Candidati nuovi (NON copiati, valuta se pubblicarli):"
comm -23 <(git -C "$ROOT" ls-files -- "${SORGENTI[@]}" | sort) \
         <(git -C "$DEST" ls-files | sort) | sed 's/^/  /' | head -40

echo
echo "Se e' quello che ti aspetti: git -C \"$DEST\" add -A && git commit && git push"
