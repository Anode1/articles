#!/usr/bin/env python3
"""PHASE2.md: the posting threshold tau swept for solves per dollar.
    run/threshold_sweep.py <tau> [<tau>...] [--draws N] [--instances a,b,...]
For each tau and instance, runs the threshold brief (run_board.sh, variant
threshold, CROSS_LAB_TAU=tau) until N scored draws exist under
runs/board-threshold/<instance>/, scoring each by the official harness as
it lands. Resumable from the tree. Rewrites runs/threshold.tsv (one row per
run) and prints solves, dollars and solves per dollar for every tau seen.
"""
import glob, json, os, shutil, subprocess, sys, datetime, collections

CL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(CL, "run")
E = os.path.expanduser("~/.local/share/cross_lab/evals/threshold")
VENVPY = os.path.expanduser("~/.local/share/cross_lab/venv/bin/python")
MODELS = "opus,sonnet,haiku"
TURNS = "100"
DEFAULT = ["sympy__sympy-20916", "matplotlib__matplotlib-23299",
           "sphinx-doc__sphinx-10614", "astropy__astropy-14369",
           "matplotlib__matplotlib-26208"]
TSV = f"{CL}/runs/threshold.tsv"

def sh(cmd, **kw):
    print("+", cmd, flush=True)
    return subprocess.run(cmd, shell=True, **kw)

def img(inst):
    return "swebench/sweb.eval.x86_64." + inst.replace("__", "_1776_") + ":latest"

def runs(inst, tau=None):
    out = []
    for d in sorted(glob.glob(f"{CL}/runs/board-threshold/{inst}/*")):
        if not os.path.exists(d + "/meta.json") or not os.path.exists(d + "/tau"):
            continue
        t = int(open(d + "/tau").read().strip())
        if tau is None or t == tau:
            out.append((d, t))
    return out

def score(inst, d):
    patch = open(d + "/patch.diff").read()
    if not patch.strip():
        json.dump({inst: {"resolved": False, "synthetic": "empty patch"}},
                  open(d + "/report.json", "w"))
        return False
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%H%M%S")
    run_id = f"tau-{inst[:20]}-{stamp}"
    pred = f"{E}/preds-{run_id}.jsonl"
    open(pred, "w").write(json.dumps({"instance_id": inst,
                                      "model_name_or_path": "tau",
                                      "model_patch": patch}) + "\n")
    sh(f'sg docker -c "{VENVPY} -m swebench.harness.run_evaluation '
       f"--dataset_name SWE-bench/SWE-bench_Verified --predictions_path {pred} "
       f'--instance_ids {inst} --run_id {run_id} --max_workers 1"', cwd=E)
    rep = f"{E}/logs/run_evaluation/{run_id}/tau/{inst}/report.json"
    if os.path.exists(rep):
        shutil.copy(rep, d + "/report.json")
        return json.load(open(rep))[inst]["resolved"]
    json.dump({inst: {"resolved": False, "synthetic": "no harness report"}},
              open(d + "/report.json", "w"))
    return False

def row(inst, d, tau):
    if os.path.exists(d + "/report.json"):
        r = json.load(open(d + "/report.json"))[inst]["resolved"]
    else:
        r = score(inst, d)
    cost = json.load(open(d + "/meta.json")).get("total_cost_usd") or 0
    posted = held = 0; confs = []
    for line in open(d + "/claims.tsv"):
        f = line.rstrip("\n").split("\t")
        if len(f) < 5:
            continue
        if f[2] != "CLAIM":
            confs.append(int(f[3]))
        if f[4] == "held":
            held += 1
        else:
            posted += 1
    log = open(d + "/room-log.txt").read() if os.path.exists(d + "/room-log.txt") else ""
    bypass = sum(1 for l in log.splitlines()
                 if l.startswith("[seat") and "(conf=" not in l and "] PASS:" not in l)
    mean = round(sum(confs) / len(confs), 1) if confs else 0
    return (tau, inst, os.path.basename(d), "RESOLVED" if r else "unresolved",
            round(cost, 2), posted, held, bypass, mean)

def write_table(rows):
    rows.sort()
    with open(TSV, "w") as f:
        f.write("tau\tinstance\trun\tverdict\tcost\tposted\theld\tbypass\tmean_conf\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    agg = collections.defaultdict(lambda: [0, 0, 0.0, 0, 0])
    for tau, _, _, v, cost, posted, held, bypass, _ in rows:
        a = agg[tau]; a[0] += 1; a[1] += v == "RESOLVED"; a[2] += cost; a[3] += held; a[4] += bypass
    print("tau  runs  solved  dollars  solves/$  held  bypass")
    for tau in sorted(agg):
        n, s, c, h, b = agg[tau]
        print(f"{tau:>3}  {n:>4}  {s:>6}  {c:>7.2f}  {s / c if c else 0:>8.3f}  {h:>4}  {b:>6}")

args = sys.argv[1:]
draws = 1; insts = DEFAULT; taus = []
while args:
    a = args.pop(0)
    if a == "--draws": draws = int(args.pop(0))
    elif a == "--instances": insts = args.pop(0).split(",")
    else: taus.append(int(a))
os.makedirs(E, exist_ok=True)
rows = []
for inst in insts:
    for tau in taus:
        while len(runs(inst, tau)) < draws:
            sh(f"CROSS_LAB_TAU={tau} {RUN}/run_board.sh {inst} {MODELS} {TURNS} threshold")
        for d, t in runs(inst, tau):
            rows.append(row(inst, d, t))
    if taus:
        sh(f'sg docker -c "docker rmi {img(inst)}" 2>/dev/null')
        sh('sg docker -c "docker container prune -f" >/dev/null')
# every run in the tree is tabulated, whatever tau it was made at
seen = {(r[1], r[2]) for r in rows}
for inst in sorted(set(insts) | {os.path.basename(p) for p in glob.glob(f"{CL}/runs/board-threshold/*")}):
    for d, t in runs(inst):
        if (inst, os.path.basename(d)) not in seen:
            rows.append(row(inst, d, t))
write_table(rows)
