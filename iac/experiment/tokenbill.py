#!/usr/bin/env python3
"""
tokenbill.py - measure the real token bill of a self-polling agent vs an iac wakeup.

The paper's economy argument is otherwise MODELED. This measures it: the Anthropic
Messages API returns exact token counts in every response (input / cache-read /
cache-write / output), which is the meter. We run a realistic agent context and
poll it on a schedule, summing the usage; iac's wakeup makes zero calls while idle,
so its idle bill is zero by construction.

Stdlib only (urllib). Needs Python 3 and ANTHROPIC_API_KEY in the environment.

TWO arms:
  poll  - a model checks for a message every --interval seconds for --duration.
          --mode warm keeps the context in the prompt cache (each poll inside the
          cache lifetime, cache-read priced); --mode cold disables caching (each
          poll pays full input). Real runs both by default.
  iac   - park `iac recv` for the same window. Zero API calls, zero idle tokens.
          Then one real call when a message finally arrives, to price the wake.

USAGE
  # validate cheaply first (3 quick polls, ~cents):
  ANTHROPIC_API_KEY=sk-... python3 tokenbill.py --fast

  # the real one-hour run (120 polls at 30s), warm+cold, ~50k context:
  ANTHROPIC_API_KEY=sk-... python3 tokenbill.py --yes \
      --model claude-sonnet-5 --context-tokens 50000 --interval 30 --duration 3600

  # the iac arm (park recv for the hour on a real room, then price one wake):
  ANTHROPIC_API_KEY=sk-... python3 tokenbill.py --arm iac \
      --room "$HOME/iac/room" --duration 3600

The token counts printed ARE the bill; the dollar figures are those counts times
the PRICING table below (verify it against console.anthropic.com/pricing before
you quote dollars - token counts are exact, prices change).
"""

import argparse, json, os, subprocess, sys, time, urllib.request, urllib.error

API_URL = "https://api.anthropic.com/v1/messages"

# $ per 1M tokens. VERIFY against current pricing; token counts below are exact,
# these multipliers are not authoritative and are the only soft numbers here.
PRICING = {
    "claude-opus-4-8":   {"in": 15.0, "out": 75.0, "cache_write": 18.75, "cache_read": 1.50},
    "claude-sonnet-5":   {"in":  3.0, "out": 15.0, "cache_write":  3.75, "cache_read": 0.30},
    "claude-haiku-4-5":  {"in":  1.0, "out":  5.0, "cache_write":  1.25, "cache_read": 0.10},
}

AGENT_SYSTEM = (
    "You are one worker in a fleet of coding agents that coordinate over a shared "
    "message board. Between turns you are dormant. When invoked, you check the board "
    "for a message addressed to you and act on it. You have tools to read and write "
    "files, run the build, and post to the board. Be precise and terse.\n\n"
)

# A realistic-looking paragraph used to pad the context to a target size. Content
# does not change token accounting (only length does); we report the MEASURED size.
FILLER = (
    "PRIOR CONTEXT. The receive model parks a blocking recv in a child process so the "
    "harness re-invokes the agent on message arrival; the poll runs in C at nanosecond "
    "cost, never in the model. The log is append-only and totally ordered; each reader "
    "keeps its own offset and filters by address; flock orders appends, backs presence, "
    "and guards single-taker claims. Prior turns: reviewed the latency table, confirmed "
    "no heap allocation on any path, fixed the presence pid bug, ported to macOS, wrote "
    "the docs, and coordinated all of it as messages on the board itself. "
)


def build_context(target_tokens):
    """Pad AGENT_SYSTEM + FILLER to roughly target_tokens (~3.7 chars/token heuristic)."""
    approx_chars = int(target_tokens * 3.7)
    body = AGENT_SYSTEM
    while len(body) < approx_chars:
        body += FILLER
    return body


def call(api_key, model, system_text, warm, max_tokens=8):
    """One Messages API call. Returns the usage dict. Raises on HTTP error."""
    sys_block = {"type": "text", "text": system_text}
    if warm:
        sys_block["cache_control"] = {"type": "ephemeral"}
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": [sys_block],
        "messages": [{
            "role": "user",
            "content": "Check the board for a new message addressed to you. "
                       "If there is none, reply with exactly one word: EMPTY",
        }],
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.load(r)
    u = resp["usage"]
    return {
        "input": u.get("input_tokens", 0),
        "output": u.get("output_tokens", 0),
        "cache_read": u.get("cache_read_input_tokens", 0),
        "cache_write": u.get("cache_creation_input_tokens", 0),
    }


def call_with_retry(api_key, model, system_text, warm, attempts=4):
    """call() with backoff on transient errors (429/5xx/network). 401/400 are fatal."""
    for k in range(attempts):
        try:
            return call(api_key, model, system_text, warm)
        except urllib.error.HTTPError as e:
            if e.code in (401, 400, 403):
                sys.exit(f"fatal HTTP {e.code}: {e.read().decode()[:200]}")
            if k == attempts - 1:
                sys.exit(f"gave up after {attempts} tries, HTTP {e.code}: {e.read().decode()[:200]}")
            print(f"    transient HTTP {e.code}, retry in {2**k}s", file=sys.stderr)
            time.sleep(2 ** k)
        except urllib.error.URLError as e:
            if k == attempts - 1:
                sys.exit(f"gave up after {attempts} tries, network: {e}")
            print(f"    network error, retry in {2**k}s", file=sys.stderr)
            time.sleep(2 ** k)


def cost(model, tot):
    p = PRICING.get(model)
    if not p:
        return None
    return (tot["input"] * p["in"] + tot["output"] * p["out"]
            + tot["cache_write"] * p["cache_write"] + tot["cache_read"] * p["cache_read"]) / 1e6


