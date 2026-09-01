#!/bin/bash
# SOLO screening of the harvested residual set.
# Phase 1: one sonnet attempt per instance (run_solo.sh). Phase 2: one
# harness evaluation over all produced patches. Instances a current solo
# seat resolves leave the experiment population; the survivors are the
# real residual. Verdicts land in runs/screen.tsv, logs on external_data.
#   run/screen.sh [model] [max_turns]
set -uo pipefail

MODEL=${1:-sonnet}; TURNS=${2:-60}
HERE=$(cd "$(dirname "$0")" && pwd)
CL=$HERE/..
E=/media/vas/kuldata/iac/evals/screen-$MODEL
VENVPY=/media/vas/kuldata/iac/venv/bin/python
mkdir -p "$E"

for ID in $(python3 -c "import json; print('\n'.join(json.load(open('$CL/harvest/residual.json'))['residual']))"); do
    if ls "$CL/runs/solo/$ID"/*/patch.diff >/dev/null 2>&1; then
        echo "== $ID: attempt exists, skipping generation"
    else
        echo "== $ID: generating"
        "$HERE/run_solo.sh" "$ID" "$MODEL" "$TURNS" || echo "== $ID: generation FAILED"
    fi
done

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

cd "$E"
sg docker -c "$VENVPY -m swebench.harness.run_evaluation \
  --dataset_name SWE-bench/SWE-bench_Verified \
  --predictions_path preds.jsonl \
  --run_id screen-$MODEL --max_workers 2"

python3 - "$CL" "$E" "$MODEL" <<'EOF'
import glob, json, os, sys
cl, e, model = sys.argv[1], sys.argv[2], sys.argv[3]
out = open(os.path.join(cl, "runs/screen.tsv"), "w")
out.write("instance_id\tverdict\tcost_usd\n")
for idd in json.load(open(os.path.join(cl, "harvest/residual.json")))["residual"]:
    runs = sorted(glob.glob(os.path.join(cl, "runs/solo", idd, "*")))
    rep = glob.glob(os.path.join(e, "logs/run_evaluation", "screen-" + model,
                                 "solo-screen", idd, "report.json"))
    verdict = "no_attempt"
    cost = ""
    if runs:
        meta = json.load(open(os.path.join(runs[-1], "meta.json")))
        cost = meta.get("total_cost_usd")
        verdict = "empty_patch"
        r = glob.glob(os.path.join(runs[-1], "report.json")) or rep
        if r:
            verdict = "RESOLVED" if json.load(open(r[0]))[idd]["resolved"] else "unresolved"
            if rep and not os.path.exists(os.path.join(runs[-1], "report.json")):
                json.dump(json.load(open(rep[0])), open(os.path.join(runs[-1], "report.json"), "w"), indent=1)
    out.write(f"{idd}\t{verdict}\t{cost}\n")
print(open(os.path.join(cl, "runs/screen.tsv")).read())
EOF
