#!/usr/bin/env python3
"""Generate the figures for the Substack piece.

Every figure carries its source inside the image, because charts get copied
away from the article they belong to. Where a value is an assumption or an
industry range rather than a cited measurement, the figure says so on its face.

Palette: reference instance, slots 1-3 (documented as validated all-pairs,
light and dark). At most two series colours per figure.
"""
from html import escape

SURF = "#fcfcfb"
INK = "#0b0b0b"
SEC = "#52514e"
GRID = "#e2e1dd"
BAND = "#ecebe7"
MUTE = "#b9b8b3"
S1 = "#2a78d6"
S2 = "#eb6834"
FONT = "Segoe UI, Helvetica, Arial, sans-serif"


def head(w, h, title):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" font-family="{FONT}">',
        f"<title>{escape(title)}</title>",
        f'<rect width="{w}" height="{h}" fill="{SURF}"/>',
    ]


def titles(o, title, sub, x=24, y=30):
    o.append(f'<text x="{x}" y="{y}" font-size="20" font-weight="600" fill="{INK}">{escape(title)}</text>')
    for i, line in enumerate(sub):
        o.append(f'<text x="{x}" y="{y+20+i*16}" font-size="14" fill="{SEC}">{escape(line)}</text>')


def source(o, w, h, lines):
    for i, line in enumerate(lines):
        o.append(f'<text x="24" y="{h-12-(len(lines)-1-i)*13}" font-size="12" fill="{SEC}">{escape(line)}</text>')


def rbar(x, y, w, h, fill, r=4):
    """Horizontal bar, rounded at the data end only."""
    if w < r:
        w = r
    return (f'<path d="M{x},{y} H{x+w-r} a{r},{r} 0 0 1 {r},{r} V{y+h-r} '
            f'a{r},{r} 0 0 1 -{r},{r} H{x} Z" fill="{fill}"/>')


def span(x0, x1, y, h, fill, r=4):
    """Range bar, rounded at both ends."""
    return f'<rect x="{x0:.1f}" y="{y}" width="{max(x1-x0, 2*r):.1f}" height="{h}" rx="{r}" fill="{fill}"/>'


def wrapped(o, x, y, lines, size=11.5, fill=None, anchor="middle", lh=14):
    fill = fill or SEC
    for i, line in enumerate(lines):
        o.append(f'<text x="{x:.1f}" y="{y+i*lh}" font-size="{size}" '
                 f'text-anchor="{anchor}" fill="{fill}">{escape(line)}</text>')


