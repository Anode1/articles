#!/bin/sh
# The pre-registered sweep re-run with cjitter_tuning.block, both arms. Needs pairNN.h from
# extract.py and a cjitter checkout carrying the block parameter (>= 0.10.0) symlinked as c/
# and example/erd/erd.c. Arm one is the whole vector and must reproduce results.csv exactly;
# block_analysis.py checks that before reporting anything about arm two.
set -e
cd "$(dirname "$0")"
: > block_results.csv
for h in pair03 pair04 pair06 pair07 pair12 pair13 pair14 pair15 pair16; do
    n=${h#pair}
    cp "$h.h" example/erd/erd_data.h
    cc -std=c99 -ffp-contract=off -O2 -DPAIR_ID=$n \
       sweep_block.c c/cjitter.c c/rng.c -lm -o sweep_bin
    echo "== $h $(date +%H:%M:%S)" >&2
    ./sweep_bin >> block_results.csv
done
wc -l block_results.csv >&2
