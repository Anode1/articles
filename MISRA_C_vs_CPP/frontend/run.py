"""run.py: the frontend agent experiment. One screen, two builds (plain JS
against the DOM, React 19 with vite), identical rendered behavior verified
by equiv.py before any task; four tasks with the same text; five
repetitions: 40 runs. Predictions and the refutation criterion were
recorded in DESIGN.md before the twins existed.

  python3 run.py --model claude-sonnet-5 --reps 5 --workers 3
"""
import argparse, json, os, random, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from tasks import TASKS
import hidden

APPEND = ("Work only inside the current directory. Do not ask questions; "
          "finish the task and stop. Do not launch a browser or open any "
          "window; verify by reading the code.")

README = {"plain": """# items screen (plain JS)

Static page: index.html + app.js + app.css, data in items.json. Serve the
directory with any static server to view, e.g.:

    python3 -m http.server 8080
""",
"react": """# items screen (React 19 + vite)

Source in src/ (App.jsx, ItemsTable.jsx, ItemRow.jsx, main.jsx), data in
public/items.json. node_modules is already installed (symlink).

    npx vite build   # build to dist/
    npx vite         # dev server
"""}


def one(side, task, rep, model, max_turns, runs_dir):
    top = os.path.join(runs_dir, f"{side}-{task}", f"r{rep}")
    done = os.path.join(top, "result.json")
    if os.path.exists(done):
        return json.load(open(done))
    shutil.rmtree(top, ignore_errors=True)
    d = os.path.join(top, "work")
    hidden.make_workdir(side, task, d)
    open(os.path.join(d, "README.md"), "w").write(README[side])
    subprocess.run("git init -q && git add -A && "
                   "git -c user.name=p -c user.email=p@p commit -qm start",
                   shell=True, cwd=d)
    cmd = ["claude", "-p", TASKS[task], "--output-format", "stream-json",
           "--verbose", "--model", model, "--max-turns", str(max_turns),
           "--max-budget-usd", "4", "--dangerously-skip-permissions",
           "--no-session-persistence", "--setting-sources", "project",
           "--disable-slash-commands", "--strict-mcp-config",
           "--append-system-prompt", APPEND]
    env = dict(os.environ)
    env.pop("CLAUDECODE", None)
    env["PATH"] = hidden.NODE_BIN + os.pathsep + env["PATH"]
    t0 = time.time()
    with open(os.path.join(top, "trace.jsonl"), "w") as tr:
        p = subprocess.run(cmd, cwd=d, stdout=tr, stderr=subprocess.PIPE,
                           text=True, env=env, timeout=2400)
    wall = time.time() - t0
    res = {"side": side, "task": task, "rep": rep, "model": model,
           "wall_s": round(wall, 1), "rc": p.returncode,
           "stderr": p.stderr[-1500:]}
    tools, final = {}, None
    for line in open(os.path.join(top, "trace.jsonl")):
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") == "tool_use":
                    tools[c["name"]] = tools.get(c["name"], 0) + 1
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
    res["tools"] = tools
    built, passed, total, fails = hidden.grade(d, side, task)
    res.update({"built": built, "passed": passed, "total": total,
                "pass_all": built and passed == total, "failures": fails[:4]})
    diff = subprocess.run("git diff", shell=True, cwd=d,
                          capture_output=True, text=True).stdout
    open(os.path.join(top, "final.diff"), "w").write(diff)
    json.dump(res, open(done, "w"), indent=1)
    shutil.rmtree(d, ignore_errors=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--max-turns", type=int, default=60)
    ap.add_argument("--runs", default=os.path.join(here, "runs"))
    a = ap.parse_args()
    jobs = [(s, t, r) for s in ("plain", "react") for t in sorted(TASKS)
            for r in range(a.reps)]
    random.Random(20260826).shuffle(jobs)
    os.makedirs(a.runs, exist_ok=True)
    out = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(one, s, t, r, a.model, a.max_turns, a.runs)
                for s, t, r in jobs]
        for f in futs:
            r = f.result()
            out.append(r)
            print(f"  {r['side']}-{r['task']} r{r['rep']}  "
                  f"pass {r['passed']}/{r['total']}  turns {r.get('num_turns')}  "
                  f"ctx {r.get('context_tokens')}", flush=True)
    json.dump(out, open(os.path.join(a.runs, "results.json"), "w"), indent=1)