# ------------------------------------------------------- 1. how you get access
def fig_access(path):
    """The hinge of the piece: four jurisdictions, none of them selling."""
    W, H = 760, 478
    o = head(W, H, "How large-load electricity access is granted in four provinces")
    titles(o, "Four provinces, four ways of not naming a price",
           ["How a large load obtains grid access. In none of the four is the answer a number you can plan around."])

    ax, ay, aw = 96, 170, 596
    X = lambda f: ax + aw * f

    o.append(f'<line x1="{ax}" y1="{ay}" x2="{ax+aw}" y2="{ay}" stroke="{GRID}" stroke-width="2"/>')
    o.append(f'<text x="{ax}" y="{ay-46}" font-size="13" font-weight="600" fill="{SEC}">a transaction</text>')
    wrapped(o, ax, ay - 29, ["anyone who pays the posted", "price connects"], 11.5, SEC, "start", 13)
    o.append(f'<text x="{ax+aw}" y="{ay-46}" font-size="13" font-weight="600" text-anchor="end" fill="{SEC}">a permission</text>')
    wrapped(o, ax + aw, ay - 29, ["someone decides whether", "you may connect at all"], 11.5, SEC, "end", 13)

    # the empty end of the scale
    o.append(f'<circle cx="{ax}" cy="{ay}" r="7" fill="none" stroke="{MUTE}" stroke-width="2" stroke-dasharray="3 2.5"/>')
    o.append(f'<text x="{ax}" y="{ay+26}" font-size="11.5" font-weight="600" text-anchor="start" fill="{MUTE}">no Canadian jurisdiction</text>')

    rows = [
        (0.30, "QUEBEC", ["posted price, by decree", "13c/kWh above 5 MW,", "roughly double the large-", "customer rate"], "proposed, hearing autumn 2026", S1, 0),
        (0.52, "ALBERTA", ["quantity cap", "1.2 GW interim limit,", "fully subscribed;", "permanent rules in design"], "in force, Phase 2 under way", S2, 1),
        (0.71, "BRITISH COLUMBIA", ["quantity plus contest", "100 MW conventional,", "300 MW AI over two years,", "awarded by competition"], "in force 1 February 2026", S2, 0),
        (0.94, "ONTARIO", ["ministerial discretion", "Bill 40 contemplates", "approval of connections;", "no regulations made"], "framework only, criteria unwritten", S2, 1),
    ]
    for f, name, body, status, col, level in rows:
        x = X(f)
        cx = min(max(x, 118), W - 118)
        ty = ay + 44 + level * 100
        o.append(f'<line x1="{x:.1f}" y1="{ay+8}" x2="{cx:.1f}" y2="{ty-30}" stroke="{MUTE}" stroke-width="1"/>')
        o.append(f'<circle cx="{x:.1f}" cy="{ay}" r="7.5" fill="{col}"/>')
        o.append(f'<text x="{cx:.1f}" y="{ty-14}" font-size="13.5" font-weight="600" text-anchor="middle" fill="{INK}">{escape(name)}</text>')
        o.append(f'<text x="{cx:.1f}" y="{ty+2}" font-size="12" font-weight="600" text-anchor="middle" fill="{col}">{escape(body[0])}</text>')
        wrapped(o, cx, ty + 19, body[1:], 11.5, SEC, "middle", 13)
        o.append(f'<text x="{cx:.1f}" y="{ty+19+13*(len(body)-1)+2}" font-size="11" font-style="italic" text-anchor="middle" fill="{MUTE}">{escape(status)}</text>')

    source(o, W, H, [
        "Placement along the scale is this article's characterisation of each mechanism, not a measured quantity. Sources for the",
        "mechanisms themselves: BC Data Centre Facility and Hydrogen Production Facility Power Supply Regulation, in force 1 Feb 2026.",
        "AESO interim approach to large load connections, 4 June 2025, 1,200 MW through 2028. Hydro-Quebec application to the Regie de",
        "l'energie, 13c/kWh above 5 MW, hearing autumn 2026. Ontario Bill 40, royal assent 11 December 2025; regulations not yet made.",
    ])
    o.append("</svg>")
    open(path, "w").write("\n".join(o))
    return path


