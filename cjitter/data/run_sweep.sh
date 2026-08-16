#!/bin/sh
set -e
cd "$(dirname "$0")"
: > results.csv
for h in pair03 pair04 pair06 pair07 pair12 pair13 pair14 pair15; do
    n=${h#pair}
    ln -sf "../../$h.h" example/erd/erd_data.h
    cc -std=c99 -ffp-contract=off -O2 -DPAIR_ID=$n \
       sweep_main.c c/cjitter.c c/rng.c -lm -o sweep_bin
    echo "== $h $(date +%H:%M:%S)" >&2
    ./sweep_bin >> results.csv
done
echo "sweep done $(date +%H:%M:%S)" >&2
wc -l results.csv >&2
