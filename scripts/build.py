"""Builds the profile README and its animated images from profile.yml.

Run from the repository root: python3 scripts/build.py
Every image comes in a light and a dark version; GitHub picks the one that matches the visitor's theme.
"""
import json
import os
import pathlib
import urllib.request
from html import escape

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = yaml.safe_load((ROOT / "profile.yml").read_text(encoding="utf-8"))

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
THEMES = {
    "light": dict(bg="#F6F8FC", panel="#FFFFFF", text="#0E1424", muted="#5A6478", line="#DCE2EE", grid="#E4E9F2",
                  accent="#2F55F5", green="#0E9F6E", warm="#E8641F", violet="#7C5CF0", amber="#D98A06", ink="#0E1424", redact="#1B2236"),
    "dark": dict(bg="#0F1422", panel="#161C2E", text="#E9EDF7", muted="#8B95AD", line="#263049", grid="#1A2134",
                 accent="#6B88FF", green="#2EE6A6", warm="#FF8A4C", violet="#A78BFA", amber="#F5B544", ink="#0F1422", redact="#2A3350"),
}
STAGES = [("idea", "Idea", "violet"), ("prototype", "Prototype", "amber"), ("beta", "Beta", "accent"), ("live", "Live", "green")]
KINDS = {"start": "warm", "hardware": "amber", "design": "violet", "software": "accent", "data": "green", "product": "warm"}
QUIET = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"


def svg(width, height, style, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">'
            f"<title>{escape(title)}</title><style>{style} {QUIET}</style>{body}</svg>")


def wrap(text, limit):
    lines, current = [], ""
    for word in text.split():
        if current and len(current) + 1 + len(word) > limit:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    return lines + [current] if current else lines


