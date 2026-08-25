#!/usr/bin/env python3
"""run.py: the site-coverage experiment.

One behavioural change that must land at every site, at four repetition counts
and one factored control. The task text is identical everywhere and names no
command, so locating the sites is part of what is measured. Grading is per site,
not pass or fail: what is recorded is how many of N landed.

  python3 run.py --model claude-sonnet-5 --reps 5 --workers 4
"""
import argparse, json, os, random, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from tasks import TASK
from gen import build, README, CHECK, CMDS
import hidden

CONDITIONS = {"rep1": 1, "rep3": 3, "rep10": 10, "rep30": 30, "fac30": 30}
APPEND = "Work only inside the current directory. Do not ask questions; finish the task and stop."

def make(cond, d):
    src, cmds = build(cond)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "store.c"), "w").write(src)
    open(os.path.join(d, "README.md"), "w").write(README)
    p = os.path.join(d, "check.sh")
    open(p, "w").write(CHECK.format(lines="\n".join(f"./store {c} abc" for c in cmds[:2])))
    os.chmod(p, 0o755)
    return cmds

def one(cond, rep, model, max_turns, runs_dir):
    top = os.path.join(runs_dir, cond, f"r{rep}")
    done = os.path.join(top, "result.json")
    if os.path.exists(done):
        return json.load(open(done))
    shutil.rmtree(top, ignore_errors=True)
    d = os.path.join(top, "work")
    make(cond, d)
    subprocess.run("git init -q && git add -A && git -c user.name=p -c user.email=p@p commit -qm start",
                   shell=True, cwd=d)
    cmd = ["claude", "-p", TASK, "--output-format", "stream-json", "--verbose", "--model", model,
           "--max-turns", str(max_turns), "--max-budget-usd", "4", "--dangerously-skip-permissions",
           "--no-session-persistence", "--setting-sources", "project", "--disable-slash-commands",
           "--strict-mcp-config", "--append-system-prompt", APPEND]
    t0 = time.time()
    env = dict(os.environ); env.pop("CLAUDECODE", None)
    with open(os.path.join(top, "trace.jsonl"), "w") as tr:
        p = subprocess.run(cmd, cwd=d, stdout=tr, stderr=subprocess.PIPE, text=True, env=env, timeout=1800)
    wall = time.time() - t0
    res = {"cond": cond, "sites": CONDITIONS[cond], "rep": rep, "model": model,
           "wall_s": round(wall, 1), "rc": p.returncode, "stderr": p.stderr[-2000:]}
    tools, edits = {}, 0
    final = None
    for line in open(os.path.join(top, "trace.jsonl")):
        try: ev = json.loads(line)
        except ValueError: continue
        if ev.get("type") == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") == "tool_use":
                    n = c["name"]; tools[n] = tools.get(n, 0) + 1
                    if n in ("Edit", "Write", "MultiEdit"): edits += 1
        elif ev.get("type") == "result":
            final = ev
    if final:
        u = final.get("usage", {})
        res.update({"num_turns": final.get("num_turns"), "cost_usd": final.get("total_cost_usd"),
                    "stop": final.get("subtype"), "output_tokens": u.get("output_tokens"),
                    "context_tokens": (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                                       + u.get("cache_creation_input_tokens", 0))})
    res["tool_calls"] = sum(tools.values()); res["tools"] = tools; res["edits"] = edits
    built, per, cov, tot = hidden.grade(d, CONDITIONS[cond])
    res.update({"built": built, "covered": cov, "total_sites": tot,
                "coverage": round(cov / tot, 4) if tot else None,
                "complete": built and cov == tot, "per_site": per})
    diff = subprocess.run("git diff", shell=True, cwd=d, capture_output=True, text=True).stdout
    open(os.path.join(top, "final.diff"), "w").write(diff)
    res["diff"] = diff[:20000]
    json.dump(res, open(done, "w"), indent=1)
    shutil.rmtree(d, ignore_errors=True)     # the record is result.json, final.diff and trace.jsonl
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--max-turns", type=int, default=60)
    ap.add_argument("--conds", default=",".join(CONDITIONS))
    ap.add_argument("--runs", default=os.path.join(here, "runs"))
    a = ap.parse_args()
    jobs = [(c, r) for c in a.conds.split(",") for r in range(a.reps)]
    random.Random(20260824).shuffle(jobs)
    os.makedirs(a.runs, exist_ok=True)
    out = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(one, c, r, a.model, a.max_turns, a.runs) for c, r in jobs]
        for f in futs:
            r = f.result(); out.append(r)
            print(f"  {r['cond']:6} r{r['rep']}  covered {r['covered']}/{r['total_sites']}"
                  f"  turns {r.get('num_turns')}  ctx {r.get('context_tokens')}", flush=True)
    json.dump(out, open(os.path.join(a.runs, "results.json"), "w"), indent=1)
