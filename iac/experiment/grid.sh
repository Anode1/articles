#!/bin/sh
# grid.sh: the poll-cost grid for Section 5.
# Warm cache throughout; the three cells of one context size run back to back so the
# prefix is written once and read by every later poll.  The p=360 cell polls at six-minute
# gaps, past the nominal five-minute cache lifetime; on 2026-11-02 the entry was still read
# at that gap; the 600 s and 900 s probes in grid/ put the expiry between 6 and 10 minutes.
# Key: ANTHROPIC_API_KEY, or ~/.config/anthropic/api_key.  Validate first:
#   python3 tokenbill.py --fast --model claude-fable-5-1
#
#   MODEL=claude-fable-5-1 REP=1 sh grid.sh      (about 14 USD at list, one hour)
set -eu
MODEL=${MODEL:-claude-fable-5-1}; REP=${REP:-1}; DUR=${DUR:-1200}
export TB_MAX_TOKENS=16
mkdir -p grid
chain() {  # $1 = context tokens; three poll intervals, DUR seconds each
  C=$1
  for P in 10 30 120; do
    python3 tokenbill.py --yes --mode warm --model "$MODEL" --context-tokens $C \
      --interval $P --duration $DUR --max-usd 8 \
      --out "grid/${MODEL}_C${C}_p${P}_r${REP}.json" > "grid/${MODEL}_C${C}_p${P}_r${REP}.log" 2>&1
  done
}
chain 10000 &
chain 50000 &
chain 150000 &
python3 tokenbill.py --yes --mode warm --model "$MODEL" --context-tokens 50000 \
  --interval 360 --polls 4 --duration 1440 --max-usd 4 \
  --out "grid/${MODEL}_C50000_p360_r${REP}.json" > "grid/${MODEL}_C50000_p360_r${REP}.log" 2>&1 &
wait
echo "done: $(ls grid/*_r${REP}.json | wc -l) cells"