# --------------------------------------------- 2. requested, available, allowed
def fig_rationing(path):
    W, H = 760, 396
    o = head(W, H, "Alberta data centre connection requests against system scale")
    titles(o, "Requested, available, allowed",
           ["Gigawatts. A connection queue is an upper bound on interest, not a measure of demand."])
    ox, oy, pw, bh, gap = 205, 96, 430, 38, 30
    xmax = 18.0
    X = lambda v: ox + pw * v / xmax
    for gv in range(0, 19, 3):
        x = X(gv)
        o.append(f'<line x1="{x:.1f}" y1="{oy-8}" x2="{x:.1f}" y2="{oy+3*(bh+gap)-gap+8}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{x:.1f}" y="{oy+3*(bh+gap)-gap+24}" font-size="12.5" text-anchor="middle" fill="{SEC}">{gv}</text>')
    o.append(f'<text x="{ox+pw/2:.1f}" y="{oy+3*(bh+gap)-gap+44}" font-size="13" text-anchor="middle" fill="{SEC}">gigawatts</text>')
    rows = [
        ("Connection requests", "29 projects, June 2025", 16.0, "16+", S1),
        ("Provincial peak load", "record, Dec 2025", 12.785, "12.8", S1),
        ("Permitted to connect", "1.2 GW, fully subscribed", 1.2, "1.2", S2),
    ]
    for i, (label, note, val, lab, col) in enumerate(rows):
        y = oy + i * (bh + gap)
        o.append(f'<text x="{ox-14}" y="{y+17}" font-size="15" text-anchor="end" fill="{INK}">{escape(label)}</text>')
        o.append(f'<text x="{ox-14}" y="{y+33}" font-size="12" text-anchor="end" fill="{SEC}">{escape(note)}</text>')
        o.append(rbar(ox, y, X(val) - ox, bh, col))
        o.append(f'<text x="{X(val)+9:.1f}" y="{y+25}" font-size="15" font-weight="600" fill="{INK}">{lab} GW</text>')
    source(o, W, H, [
        "Source: AESO, interim approach to large load connections, 4 June 2025: 29 proposed data centre projects representing more",
        "than 16 GW. Interim limit 1,200 MW through 2028, fully allocated: P2936 GLDC Load 970 MW, P3083 Keephills Phase I 230 MW.",
        "Later requests fall into Phase 2, for which AESO has published no aggregate. This is the most recent verified total.",
        "Peak load 12,785 MW, 11 December 2025, AESO 2025 Annual Market Statistics.",
    ])
    o.append("</svg>")
    open(path, "w").write("\n".join(o))
    return path


# ------------------------------------------------------------- 3. time to power
def fig_window(path):
    W, H = 760, 500
    o = head(W, H, "Earliest realistic energisation by pathway")
    titles(o, "The fastest thing on this chart is a tariff, not a turbine",
           ["Earliest realistic in-service date by pathway, for a project starting now."])
    ox, oy, pw, bh, gap = 185, 108, 470, 30, 26
    y0, y1 = 2026, 2036
    X = lambda t: ox + pw * (t - y0) / (y1 - y0)
    o.append(f'<rect x="{X(2027):.1f}" y="{oy-14}" width="{X(2030)-X(2027):.1f}" height="{5*(bh+gap)-gap+22}" fill="{BAND}"/>')
    o.append(f'<rect x="{X(2027):.1f}" y="{oy-14}" width="{X(2030)-X(2027):.1f}" height="{5*(bh+gap)-gap+22}" fill="none" stroke="{SEC}" stroke-width="1" stroke-dasharray="4 3"/>')
    o.append(f'<text x="{(X(2027)+X(2030))/2:.1f}" y="{oy-20}" font-size="13" font-weight="600" text-anchor="middle" fill="{SEC}">the 2027-2029 window</text>')
    for t in range(y0, y1 + 1, 2):
        o.append(f'<text x="{X(t):.1f}" y="{oy+5*(bh+gap)-gap+24}" font-size="12.5" text-anchor="middle" fill="{SEC}">{t}</text>')
    rows = [
        ("Interruptible connection", "a rate class. no construction.", 2027.0, 2027.6, S1),
        ("Co-location", "at an existing interconnection", 2027.4, 2028.4, S1),
        ("Solar plus storage", "typical utility-scale build", 2027.6, 2028.6, MUTE),
        ("New gas turbine", "heavy frame, ordered today", 2030.0, 2031.6, S2),
        ("Nuclear or large hydro", "ordered today", 2035.0, 2037.0, S2),
    ]
    for i, (label, note, a, b, col) in enumerate(rows):
        y = oy + i * (bh + gap)
        weight = "600" if i == 0 else "400"
        o.append(f'<text x="{ox-14}" y="{y+14}" font-size="14" font-weight="{weight}" text-anchor="end" fill="{INK}">{escape(label)}</text>')
        o.append(f'<text x="{ox-14}" y="{y+29}" font-size="11.5" text-anchor="end" fill="{SEC}">{escape(note)}</text>')
        xa = X(a)
        if b > y1:
            xb = ox + pw
            o.append(f'<path d="M{xa},{y} H{xb} l10,{bh/2:.0f} l-10,{bh/2:.0f} H{xa} Z" fill="{col}"/>')
            o.append(f'<text x="{xb+18}" y="{y+21}" font-size="13.5" fill="{INK}">2035+</text>')
        else:
            o.append(span(xa, min(X(b), ox + pw), y, bh, col))
    source(o, W, H, [
        "Gas turbine delivery: GE Vernova Q2 2026 order book, 116 GW backlog, reservations booked four to five years out, company on",
        "track to be more than halfway contracted for 2031 deliveries by end of 2026. It is the largest heavy-frame supplier.",
        "Interruptible connection: AESO Phase 2 large load integration is developing interruptible rate classes, proposal targeted 2026.",
        "Co-location, solar plus storage and nuclear or hydro durations are indicative industry ranges, not sourced to a single document.",
    ])
    o.append("</svg>")
    open(path, "w").write("\n".join(o))
    return path


