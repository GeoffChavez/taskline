"""Build docs/schedule.html: a printable Gantt chart and monthly calendars of graded deliverables.

Reads data/deliverables.json, data/schedule.csv, data/people.csv and data/site.json.
Run on its own (python print_schedule.py) or through build.py. Open the page and print it
(landscape, Letter) to get the PDF.
"""
import calendar
import csv
import html
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "docs" / "schedule.html"

LANES = [
    ("pgm", "Program & project management", "#25554A"),
    ("vse", "VSE: vehicle systems engineering", "#0B6273"),
    ("vhi", "VHI: vehicle hardware & integration", "#3F6E0F"),
    ("pcm", "PCM: propulsion controls & modeling", "#5B3E8C"),
    ("hvb", "HVB: high voltage battery", "#A8500B"),
    ("biz", "PIT, MarCom & business", "#8A2B4E"),
]
LANE_COLOR = {k: c for k, _, c in LANES}
LANE_NAME = {k: n for k, n, _ in LANES}
START, END = date(2026, 9, 1), date(2027, 5, 31)
CAL_MONTHS = [(2026, m) for m in range(10, 13)] + [(2027, m) for m in range(1, 6)]
SHORT = {
    "Studio 1: SDV Business Understanding and Wedge Hypothesis Formation": "Studio 1: SDV Business & Wedge Hypothesis",
    "Studio 2: Customer Discovery and Wedge Validation": "Studio 2: Customer Discovery & Wedge Validation",
    "Studio 1 Check-In: Business Portfolio Review": "Studio 1 Check-In",
    "Studio 2 Check-in: Customer / Business Portfolio Review": "Studio 2 Check-In",
    "University Stakeholder Executive Meeting - Preparation": "Stakeholder Exec Meeting: Preparation",
    "University Stakeholder Executive Meeting - Proof of Execution": "Stakeholder Exec Meeting: Proof of Execution",
    "Social Media Data, Outreach Data and Asset Library": "Social Media Data, Outreach Data, Asset Library",
    "Final Technical Report (Box and ASME submission)": "Final Technical Report (Box + ASME)",
    "Micro-Learning 1: Market and Wedge Understanding": "Micro-Learning 1",
    "Micro-Learning 2: Customer Discovery": "Micro-Learning 2",
}
TRACK_NAMES = {"biz": None}


def d(s):
    return date.fromisoformat(s)


def back_business_days(day, n):
    while n:
        day -= timedelta(days=1)
        if day.weekday() < 5:
            n -= 1
    return day


def esc(s):
    return html.escape(str(s), quote=True)


def load():
    deliverables = json.loads((DATA / "deliverables.json").read_text(encoding="utf-8"))
    with open(DATA / "schedule.csv", newline="", encoding="utf-8") as f:
        tasks = list(csv.DictReader(f))
    with open(DATA / "people.csv", newline="", encoding="utf-8") as f:
        people = {r["key"]: r["name"] for r in csv.DictReader(f)}
    site = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
    return deliverables, tasks, people, site


def first_name(people, key):
    name = people.get(key, key)
    return name.split()[0] if name and name != "UNFILLED" else name


def x_pct(day):
    return (day - START).days / (END - START).days * 100


def month_ticks():
    out, cur = [], START
    while cur <= END:
        nxt = date(cur.year + (cur.month == 12), cur.month % 12 + 1, 1)
        out.append((cur, min(nxt, END + timedelta(days=1))))
        cur = nxt
    return out


