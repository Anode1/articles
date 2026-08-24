#!/usr/bin/env python3
"""Run the pilot: task x language x repetition, each in a fresh copy of the
template, with `claude -p` headless, hypothesis-blind, same prompt for every
language. Order is a seeded shuffle. Records the full stream-json trace, the
usage, the tool calls, the final diff and the hidden-test verdict.

  python3 run.py --model claude-sonnet-5 --reps 3 --workers 4 [--tasks t1_diff,t3_bug] [--langs c,java]
"""
import argparse, json, os, random, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from langs import LANGS
from tasks import TASKS
import hidden

here = os.path.dirname(os.path.abspath(__file__))
APPEND = ("Work only inside the current directory. Do not ask questions; finish the task and stop.")

def one(task, lang, rep, model, max_turns, runs_dir):
    top = os.path.join(runs_dir, task, lang, f"r{rep}")
    if os.path.exists(os.path.join(top, "result.json")):
        return json.load(open(os.path.join(top, "result.json")))
    shutil.rmtree(top, ignore_errors=True)
    d = os.path.join(top, "work")          # the agent's cwd; every record stays outside it
    shutil.copytree(os.path.join(here, "templates", lang), d)
    L = LANGS[lang]
    if task == "t3_bug":
        p = os.path.join(d, L["src"]); s = open(p).read()
        assert s.count(L["bug"][0]) == 1
        open(p, "w").write(s.replace(*L["bug"]))
    subprocess.run("git init -q && git add -A && git -c user.name=p -c user.email=p@p commit -qm start", shell=True, cwd=d)
    cmd = ["claude", "-p", TASKS[task], "--output-format", "stream-json", "--verbose", "--model", model,
           "--max-turns", str(max_turns), "--max-budget-usd", "4", "--dangerously-skip-permissions",
           "--no-session-persistence", "--setting-sources", "project", "--disable-slash-commands",
           "--strict-mcp-config", "--append-system-prompt", APPEND]
    t0 = time.time()
    env = dict(os.environ); env.pop("CLAUDECODE", None)
    with open(os.path.join(top, "trace.jsonl"), "w") as tr:
        p = subprocess.run(cmd, cwd=d, stdout=tr, stderr=subprocess.PIPE, text=True, env=env, timeout=1800)
    wall = time.time() - t0
    res = {"task": task, "lang": lang, "rep": rep, "model": model, "wall_s": round(wall, 1), "rc": p.returncode,
           "stderr": p.stderr[-2000:]}
    tools, reads, bashes, edits = {}, [], [], 0
    final = None
    for line in open(os.path.join(top, "trace.jsonl")):
        try: ev = json.loads(line)
        except ValueError: continue
        if ev.get("type") == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") == "tool_use":
                    n = c["name"]; tools[n] = tools.get(n, 0) + 1
                    inp = c.get("input", {})
                    if n == "Read": reads.append(inp.get("file_path"))
                    if n == "Bash": bashes.append(inp.get("command"))
                    if n in ("Edit", "Write", "MultiEdit"): edits += 1
        elif ev.get("type") == "result":
            final = ev
    if final:
        u = final.get("usage", {})
        res.update({"num_turns": final.get("num_turns"), "cost_usd": final.get("total_cost_usd"),
                    "duration_api_ms": final.get("duration_api_ms"), "stop": final.get("subtype"),
                    "input_tokens": u.get("input_tokens", 0), "cache_read": u.get("cache_read_input_tokens", 0),
                    "cache_create": u.get("cache_creation_input_tokens", 0), "output_tokens": u.get("output_tokens", 0),
                    "final_text": (final.get("result") or "")[:1500]})
        res["context_tokens"] = res["input_tokens"] + res["cache_read"] + res["cache_create"]
    res.update({"tool_calls": sum(tools.values()), "tools": tools, "reads": reads, "bash": bashes, "edits": edits})
    ex = "-- . ':(exclude)bench' ':(exclude)obj' ':(exclude)*.class' ':(exclude)__pycache__'"
    diff = subprocess.run(f"git add -A && git diff --cached --stat HEAD {ex} && git diff --cached HEAD {ex}", shell=True, cwd=d,
                          capture_output=True, text=True).stdout
    open(os.path.join(top, "final.diff"), "w").write(diff)
    res["diff_files"] = [l.split("|")[0].strip() for l in diff.splitlines() if "|" in l and "changed" not in l]
    subprocess.run("git -c user.name=p -c user.email=p@p commit -qm final --allow-empty", shell=True, cwd=d)
    h = hidden.evaluate(task, lang, d)
    res.update({"build_ok": h["build_ok"], "hidden_pass": h["pass"], "hidden_checks": h["checks"]})
    open(os.path.join(top, "hidden.log"), "w").write(h["log"])
    json.dump(res, open(os.path.join(top, "result.json"), "w"), indent=1)
    print(f"{task:13s} {lang:7s} r{rep} turns={res.get('num_turns')} tools={res['tool_calls']} "
          f"ctx={res.get('context_tokens')} out={res.get('output_tokens')} pass={res['hidden_pass']} {wall:.0f}s", flush=True)
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-sonnet-5"); ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--workers", type=int, default=4); ap.add_argument("--max-turns", type=int, default=50)
    ap.add_argument("--tasks", default=",".join(TASKS)); ap.add_argument("--langs", default=",".join(LANGS))
    ap.add_argument("--runs", default=os.path.join(here, "runs"))
    a = ap.parse_args()
    jobs = [(t, l, r) for t in a.tasks.split(",") for l in a.langs.split(",") for r in range(a.reps)]
    random.Random(1).shuffle(jobs)
    with ThreadPoolExecutor(a.workers) as ex:
        results = list(ex.map(lambda j: one(*j, a.model, a.max_turns, a.runs), jobs))
    json.dump(results, open(os.path.join(a.runs, "results.json"), "w"), indent=1)