# ---------- header: a document goes in on the left, clean XML comes out on the right ----------
def header(t):
    p = DATA["person"]
    xml = ["<Invoice>", "  <ID>RE-2041</ID>", "  <Date>2026-11-03</Date>", "  <Total>1240.00</Total>", "  <Currency>EUR</Currency>", "</Invoice>"]
    cycle = 7
    keyframes = "".join(
        f"@keyframes x{i} {{ 0%, {30 + i * 7}% {{ opacity: 0; }} {34 + i * 7}%, 90% {{ opacity: 1; }} 100% {{ opacity: 0; }} }} .x{i} {{ animation: x{i} {cycle}s infinite; }}"
        for i in range(len(xml)))
    lines = p.get("terminal", [])
    slot, turn = 100 / max(len(lines), 1), 3.5 * max(len(lines), 1)
    term_css = "".join(
        f"@keyframes t{i} {{ 0%, {i * slot:.1f}% {{ opacity: 0; }} {i * slot + 2:.1f}%, {(i + 1) * slot - 2:.1f}% {{ opacity: 1; }} {(i + 1) * slot:.1f}%, 100% {{ opacity: 0; }} }} .t{i} {{ animation: t{i} {turn}s infinite; }}"
        for i in range(len(lines)))
    term = "".join(
        f'<text class="mono t{i}" x="66" y="276" font-size="14" fill="{t["muted"]}" opacity="{1 if i == 0 else 0}">$ {escape(l["cmd"])}'
        f'<tspan fill="{t["accent"]}">  # {escape(l["note"])}</tspan></text>'
        for i, l in enumerate(lines))
    # each greeting is typed out letter by letter next to its language tag, then the next one takes over
    hellos = p.get("greetings", [])
    slot, per_char, char_w = 2.0, 0.07, 18
    cycle_g, share, last = slot * len(hellos), 100 / max(len(hellos), 1), len(hellos) - 1
    hello_css, hello = ".cover { display: inline; } @media (prefers-reduced-motion: reduce) { .cover { display: none; } }", ""
    for i, g in enumerate(hellos):
        a, b = i * share, (i + 1) * share
        typed = a + len(g["text"]) * per_char / cycle_g * 100
        hello_css += (f"@keyframes g{i} {{ 0%, {a:.2f}% {{ opacity: 0; }} {a + .6:.2f}%, {b - .8:.2f}% {{ opacity: 1; }} {b:.2f}%, 100% {{ opacity: 0; }} }}"
                      f".g{i} {{ animation: g{i} {cycle_g}s infinite; }}"
                      f"@keyframes c{i} {{ 0%, {a:.2f}% {{ transform: translateX(0); animation-timing-function: steps({len(g['text'])}, end); }} {typed:.2f}%, 100% {{ transform: translateX({len(g['text']) * char_w}px); }} }}"
                      f".c{i} {{ animation: c{i} {cycle_g}s infinite; }}")
        color = t["green"] if i == last else t["text"]
        hello += (f'<g class="g{i}" opacity="{1 if i == 0 else 0}">'
                  f'<rect x="66" y="55" width="42" height="26" rx="7" fill="none" stroke="{t["green"] if i == last else t["accent"]}" stroke-width="1.5"/>'
                  f'<text class="mono" x="87" y="73" font-size="12" font-weight="700" text-anchor="middle" fill="{t["green"] if i == last else t["accent"]}">{escape(g["lang"])}</text>'
                  f'<text class="mono" x="122" y="78" font-size="30" font-weight="600" fill="{color}">{escape(g["text"])}</text>'
                  f'<g class="cover c{i}"><rect x="120" y="46" width="440" height="42" fill="{t["bg"]}"/><rect x="120" y="46" width="440" height="42" fill="url(#dots)"/>'
                  f'<rect class="caret" x="121" y="52" width="3" height="32" fill="{color}"/></g></g>')
    style = (f"text {{ font-family: {SANS}; }} .mono {{ font-family: {MONO}; }}" + term_css + hello_css +
             f"@keyframes scan {{ 0% {{ transform: translateY(0); opacity: 0; }} 8% {{ opacity: 1; }} 40% {{ transform: translateY(118px); opacity: 1; }} 46%, 100% {{ transform: translateY(118px); opacity: 0; }} }}"
             f".scan {{ animation: scan {cycle}s infinite; }}"
             f"@keyframes chip {{ 0%, 12% {{ transform: translateX(0); opacity: 0; }} 18% {{ opacity: 1; }} 44% {{ transform: translateX(150px); opacity: 1; }} 50%, 100% {{ transform: translateX(150px); opacity: 0; }} }}"
             f".chip {{ animation: chip {cycle}s infinite; }}"
             f"@keyframes ring {{ 0%, 100% {{ opacity: .25; }} 50% {{ opacity: 1; }} }} .ring {{ animation: ring 1.6s infinite; }}"
             f"@keyframes blink {{ 50% {{ opacity: 0; }} }} .caret {{ animation: blink 1s steps(1) infinite; }}" + keyframes)
    chips = "".join(
        f'<rect class="chip" style="animation-delay:{i * 0.35:.2f}s" x="770" y="{142 + (i % 3) * 14}" width="{18 + (i % 2) * 10}" height="8" rx="4" fill="{t[["accent", "green", "warm"][i % 3]]}"/>'
        for i in range(5))
    doc_lines = "".join(f'<rect x="672" y="{132 + i * 16}" width="{[70, 52, 64, 40, 58, 30][i]}" height="6" rx="3" fill="{t["line"]}"/>' for i in range(6))
    xml_lines = "".join(
        f'<text class="mono x{i}" x="958" y="{122 + i * 22}" font-size="13" fill="{t["accent"] if not line.startswith(" ") else t["text"]}">{escape(line)}</text>'
        for i, line in enumerate(xml))
    body = f"""
<defs><pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{t['grid']}"/></pattern>
<clipPath id="doc"><rect x="656" y="92" width="112" height="150" rx="12"/></clipPath></defs>
<rect width="1200" height="320" rx="28" fill="{t['bg']}"/><rect width="1200" height="320" rx="28" fill="url(#dots)"/>
{hello}
<text x="64" y="144" font-size="66" font-weight="800" fill="{t['text']}" letter-spacing="-1.5">{"I'm " if hellos else ""}{escape(p['name'])}.</text>
<text x="66" y="190" font-size="28" font-weight="600" fill="{t['accent']}">{escape(p['headline'])}</text>
<text x="66" y="228" font-size="22" fill="{t['muted']}">{escape(p['role'])}</text>
{term}
<rect x="656" y="92" width="112" height="150" rx="12" fill="{t['panel']}" stroke="{t['line']}" stroke-width="1.5"/>
<rect x="672" y="106" width="34" height="14" rx="4" fill="{t['warm']}"/><text x="676" y="117" font-size="10" font-weight="700" fill="#fff">PDF</text>
{doc_lines}
<g clip-path="url(#doc)"><rect class="scan" x="656" y="96" width="112" height="3" fill="{t['accent']}"/></g>
{chips}
<circle class="ring" cx="860" cy="160" r="30" fill="none" stroke="{t['accent']}" stroke-width="2"/>
<circle cx="860" cy="160" r="21" fill="{t['panel']}" stroke="{t['line']}" stroke-width="1.5"/>
<text class="mono" x="860" y="165" font-size="13" font-weight="700" text-anchor="middle" fill="{t['accent']}">{{ }}</text>
<rect x="938" y="92" width="226" height="150" rx="12" fill="{t['panel']}" stroke="{t['line']}" stroke-width="1.5"/>
{xml_lines}
"""
    return svg(1200, 320, style, body, f"Hello, I'm {p['name']}. {p['headline']} {p['role']}")


