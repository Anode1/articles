#!/bin/sh
# The path-with-read run: the index returns a document path, the agent reads it; the
# search arm greps and reads the same tree. Both arms pay for the reading.
# The harness is ../run.py; the ais binary is built in its checkout, AIS_REPO.
#   REPEATS=5 sh run.sh            (from this directory; needs the key in
#                                   ANTHROPIC_API_KEY or ~/.config/anthropic/api_key)
set -eu
PY=${PY:-python3}; REPEATS=${REPEATS:-5}; MODEL=${MODEL:-claude-sonnet-4-6}
ROOT=${ROOT:-$HOME/kul}; OUT=${OUT:-results.csv}; AIS_REPO=${AIS_REPO:-$HOME/ais}
[ -n "${ANTHROPIC_API_KEY:-}" ] || ANTHROPIC_API_KEY=$(cat ~/.config/anthropic/api_key); export ANTHROPIC_API_KEY
AIS="$AIS_REPO/ais" sh build_index.sh index
exec "$PY" ../run.py --ais "$AIS_REPO/ais" --index index --search-root "$ROOT" --exclude PRIVATE \
  --questions questions.json --model "$MODEL" --repeats "$REPEATS" --out "$OUT"
