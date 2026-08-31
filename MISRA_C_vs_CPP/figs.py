#!/usr/bin/env python3
"""Figures for the IEEE Software version (ieee_software.tex).

Reads the raw run records (pairs/runs, endpoint/runs, frontend/runs2) and
the closure numbers, emits fig_closures.pdf, fig_pairs.pdf, fig_runs.pdf.
Bootstrap CIs: 20,000 resamples, seed 1.
"""
import json
import random
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PLAIN = "#4878a8"
LAYER = "#c0504d"
LIGHT = "#e3b0ae"
GRAY = "#888888"

plt.rcParams.update({
    "font.size": 8.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "pdf.fonttype": 42,
})


def fig_closures():
    # (label, repo_k, outside_k, convention) at matched granularity per pair
    rows = [
        ("plain C, ais (whole files)", 90.2, 0, False),
        ("idiomatic C++, taskwarrior (whole files)", 256.7, 0, False),
        ("plain Java + JDBC, System A (regions)", 7.6, 0, False),
        ("Spring Boot 4 endpoint (regions)", 8.2, 123.8, True),
        ("plain JS twin (whole page)", 1.1, 0, False),
        ("React 19 twin (whole page)", 1.1, 282.7, True),
    ]
    fig, ax = plt.subplots(figsize=(4.9, 2.5))
    y = [5.4, 4.6, 3.2, 2.4, 1.0, 0.2]
    for yi, (label, repo, out, conv) in zip(y, rows):
        color = LAYER if ("C++" in label or "Spring" in label or "React" in label) else PLAIN
        ax.barh(yi, repo, height=0.6, color=color)
        if out:
            ax.barh(yi, out, left=repo, height=0.6, color=LIGHT)
        total = repo + out
        note = f"{repo:g}k" if not out else f"{repo:g}k + {out:g}k out"
        if conv:
            note += "\n+ convention"
        ax.text(total + 4, yi, note, va="center", fontsize=7.5)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=8)
    ax.set_xlabel("tokens-to-trace, thousands of o200k tokens")
    ax.set_xlim(0, 478)
    fig.tight_layout()
    fig.savefig("fig_closures.pdf")


PATHS = [
    ("plain C\n90k", [
        ("main", 0), ("arg parse + dispatch", 0), ("query", 0),
        ("store read", 0), ("print records", 0)]),
    ("idiomatic C++\n257k", [
        ("main", 0), ("app object run", 0), ("command registry", 1),
        ("command object", 0), ("query", 0), ("operator overloads", 1),
        ("store read", 0), ("formatter factory", 1), ("print records", 0)]),
    ("plain Java\n7.6k in repo", [
        ("dispatcher servlet", 0), ("route + auth", 0),
        ("endpoint branch", 0), ("DAO query", 0), ("SQL read", 0),
        ("rows to JSON", 0)]),
    ("Spring\n8.2k +124k +conv.", [
        ("filter chain auth", 1), ("framework dispatcher", 0),
        ("route mapping", 1), ("argument binding", 1),
        ("controller + service", 0), ("tx proxy", 1),
        ("repository iface", 0), ("query derivation", 1),
        ("dynamic SQL read", 1), ("serializer to JSON", 1)]),
    ("plain JS\n1.1k in page", [
        ("event listener", 0), ("handler", 0), ("filter + sort", 0),
        ("template string", 0), ("innerHTML write", 0),
        ("browser paints", 0)]),
    ("React 19\n1.1k +283k +conv.", [
        ("synthetic event", 1), ("priority lane", 1), ("state setter", 0),
        ("hook state store", 1), ("component function", 0),
        ("filter + sort", 0), ("reconciler diff", 1), ("key identity", 1),
        ("commit phase", 1), ("prop application", 1),
        ("browser paints", 0)]),
]


def fig_paths():
    n = max(len(steps) for _, steps in PATHS)
    fig, ax = plt.subplots(figsize=(7.0, 3.1))
    ax.set_axis_off()
    ax.set_xlim(0, 6)
    ax.set_ylim(-0.6, n + 1.6)
    for col, (head, steps) in enumerate(PATHS):
        x = col + 0.5
        ax.text(x, n + 0.7, head, ha="center", va="bottom", fontsize=7,
                fontweight="bold")
        for i, (label, ind) in enumerate(steps):
            y = n - i
            fc = "#f5dedd" if ind else "#e8eef5"
            ec = LAYER if ind else PLAIN
            ax.add_patch(plt.Rectangle((x - 0.46, y - 0.32), 0.92, 0.64,
                                       facecolor=fc, edgecolor=ec,
                                       lw=1.1 if ind else 0.7))
            ax.text(x, y, label, ha="center", va="center", fontsize=6.2)
            if i < len(steps) - 1:
                ax.annotate("", xy=(x, y - 0.68), xytext=(x, y - 0.34),
                            arrowprops=dict(arrowstyle="->", lw=0.6,
                                            color="#666666"))
    ax.add_patch(plt.Rectangle((0.04, -0.5), 0.22, 0.42,
                               facecolor="#e8eef5", edgecolor=PLAIN, lw=0.7))
    ax.text(0.32, -0.29, "a name at the call site: one search",
            va="center", fontsize=6.5)
    ax.add_patch(plt.Rectangle((2.54, -0.5), 0.22, 0.42,
                               facecolor="#f5dedd", edgecolor=LAYER, lw=1.1))
    ax.text(2.82, -0.29, "resolves only in a registry, an interpreter, "
            "an overload set, or a version convention", va="center",
            fontsize=6.5)
    fig.tight_layout()
    fig.savefig("fig_paths.pdf")