# ---------- the pipeline: every project sits on its stage and moves right over time ----------
def pipeline(t):
    projects = DATA["projects"]
    col_w, gap, top, card_h, card_gap = 270, 22, 78, 104, 14
    rows = max([sum(1 for p in projects if p["stage"] == key) for key, _, _ in STAGES] + [1])
    height = top + rows * (card_h + card_gap) + 26
    style = (f"text {{ font-family: {SANS}; }} .mono {{ font-family: {MONO}; }}"
             "@keyframes flow { 0% { transform: translateX(0); opacity: 0; } 20%, 80% { opacity: 1; } 100% { transform: translateX(16px); opacity: 0; } }"
             ".flow { animation: flow 1.8s infinite; }"
             "@keyframes glow { 0%, 100% { opacity: .15; } 50% { opacity: .9; } } .glow { animation: glow 2.4s infinite; }"
             "@keyframes redact { 0%, 100% { opacity: .9; } 50% { opacity: .55; } } .redact { animation: redact 2.8s infinite; }")
    parts = [f'<rect width="1200" height="{height}" rx="28" fill="{t["bg"]}"/>']
    for c, (key, label, color) in enumerate(STAGES):
        x = 30 + c * (col_w + gap)
        items = [p for p in projects if p["stage"] == key]
        parts.append(f'<circle cx="{x + 8}" cy="40" r="6" fill="{t[color]}"/>'
                     f'<text x="{x + 22}" y="46" font-size="17" font-weight="700" fill="{t["text"]}" letter-spacing="1">{label.upper()}</text>'
                     f'<text class="mono" x="{x + col_w - 4}" y="46" font-size="14" text-anchor="end" fill="{t["muted"]}">{len(items):02d}</text>'
                     f'<rect x="{x}" y="58" width="{col_w}" height="2" rx="1" fill="{t[color]}" opacity=".5"/>')
        if c < len(STAGES) - 1:
            for k in range(3):
                parts.append(f'<circle class="flow" style="animation-delay:{k * .6:.1f}s" cx="{x + col_w + 3}" cy="40" r="2.5" fill="{t["muted"]}"/>')
        if not items:
            y = top
            parts.append(f'<rect x="{x}" y="{y}" width="{col_w}" height="{card_h}" rx="18" fill="none" stroke="{t["line"]}" stroke-width="1.5" stroke-dasharray="6 6"/>'
                         f'<text x="{x + col_w / 2}" y="{y + card_h / 2 + 5}" font-size="14" text-anchor="middle" fill="{t["muted"]}">The next idea parks here</text>')
        for r, p in enumerate(items):
            y = top + r * (card_h + card_gap)
            if p.get("featured"):
                parts.append(f'<rect class="glow" x="{x - 3}" y="{y - 3}" width="{col_w + 6}" height="{card_h + 6}" rx="21" fill="none" stroke="{t[color]}" stroke-width="2"/>')
            parts.append(f'<rect x="{x}" y="{y}" width="{col_w}" height="{card_h}" rx="18" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="1.5"/>'
                         f'<rect x="{x + 16}" y="{y + 18}" width="4" height="{card_h - 36}" rx="2" fill="{t[color]}"/>')
            if p.get("private"):
                parts.append(f'<text x="{x + 34}" y="{y + 38}" font-size="19" font-weight="700" fill="{t["text"]}">Classified</text>'
                             f'<rect x="{x + col_w - 84}" y="{y + 22}" width="66" height="22" rx="11" fill="none" stroke="{t["muted"]}"/>'
                             f'<text class="mono" x="{x + col_w - 51}" y="{y + 37}" font-size="11" text-anchor="middle" fill="{t["muted"]}">PRIVATE</text>'
                             f'<rect class="redact" x="{x + 34}" y="{y + 54}" width="170" height="12" rx="3" fill="{t["redact"]}"/>'
                             f'<rect class="redact" style="animation-delay:.6s" x="{x + 34}" y="{y + 74}" width="118" height="12" rx="3" fill="{t["redact"]}"/>')
            else:
                parts.append(f'<text x="{x + 34}" y="{y + 38}" font-size="19" font-weight="700" fill="{t["text"]}">{escape(p["name"])}</text>')
                for i, line in enumerate(wrap(p.get("line", ""), 30)[:2]):
                    parts.append(f'<text x="{x + 34}" y="{y + 64 + i * 20}" font-size="14" fill="{t["muted"]}">{escape(line)}</text>')
    return svg(1200, height, style, "".join(parts), "Projects by stage: " + ", ".join(f"{p['name']} ({p['stage']})" for p in projects))