def run_poll(api_key, model, system_text, warm, polls, interval, label, max_usd=None):
    tot = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    measured_ctx = None
    done = 0
    print(f"\n=== poll arm [{label}] : {polls} polls, every {interval}s, mode={'warm' if warm else 'cold'} ===")
    for i in range(polls):
        t0 = time.time()
        u = call_with_retry(api_key, model, system_text, warm)
        for k in tot:
            tot[k] += u[k]
        done = i + 1
        if measured_ctx is None:
            measured_ctx = u["input"] + u["cache_read"] + u["cache_write"]
        billed = cost(model, tot)
        print(f"  poll {i+1:3d}/{polls}: read={u['cache_read']} in={u['input']} "
              f"write={u['cache_write']} out={u['output']}  running_$={billed:.4f}"
              if billed is not None else f"  poll {i+1}/{polls}: {u}")
        if max_usd is not None and billed is not None and billed >= max_usd:
            print(f"  BUDGET GUARD: running cost ${billed:.4f} reached --max-usd ${max_usd}; "
                  f"stopping cleanly after {done} polls.", file=sys.stderr)
            break
        if i < polls - 1:
            time.sleep(max(0.0, interval - (time.time() - t0)))
    return {"label": label, "mode": "warm" if warm else "cold", "polls_requested": polls,
            "polls_done": done, "context_tokens": measured_ctx, "totals": tot, "usd": cost(model, tot)}


def run_iac(room, name, duration):
    print(f"\n=== iac arm : park recv on {room} as {name} for {duration}s ===")
    print("  API calls while idle: 0   idle tokens: 0   idle $: 0.0000")
    iac = os.path.expanduser("~/iac/iac")
    t0 = time.time()
    try:
        subprocess.run([iac, "recv", room, name, str(duration)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print(f"  (iac binary not found at {iac}; the idle result is 0 regardless)")
    waited = time.time() - t0
    print(f"  waited {waited:.0f}s, made 0 model calls. The model is invoked once, on a "
          f"real message: one context-sized call (price the wake with --arm poll --polls 1).")
    return {"arm": "iac", "waited_s": round(waited), "idle_calls": 0, "idle_tokens": 0, "idle_usd": 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["poll", "iac"], default="poll")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--context-tokens", type=int, default=50000)
    ap.add_argument("--interval", type=float, default=30.0)
    ap.add_argument("--duration", type=int, default=3600)
    ap.add_argument("--polls", type=int, default=None, help="override; else duration/interval")
    ap.add_argument("--mode", choices=["warm", "cold", "both"], default="both")
    ap.add_argument("--room", default=os.path.expanduser("~/iac/room"))
    ap.add_argument("--name", default="benchagent")
    ap.add_argument("--fast", action="store_true", help="3 polls, 2s interval - cheap validation")
    ap.add_argument("--yes", action="store_true", help="required to run a real (non-fast) poll arm")
    ap.add_argument("--out", default="tokenbill_result.json")
    ap.add_argument("--max-usd", type=float, default=None,
                    help="stop cleanly if cumulative billed cost reaches this (safety for low-balance accounts)")
    a = ap.parse_args()

    if a.arm == "iac":
        res = run_iac(a.room, a.name, 5 if a.fast else a.duration)
        json.dump(res, open(a.out, "w"), indent=2)
        print(f"\nsaved {a.out}")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("set ANTHROPIC_API_KEY")

    if a.fast:
        polls, interval = 3, 2.0
    else:
        polls = a.polls if a.polls else int(a.duration / a.interval)
        interval = a.interval
        est = polls * a.context_tokens
        print(f"About to make {polls} real API calls with ~{a.context_tokens} context tokens each.")
        print(f"Rough worst-case (cold) processed tokens: {est:,}. Model: {a.model}.")
        if not a.yes:
            sys.exit("Re-run with --yes to spend real tokens (or --fast to validate cheaply).")

    ctx = build_context(a.context_tokens)
    results = []
    modes = ["warm", "cold"] if a.mode == "both" else [a.mode]
    for m in modes:
        results.append(run_poll(api_key, a.model, ctx, warm=(m == "warm"),
                                polls=polls, interval=interval, label=m, max_usd=a.max_usd))

    print("\n================ SUMMARY (poll arm) ================")
    print(f"model={a.model}  polls={polls}  interval={interval}s  "
          f"measured context={results[0]['context_tokens']} tokens")
    for r in results:
        t = r["totals"]
        print(f"  {r['mode']:5s}: processed={t['input']+t['cache_read']+t['cache_write']:,}  "
              f"billed_tokens(in={t['input']:,} read={t['cache_read']:,} write={t['cache_write']:,} "
              f"out={t['output']:,})  $={r['usd']:.4f}")
    # Cold bill can be DERIVED from any run's processed tokens without paying for a
    # cold run: a cache miss bills every processed token at the full input rate.
    p = PRICING.get(a.model)
    if p:
        for r in results:
            t = r["totals"]
            processed = t["input"] + t["cache_read"] + t["cache_write"]
            derived_cold = (processed * p["in"] + t["output"] * p["out"]) / 1e6
            print(f"  derived cold bill from {r['mode']} run's {processed:,} processed tokens "
                  f"(all at full input rate): ${derived_cold:.4f}")
            break
    print("  iac wakeup (idle): 0 calls, 0 tokens, $0.0000")
    json.dump({"model": a.model, "polls": polls, "interval": interval, "arms": results},
              open(a.out, "w"), indent=2)
    print(f"\nsaved {a.out}")


if __name__ == "__main__":
    main()
