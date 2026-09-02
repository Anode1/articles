#!/usr/bin/env python3
"""Phase-1 SOLO arms per PREREGISTRATION.md (signed 2026-09-01).

For each surviving instance and each model in the lineup: fresh attempts
until one scores resolved or spend reaches B. Instances processed in
groups so instance images fit the root disk; images retired per group.
Resumable: state is recomputed from runs/solo/*/*/meta.json+report.json.
Attempts timestamped before START are selection/pilots and do not count.
"""
import glob, json, os, shutil, subprocess, sys, datetime

CL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(CL, "run")
E = os.path.expanduser("~/.local/share/cross_lab/evals/phase1")
VENVPY = os.path.expanduser("~/.local/share/cross_lab/venv/bin/python")
B = 3.00
MODELS = ["haiku", "sonnet", "opus", "fable"]
GROUP = 6
TURNS = "60"
START = "20260901T210000Z"
MODELKEY = {"claude-haiku": "haiku", "claude-sonnet": "sonnet",
            "claude-opus": "opus", "claude-fable": "fable"}

def sh(cmd, **kw):
    print("+", cmd, flush=True)
    return subprocess.run(cmd, shell=True, **kw)

def attempt_model(meta):
    mu = meta.get("model_usage_usd") or {}
    if not mu:
        return None
    top = max(mu, key=mu.get)
    for pref, m in MODELKEY.items():
        if top.startswith(pref):
            return m
    return None

def attempts(inst):
    out = []
    for d in sorted(glob.glob(f"{CL}/runs/solo/{inst}/*")):
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
        out.append({"dir": d, "model": attempt_model(meta),
                    "cost": meta.get("total_cost_usd") or 0, "resolved": resolved})
    return out

def img(inst):
    return "swebench/sweb.eval.x86_64." + inst.replace("__", "_1776_") + ":latest"

survivors = [l.split("\t")[0] for l in
             open(CL + "/runs/screen.tsv").read().splitlines()[1:]
             if l.split("\t")[1] == "unresolved"]
assert len(survivors) == 18, survivors
os.makedirs(E, exist_ok=True)

for gi in range(0, len(survivors), GROUP):
    group = survivors[gi:gi + GROUP]
    print(f"== group {gi//GROUP + 1}: {group}", flush=True)
    round_no = 0
    while True:
        round_no += 1
        gen = []
        for inst in group:
            for m in MODELS:
                ats = [a for a in attempts(inst) if a["model"] == m]
                if any(a["resolved"] for a in ats):
                    continue
                if sum(a["cost"] for a in ats) >= B:
                    continue
                gen.append((inst, m))
        if not gen:
            break
        print(f"== round {round_no}: {len(gen)} attempts", flush=True)
        for inst, m in gen:
            sh(f"{RUN}/run_solo.sh {inst} {m} {TURNS}")
        stamp = datetime.datetime.utcnow().strftime("%H%M%S")
        for m in MODELS:
            rows = []
            for inst in group:
                ats = [a for a in attempts(inst)
                       if a["model"] == m and a["resolved"] is None]
                for a in ats:
                    patch = open(a["dir"] + "/patch.diff").read()
                    if patch.strip():
                        rows.append((inst, a["dir"], patch))
                    else:
                        json.dump({inst: {"resolved": False, "synthetic": "empty patch"}},
                                  open(a["dir"] + "/report.json", "w"))
            if not rows:
                continue
            run_id = f"p1-{m}-g{gi//GROUP+1}r{round_no}-{stamp}"
            pred = f"{E}/preds-{run_id}.jsonl"
            with open(pred, "w") as f:
                for inst, _, patch in rows:
                    f.write(json.dumps({"instance_id": inst,
                                        "model_name_or_path": "p1-" + m,
                                        "model_patch": patch}) + "\n")
            ids = " ".join(i for i, _, _ in rows)
            sh(f'sg docker -c "{VENVPY} -m swebench.harness.run_evaluation '
               f"--dataset_name SWE-bench/SWE-bench_Verified "
               f"--predictions_path {pred} --instance_ids {ids} "
               f'--run_id {run_id} --max_workers 2"', cwd=E)
            for inst, d, _ in rows:
                rep = f"{E}/logs/run_evaluation/{run_id}/p1-{m}/{inst}/report.json"
                if os.path.exists(rep):
                    shutil.copy(rep, d + "/report.json")
                else:
                    json.dump({inst: {"resolved": False, "synthetic": "no harness report"}},
                              open(d + "/report.json", "w"))
    for inst in group:
        sh(f'sg docker -c "docker rmi {img(inst)}" 2>/dev/null')
    sh('sg docker -c "docker container prune -f" >/dev/null')

print("== phase-1 SOLO summary")
print("instance\t" + "\t".join(MODELS))
for inst in survivors:
    row = [inst]
    for m in MODELS:
        ats = [a for a in attempts(inst) if a["model"] == m]
        if any(a["resolved"] for a in ats):
            row.append("SOLVED")
        else:
            row.append(f"no({sum(a['cost'] for a in ats):.2f})")
    print("\t".join(row))
