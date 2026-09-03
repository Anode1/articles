#!/bin/bash
# One board-arm attempt on one instance: N seats, one shared checkout, an
# iac room for coordination. HOMO = same model three times; HETERO = one
# model per lab (a non-claude seat needs its vendor CLI on PATH; until the
# keys exist this runs claude-only).
#   run/run_board.sh <instance_id> <model1,model2,model3> [max_turns_per_seat] [standard|subtractive|threshold]
# The fourth argument selects the brief; non-standard runs land in runs/board-<variant>/.
# threshold: every post goes through $ROOM/post, which holds any claim rated
# under CROSS_LAB_TAU (0-100, default 0) and posts a PASS line instead.
# Archives: collective patch (git diff of the shared tree), per-seat cost
# JSON, and the room log, under runs/board/<id>/<stamp>/.
set -euo pipefail

ID=$1; MODELS=$2; TURNS=${3:-80}; VARIANT=${4:-standard}
HERE=$(cd "$(dirname "$0")" && pwd)
TASKS=$HERE/../harvest/tasks.json
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT=$HERE/../runs/board$([ "$VARIANT" = standard ] || echo "-$VARIANT")/$ID/$STAMP
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

if [ "$VARIANT" = standard ]; then
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
6. Wait for others: $IAC recv $ROOM <your name> 120 -a -e 300
   Exit 0: one or more messages arrived, act on them, return here.
   Exit 1: timeout, run the same recv again, at most 4 times total,
   then post your final state and finish.
   Exit 3: you are alone, the other seats are gone; post your final
   state and finish. When all three have posted DONE, finish.

Every message under 60 words, prefixed [<name>]. Do not create new test
files. Do not commit. Disagreement is data: post it, do not silently
overwrite another seat's edit.
EOF
elif [ "$VARIANT" = threshold ]; then
TAU=${CROSS_LAB_TAU:-0}
cat > "$ROOM/post" <<EOF
#!/bin/bash
# post <name> <KIND> <conf 0-100> <text...>   every board message goes through here
NAME=\$1; KIND=\$2; CONF=\$3; shift 3; TEXT="\$*"
case "\$CONF" in ''|*[!0-9]*) echo "conf must be an integer 0-100"; exit 2;; esac
if [ "\$KIND" != CLAIM ] && [ "\$CONF" -lt $TAU ]; then
  printf '%s\t%s\t%s\t%s\theld\t%s\n' "\$(date -u +%FT%TZ)" "\$NAME" "\$KIND" "\$CONF" "\$TEXT" >> $ROOM/claims.tsv
  $IAC send $ROOM '*' "[\$NAME] PASS: \$KIND withheld, conf=\$CONF under $TAU. Another seat continues."
  echo "held: conf \$CONF is under $TAU. If this was DONE, revert your edit. Get a receipt that raises it, or recv."
  exit 0
fi
printf '%s\t%s\t%s\t%s\tposted\t%s\n' "\$(date -u +%FT%TZ)" "\$NAME" "\$KIND" "\$CONF" "\$TEXT" >> $ROOM/claims.tsv
$IAC send $ROOM '*' "[\$NAME] \$KIND (conf=\$CONF): \$TEXT"
EOF
chmod +x "$ROOM/post"; : > "$ROOM/claims.tsv"
cat > "$ROOM/BRIEF.md" <<EOF
# BRIEF: fix one issue, as a team of three, posting only what you are sure of

Seats: $(echo $SEATS | tr '\n' ' '). Your name and model are in your prompt.
The issue: $WORK/PROBLEM.md. The shared checkout you all edit: $WORK/repo.
The board room (use the full path in every command): $ROOM

Every board message is posted with one command and carries your confidence:
    $ROOM/post <your name> <KIND> <conf> "<text under 60 words>"
conf is an integer 0 to 100: the probability that the claim survives a
peer running a command against it. 100 means you ran it and saw the output.
A claim you have not executed is at most 60. The board holds any message
rated under $TAU and posts a PASS line in its place; a PASS costs nothing,
a wrong claim costs the team the run. After a held post: run the thing and
post again with the receipt, or wait and let another seat continue. A held
DONE means your edit is not trusted: revert it (git checkout -- <file>).

Protocol, in order:
1. $IAC join $ROOM <your name>
2. Read the issue. Investigate the repo. Before reading any board message,
   post your own diagnosis: post <name> DIAGNOSIS <conf> "<cause, file>"
3. $IAC drain $ROOM <your name>   then agree who edits which file.
   Claim before editing: post <name> CLAIM 100 "<path>"  (CLAIM is never held)
   Never edit a file another seat has claimed and not released.
