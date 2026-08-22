#!/bin/sh
# sweep2: the panel, the clearance arm and the reference layouts. Needs pairNN.h from
# extract.py and a cjitter checkout carrying the block parameter, given as $1 (default
# ~/cjitter). PANEL and GAP are environment variables; the defaults reproduce the record.
#   PANEL=101 GAP=12 ./run_sweep2.sh ~/cjitter
# Run it once per clearance and concatenate. At PANEL=101 the whole thing is a few hours on
# four cores; at the default 5 it is sixteen minutes on one.
#
# Builds in a private tree: see the warning in run_sweep.sh about never writing pairNN.h
# over the checkout's tracked, anonymized example/erd/erd_data.h.
set -e
FORCE=${FORCE:-0}
PANEL=${PANEL:-5}
GAP=${GAP:-12}
cd "$(dirname "$0")"
HERE=$(pwd)
CJ=${1:-$HOME/cjitter}
[ -d "$CJ/c" ] || { echo "no cjitter checkout at $CJ" >&2; exit 1; }
BUILD=$(mktemp -d "${TMPDIR:-/tmp}/cjsweep2.XXXXXX")
trap 'rm -rf "$BUILD"' EXIT
mkdir -p "$BUILD/example/erd"
ln -sfn "$CJ/c" "$BUILD/c"
ln -sfn "$CJ/example/erd/erd.c" "$BUILD/example/erd/erd.c"
cp sweep2.c "$BUILD/"

RESULT=sweep2_p${PANEL}_g${GAP}.csv
OUT=$BUILD/$RESULT
: > "$OUT"
for h in pair03 pair04 pair06 pair07 pair12 pair13 pair14 pair15 pair16; do
    n=${h#pair}
    cp "$HERE/$h.h" "$BUILD/example/erd/erd_data.h"
    ( cd "$BUILD" && cc -std=c99 -ffp-contract=off -O2 -DPAIR_ID=$n -DPANEL=$PANEL -DNODE_GAP=$GAP.0 \
        sweep2.c c/cjitter.c c/rng.c -lm -o sweep_bin )
    echo "== $h $(date +%H:%M:%S)" >&2
    "$BUILD/sweep_bin" >> "$OUT"
done

# Never clobber the record on a whim: if $RESULT exists, reproduce and compare.
# A byte-for-byte match is the check that licenses trusting a later arm against it.
if [ -f $RESULT ] && [ "$FORCE" != 1 ]; then
    if diff -q "$OUT" $RESULT >/dev/null; then
        echo "$RESULT reproduces byte for byte; leaving it alone" >&2
    else
        cp "$OUT" $RESULT.new
        echo "MISMATCH against the existing $RESULT. Wrote $RESULT.new; diff them." >&2
        exit 2
    fi
else
    cp "$OUT" $RESULT
fi
wc -l $RESULT >&2
