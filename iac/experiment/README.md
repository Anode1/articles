# Token-bill experiment

Turns the paper's economy argument from *modeled* into *measured*. The paper's
Section 5 currently argues, by arithmetic, that a self-polling agent burns up to
millions of tokens an hour to watch an empty mailbox while an iac-wakeup agent
burns zero. This measures it against real billing.

The trick: the Anthropic Messages API returns exact token counts in every response
(`input_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`,
`output_tokens`). Those counts **are** the meter. We sum them across a run of polls.
The iac arm makes no API calls while idle, so its idle bill is zero by construction,
not by estimate.

## What it does

Two arms, matching the paper:

- **poll** - a model with a realistic ~50k-token agent context is asked to "check
  for a message" every `--interval` seconds for `--duration` seconds. Each call's
  usage is recorded and summed.
  - `--mode warm` keeps the context in the prompt cache (polls fall inside the
    cache lifetime, so the prefix is priced as a cache read).
  - `--mode cold` disables caching, so every poll pays full input price - the
    "cache evicted / polled sparsely" case.
- **iac** - parks `iac recv` for the same window. Zero API calls, zero idle tokens.
  The model is invoked exactly once, when a real message arrives; price that single
  wake with one `--polls 1` call.

## Prerequisites

- Python 3 (standard library only - no `pip install`).
- An API key in the environment: `export ANTHROPIC_API_KEY=sk-...`

## Run it

**1. Validate cheaply first** (3 quick polls, a few cents - always do this):

```sh
ANTHROPIC_API_KEY=sk-... python3 tokenbill.py --fast
```

Confirm it prints per-poll usage and a running dollar total.

**2. The real one-hour run** (120 polls at 30s, ~50k context, warm + cold):

```sh
ANTHROPIC_API_KEY=sk-... python3 tokenbill.py --yes \
    --model claude-sonnet-5 --context-tokens 50000 --interval 30 --duration 3600
```

`--yes` is required for a real (non-`--fast`) run so you cannot spend by accident.

Practical tip: the **warm** arm must be spaced at 30s (inside the cache lifetime)
to stay warm, so it takes the real hour. The **cold** arm's bill does not depend on
spacing (caching is off), so you can run it fast and separately to save wall-clock:

```sh
ANTHROPIC_API_KEY=sk-... python3 tokenbill.py --yes --mode cold --interval 1 \
    --model claude-sonnet-5 --context-tokens 50000 --polls 120
```

**3. The iac arm** (park recv for the hour on a real room; zero calls by construction):

```sh
python3 tokenbill.py --arm iac --room "$HOME/iac/room" --duration 3600
```

Then price the single wake (one context-sized call):

```sh
ANTHROPIC_API_KEY=sk-... python3 tokenbill.py --yes --mode warm --polls 1 \
    --model claude-sonnet-5 --context-tokens 50000
```

## Cost to run

The key money-saver: **you do not pay for a separate cold-cache run.** A cold
(cache-miss) bill is just every *processed* token priced at the full input rate, and
the warm run already measures the processed-token count. So one cheap warm run yields
all three numbers - warm (measured directly), cold (derived from the same measured
processed tokens), and iac (zero). The script prints the derived cold line for you.

So the only real spend is the **warm run** (120 polls, ~50k context):

| Model | warm run (what you spend) | cold (derived, $0 extra) | iac idle |
|-------|--------------------------:|-------------------------:|---------:|
| claude-haiku-4-5  | ~$0.7 | ~$6  | $0 |
| claude-sonnet-5   | ~$2   | ~$18 | $0 |
| claude-opus-4-8   | ~$10  | ~$90 | $0 |

**Is $5 enough? Yes, comfortably.** Recommended: **Sonnet warm run ~$2**, plus
`--fast` validation (~$0.05), plus an optional 5-poll cold spot-check to confirm the
derivation (~$0.75). Total ~$3, under $5. The polling-vs-iac point is model-independent
and iac is always $0, so Sonnet makes the same case as Opus for a tenth the cost.

Run **Opus** (~$10 warm) only if you specifically want the figure for an Opus-class
agent - that matches the ~$10 / one-hour spend of the ais statistics run. The cold
Opus number (~$90) is never actually spent; it is derived.

## Reading the result

- The **token counts are exact** (straight from the API). Quote those with confidence.
- The **dollar figures are derived** by multiplying counts by the `PRICING` table in
  `tokenbill.py`. Verify that table against console.anthropic.com/pricing before you
  quote dollars, and cross-check the run's total against the **Console usage dashboard**
  for the run window - that is the ground-truth bill.
- Output is printed and saved to `tokenbill_result.json`.

## What goes into the paper

The result replaces the *modeled* figures in Section 5's token table with *measured*
ones. Fill this in from the run and hand it back:

```
Measured: <model>, <date>, context = <measured input_tokens> tokens, 120 polls at 30s.
  poll, warm cache : processed <X> tokens, billed <Y> tokens = $<Z>
  poll, cold cache : processed <X> tokens, billed <X> tokens = $<Z'>
  iac wakeup, idle : 0 calls, 0 tokens, $0.00 (single wake on arrival: ~<C> tokens = $<w>)
```

Then Section 5's caption changes from "modeled from the cost equation" to "measured
on the Anthropic API, <date>," and the economy bullet in the abstract stands on a
receipt rather than arithmetic.

## Caveats (kept deliberately conservative)

- The poll is the *cheapest possible* check: full context in, a one-word reply out
  (`max_tokens=8`). A real agent that reasons before answering costs **more**, so the
  measured poll cost is a floor, favorable to polling.
- Context is padded to a target size with realistic filler; content does not change
  token accounting, only length does, and the script reports the **measured** size.
- The cold arm models cache eviction / sparse polling by disabling caching; it is an
  true upper bound on the bill, not a worst-case fiction.