# ---------- the path: each step lights up in turn, left to right ----------
def path(t):
    steps = DATA["path"]
    left, right, axis, cycle = 120, 1080, 140, 9
    span = (right - left) / (len(steps) - 1)
    run = 70  # percent of the cycle spent drawing the line
    keyframes = "".join(
        f"@keyframes s{i} {{ 0%, {i / (len(steps) - 1) * run:.1f}% {{ opacity: .25; }} {i / (len(steps) - 1) * run + 3:.1f}%, 94% {{ opacity: 1; }} 100% {{ opacity: .25; }} }} .s{i} {{ animation: s{i} {cycle}s infinite; }}"
        for i in range(len(steps)))
    style = (f"text {{ font-family: {SANS}; }}"
             f"@keyframes draw {{ 0% {{ stroke-dashoffset: {right - left}; }} {run}%, 94% {{ stroke-dashoffset: 0; }} 100% {{ stroke-dashoffset: {right - left}; }} }}"
             f".draw {{ stroke-dasharray: {right - left}; animation: draw {cycle}s infinite; }}" + keyframes)
    parts = [f'<rect width="1200" height="300" rx="28" fill="{t["bg"]}"/>',
             f'<line x1="{left}" y1="{axis}" x2="{right}" y2="{axis}" stroke="{t["line"]}" stroke-width="4" stroke-linecap="round"/>',
             f'<line class="draw" x1="{left}" y1="{axis}" x2="{right}" y2="{axis}" stroke="{t["accent"]}" stroke-width="4" stroke-linecap="round"/>']
    for i, step in enumerate(steps):
        x = left + i * span
        color = t[KINDS[step["kind"]]]
        above = i % 2 == 0
        ly = axis - 52 if above else axis + 50
        parts.append(f'<g class="s{i}">'
                     f'<line x1="{x}" y1="{axis}" x2="{x}" y2="{axis - 24 if above else axis + 24}" stroke="{color}" stroke-width="2"/>'
                     f'<circle cx="{x}" cy="{axis}" r="11" fill="{t["bg"]}" stroke="{color}" stroke-width="3"/><circle cx="{x}" cy="{axis}" r="5" fill="{color}"/>'
                     f'<text x="{x}" y="{ly}" font-size="16" font-weight="700" text-anchor="middle" fill="{t["text"]}">{escape(step["label"])}</text>'
                     f'<text x="{x}" y="{ly + 20}" font-size="13" text-anchor="middle" fill="{t["muted"]}">{escape(step["note"])}</text></g>')
    legend = [("hardware", "Hardware"), ("design", "Design"), ("software", "Software"), ("data", "Data"), ("product", "Product")]
    for i, (kind, label) in enumerate(legend):
        x = 70 + i * 130
        parts.append(f'<circle cx="{x}" cy="270" r="5" fill="{t[KINDS[kind]]}"/><text x="{x + 12}" y="275" font-size="13" fill="{t["muted"]}">{label}</text>')
    return svg(1200, 300, style, "".join(parts), "Path: " + " → ".join(s["label"] for s in steps))


