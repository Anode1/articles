#!/usr/bin/env python3
"""Room-log instrument: parse an iac room log into a per-message table a
reviewer (human or LLM judge) scores quickly. Counts only what is countable
without judgment: message kinds by declared prefix, timing, volume per seat.
Branch width and conformity need semantic judgment; this prints the table
that judgment reads.

Usage: analyze_room.py <room-log.txt> [--tsv]
"""
import re, sys

HDR = re.compile(r"^([A-Za-z0-9_.-]+)\|([^|]*)\|(\d+)\|(\d+)$")
KIND = re.compile(r"^\[[^\]]+\]\s*([A-Z]{3,12})\b[: ]")

def parse(path):
    msgs, cur = [], None
    for line in open(path):
        m = HDR.match(line.rstrip("\n"))
        if m:
            if cur:
                msgs.append(cur)
            cur = {"from": m.group(1), "to": m.group(2),
                   "t": int(m.group(3)), "body": ""}
        elif cur is not None:
            cur["body"] += line
    if cur:
        msgs.append(cur)
    return msgs

def main():
    msgs = parse(sys.argv[1])
    if not msgs:
        print("no messages"); return
    t0 = msgs[0]["t"]
    tsv = "--tsv" in sys.argv
    kinds, per_seat = {}, {}
    if tsv:
        print("t\tfrom\tto\tkind\twords\ttext")
    for m in msgs:
        body = m["body"].strip()
        k = KIND.match(body)
        kind = k.group(1) if k else "-"
        kinds[kind] = kinds.get(kind, 0) + 1
        per_seat[m["from"]] = per_seat.get(m["from"], 0) + 1
        if tsv:
            text = " ".join(body.split())
            print(f"{m['t']-t0}\t{m['from']}\t{m['to']}\t{kind}"
                  f"\t{len(body.split())}\t{text[:100]}")
        else:
            print(f"t+{m['t']-t0:<5d} {m['from']:<14s} {kind:<10s} "
                  f"{len(body.split()):>3d}w  {' '.join(body.split())[:80]}")
    span = msgs[-1]["t"] - t0
    print(f"\n{len(msgs)} messages over {span}s; per seat: " +
          ", ".join(f"{s}={n}" for s, n in sorted(per_seat.items())) +
          "; kinds: " + ", ".join(f"{k}={n}" for k, n in sorted(kinds.items())))

if __name__ == "__main__":
    main()
