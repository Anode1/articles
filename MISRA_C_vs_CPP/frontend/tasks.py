"""tasks.py: the four maintenance tasks, their hidden scenarios, and the
reference model the grader compares the rendered DOM against.

The task texts are identical on both sides. The scenarios drive the live
page (fresh load each) and the model computes what the spec says the DOM
must show. t4 injects the defect at build time; DEFECTS carries the exact
patch per side.
"""
import json, os

here = os.path.dirname(os.path.abspath(__file__))

TASKS = {
    "t1": "Each item row must also show the length of the item's name: a "
          "span with class item-len, placed right after the name, containing "
          "the number of characters. Example: for the name teapot it shows 6.",
    "t2": "Add a state filter: a select element with id stateFilter, first "
          "option All (empty value), then one option per state that appears "
          "in the data. Choosing a state keeps only rows in that state; it "
          "combines with the existing text and minimum-length filters.",
    "t3": "Change the empty state: when the filters hide every row, the rows "
          "area must show the text Nothing matches. instead of No items "
          "found., and the count line must carry the class is-empty while it "
          "reads 0 items. The class must go away as soon as rows are visible "
          "again.",
    "t4": "The text filter must match anywhere inside the name or the "
          "author, case-insensitive, but it currently matches only from the "
          "beginning of them. Make it match anywhere again.",
    "tdef": "Some items in the data have no state field. They must render "
            "exactly like items whose state is draft: the same badge, the "
            "same text. Items that do have a state keep their own.",
    "tfoc": "After a row is deleted with its Delete button, keyboard focus "
            "must land on the text filter input, so the user can refine the "
            "list right away. Focus must not move on any other action.",
}

DEFECTS = {
    ("plain", "t4"): [("app.js",
        "      if (q && it.name.toLowerCase().indexOf(q) < 0\n"
        "            && it.author.toLowerCase().indexOf(q) < 0) return false;",
        "      if (q && !it.name.toLowerCase().startsWith(q)\n"
        "            && !it.author.toLowerCase().startsWith(q)) return false;")],
    ("react", "t4"): [("src/App.jsx",
        "        if (q && !it.name.toLowerCase().includes(q)\n"
        "               && !it.author.toLowerCase().includes(q)) return false;",
        "        if (q && !it.name.toLowerCase().startsWith(q)\n"
        "               && !it.author.toLowerCase().startsWith(q)) return false;")],
}

# Ops: (kind, arg). Each scenario is a fresh page load followed by its ops.
BASE = [
    [],
    [("text", "cup")],
    [("text", "RES")],                      # mid-string, case-insensitive
    [("minlen", "6")],
    [("text", "a"), ("minlen", "7")],
    [("sort", "name")],
    [("sort", "name"), ("sort", "name")],
    [("toggle", "3"), ("toggle", "7")],
    [("toggle", "3"), ("delete", "3")],
    [("text", "zzz")],
]

SCENARIOS = {
    "t1": BASE,
    "t2": BASE + [
        [("state", "draft")],
        [("state", "draft"), ("text", "e")],
        [("state", "active"), ("minlen", "6")],
    ],
    "t3": BASE + [[("text", "zzz"), ("text", "")]],
    "t4": BASE,
    "tdef": BASE,
    "tfoc": BASE + [[("delete", "5")], [("text", "cup"), ("delete", "3")]],
}


def load_items():
    return json.load(open(os.path.join(here, "plain", "items.json")))


def items_def():
    """The tdef variant: two items with no state field at all."""
    return load_items() + [{"id": 25, "author": "dave", "name": "beaker"},
                           {"id": 26, "author": "alice", "name": "flask"}]


def model(ops, task):
    """Apply ops per the spec; return the projection the DOM must show."""
    items = [dict(it) for it in (items_def() if task == "tdef"
                                 else load_items())]
    selected, sort = set(), {"key": "id", "dir": 1}
    text, minlen, state = "", 0, ""
    for kind, arg in ops:
        if kind == "text":
            text = arg
        elif kind == "minlen":
            minlen = int(arg or 0)
        elif kind == "state":
            state = arg
        elif kind == "sort":
            if sort["key"] == arg:
                sort["dir"] = -sort["dir"]
            else:
                sort = {"key": arg, "dir": 1}
        elif kind == "toggle":
            selected ^= {arg}
        elif kind == "delete":
            items = [it for it in items if str(it["id"]) != arg]
            selected.discard(arg)
    q = text.lower()
    for it in items:
        if task == "tdef":
            it["state"] = it.get("state", "draft")
    rows = [it for it in items
            if (not q or q in it["name"].lower() or q in it["author"].lower())
            and len(it["name"]) >= minlen
            and (not state or it["state"] == state)]
    rows.sort(key=lambda it: it[sort["key"]], reverse=sort["dir"] < 0)
    n = len(rows)
    sel = sum(1 for it in rows if str(it["id"]) in selected)
    exp = {
        "count": f"{n} item" if n == 1 else f"{n} items",
        "selected": f"{sel} selected" if sel else "",
        "rows": [{"id": str(it["id"]), "author": it["author"],
                  "name": it["name"], "badge": "badge badge-" + it["state"],
                  "checked": str(it["id"]) in selected} for it in rows],
        "caret_id": "ID" + (" ▲" if sort["key"] == "id" and sort["dir"] > 0
                            else " ▼" if sort["key"] == "id" else ""),
        "caret_name": "Name" + (" ▲" if sort["key"] == "name" and sort["dir"] > 0
                                else " ▼" if sort["key"] == "name" else ""),
        "empty": None if n else ("Nothing matches." if task == "t3"
                                 else "No items found."),
    }
    if task == "t1":
        for r in exp["rows"]:
            r["len"] = str(len(r["name"]))
    if task == "t3":
        exp["count_empty_class"] = n == 0
    if task == "tfoc" and any(k == "delete" for k, _ in ops):
        exp["focused"] = "filter"
    return exp
