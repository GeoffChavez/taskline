#!/usr/bin/env python3
"""
Build the EcoCAR Year 1 taskline website.

    python build.py

Reads:   data/schedule.csv, data/people.csv, data/details.json, template.html
Writes:  docs/index.html   (one self-contained file - no server needed)

Nothing else needs editing. To change a date, open data/schedule.csv in Excel,
change the date, save as CSV, and run this again.
"""

import csv, json, datetime, pathlib, sys

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data"
OUT  = ROOT / "docs" / "index.html"

VALID_TYPES = {"bar", "milestone", "freeze", "tbd"}


def read_csv(name):
    with open(DATA / name, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def check(tasks, people):
    """Catch the mistakes that would silently produce a broken chart."""
    problems, keys = [], {p["key"] for p in people}
    seen = set()
    for i, t in enumerate(tasks, start=2):          # row 2 = first data row in Excel
        where = f"schedule.csv row {i} ({t.get('task','?')[:40]})"
        if not t.get("id"):
            problems.append(f"{where}: missing id")
        elif t["id"] in seen:
            problems.append(f"{where}: duplicate id '{t['id']}'")
        else:
            seen.add(t["id"])

        if t.get("type") not in VALID_TYPES:
            problems.append(f"{where}: type must be one of {sorted(VALID_TYPES)}, got '{t.get('type')}'")

        for field in ("start", "end"):
            v = (t.get(field) or "").strip()
            if not v:
                if field == "start":
                    problems.append(f"{where}: start date is required")
                continue
            try:
                datetime.date.fromisoformat(v)
            except ValueError:
                problems.append(f"{where}: {field} '{v}' is not YYYY-MM-DD")

        if t.get("type") != "milestone" and not (t.get("end") or "").strip():
            problems.append(f"{where}: a '{t['type']}' row needs an end date")

        s, e = (t.get("start") or "").strip(), (t.get("end") or "").strip()
        if s and e and e < s:
            problems.append(f"{where}: end {e} is before start {s}")

        for k in (t.get("owners") or "").split():
            if k not in keys:
                problems.append(f"{where}: owner '{k}' is not in people.csv")
    return problems


def main():
    tasks   = read_csv("schedule.csv")
    people  = read_csv("people.csv")
    details = json.loads((DATA / "details.json").read_text(encoding="utf-8"))

    problems = check(tasks, people)
    if problems:
        print("Build stopped. Fix these and run again:\n")
        for p in problems:
            print("  -", p)
        sys.exit(1)

    unknown = set(details) - {t["id"] for t in tasks}
    if unknown:
        print("Note: details.json has entries with no matching task id:", ", ".join(sorted(unknown)))

    payload = {
        "today":   datetime.date.today().isoformat(),
        "built":   datetime.date.today().strftime("%d %B %Y"),
        "people":  {p["key"]: {"n": p["name"], "r": p["role"], "c": p["color"]} for p in people},
        "tasks":   tasks,
        "details": details,
    }

    html = (ROOT / "template.html").read_text(encoding="utf-8").replace(
        "/*__DATA__*/", "const DATA = " + json.dumps(payload, ensure_ascii=False) + ";", 1)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")

    lanes = {}
    for t in tasks:
        lanes[t["lane"]] = lanes.get(t["lane"], 0) + 1
    print(f"Built {OUT.relative_to(ROOT)}  -  {len(tasks)} tasks, "
          f"{len(details)} with detail, {len(people)} people")
    print("   by lane:", ", ".join(f"{k}={v}" for k, v in sorted(lanes.items())))
    print("\nOpen docs/index.html to check it, then commit and push.")


if __name__ == "__main__":
    main()
