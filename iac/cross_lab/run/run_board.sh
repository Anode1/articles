#!/bin/bash
# One board-arm attempt on one instance: N seats, one shared checkout, an
# iac room for coordination. HOMO = same model three times; HETERO = one
# model per lab (a non-claude seat needs its vendor CLI on PATH; until the
# keys exist this runs claude-only).
#   run/run_board.sh <instance_id> <model1,model2,model3> [max_turns_per_seat]
# Archives: collective patch (git diff of the shared tree), per-seat cost
# JSON, and the room log, under runs/board/<id>/<stamp>/.
set -euo pipefail

ID=$1; MODELS=$2; TURNS=${3:-80}
HERE=$(cd "$(dirname "$0")" && pwd)
TASKS=$HERE/../harvest/tasks.json
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT=$HERE/../runs/board/$ID/$STAMP
WORK=${CROSS_LAB_WORK:-/tmp/cross_lab_work}/board-$ID-$STAMP
ROOM=$WORK/room
IAC=${IAC_BIN:-$HOME/iac/iac}

read -r REPO COMMIT < <(python3 - "$ID" "$TASKS" <<'EOF'
import json, sys
t = next(t for t in json.load(open(sys.argv[2])) if t["instance_id"] == sys.argv[1])
print(t["repo"], t["base_commit"])
EOF
)

mkdir -p "$OUT" "$WORK/repo" "$ROOM"
python3 - "$ID" "$TASKS" > "$WORK/PROBLEM.md" <<'EOF'
import json, sys
t = next(t for t in json.load(open(sys.argv[2])) if t["instance_id"] == sys.argv[1])
print(t["problem_statement"])
EOF

git -C "$WORK/repo" init -q
git -C "$WORK/repo" remote add origin "https://github.com/$REPO.git"
git -C "$WORK/repo" fetch -q --depth 1 origin "$COMMIT"
git -C "$WORK/repo" checkout -q FETCH_HEAD

SEATS=$(echo "$MODELS" | tr ',' '\n' | awk '{print "seat" NR "-" $0}')

cat > "$ROOM/BRIEF.md" <<EOF
# BRIEF: fix one issue, as a team of three

Seats: $(echo $SEATS | tr '\n' ' '). Your name and model are in your prompt.
The issue: $WORK/PROBLEM.md. The shared checkout you all edit: $WORK/repo.
The board room (use the full path in every command): $ROOM

Protocol, in order:
1. $IAC join $ROOM <your name>
2. Read the issue. Investigate the repo. Before reading any board message,
   post your own diagnosis: $IAC send $ROOM '*' "[<name>] DIAGNOSIS: ..."
   (this is what makes three seats worth more than one)
3. $IAC drain $ROOM <your name>   then discuss: agree who edits which file.
   Claim before editing: $IAC send $ROOM '*' "[<name>] CLAIM: <path>"
   Never edit a file another seat has claimed and not released.
4. Edit the shared checkout. Run tests if the repo allows it.
5. When your part is in: $IAC send $ROOM '*' "[<name>] DONE: <what you did>"
6. Wait for others: $IAC recv $ROOM <your name> 120
   Exit 1 means timeout: run the same recv again, at most 4 times total,
   then post your final state and finish. Exit 0 means a message: act on
   it and return to this step. When all three have posted DONE, finish.

Every message under 60 words, prefixed [<name>]. Do not create new test
files. Do not commit. Disagreement is data: post it, do not silently
overwrite another seat's edit.
EOF

i=0
PIDS=""
for SEAT in $SEATS; do
    i=$((i+1))
    MODEL=$(echo "$MODELS" | cut -d, -f$i)
    STREAMS=/media/vas/kuldata/iac/streams/board-$ID-$STAMP
    mkdir -p "$STREAMS"
    IAC_FROM=$SEAT claude -p "You are $SEAT (model $MODEL), one of three seats fixing one issue together over an iac message board. Read $ROOM/BRIEF.md and follow it exactly. Your name: $SEAT" \
      --model "$MODEL" --max-turns "$TURNS" \
      --allowedTools "Read" "Glob" "Grep" "Edit" "Write" "Bash" \
      --verbose --output-format stream-json > "$STREAMS/$SEAT.stream.jsonl" 2> "$OUT/$SEAT.stderr" &
    PIDS="$PIDS $!"
done
wait $PIDS || true

for SEAT in $SEATS; do
    python3 - "/media/vas/kuldata/iac/streams/board-$ID-$STAMP/$SEAT.stream.jsonl" > "$OUT/$SEAT.json" <<'EOF' || true
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
done
echo "/media/vas/kuldata/iac/streams/board-$ID-$STAMP" > "$OUT/streams.path"
git -C "$WORK/repo" diff > "$OUT/patch.diff"
cp "$ROOM/BRIEF.md" "$OUT/BRIEF.md"
$IAC log "$ROOM" > "$OUT/room-log.txt" 2>/dev/null || true
python3 - "$OUT" <<'EOF' > "$OUT/meta.json"
import glob, json, sys
out = sys.argv[1]
seats = {}
total = 0.0
for p in sorted(glob.glob(out + "/seat*.json")):
    name = p.split("/")[-1][:-5]
    try:
        d = json.load(open(p))
    except Exception:
        seats[name] = {"error": "unparseable"}
        continue
    c = d.get("total_cost_usd") or 0
    total += c
    seats[name] = {"subtype": d.get("subtype"), "num_turns": d.get("num_turns"),
                   "cost_usd": round(c, 4),
                   "duration_s": round((d.get("duration_ms") or 0) / 1000)}
json.dump({"seats": seats, "total_cost_usd": round(total, 4)}, sys.stdout, indent=1)
EOF
echo "$ID [$MODELS]: $(wc -l < "$OUT/patch.diff") diff lines, $(python3 -c "import json;print(json.load(open('$OUT/meta.json'))['total_cost_usd'])") USD -> $OUT"
