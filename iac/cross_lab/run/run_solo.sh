#!/bin/bash
# One SOLO attempt on one residual instance.
#   run/run_solo.sh <instance_id> <model> [max_turns]
# Clones the repo at base_commit into a scratch workdir, gives the seat the
# problem statement and the tree, nothing else. Archives the patch (git diff),
# the seat's cost JSON, and run metadata under runs/solo/<id>/<utc-stamp>/.
# Evaluation is separate and later; see ../RUNBOOK.md.
set -euo pipefail

ID=$1; MODEL=$2; TURNS=${3:-80}
HERE=$(cd "$(dirname "$0")" && pwd)
TASKS=$HERE/../harvest/tasks.json
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT=$HERE/../runs/solo/$ID/$STAMP
WORK=${CROSS_LAB_WORK:-/tmp/cross_lab_work}/$ID-$STAMP

read -r REPO COMMIT < <(python3 - "$ID" "$TASKS" <<'EOF'
import json, sys
t = next(t for t in json.load(open(sys.argv[2])) if t["instance_id"] == sys.argv[1])
print(t["repo"], t["base_commit"])
EOF
)

mkdir -p "$OUT" "$WORK"
python3 - "$ID" "$TASKS" > "$WORK/PROBLEM.md" <<'EOF'
import json, sys
t = next(t for t in json.load(open(sys.argv[2])) if t["instance_id"] == sys.argv[1])
print(t["problem_statement"])
EOF

git -C "$WORK" init -q
git -C "$WORK" remote add origin "https://github.com/$REPO.git"
git -C "$WORK" fetch -q --depth 1 origin "$COMMIT"
git -C "$WORK" checkout -q FETCH_HEAD

STREAMS=/media/vas/kuldata/iac/streams/solo-$ID-$STAMP
mkdir -p "$STREAMS"
claude -p "You are fixing one issue in the repository at $WORK (checked out at the relevant commit). The issue is in $WORK/PROBLEM.md. Read it, locate the fault, and fix it by editing the repository. Do not create new test files; do not commit. When the fix is in place, stop." \
  --model "$MODEL" --max-turns "$TURNS" \
  --allowedTools "Read" "Glob" "Grep" "Edit" "Write" "Bash" \
  --verbose --output-format stream-json > "$STREAMS/seat.stream.jsonl" 2> "$OUT/seat.stderr" || true
python3 - "$STREAMS/seat.stream.jsonl" > "$OUT/seat.json" <<'EOF' || true
import json, sys
res = {}
for line in open(sys.argv[1]):
    try:
        d = json.loads(line)
    except Exception:
        continue
    if d.get("type") == "result":
        res = d
print(json.dumps(res))
EOF
echo "$STREAMS" > "$OUT/streams.path"

git -C "$WORK" diff > "$OUT/patch.diff"
python3 - "$OUT/seat.json" <<'EOF' > "$OUT/meta.json"
import json, sys
d = json.load(open(sys.argv[1]))
json.dump({"subtype": d.get("subtype"), "num_turns": d.get("num_turns"),
           "total_cost_usd": d.get("total_cost_usd"),
           "duration_s": round((d.get("duration_ms") or 0) / 1000),
           "model_usage_usd": {m: round(v.get("costUSD", 0), 4)
                               for m, v in (d.get("modelUsage") or {}).items()}},
          sys.stdout, indent=1)
EOF
echo "$ID $MODEL: $(wc -l < "$OUT/patch.diff") diff lines, $(python3 -c "import json;print(json.load(open('$OUT/meta.json'))['total_cost_usd'])") USD -> $OUT"