# ---------- the toolbox: one card per area, everyday tools filled, the rest outlined ----------
def toolbox(t):
    areas = DATA["toolbox"]
    cols, margin, gap, card_w, pad, chip_h, chip_gap = 3, 30, 20, 366, 20, 28, 8
    def chip_w(name):
        return int(len(name) * 7.3 + 26)
    def layout(area):
        chips, x, y = [], 0, 0
        rest = [(f"+{len(area['used'])} more", False)] if area["used"] else []
        for name, daily in [(n, True) for n in area["daily"]] + rest:
            w = chip_w(name)
            if x and x + w > card_w - 2 * pad:
                x, y = 0, y + chip_h + chip_gap
            chips.append((name, daily, x, y, w))
            x += w + chip_gap
        return chips, y + chip_h
    laid = [layout(a) for a in areas]
    top, parts, row_y = 70, [], 70
    rows = [list(range(i, min(i + cols, len(areas)))) for i in range(0, len(areas), cols)]
    style = (f"text {{ font-family: {SANS}; }}"
             "@keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }"
             ".card { animation: rise .7s cubic-bezier(.2,.9,.2,1) backwards; }"
             "@keyframes beat { 0%, 100% { opacity: 1; } 50% { opacity: .35; } } .beat { animation: beat 2.2s infinite; }")
    for row in rows:
        height = max(laid[i][1] for i in row) + 74
        for c, i in enumerate(row):
            x = margin + c * (card_w + gap)
            chips, _ = laid[i]
            body = (f'<rect x="{x}" y="{row_y}" width="{card_w}" height="{height}" rx="18" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="1.5"/>'
                    f'<text x="{x + pad}" y="{row_y + 34}" font-size="16" font-weight="700" fill="{t["text"]}">{escape(areas[i]["area"])}</text>'
                    f'<text x="{x + card_w - pad}" y="{row_y + 34}" font-size="13" text-anchor="end" fill="{t["muted"]}">{len(areas[i]["daily"]) + len(areas[i]["used"])}</text>')
            for name, daily, cx, cy, w in chips:
                X, Y = x + pad + cx, row_y + 52 + cy
                if daily:
                    body += (f'<rect x="{X}" y="{Y}" width="{w}" height="{chip_h}" rx="14" fill="{t["accent"]}"/>'
                             f'<text x="{X + w / 2}" y="{Y + 19}" font-size="13" font-weight="600" text-anchor="middle" fill="#FFFFFF">{escape(name)}</text>')
                else:
                    body += (f'<rect x="{X + .75}" y="{Y + .75}" width="{w - 1.5}" height="{chip_h - 1.5}" rx="13.25" fill="none" stroke="{t["line"]}" stroke-width="1.5"/>'
                             f'<text x="{X + w / 2}" y="{Y + 19}" font-size="13" text-anchor="middle" fill="{t["muted"]}">{escape(name)}</text>')
            parts.append(f'<g class="card" style="animation-delay:{i * .12:.2f}s">{body}</g>')
        row_y += height + gap
    total = row_y + 10
    total_tools = sum(len(a["daily"]) + len(a["used"]) for a in areas)
    legend = (f'<circle class="beat" cx="42" cy="38" r="6" fill="{t["accent"]}"/><text x="56" y="43" font-size="14" fill="{t["text"]}">Every week</text>'
              f'<circle cx="170" cy="38" r="5.25" fill="none" stroke="{t["muted"]}" stroke-width="1.5"/><text x="184" y="43" font-size="14" fill="{t["muted"]}">Worked with, full list below</text>'
              f'<text x="1170" y="43" font-size="14" text-anchor="end" fill="{t["muted"]}">{total_tools} tools across {len(areas)} areas</text>')
    return svg(1200, total, style, f'<rect width="1200" height="{total}" rx="28" fill="{t["bg"]}"/>' + legend + "".join(parts),
               "Toolbox: " + "; ".join(f"{a['area']}: {', '.join(a['daily'] + a['used'])}" for a in areas))