def gantt_page(title, lanes, deliverables, tasks, people, today, page_note):
    tmap = {t["id"]: t for t in tasks}
    ticks = month_ticks()
    head = "".join(
        f'<span style="left:{x_pct(a):.3f}%;width:{x_pct(b) - x_pct(a):.3f}%">{a.strftime("%b")}{" " + str(a.year) if a.month in (9, 1) else ""}</span>'
        for a, b in ticks
    )
    grid = "".join(f'<i class="vline" style="left:{x_pct(a):.3f}%"></i>' for a, _ in ticks[1:])
    tx = x_pct(today)
    rows = []
    for lane in lanes:
        items = sorted((x for x in deliverables if x["lane"] == lane), key=lambda x: x["due"])
        if not items:
            continue
        rows.append(f'<div class="g-group" style="--c:{LANE_COLOR[lane]}"><div>{esc(LANE_NAME[lane])}</div><div></div><div></div></div>')
        for x in items:
            due = d(x["due"])
            work = [tmap[i] for i in x.get("work_tasks", []) if i in tmap]
            starts = [d(t["start"]) for t in work]
            start = min(starts) if starts else back_business_days(due, 15)
            freeze = back_business_days(due, 5)
            past = due < today
            pts = x.get("points")
            pts_txt = str(pts) if pts else "req."
            owner = first_name(people, x["owner"])
            label = SHORT.get(x["title"], x["title"])
            l, r_, f = x_pct(start), x_pct(due), x_pct(freeze)
            bar = (
                f'<i class="bar" style="left:{l:.3f}%;width:{max(r_ - l, .4):.3f}%"></i>'
                f'<i class="frz" style="left:{f:.3f}%;width:{max(r_ - f, .3):.3f}%"></i>'
                f'<i class="dia" style="left:{r_:.3f}%"></i>'
                f'<b class="due" style="left:{r_:.3f}%">{due.day} {due.strftime("%b")}</b>'
            )
            rows.append(
                f'<div class="g-row{" past" if past else ""}" style="--c:{LANE_COLOR[lane]}">'
                f'<div class="g-name"><b>{esc(label)}</b><span>{esc(owner)}</span></div>'
                f'<div class="g-pts">{esc(pts_txt)}</div>'
                f'<div class="g-track">{grid}{bar}<i class="today" style="left:{tx:.3f}%"></i></div></div>'
            )
    return f'''<section class="sheet">
<header><div><h1>{esc(title)}</h1><p>{esc(page_note)}</p></div><div class="brand">Cal State LA EcoCAR<br><span>EcoCAR Innovation Challenge · Stellantis track · Year 1</span></div></header>
<div class="gantt">
<div class="g-head"><div>Deliverable · owner</div><div class="g-pts">Pts</div><div class="g-months">{head}<i class="today" style="left:{tx:.3f}%"></i><em class="today-lbl" style="left:{tx:.3f}%">Today {today.day} {today.strftime("%b")}</em></div></div>
{"".join(rows)}
</div>
<footer class="legend"><span><i class="lg bar"></i>Work window (planned start to due)</span><span><i class="lg frz"></i>Final 5 business days: freeze, red team, submit</span><span><i class="lg dia"></i>Official due date, 4 PM local unless noted</span><span><i class="lg today"></i>Today</span><span class="muted">Grey rows are past. “req.” = leadership requirement, no points.</span></footer>
</section>'''


