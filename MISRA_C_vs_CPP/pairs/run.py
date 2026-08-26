#!/usr/bin/env python3
"""run.py: the 240-run six-pair experiment of the registered design.

6 pairs x 2 languages x 4 tasks x 5 repetitions. Each run gets a fresh work
directory built by gen.py (t4 with the defect injected), a git baseline, and
one task text naming behavior only; grading is hidden.py, never shown to the
agent. Predictions were recorded 2026-08-24, before any pair existed.

  python3 run.py --model claude-sonnet-5 --reps 5 --workers 4
"""
import argparse, json, os, random, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from gen import build, PAIRS
from tasks import TASKS
import hidden

APPEND = ("Work only inside the current directory. Do not ask questions; "
          "finish the task and stop.")


def make(pair, lang, task, d):
    os.makedirs(d, exist_ok=True)
    for name, content in build(pair, lang).items():
        open(os.path.join(d, name), "w").write(content)
    if task == "t4":
        hidden.apply_defects(d, pair, lang)


def one(pair, lang, task, rep, model, max_turns, runs_dir):
    top = os.path.join(runs_dir, f"{pair}-{lang}-{task}", f"r{rep}")
    done = os.path.join(top, "result.json")
    if os.path.exists(done):
        return json.load(open(done))
    shutil.rmtree(top, ignore_errors=True)
    d = os.path.join(top, "work")
    make(pair, lang, task, d)
    subprocess.run("git init -q && git add -A && "
                   "git -c user.name=p -c user.email=p@p commit -qm start",
                   shell=True, cwd=d)
    cmd = ["claude", "-p", TASKS[(pair, task)], "--output-format",
           "stream-json", "--verbose", "--model", model,
           "--max-turns", str(max_turns), "--max-budget-usd", "4",
           "--dangerously-skip-permissions", "--no-session-persistence",
           "--setting-sources", "project", "--disable-slash-commands",
           "--strict-mcp-config", "--append-system-prompt", APPEND]
    t0 = time.time()
    env = dict(os.environ)
    env.pop("CLAUDECODE", None)
    with open(os.path.join(top, "trace.jsonl"), "w") as tr:
        p = subprocess.run(cmd, cwd=d, stdout=tr, stderr=subprocess.PIPE,
                           text=True, env=env, timeout=1800)
    wall = time.time() - t0
    res = {"pair": pair, "lang": lang, "task": task, "rep": rep,
           "model": model, "wall_s": round(wall, 1), "rc": p.returncode,
           "stderr": p.stderr[-2000:]}
    tools, edits, reads = {}, 0, 0
    final = None
    for line in open(os.path.join(top, "trace.jsonl")):
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") == "tool_use":
                    n = c["name"]
                    tools[n] = tools.get(n, 0) + 1
                    if n in ("Edit", "Write", "MultiEdit"):
                        edits += 1
                    if n == "Read":
                        reads += 1
        elif ev.get("type") == "result":
            final = ev
    if final:
        u = final.get("usage", {})
        res.update({"num_turns": final.get("num_turns"),
                    "cost_usd": final.get("total_cost_usd"),
                    "stop": final.get("subtype"),
                    "output_tokens": u.get("output_tokens"),
                    "context_tokens": (u.get("input_tokens", 0)
                                       + u.get("cache_read_input_tokens", 0)
                                       + u.get("cache_creation_input_tokens", 0))})
    res["tool_calls"] = sum(tools.values())
    res["tools"] = tools
    res["edits"] = edits
    res["reads"] = reads
    built, passed, total, fails = hidden.grade(d, pair, task)
    res.update({"built": built, "passed": passed, "total": total,
                "pass_all": built and passed == total, "failures": fails[:5]})
    diff = subprocess.run("git diff", shell=True, cwd=d,
                          capture_output=True, text=True).stdout
    open(os.path.join(top, "final.diff"), "w").write(diff)
    res["diff_bytes"] = len(diff)
    json.dump(res, open(done, "w"), indent=1)
    shutil.rmtree(d, ignore_errors=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--max-turns", type=int, default=60)
    ap.add_argument("--only", default="")
    ap.add_argument("--runs", default=os.path.join(here, "runs"))
    a = ap.parse_args()
    jobs = [(p, l, t, r) for p in PAIRS for l in ("c", "cpp")
            for t in ("t1", "t2", "t3", "t4") for r in range(a.reps)]
    if a.only:
        want = set(a.only.split(","))
        jobs = [j for j in jobs if f"{j[0]}-{j[1]}-{j[2]}" in want]
    random.Random(20260824).shuffle(jobs)
    os.makedirs(a.runs, exist_ok=True)
    out = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(one, p, l, t, r, a.model, a.max_turns, a.runs)
                for p, l, t, r in jobs]
        for f in futs:
            r = f.result()
            out.append(r)
            print(f"  {r['pair']}-{r['lang']}-{r['task']} r{r['rep']}  "
                  f"pass {r['passed']}/{r['total']}  turns {r.get('num_turns')}  "
                  f"ctx {r.get('context_tokens')}", flush=True)
    json.dump(out, open(os.path.join(a.runs, "results.json"), "w"), indent=1)