# ---------- live numbers, shown only once they are worth showing ----------
def live(repo):
    def get(url):
        request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
        if os.environ.get("GITHUB_TOKEN"):
            request.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    try:
        info = get(f"https://api.github.com/repos/{repo}")
        releases = get(f"https://api.github.com/repos/{repo}/releases")
    except Exception:
        return []
    facts = []
    if releases:
        facts.append(f"latest release **{releases[0]['tag_name']}**")
    downloads = sum(a["download_count"] for r in releases for a in r.get("assets", []))
    if downloads >= 100:
        facts.append(f"**{downloads:,}** downloads")
    if info.get("stargazers_count", 0) >= 25:
        facts.append(f"**{info['stargazers_count']}** stars")
    if info.get("license"):
        facts.append(info["license"].get("spdx_id", ""))
    return [f for f in facts if f]


def picture(name, alt):
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">'
            f'<img src="assets/{name}-light.svg" alt="{escape(alt)}" width="100%"></picture>')


def readme():
    p = DATA["person"]
    featured = next(x for x in DATA["projects"] if x.get("featured"))
    facts = live(featured["repo"]) if featured.get("repo") else []
    links = " · ".join(f'<a href="{l["url"]}"><b>{l["label"]}</b></a>' for l in p["links"])
    cells = [f'<td width="50%" valign="top"><h3>{a["icon"]} {escape(a["title"])}</h3>{escape(a["text"])}</td>' for a in DATA["areas"]]
    areas = "<table>" + "".join(f"<tr>{''.join(cells[i:i + 2])}</tr>" for i in range(0, len(cells), 2)) + "</table>"
    stories = "\n\n".join(
        f"<details>\n<summary><b>{s['title']}</b> · <i>{s['when']}</i></summary>\n\n"
        f"- **Problem:** {s['problem']}\n- **What I did:** {s['did']}\n- **Result:** {s['result']}\n\n</details>"
        for s in DATA["stories"])
    principles = "\n".join(f"- **{x['title']}** {x['text']}" for x in DATA["principles"])
    toolbox = "\n".join(f"| {a['area']} | {' · '.join([f'**{n}**' for n in a['daily']] + a['used'])} |" for a in DATA["toolbox"])
    shown = [x for x in DATA["projects"] if not x.get("private")]
    project_list = "\n".join(f"- **[{x['name']}]({x['url']})**: {x['line']} · *{x['stage']}*" for x in shown)
    fact_line = (" · ".join(facts)[:1].upper() + " · ".join(facts)[1:]) if facts else ""
    return f"""<p align="center">{picture("header", f"{p['name']}: {p['headline']}")}</p>

<p align="center">{links}</p>

{p['plain']}

> **Now:** {p['now']}

## What I build

{areas}

## Selected work

{stories}

## Projects

Every project sits on its stage and moves right as it grows.

{picture("pipeline", "Projects by stage")}

{project_list}

**[{featured['name']}]({featured['url']})** · {featured['line']}. {fact_line}

## Toolbox

{picture("toolbox", "Tools I use every week, by area")}

<details>
<summary><b>All {sum(len(a['daily']) + len(a['used']) for a in DATA['toolbox'])} tools</b> (bold = every week)</summary>

| Area | Tools |
|---|---|
{toolbox}

</details>

## Path

{picture("path", "Path from hardware and networks to Morcatt Labs")}

<details>
<summary><b>How I work</b></summary>

{principles}

</details>

## Let's talk

{DATA['closing']}

🗣️ {p['languages']}

{links}

<sub>This profile builds itself from <a href="profile.yml">profile.yml</a>.</sub>
"""


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    for theme, colors in THEMES.items():
        (ASSETS / f"header-{theme}.svg").write_text(header(colors), encoding="utf-8")
        (ASSETS / f"pipeline-{theme}.svg").write_text(pipeline(colors), encoding="utf-8")
        (ASSETS / f"path-{theme}.svg").write_text(path(colors), encoding="utf-8")
        (ASSETS / f"toolbox-{theme}.svg").write_text(toolbox(colors), encoding="utf-8")
    (ROOT / "README.md").write_text(readme(), encoding="utf-8")
    print("built README.md and", len(list(ASSETS.glob("*-*.svg"))), "images")
