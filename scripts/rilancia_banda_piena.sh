#!/usr/bin/env bash
# Re-run dell'intero corpus a BANDA PIENA (48000 Hz = Nyquist dei 96 kHz),
# per allineare §3/§4 alla §5 (LEAP, gia' a 48000 Hz). Non distruttivo: scrive
# CSV con suffisso _48000hz accanto agli esistenti _10000hz.
#
# Riproduce esattamente la pipeline di taglia_segnali.py / analizza_catalogo.py:
# stesso analisi.py sui WAV per-segmento gia' tagliati, stessi gate, solo banda 48000.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
PY=python
A="$ROOT/scripts/analisi.py"
BAND=48000

run_dir() {  # $1 = cartella analisi/<config>, $2... = gate args
  local base="$1"; shift
  local gates=("$@")
  local n=0
  for d in "$ROOT/$base"/*/; do
    local name; name="$(basename "$d")"
    local wav="$d$name.wav"
    [ -f "$wav" ] || continue
    "$PY" "$A" "$wav" --max-freq "$BAND" --output-dir "$d" --no-plot "${gates[@]}" \
      >/dev/null 2>&1
    n=$((n+1))
  done
  echo "[$base] $n segmenti a $BAND Hz"
}

echo "=== sintetici (no gate) ==="
run_dir analisi/sintetici
echo "=== test_segnali_-30db (no gate) ==="
run_dir analisi/test_segnali_-30db
for r in recs-002 recs-003 recs-004; do
  echo "=== $r (gate -65/-30) ==="
  run_dir "analisi/$r" --gate-dbfs -65 --gate-rel-db -30
done

echo "=== cataloghi (4ch->mono, gate -65/-30) ==="
"$PY" "$ROOT/scripts/analizza_catalogo.py" "$ROOT/segnali/francesco/clarinettocb" \
  --max-freq "$BAND" --output-root "$ROOT/analisi/clarinettocb" >/dev/null 2>&1
echo "[clarinettocb] fatto"
"$PY" "$ROOT/scripts/analizza_catalogo.py" "$ROOT/segnali/francesco/timpano" \
  --max-freq "$BAND" --output-root "$ROOT/analisi/timpano" >/dev/null 2>&1
echo "[timpano] fatto"

echo "=== FATTO: corpus a banda piena ($BAND Hz) ==="
