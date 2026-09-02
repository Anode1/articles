#!/bin/bash
# Batched evaluation of screening patches on a space-limited root disk.
# Evaluates already-pulled instance images first, removes each batch's
# images after scoring, then pulls the rest in chunks. Reruns resume:
# the harness skips instances already scored under the same run_id.
#   run/eval_batched.sh [chunk_size]
set -uo pipefail

CHUNK=${1:-6}
HERE=$(cd "$(dirname "$0")" && pwd)
CL=$HERE/..
E=$HOME/.local/share/cross_lab/evals/screen-sonnet
VENVPY=$HOME/.local/share/cross_lab/venv/bin/python
RUN_ID=screen-sonnet
MIN_FREE_G=6
mkdir -p "$E"

python3 - "$CL" "$E" <<'EOF'
import glob, json, os, sys
cl, e = sys.argv[1], sys.argv[2]
with open(os.path.join(e, "preds.jsonl"), "w") as f:
    for idd in json.load(open(os.path.join(cl, "harvest/residual.json")))["residual"]:
        runs = sorted(glob.glob(os.path.join(cl, "runs/solo", idd, "*")))
        if not runs:
            continue
        patch = open(os.path.join(runs[-1], "patch.diff")).read()
        if patch.strip():
            f.write(json.dumps({"instance_id": idd,
                                "model_name_or_path": "solo-screen",
                                "model_patch": patch}) + "\n")
EOF

ALL=$(python3 -c "
import json
print(' '.join(json.loads(l)['instance_id'] for l in open('$E/preds.jsonl')))")
PULLED=$(docker images --format '{{.Repository}}' | grep '^swebench/sweb.eval' \
         | sed 's/.*x86_64\.//; s/_1776_/__/' || true)

ordered=""
for id in $ALL; do echo "$PULLED" | grep -qx "$id" && ordered="$ordered $id"; done
for id in $ALL; do echo "$PULLED" | grep -qx "$id" || ordered="$ordered $id"; done

batch=""
n=0
run_batch() {
    [ -z "$batch" ] && return 0
    free=$(df --output=avail -BG / | tail -1 | tr -dc 0-9)
    if [ "$free" -lt $MIN_FREE_G ]; then
        echo "!! only ${free}G free on /, aborting before batch:$batch"
        exit 1
    fi
    echo "== evaluating:$batch"
    (cd "$E" && $VENVPY -m swebench.harness.run_evaluation \
        --dataset_name SWE-bench/SWE-bench_Verified \
        --predictions_path "$E/preds.jsonl" \
        --instance_ids $batch --run_id "$RUN_ID" --max_workers 2)
    for id in $batch; do
        docker rmi "swebench/sweb.eval.x86_64.$(echo "$id" | sed 's/__/_1776_/'):latest" 2>/dev/null
    done
    docker container prune -f >/dev/null
    batch=""
    n=0
}
for id in $ordered; do
    batch="$batch $id"
    n=$((n+1))
    [ "$n" -ge "$CHUNK" ] && run_batch
done
run_batch

python3 - "$CL" "$E" <<'EOF'
import glob, json, os, sys
cl, e = sys.argv[1], sys.argv[2]
out = open(os.path.join(cl, "runs/screen.tsv"), "w")
out.write("instance_id\tverdict\tcost_usd\n")
solved = 0
for idd in json.load(open(os.path.join(cl, "harvest/residual.json")))["residual"]:
    runs = sorted(glob.glob(os.path.join(cl, "runs/solo", idd, "*")))
    rep = glob.glob(os.path.join(e, "logs/run_evaluation/screen-sonnet/solo-screen", idd, "report.json"))
    verdict, cost = "no_attempt", ""
    if runs:
        cost = json.load(open(os.path.join(runs[-1], "meta.json"))).get("total_cost_usd")
        local = os.path.join(runs[-1], "report.json")
        r = [local] if os.path.exists(local) else rep
        verdict = "not_scored"
        if r:
            verdict = "RESOLVED" if json.load(open(r[0]))[idd]["resolved"] else "unresolved"
            if rep and not os.path.exists(local):
                json.dump(json.load(open(rep[0])), open(local, "w"), indent=1)
    solved += verdict == "RESOLVED"
    out.write(f"{idd}\t{verdict}\t{cost}\n")
out.close()
print(open(os.path.join(cl, "runs/screen.tsv")).read())
print(f"RESOLVED by solo screen: {solved} of 37; survivors: {37 - solved}")
EOF
