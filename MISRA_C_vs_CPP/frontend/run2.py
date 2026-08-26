"""run2.py: the stale-recall condition (C2 of DESIGN.md). Two tasks whose
correct idiom changed between React 18 and 19, each run against both pinned
versions, plus the plain control where the platform never moved:

  tdef  default for a missing field   defaultProps works on 18, silent no-op on 19
  tfoc  focus a child component's input   ref-as-prop works on 19, silently stripped on 18

Six cells, five repetitions, 30 runs. The repository pins its version in
package.json and carries no documentation; the measurement is which
version's idiom the agent writes and whether the result is silently wrong
for the pinned version.

  python3 run2.py --model claude-sonnet-5 --reps 5 --workers 3
"""
import argparse, json, os, random
from concurrent.futures import ThreadPoolExecutor

import run as base

CELLS = [("plain", "tdef"), ("react", "tdef"), ("react18", "tdef"),
         ("plain", "tfoc"), ("react19f", "tfoc"), ("react18f", "tfoc")]

base.README["react18"] = base.README["react"].replace("React 19", "React 18")
base.README["react19f"] = base.README["react"]
base.README["react18f"] = base.README["react18"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--max-turns", type=int, default=60)
    ap.add_argument("--runs", default=os.path.join(base.here, "runs2"))
    a = ap.parse_args()
    jobs = [(s, t, r) for s, t in CELLS for r in range(a.reps)]
    random.Random(20260827).shuffle(jobs)
    os.makedirs(a.runs, exist_ok=True)
    out = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(base.one, s, t, r, a.model, a.max_turns, a.runs)
                for s, t, r in jobs]
        for f in futs:
            r = f.result()
            out.append(r)
            print(f"  {r['side']}-{r['task']} r{r['rep']}  "
                  f"pass {r['passed']}/{r['total']}  turns {r.get('num_turns')}",
                  flush=True)
    json.dump(out, open(os.path.join(a.runs, "results.json"), "w"), indent=1)
