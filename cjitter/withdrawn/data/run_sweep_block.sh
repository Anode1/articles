#!/bin/sh
# The pre-registered sweep re-run with cjitter_tuning.block, both arms. Needs pairNN.h from
# extract.py and a cjitter checkout carrying the block parameter (>= 0.10.0), given as $1
# (default ~/cjitter). Arm one is the whole vector and must reproduce results.csv exactly;
# block_analysis.py checks that before reporting anything about arm two.
#
# Builds in a private tree: see the warning in run_sweep.sh about never writing pairNN.h
# over the checkout's tracked, anonymized example/erd/erd_data.h.
set -e
FORCE=${FORCE:-0}
cd "$(dirname "$0")"
HERE=$(pwd)
CJ=${1:-$HOME/cjitter}
[ -d "$CJ/c" ] || { echo "no cjitter checkout at $CJ" >&2; exit 1; }
BUILD=$(mktemp -d "${TMPDIR:-/tmp}/cjblock.XXXXXX")
trap 'rm -rf "$BUILD"' EXIT
mkdir -p "$BUILD/example/erd"
ln -sfn "$CJ/c" "$BUILD/c"
ln -sfn "$CJ/example/erd/erd.c" "$BUILD/example/erd/erd.c"
cp sweep_block.c "$BUILD/"

OUT=$BUILD/block_results.csv
: > "$OUT"
for h in pair03 pair04 pair06 pair07 pair12 pair13 pair14 pair15 pair16; do
    n=${h#pair}
    cp "$HERE/$h.h" "$BUILD/example/erd/erd_data.h"
    ( cd "$BUILD" && cc -std=c99 -ffp-contract=off -O2 -DPAIR_ID=$n \
        sweep_block.c c/cjitter.c c/rng.c -lm -o sweep_bin )
    echo "== $h $(date +%H:%M:%S)" >&2
    "$BUILD/sweep_bin" >> "$OUT"
done

# Never clobber the record on a whim: if block_results.csv exists, reproduce and compare.
# A byte-for-byte match is the check that licenses trusting a later arm against it.
if [ -f block_results.csv ] && [ "$FORCE" != 1 ]; then
    if diff -q "$OUT" block_results.csv >/dev/null; then
        echo "block_results.csv reproduces byte for byte; leaving it alone" >&2
    else
        cp "$OUT" block_results.csv.new
        echo "MISMATCH against the existing block_results.csv. Wrote block_results.csv.new; diff them." >&2
        exit 2
    fi
else
    cp "$OUT" block_results.csv
fi
wc -l block_results.csv >&2
