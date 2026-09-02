#!/usr/bin/env python3
"""Phase-1 BOARD arm per PREREGISTRATION.md (signed 2026-09-01).

Per surviving instance: board runs (opus,sonnet,haiku, max-turns 100,
run_board.sh) until one scores resolved or spend reaches B. Each new
patch is scored immediately; the instance image is retired afterwards.
Resumable from the runs tree; attempts before START do not count
(the pilot board run predates the signing and is excluded).
"""
import glob, json, os, shutil, subprocess, sys, datetime

CL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(CL, "run")
E = os.path.expanduser("~/.local/share/cross_lab/evals/phase1")
VENVPY = os.path.expanduser("~/.local/share/cross_lab/venv/bin/python")
B = 3.00
MODELS = "opus,sonnet,haiku"
TURNS = "100"
START = "20260901T210000Z"

def sh(cmd, **kw):
    print("+", cmd, flush=True)
    return subprocess.run(cmd, shell=True, **kw)

def attempts(inst):
    out = []
    for d in sorted(glob.glob(f"{CL}/runs/board/{inst}/*")):
        if os.path.basename(d) < START:
            continue
        try:
            meta = json.load(open(d + "/meta.json"))
        except Exception:
            continue
        resolved = None
        rp = d + "/report.json"
        if os.path.exists(rp):
            try:
                resolved = json.load(open(rp))[inst]["resolved"]
            except Exception:
                resolved = False
        out.append({"dir": d, "cost": meta.get("total_cost_usd") or 0,
                    "resolved": resolved})
    return out

def img(inst):
    return "swebench/sweb.eval.x86_64." + inst.replace("__", "_1776_") + ":latest"

survivors = [l.split("\t")[0] for l in
             open(CL + "/runs/screen.tsv").read().splitlines()[1:]
             if l.split("\t")[1] == "unresolved"]
assert len(survivors) == 18, survivors
os.makedirs(E, exist_ok=True)

for inst in survivors:
    while True:
        ats = attempts(inst)
        if any(a["resolved"] for a in ats):
            break
        if sum(a["cost"] for a in ats) >= B:
            break
        sh(f"{RUN}/run_board.sh {inst} {MODELS} {TURNS}")
        for a in attempts(inst):
            if a["resolved"] is not None:
                continue
            patch = open(a["dir"] + "/patch.diff").read()
            if not patch.strip():
                json.dump({inst: {"resolved": False, "synthetic": "empty patch"}},
                          open(a["dir"] + "/report.json", "w"))
                continue
            stamp = datetime.datetime.utcnow().strftime("%H%M%S")
            run_id = f"p1b-{inst[:24]}-{stamp}"
            pred = f"{E}/preds-{run_id}.jsonl"
            open(pred, "w").write(json.dumps({"instance_id": inst,
                                              "model_name_or_path": "p1-board",
                                              "model_patch": patch}) + "\n")
            sh(f'sg docker -c "{VENVPY} -m swebench.harness.run_evaluation '
               f"--dataset_name SWE-bench/SWE-bench_Verified "
               f"--predictions_path {pred} --instance_ids {inst} "
               f'--run_id {run_id} --max_workers 1"', cwd=E)
            rep = f"{E}/logs/run_evaluation/{run_id}/p1-board/{inst}/report.json"
            if os.path.exists(rep):
                shutil.copy(rep, a["dir"] + "/report.json")
            else:
                json.dump({inst: {"resolved": False, "synthetic": "no harness report"}},
                          open(a["dir"] + "/report.json", "w"))
    sh(f'sg docker -c "docker rmi {img(inst)}" 2>/dev/null')
    sh('sg docker -c "docker container prune -f" >/dev/null')

print("== phase-1 BOARD summary")
for inst in survivors:
    ats = attempts(inst)
    v = "SOLVED" if any(a["resolved"] for a in ats) else \
        f"no({sum(a['cost'] for a in ats):.2f})"
    print(f"{inst}\t{v}\truns={len(ats)}")