def boot_ci(a, b, n=20000):
    out = []
    for _ in range(n):
        ra = [random.choice(a) for _ in a]
        rb = [random.choice(b) for _ in b]
        out.append(st.mean(rb) - st.mean(ra))
    out.sort()
    return out[int(0.025 * n)], out[int(0.975 * n)]


def fig_pairs():
    random.seed(1)
    P = json.load(open("pairs/runs/results.json"))
    names = {
        "virt": "virtual registry, 8 files",
        "mix": "mixed constructs, 4 files",
        "tmpl": "template, 2 files",
        "raii": "RAII, 2 files",
        "inh": "inheritance, 2 files",
        "virt1": "registry, 1 file (control)",
        "oper": "operator overloads, 2 files",
    }
    stats = []
    for key, label in names.items():
        c = [r["num_turns"] for r in P if r["pair"] == key and r["lang"] == "c"]
        x = [r["num_turns"] for r in P if r["pair"] == key and r["lang"] == "cpp"]
        lo, hi = boot_ci(c, x)
        stats.append((label, st.mean(x) - st.mean(c), lo, hi, key == "virt1"))
    stats.sort(key=lambda s: s[1], reverse=True)
    fig, ax = plt.subplots(figsize=(4.9, 2.2))
    ys = range(len(stats), 0, -1)
    ax.axvspan(-1.05, 1.05, color=GRAY, alpha=0.15, lw=0)
    ax.axvline(0, color=GRAY, lw=0.8)
    for yi, (label, d, lo, hi, ctrl) in zip(ys, stats):
        color = PLAIN if ctrl else LAYER
        marker = "o" if not ctrl else "s"
        ax.plot([lo, hi], [yi, yi], color=color, lw=1.4)
        ax.plot([d], [yi], marker, color=color, ms=5)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([s[0] for s in stats], fontsize=8)
    ax.set_xlabel("extra turns on the C++ side, mean and bootstrap 95% CI, 40 runs per row")
    ax.text(0, len(stats) + 0.55, "rerun noise band: the same C program,\ntwo batches of 20, differs by 1.05 turns",
            fontsize=7, ha="center", color="#555555")
    fig.tight_layout()
    fig.savefig("fig_pairs.pdf")


def _dots(ax, x, vals, color):
    step = min(0.055, 0.42 / max(len(vals), 1))
    for i, v in enumerate(vals):
        ax.plot(x + (i - len(vals) / 2 + 0.5) * step, v, "o",
                color=color, ms=2.6, alpha=0.75, mew=0)


def fig_runs():
    E = (json.load(open("endpoint/runs/results.json"))
         + json.load(open("endpoint/runs2/results.json")))
    F2 = json.load(open("frontend/runs2/results.json"))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(4.9, 2.3),
                                 gridspec_kw={"width_ratios": [4, 2.1]})
    tasks = [("t1", "add a\nfield"), ("t2", "add a\nfilter"),
             ("t3", "change\nthe 401"), ("t4", "find the\ndefect")]
    for i, (t, label) in enumerate(tasks):
        p = [r["num_turns"] for r in E if r["task"] == t and r["side"] == "plain"]
        s = [r["num_turns"] for r in E if r["task"] == t and r["side"] == "spring"]
        a1.bar(i - 0.19, st.mean(p), 0.34, color=PLAIN)
        a1.bar(i + 0.19, st.mean(s), 0.34, color=LAYER)
        _dots(a1, i - 0.19, p, "#26496b")
        _dots(a1, i + 0.19, s, "#7a2f2c")
    a1.annotate("6/10 pass: the silent\nbinding miss, four times", xy=(1.19, 13.9),
                xytext=(1.85, 19.5), fontsize=7, ha="left",
                arrowprops=dict(arrowstyle="-", lw=0.7, color="#555555"))
    a1.set_xticks(range(4))
    a1.set_xticklabels([t[1] for t in tasks], fontsize=7.5)
    a1.set_ylim(0, 24)
    a1.set_ylabel("mean turns, 10 runs per bar")
    a1.set_title("one endpoint, two Java stacks", fontsize=8.5, pad=2)
    a1.legend(["plain JDK + JDBC", "Spring Boot"], fontsize=7, frameon=False,
              loc="upper left", handlelength=1.2)

    cells = [("plain", "plain", PLAIN), ("react19f", "React\n19", LAYER),
             ("react18f", "React\n18", LAYER)]
    for i, (side, label, color) in enumerate(cells):
        v = [r["num_turns"] for r in F2 if r["task"] == "tfoc" and r["side"] == side]
        a2.bar(i, st.mean(v), 0.6, color=color)
        _dots(a2, i, v, "#26496b" if color == PLAIN else "#7a2f2c")
    a2.set_xticks(range(3))
    a2.set_xticklabels([c[1] for c in cells], fontsize=7)
    a2.set_title("web: cross a component\nboundary", fontsize=8.5)
    fig.tight_layout()
    fig.savefig("fig_runs.pdf")


if __name__ == "__main__":
    fig_closures()
    fig_paths()
    fig_pairs()
    fig_runs()
    print("wrote fig_closures.pdf fig_paths.pdf fig_pairs.pdf fig_runs.pdf")
