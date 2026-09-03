#!/usr/bin/env python3
"""PREDICTIONS.md item 7: the subtractive brief against the standard brief
on the five instances the phase-1 board lost. One run per brief per
instance, each scored immediately by the official harness. Standard runs
land in runs/board/, subtractive in runs/board-subtractive/; both carry a
brief.variant file. Verdicts to runs/norm_test.tsv.
"""
import glob, json, os, shutil, subprocess, datetime

CL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(CL, "run")
E = os.path.expanduser("~/.local/share/cross_lab/evals/norm_test")
VENVPY = os.path.expanduser("~/.local/share/cross_lab/venv/bin/python")
MODELS = "opus,sonnet,haiku"
TURNS = "100"
LOSSES = ["sympy__sympy-20916", "matplotlib__matplotlib-23299",
          "sphinx-doc__sphinx-10614", "astropy__astropy-14369",
          "matplotlib__matplotlib-26208"]
START = "20260903T"

def sh(cmd, **kw):
    print("+", cmd, flush=True)
    return subprocess.run(cmd, shell=True, **kw)

def img(inst):
    return "swebench/sweb.eval.x86_64." + inst.replace("__", "_1776_") + ":latest"

def newest_run(inst, variant):
    base = "board" if variant == "standard" else "board-" + variant
    runs = sorted(d for d in glob.glob(f"{CL}/runs/{base}/{inst}/*")
                  if os.path.basename(d) >= START)
    return runs[-1] if runs else None

def score(inst, d):
    patch = open(d + "/patch.diff").read()
    if not patch.strip():
        json.dump({inst: {"resolved": False, "synthetic": "empty patch"}},
                  open(d + "/report.json", "w"))
        return False
    stamp = datetime.datetime.utcnow().strftime("%H%M%S")
    run_id = f"norm-{inst[:20]}-{stamp}"
    pred = f"{E}/preds-{run_id}.jsonl"
    open(pred, "w").write(json.dumps({"instance_id": inst,
                                      "model_name_or_path": "norm",
                                      "model_patch": patch}) + "\n")
    sh(f'sg docker -c "{VENVPY} -m swebench.harness.run_evaluation '
       f"--dataset_name SWE-bench/SWE-bench_Verified --predictions_path {pred} "
       f'--instance_ids {inst} --run_id {run_id} --max_workers 1"', cwd=E)
    rep = f"{E}/logs/run_evaluation/{run_id}/norm/{inst}/report.json"
    if os.path.exists(rep):
        shutil.copy(rep, d + "/report.json")
        return json.load(open(rep))[inst]["resolved"]
    json.dump({inst: {"resolved": False, "synthetic": "no harness report"}},
              open(d + "/report.json", "w"))
    return False

os.makedirs(E, exist_ok=True)
results = {}
for inst in LOSSES:
    for variant in ("standard", "subtractive"):
        d = newest_run(inst, variant)
        if d is None or not os.path.exists(d + "/meta.json"):
            sh(f"{RUN}/run_board.sh {inst} {MODELS} {TURNS} {variant}")
            d = newest_run(inst, variant)
        if d is None:
            results[(inst, variant)] = ("no_run", 0)
            continue
        if os.path.exists(d + "/report.json"):
            r = json.load(open(d + "/report.json"))[inst]["resolved"]
        else:
            r = score(inst, d)
        cost = (json.load(open(d + "/meta.json")).get("total_cost_usd") or 0)
        results[(inst, variant)] = ("RESOLVED" if r else "unresolved", cost)
    sh(f'sg docker -c "docker rmi {img(inst)}" 2>/dev/null')
    sh('sg docker -c "docker container prune -f" >/dev/null')

with open(f"{CL}/runs/norm_test.tsv", "w") as f:
    f.write("instance\tstandard\tcost\tsubtractive\tcost\n")
    for inst in LOSSES:
        s, sc = results[(inst, "standard")]; t, tc = results[(inst, "subtractive")]
        f.write(f"{inst}\t{s}\t{sc:.2f}\t{t}\t{tc:.2f}\n")
print(open(f"{CL}/runs/norm_test.tsv").read())