def calendar_pages(deliverables, tasks, people, today):
    linked = {x.get("schedule_id") for x in deliverables}
    due_lane_days = {(x["due"], x["lane"]) for x in deliverables}
    events = {}
    for t in tasks:
        if t["type"] not in ("milestone", "freeze") or t["id"] in linked:
            continue
        if (t["start"], t["lane"]) in due_lane_days:
            continue
        if t["type"] == "freeze":
            text = f"Freeze & red team starts · {t['lane'].upper()}"
        else:
            text = t["task"]
        events.setdefault(t["start"], []).append((text, t["label"], t["lane"]))
    dues = {}
    for x in deliverables:
        dues.setdefault(x["due"], []).append(x)
    cal = calendar.Calendar(firstweekday=6)
    pages = []
    for y, m in CAL_MONTHS:
        weeks = cal.monthdatescalendar(y, m)
        month_items = [x for x in deliverables if d(x["due"]).year == y and d(x["due"]).month == m]
        month_pts = sum(x.get("points") or 0 for x in month_items)
        cells = []
        for week in weeks:
            for day in week:
                iso = day.isoformat()
                inside = day.month == m
                chips = []
                if inside:
                    for x in sorted(dues.get(iso, []), key=lambda x: x["lane"]):
                        pts = x.get("points")
                        meta = " · ".join(p for p in [
                            "end of day" if "end" in x.get("due_time", "").lower() else "4 PM",
                            f"{pts} pts" if pts else "requirement",
                            first_name(people, x["owner"]),
                        ] if p)
                        chips.append(
                            f'<div class="chip{" past" if day < today else ""}" style="--c:{LANE_COLOR[x["lane"]]}"><b>{esc(SHORT.get(x["title"], x["title"]))}</b><span>{esc(meta)}</span></div>'
                        )
                    for text, label, lane in events.get(iso, []):
                        chips.append(f'<div class="ev" style="--c:{LANE_COLOR.get(lane, "#555")}">◆ {esc(text)}</div>')
                cls = "day" + ("" if inside else " out") + (" is-today" if day == today else "") + (" wk" if day.weekday() >= 5 else "")
                cells.append(f'<div class="{cls}"><div class="num">{day.day}</div>{"".join(chips)}</div>')
        dow = "".join(f"<div>{n}</div>" for n in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
        summary = f"{len(month_items)} graded or required submissions" + (f" · {month_pts} points" if month_pts else "")
        pages.append(f'''<section class="sheet">
<header><div><h1>{calendar.month_name[m]} {y}</h1><p>{esc(summary)}</p></div><div class="brand">Cal State LA EcoCAR<br><span>Year 1 deliverables calendar</span></div></header>
<div class="cal"><div class="dow">{dow}</div><div class="days" style="grid-template-rows:repeat({len(weeks)},minmax(0,1fr))">{"".join(cells)}</div></div>
<footer class="legend">{"".join(f'<span><i class="lg sw" style="background:{c}"></i>{esc(n)}</span>' for k, n, c in LANES)}<span>◆ team milestone or event</span></footer>
</section>''')
    return pages


CSS = """
@page{size:11in 8.5in;margin:0}
*{box-sizing:border-box}
:root{--gold:#FFCE00;--ink:#111;--muted:#5d5d5d;--line:#d8d8d8}
body{margin:0;background:#e9e9e6;font:12px/1.35 Calibri,Carlito,"Segoe UI",Arial,sans-serif;color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.sheet{width:11in;height:8.5in;padding:.36in .45in .32in;background:#fff;margin:18px auto;display:flex;flex-direction:column;page-break-after:always;break-after:page;overflow:hidden}

header{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:4px solid var(--gold);padding-bottom:8px;margin-bottom:10px}
h1{margin:0;font-size:24px;line-height:1.1}
header p{margin:3px 0 0;color:var(--muted);font-size:11.5px}
.brand{text-align:right;font-weight:700;font-size:13px}.brand span{font-weight:400;color:var(--muted);font-size:10.5px}
.gantt{flex:1;display:flex;flex-direction:column}
.g-head,.g-row,.g-group{display:grid;grid-template-columns:3.15in .38in 1fr;align-items:center}
.g-head{font-size:10.5px;font-weight:700;color:var(--muted);border-bottom:1.5px solid #222;height:26px}
.g-months{position:relative;height:100%}
.g-months span{position:absolute;top:0;bottom:0;display:flex;align-items:center;justify-content:center;border-left:1px solid var(--line);color:#222}
.g-pts{text-align:right;padding-right:8px;font-variant-numeric:tabular-nums}
.g-group{height:22px;margin-top:6px;font-weight:700;font-size:11.5px;color:var(--c);border-bottom:1px solid var(--c)}
.g-row{height:27px;border-bottom:1px solid #eee}
.g-name{display:flex;justify-content:space-between;gap:6px;padding-right:6px;white-space:nowrap;overflow:hidden}
.g-name b{font-weight:600;overflow:hidden;text-overflow:ellipsis}.g-name span{color:var(--muted);font-size:10.5px}
.g-track{position:relative;height:100%}
.vline{position:absolute;top:0;bottom:0;border-left:1px solid #ececec}
.bar{position:absolute;top:8px;height:9px;background:var(--c);opacity:.28;border-radius:2px}
.frz{position:absolute;top:8px;height:9px;background:var(--c);border-radius:2px}
.dia{position:absolute;top:7px;width:11px;height:11px;margin-left:-5.5px;background:var(--gold);border:1.5px solid #111;transform:rotate(45deg)}
.due{position:absolute;top:5px;margin-left:10px;font-size:10px;font-weight:700;white-space:nowrap}
.today{position:absolute;top:0;bottom:0;border-left:2px solid #111;z-index:2}
.today-lbl{position:absolute;top:-15px;transform:translateX(-50%);font-style:normal;font-size:9.5px;font-weight:700;background:var(--gold);padding:0 4px;white-space:nowrap}
.g-row.past .bar,.g-row.past .frz{background:#9a9a9a}.g-row.past .dia{background:#ccc;border-color:#888}.g-row.past b,.g-row.past .g-pts{color:#8a8a8a}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:10.5px;color:#333;border-top:1px solid var(--line);padding-top:7px;margin-top:8px}
.legend .muted{color:var(--muted)}
.lg{display:inline-block;vertical-align:middle;margin-right:5px}
.lg.bar{position:static;width:22px;height:9px;background:#0B6273;opacity:.3}
.lg.frz{position:static;width:12px;height:9px;background:#0B6273}
.lg.dia{position:static;width:9px;height:9px;margin:0 7px 0 2px;background:var(--gold);border:1.5px solid #111;transform:rotate(45deg)}
.lg.today{position:static;width:2px;height:12px;background:#111}
.lg.sw{width:10px;height:10px;border-radius:2px}
.cal{flex:1;min-height:0;display:flex;flex-direction:column;border:1px solid #bbb}
.dow{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));background:#111;color:#fff;font-weight:700;font-size:11px}
.dow div{padding:4px 7px}
.days{flex:1;min-height:0;display:grid;grid-template-columns:repeat(7,minmax(0,1fr))}
.day{min-height:0;min-width:0;border-right:1px solid var(--line);border-bottom:1px solid var(--line);padding:3px 4px;overflow:hidden;display:flex;flex-direction:column;gap:1px}
.day:nth-child(7n){border-right:0}
.day.wk{background:#fafafa}.day.out{background:#f1f1f1}.day.out .num{color:#bbb}
.num{font-weight:700;font-size:11px;line-height:1.1}
.day.is-today{outline:3px solid var(--gold);outline-offset:-3px}
.day.is-today .num:after{content:" Today";font-size:9.5px;background:var(--gold);padding:0 4px;margin-left:3px}
.chip{border-left:4px solid var(--c);background:#f6f6f3;padding:1px 4px;border-radius:2px}
.chip b{display:block;font-size:10px;line-height:1.15}
.chip span{display:block;font-size:9px;line-height:1.15;color:var(--muted)}
.chip.past{opacity:.55}
.ev{font-size:9.5px;color:var(--c);line-height:1.2;font-weight:600}
.toolbar{max-width:11in;margin:14px auto 0;display:flex;justify-content:space-between;align-items:center;font:13px system-ui,sans-serif}
.toolbar button{font:inherit;padding:7px 14px;border:0;border-radius:6px;background:#111;color:#fff;cursor:pointer}
.toolbar a{color:#25554A}
.sheet:last-of-type{break-after:auto;page-break-after:auto}
@media print{body{background:#fff}.sheet{margin:0}.toolbar.noprint{display:none}}
"""


def main(today=None):
    deliverables, tasks, people, site = load()
    today = today or date.today()
    asof = site.get("official_schedule_as_of", "")
    note = f"Official dates from the EcoCAR Team Dashboard dated {d(asof).day} {d(asof).strftime('%b %Y')}." if asof else ""
    tech = gantt_page("Year 1 Gantt: vehicle track and program", ["pgm", "vse", "vhi", "pcm", "hvb"], deliverables, tasks, people, today, note)
    biz = gantt_page("Year 1 Gantt: PIT, MarCom and business", ["biz"], deliverables, tasks, people, today, note)
    cals = calendar_pages(deliverables, tasks, people, today)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Year 1 Schedule — Cal State LA EcoCAR</title><style>{CSS}</style></head><body>
<div class="toolbar noprint"><a href="index.html">&larr; Back to the execution hub</a><span>Print landscape, Letter, margins none · built {today.isoformat()}</span><button onclick="window.print()">Print or save as PDF</button></div>
{tech}{biz}{"".join(cals)}
</body></html>"""
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"Built {OUT.relative_to(ROOT)}: 2 Gantt pages, {len(cals)} calendar months.")


if __name__ == "__main__":
    main()