# ------------------------------------------------- 4. the trade nobody can make
def fig_headroom(path):
    W, H = 760, 400
    o = head(W, H, "New load absorbed against curtailment accepted")
    titles(o, "The trade nobody is allowed to make",
           ["New load existing US grids could absorb, against how much curtailment the load accepts in exchange."])
    ox, oy, pw, bh, gap = 250, 116, 400, 46, 44
    xmax = 140.0
    X = lambda v: ox + pw * v / xmax
    for gv in range(0, 141, 20):
        x = X(gv)
        o.append(f'<line x1="{x:.1f}" y1="{oy-10}" x2="{x:.1f}" y2="{oy+2*(bh+gap)-gap+8}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{x:.1f}" y="{oy+2*(bh+gap)-gap+26}" font-size="12.5" text-anchor="middle" fill="{SEC}">{gv}</text>')
    o.append(f'<text x="{ox+pw/2:.1f}" y="{oy+2*(bh+gap)-gap+46}" font-size="13" text-anchor="middle" fill="{SEC}">gigawatts of new load absorbed</text>')
    rows = [
        ("0.25% of annual energy", "about 85 hours affected", 76.0, "76 GW"),
        ("1% of annual energy", "proportionally more hours", 126.0, "126 GW"),
    ]
    for i, (label, note, val, lab) in enumerate(rows):
        y = oy + i * (bh + gap)
        o.append(f'<text x="{ox-16}" y="{y+21}" font-size="15.5" font-weight="600" text-anchor="end" fill="{INK}">{escape(label)}</text>')
        o.append(f'<text x="{ox-16}" y="{y+38}" font-size="12" text-anchor="end" fill="{SEC}">{escape(note)}</text>')
        o.append(rbar(ox, y, X(val) - ox, bh, S1))
        o.append(f'<text x="{X(val)+10:.1f}" y="{y+30}" font-size="15.5" font-weight="600" fill="{INK}">{lab}</text>')
    # scale anchor
    xq = X(16.0)
    o.append(f'<line x1="{xq:.1f}" y1="{oy-22}" x2="{xq:.1f}" y2="{oy+2*(bh+gap)-gap+2}" stroke="{S2}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    o.append(f'<text x="{xq+7:.1f}" y="{oy-27}" font-size="12" font-weight="600" fill="{S2}">Alberta&#8217;s entire queue, 16 GW</text>')
    source(o, W, H, [
        "Source: Duke University Nicholas Institute, Rethinking Load Growth. The 22 largest US balancing areas, about 95 per cent of US",
        "load, could absorb 76 GW at 0.25 per cent annual energy curtailment and 126 GW at 1 per cent. The authors describe this as a",
        "first-order estimate that does not model transmission constraints: technical headroom, not committed flexibility. Curtailment is",
        "partial, and for 88 per cent of it half the load keeps running, so more hours are touched than the energy share alone implies:",
        "the study puts the 0.25 per cent case at roughly 85 hours a year. No hours figure is published for the 1 per cent case.",
    ])
    o.append("</svg>")
    open(path, "w").write("\n".join(o))
    return path


# ------------------------------------------------------- 5. the two new loads
def fig_asymmetry(path):
    W, H = 760, 492
    o = head(W, H, "How Canada treats its two new electrical loads")
    titles(o, "The load we subsidise and the load we cap",
           ["Same grid, same decade, opposite treatment. Both figures describe delivering flexibility to the system."])

    cw = 336
    lx, rx = 24, 24 + cw + 40
    top = 92
    for x, tint in ((lx, BAND), (rx, "#eef4fc")):
        o.append(f'<rect x="{x}" y="{top}" width="{cw}" height="246" rx="8" fill="{tint}"/>')

    def col(x, kicker, kcol, big, biglab, rows, foot):
        o.append(f'<text x="{x+22}" y="{top+30}" font-size="12.5" font-weight="600" fill="{kcol}" letter-spacing="0.6">{escape(kicker)}</text>')
        o.append(f'<text x="{x+22}" y="{top+82}" font-size="40" font-weight="600" fill="{INK}">{escape(big)}</text>')
        o.append(f'<text x="{x+22}" y="{top+104}" font-size="12.5" fill="{SEC}">{escape(biglab)}</text>')
        for i, (a, b) in enumerate(rows):
            yy = top + 138 + i * 30
            o.append(f'<text x="{x+22}" y="{yy}" font-size="13" fill="{SEC}">{escape(a)}</text>')
            o.append(f'<text x="{x+cw-22}" y="{yy}" font-size="13" font-weight="600" text-anchor="end" fill="{INK}">{escape(b)}</text>')
            o.append(f'<line x1="{x+22}" y1="{yy+9}" x2="{x+cw-22}" y2="{yy+9}" stroke="{MUTE}" stroke-width="0.75" opacity="0.5"/>')
        o.append(f'<text x="{x+22}" y="{top+230}" font-size="12" font-style="italic" fill="{SEC}">{escape(foot)}</text>')

    col(lx, "ELECTRIC VEHICLES", S2, "222,700", "enrolled households to deliver 100 MW",
        [("Enrolled customers, US 2024", "10.7 million"),
         ("Actual peak savings", "4,785 MW"),
         ("Per customer", "0.449 kW")],
        "Distribution upgrades: paid by every ratepayer.")

    col(rx, "ONE DATA CENTRE CLUSTER", S1, "1", "counterparty to deliver 100 MW",
        [("Meters", "one"),
         ("Contracts to negotiate", "one"),
         ("Telemetry", "full")],
        "Network upgrades: deposit plus contribution.")

    o.append(f'<text x="24" y="{top+284}" font-size="15" fill="{INK}">'
             f'One load is subsidised at purchase and has its wires socialised.</text>')
    o.append(f'<text x="24" y="{top+306}" font-size="15" fill="{INK}">'
             f'The other pays its own way, and is capped anyway.</text>')

    source(o, W, H, [
        "Sources: EIA Electric Power Annual, Table 10.3: US residential demand response 2024, 10,658,027 customers enrolled, 4,785 MW",
        "actual peak demand savings, giving 0.449 kW each. The 222,700 figure is that rate scaled to 100 MW; the arithmetic is mine.",
        "Cost allocation: distribution capital in Canada is recovered through regulated rates paid by all customers of the utility, while",
        "large-load customers are generally subject to connection deposits and contributions in aid of construction for upgrades they trigger.",
    ])
    o.append("</svg>")
    open(path, "w").write("\n".join(o))
    return path


# ------------------------------------------ 6. what refusing to sell produces
def fig_exit(path):
    W, H = 760, 636
    o = head(W, H, "Emissions intensity of grid-served against self-supplied load")
    titles(o, "What refusing to sell produces",
           ["Grams of CO2e per kilowatt hour. The load gets built either way;",
            "the connection decides which of these two groups it lands in."])
    ox, oy, pw, bh, gap, grp = 236, 148, 380, 34, 26, 30
    xmax = 820.0
    X = lambda v: ox + pw * v / xmax
    rowy = lambda i: oy + i * (bh + gap) + (grp if i >= 2 else 0)
    bot = rowy(3) + bh

    for gv in range(0, 801, 200):
        x = X(gv)
        o.append(f'<line x1="{x:.1f}" y1="{oy-32}" x2="{x:.1f}" y2="{bot+8}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{x:.1f}" y="{bot+28}" font-size="12.5" text-anchor="middle" fill="{SEC}">{gv}</text>')
    o.append(f'<text x="{ox+pw/2:.1f}" y="{bot+48}" font-size="13" text-anchor="middle" fill="{SEC}">grams CO2e per kWh</text>')

    o.append(f'<text x="{ox-16}" y="{oy-14}" font-size="12" font-weight="600" text-anchor="end" fill="{S1}" letter-spacing="0.5">SERVED BY THE GRID</text>')
    rows = [
        ("Modern combined cycle", "cited", 340, 370, S1, "340-370"),
        ("Alberta fleet average", "cited, 2022", 470, 470, S1, "470"),
        ("Simple-cycle gas on site", "indicative", 550, 650, S2, "550-650"),
        ("Diesel reciprocating on site", "indicative", 650, 750, S2, "650-750"),
    ]
    for i, (label, tag, a, b, colr, lab) in enumerate(rows):
        y = rowy(i)
        if i == 2:
            o.append(f'<text x="{ox-16}" y="{y-14}" font-size="12" font-weight="600" text-anchor="end" fill="{S2}" letter-spacing="0.5">BUILT BEHIND THE FENCE</text>')
        o.append(f'<text x="{ox-16}" y="{y+16}" font-size="14" text-anchor="end" fill="{INK}">{escape(label)}</text>')
        o.append(f'<text x="{ox-16}" y="{y+31}" font-size="11" font-style="italic" text-anchor="end" fill="{MUTE}">{escape(tag)}</text>')
        o.append(rbar(ox, y, X(a) - ox, bh, colr))
        if b != a:
            o.append(f'<rect x="{X(a):.1f}" y="{y}" width="{X(b)-X(a):.1f}" height="{bh}" rx="4" fill="{colr}" opacity="0.45"/>')
        o.append(f'<text x="{X(b)+10:.1f}" y="{y+23}" font-size="14" font-weight="600" fill="{INK}">{lab}</text>')

    o.append(f'<text x="24" y="{bot+92}" font-size="15" fill="{INK}">'
             f'A third of Alberta&#8217;s queue is about 33 TWh a year.</text>')
    o.append(f'<text x="24" y="{bot+114}" font-size="15" fill="{INK}">'
             f'Grid-served that is <tspan font-weight="600">12 to 15 Mt</tspan> a year. '
             f'Self-supplied, about <tspan font-weight="600">18 to 23 Mt</tspan>.</text>')

    source(o, W, H, [
        "Cited values: Canada Energy Regulator, Alberta electricity intensity 470 g/kWh in 2022, down 48 per cent since 2005, a fleet",
        "average including zero-emitting generation. Combined-cycle band from Capital Power Genesee 0.35, Kineticor Cascade 0.35-0.37,",
        "AESO reference plant 0.34, Alberta TIER good-as-best-gas benchmark 0.37. The two on-site rows are marked indicative because",
        "they are derived, not cited: fuel carbon divided by typical plant efficiency, not measurements of any installed unit. A large",
        "enough campus could instead build combined cycle on site and land near the grid figure; the band assumes the fast-deploying",
        "reciprocating and simple-cycle equipment realistic inside a three-year window. Megatonne arithmetic is mine, at 5.3 GW and 70%.",
    ])
    o.append("</svg>")
    open(path, "w").write("\n".join(o))
    return path


# ------------------------------------- 7. turbine order book (kept, not used)
def fig_orderbook(path):
    """Retained from the earlier draft. The window figure now carries this
    point, but the standalone version is kept in case it is wanted back."""
    W, H = 760, 330
    o = head(W, H, "Gas turbine order book against the window")
    titles(o, "The equipment is spoken for before the window opens",
           ["Heavy-frame gas turbine delivery availability. An order placed in 2026 does not produce power until the decade turns."])
    ox, oy, pw = 70, 140, 620
    y0, y1 = 2026, 2032
    X = lambda t: ox + pw * (t - y0) / (y1 - y0)
    o.append(f'<rect x="{X(2027):.1f}" y="{oy-46}" width="{X(2030)-X(2027):.1f}" height="68" fill="{BAND}"/>')
    o.append(f'<rect x="{X(2027):.1f}" y="{oy-46}" width="{X(2030)-X(2027):.1f}" height="68" fill="none" stroke="{SEC}" stroke-width="1" stroke-dasharray="4 3"/>')
    o.append(f'<text x="{(X(2027)+X(2030))/2:.1f}" y="{oy-54}" font-size="13.5" font-weight="600" text-anchor="middle" fill="{SEC}">the 2027-2029 window</text>')
    o.append(rbar(X(2026), oy - 22, X(2031) - X(2026), 26, MUTE))
    o.append(f'<text x="{(X(2026)+X(2031))/2:.1f}" y="{oy-4}" font-size="13.5" font-weight="600" text-anchor="middle" fill="{INK}">delivery slots contracted</text>')
    o.append(rbar(X(2031), oy - 22, X(2032) - X(2031), 26, S2))
    o.append(f'<text x="{X(2031)+8:.1f}" y="{oy-4}" font-size="13.5" fill="{INK}">2031 half contracted</text>')
    o.append(f'<line x1="{ox}" y1="{oy+18}" x2="{ox+pw}" y2="{oy+18}" stroke="{GRID}" stroke-width="1"/>')
    for t in range(y0, y1 + 1):
        x = X(t)
        o.append(f'<line x1="{x:.1f}" y1="{oy+18}" x2="{x:.1f}" y2="{oy+24}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{x:.1f}" y="{oy+40}" font-size="12.5" text-anchor="middle" fill="{SEC}">{t}</text>')
    o.append(f'<text x="{ox}" y="{oy+84}" font-size="14" fill="{INK}">Backlog at Q2 2026: <tspan font-weight="600">116 GW</tspan>. No heavy-frame order placed now lands inside the window.</text>')
    source(o, W, H, [
        "Source: GE Vernova Q2 2026 results. Backlog 116 GW, expected to reach 125 GW including slot reservations by end 2026.",
        "Reservations are booked four to five years out; CEO states the company is on track to be more than halfway contracted",
        "for 2031 by year end, with 2032 timing not yet articulated. GE Vernova is the largest heavy-frame gas turbine supplier.",
    ])
    o.append("</svg>")
    open(path, "w").write("\n".join(o))
    return path


FIGURES = [
    (fig_access, "chart_access.svg"),
    (fig_asymmetry, "chart_asymmetry.svg"),
    (fig_headroom, "chart_headroom.svg"),
    (fig_exit, "chart_exit.svg"),
    (fig_rationing, "chart_rationing.svg"),
    (fig_window, "chart_window.svg"),
    (fig_orderbook, "chart_orderbook.svg"),
]

if __name__ == "__main__":
    for fn, name in FIGURES:
        print("wrote", fn(name))