4. Edit the shared checkout. Run tests if the repo allows it.
5. When your part is in: post <name> DONE <conf> "<file>: <what you ran and what it printed>"
6. Wait for others: $IAC recv $ROOM <your name> 120 -a -e 300
   Exit 0: one or more messages arrived, act on them, return here.
   Exit 1: timeout, run the same recv again, at most 4 times total,
   then post your final state and finish.
   Exit 3: you are alone, the other seats are gone; post your final
   state and finish. When all three have posted DONE or PASS, finish.

Other kinds: REPRO, VETO (with the output that shows an edit wrong), NOTE.
Do not use $IAC send directly. Do not create new test files. Do not commit.
Disagreement is data: post it, do not silently overwrite another seat's edit.
EOF
else
cat > "$ROOM/BRIEF.md" <<EOF
# BRIEF: fix one issue, as a team of three, by subtraction

Seats: $(echo $SEATS | tr '\n' ' '). Your name and model are in your prompt.
The issue: $WORK/PROBLEM.md. The shared checkout you all edit: $WORK/repo.
The board room (use the full path in every command): $ROOM

The rule this team runs on: a wrong addition costs more than a missing
one. Nothing enters the shared tree without a receipt, and the team's
last act is removal.

Protocol, in order:
1. $IAC join $ROOM <your name>
2. Reproduce the issue before anything else: a command or short script
   that shows the failure on the unmodified tree. Post its output:
   $IAC send $ROOM '*' "[<name>] REPRO: <command> -> <what it printed>"
   Post before reading any board message. No repro, no diagnosis.
3. Post the smallest change you believe fixes the repro, as one file and
   one hunk if possible: $IAC send $ROOM '*' "[<name>] PROPOSAL: <file>: <change>"
   Then $IAC drain $ROOM <your name> and read the others.
4. Claim before editing: $IAC send $ROOM '*' "[<name>] CLAIM: <path>".
   Edit only the file you claimed. Never edit, add or delete a test.
   Never touch a file that is not in your own proposal.
5. Any seat may veto any edit, its own included, with a receipt:
   $IAC send $ROOM '*' "[<name>] VETO: <file>: <the repro output that shows it unnecessary or harmful>"
   The author of a vetoed edit reverts it (git checkout -- <file>) and says so.
6. When your change is in and the repro passes, post the receipt:
   $IAC send $ROOM '*' "[<name>] DONE: <file>: repro now prints <output>"
7. seat1 is the integrator and finishes by subtraction: run the repro on
   the final tree, list every modified file (git status --short), and
   revert anything the repro does not need. Post:
   $IAC send $ROOM '*' "[seat1] FINAL: <files kept> <files reverted> <repro output>"
8. Wait for others: $IAC recv $ROOM <your name> 120 -a -e 300
   Exit 0: messages arrived, act on them, return here.
   Exit 1: timeout, run the same recv again, at most 4 times total.
   Exit 3: you are alone; finish.

Every message under 60 words, prefixed [<name>]. Do not commit.
EOF
fi

i=0
PIDS=""
for SEAT in $SEATS; do
    i=$((i+1))
    MODEL=$(echo "$MODELS" | cut -d, -f$i)
    STREAMS=$HOME/.local/share/cross_lab/streams/board-$ID-$STAMP
    mkdir -p "$STREAMS"
    (cd "$WORK/repo" && APPORT_REPORT_DIR=/tmp/cross_lab_apport IAC_FROM=$SEAT claude -p "You are $SEAT (model $MODEL), one of three seats fixing one issue together over an iac message board. Read $ROOM/BRIEF.md and follow it exactly. Your name: $SEAT" \
      --model "$MODEL" --max-turns "$TURNS" \
      --allowedTools "Read" "Glob" "Grep" "Edit" "Write" "Bash" \
      --verbose --output-format stream-json > "$STREAMS/$SEAT.stream.jsonl" 2> "$OUT/$SEAT.stderr") &
    PIDS="$PIDS $!"
done
wait $PIDS || true

for SEAT in $SEATS; do
    python3 - "$HOME/.local/share/cross_lab/streams/board-$ID-$STAMP/$SEAT.stream.jsonl" > "$OUT/$SEAT.json" <<'EOF' || true
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
echo "$HOME/.local/share/cross_lab/streams/board-$ID-$STAMP" > "$OUT/streams.path"
git -C "$HOME/iac" rev-parse --short HEAD > "$OUT/iac.rev" 2>/dev/null || true
git -C "$WORK/repo" diff > "$OUT/patch.diff"
cp "$ROOM/BRIEF.md" "$OUT/BRIEF.md"
echo "$VARIANT" > "$OUT/brief.variant"
if [ "$VARIANT" = threshold ]; then echo "$TAU" > "$OUT/tau"; cp "$ROOM/claims.tsv" "$OUT/claims.tsv"; fi
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
