#!/bin/sh
# The frozen pre-registered sweep. Needs pairNN.h from extract.py and a cjitter checkout,
# given as $1 (default ~/cjitter).
#
# This builds in a private tree under $TMPDIR rather than writing into the checkout. The
# earlier version symlinked pairNN.h over example/erd/erd_data.h inside the checkout, which
# is a tracked file holding the ANONYMIZED shipped instance: running it replaced that file
# with real table names in the working tree, one "git commit -a" away from publishing the
# schema the provenance rules exist to protect. Never write into the checkout.
set -e
FORCE=${FORCE:-0}
cd "$(dirname "$0")"
HERE=$(pwd)
CJ=${1:-$HOME/cjitter}
[ -d "$CJ/c" ] || { echo "no cjitter checkout at $CJ" >&2; exit 1; }
BUILD=$(mktemp -d "${TMPDIR:-/tmp}/cjsweep.XXXXXX")
trap 'rm -rf "$BUILD"' EXIT
mkdir -p "$BUILD/example/erd"
ln -sfn "$CJ/c" "$BUILD/c"
ln -sfn "$CJ/example/erd/erd.c" "$BUILD/example/erd/erd.c"
cp sweep_main.c "$BUILD/"

OUT=$BUILD/results.csv
: > "$OUT"
for h in pair03 pair04 pair06 pair07 pair12 pair13 pair14 pair15; do
    n=${h#pair}
    cp "$HERE/$h.h" "$BUILD/example/erd/erd_data.h"
    ( cd "$BUILD" && cc -std=c99 -ffp-contract=off -O2 -DPAIR_ID=$n \
        sweep_main.c c/cjitter.c c/rng.c -lm -o sweep_bin )
    echo "== $h $(date +%H:%M:%S)" >&2
    "$BUILD/sweep_bin" >> "$OUT"
done
echo "sweep done $(date +%H:%M:%S)" >&2

# Never clobber the record on a whim: if results.csv exists, reproduce and compare.
# A byte-for-byte match is the check that licenses trusting a later arm against it.
if [ -f results.csv ] && [ "$FORCE" != 1 ]; then
    if diff -q "$OUT" results.csv >/dev/null; then
        echo "results.csv reproduces byte for byte; leaving it alone" >&2
    else
        cp "$OUT" results.csv.new
        echo "MISMATCH against the existing results.csv. Wrote results.csv.new; diff them." >&2
        exit 2
    fi
else
    cp "$OUT" results.csv
fi
wc -l results.csv >&2
