#!/usr/bin/env python3
"""Build and validate the EcoCAR Year 1 Execution Hub.

Usage:
    python build.py          # validate and write docs/index.html
    python build.py --check  # validate only (used by GitHub Actions)

The public site is generated from small CSV/JSON files in data/. Official source
documents and submission artifacts do not belong in this public repository.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import pathlib
import re
from collections import Counter


ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data"
OUT = ROOT / "docs" / "index.html"

VALID_TYPES = {"bar", "milestone", "freeze", "tbd"}
VALID_TASK_STATUS = {"Not started", "Ready", "In progress", "Verify", "Blocked", "Done"}
VALID_HEALTH = {"green", "yellow", "red", "gray"}
VALID_ROLE_STATUS = {"Filled", "Confirm", "Open"}
VALID_DECISION_STATUS = {"Open", "Proposed", "Closed"}
VALID_RISK_STATES = {"Draft", "Open", "Monitoring", "Mitigated", "Closed"}
SENSITIVE_EXTENSIONS = {".docx", ".xlsx", ".xls", ".pdf", ".pptx", ".mat", ".mf4", ".mp4"}


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def read_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def parse_date(value: str, where: str, problems: list[str], required: bool = True):
    value = (value or "").strip()
    if not value:
        if required:
            problems.append(f"{where}: date is required")
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        problems.append(f"{where}: '{value}' is not YYYY-MM-DD")
        return None


def business_days_before(value: str, count: int) -> str:
    current = dt.date.fromisoformat(value)
    remaining = count
    while remaining:
        current -= dt.timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current.isoformat()


def unique_ids(rows, field, where, problems):
    seen = set()
    for index, row in enumerate(rows, start=2):
        value = (row.get(field) or "").strip() if isinstance(row, dict) else ""
        if not value:
            problems.append(f"{where} row {index}: missing {field}")
        elif value in seen:
            problems.append(f"{where} row {index}: duplicate {field} '{value}'")
        seen.add(value)
    return seen


def validate(bundle):
    problems, warnings = [], []
    tasks = bundle["tasks"]
    people = bundle["people_rows"]
    person_keys = unique_ids(people, "key", "people.csv", problems)
    task_ids = unique_ids(tasks, "id", "schedule.csv", problems)
    details = bundle["details"]

    for index, task in enumerate(tasks, start=2):
        where = f"schedule.csv row {index} ({task.get('task', '?')[:45]})"
        if task.get("type") not in VALID_TYPES:
            problems.append(f"{where}: invalid type '{task.get('type')}'")
        start = parse_date(task.get("start", ""), f"{where} start", problems)
        end = parse_date(task.get("end", ""), f"{where} end", problems, required=False)
        if task.get("type") != "milestone" and not end:
            problems.append(f"{where}: non-milestone rows require an end date")
        if start and end and end < start:
            problems.append(f"{where}: end precedes start")
        owners = (task.get("owners") or "").split()
        if not owners:
            problems.append(f"{where}: at least one owner is required")
        for owner in owners:
            if owner not in person_keys:
                problems.append(f"{where}: unknown owner '{owner}'")

    unknown_details = set(details) - task_ids
    if unknown_details:
        warnings.append("details.json contains unmatched task IDs: " + ", ".join(sorted(unknown_details)))

    deliverable_ids = set()
    for index, item in enumerate(bundle["deliverables"], start=1):
        where = f"deliverables.json item {index}"
        item_id = item.get("id", "")
        if not item_id:
            problems.append(f"{where}: missing id")
        elif item_id in deliverable_ids:
            problems.append(f"{where}: duplicate id '{item_id}'")
        deliverable_ids.add(item_id)
        due = parse_date(item.get("due", ""), f"{where} due", problems)
        owner = item.get("owner", "")
        if owner not in person_keys:
            problems.append(f"{where}: unknown accountable owner '{owner}'")
        for contributor in item.get("contributors", []):
            if contributor not in person_keys:
                problems.append(f"{where}: unknown contributor '{contributor}'")
        schedule_id = item.get("schedule_id", "")
        if schedule_id not in task_ids:
            problems.append(f"{where}: schedule_id '{schedule_id}' is missing")
        else:
            schedule_task = next(task for task in tasks if task["id"] == schedule_id)
            if due and schedule_task.get("start") != due.isoformat():
                problems.append(
                    f"{where}: due date {due.isoformat()} differs from schedule milestone "
                    f"{schedule_task.get('start')}"
                )
        if not item.get("artifacts") or not item.get("done"):
            problems.append(f"{where}: artifacts and completion checks are required")

    statuses = bundle["statuses"]
    unique_ids(statuses, "task_id", "task_status.csv", problems)
    for index, row in enumerate(statuses, start=2):
        where = f"task_status.csv row {index}"
        if row.get("task_id") not in task_ids:
            problems.append(f"{where}: unknown task_id '{row.get('task_id')}'")
        if row.get("status") not in VALID_TASK_STATUS:
            problems.append(f"{where}: invalid status '{row.get('status')}'")
        if row.get("health") not in VALID_HEALTH:
            problems.append(f"{where}: invalid health '{row.get('health')}'")
        try:
            progress = int(row.get("progress", ""))
            if not 0 <= progress <= 100:
                raise ValueError
        except ValueError:
            problems.append(f"{where}: progress must be an integer from 0 to 100")
        parse_date(row.get("updated", ""), f"{where} updated", problems)

    role_ids = unique_ids(bundle["roles"], "role_id", "roles.csv", problems)
    for index, row in enumerate(bundle["roles"], start=2):
        where = f"roles.csv row {index}"
        if row.get("status") not in VALID_ROLE_STATUS:
            problems.append(f"{where}: invalid status '{row.get('status')}'")
        for field in ("owner_key", "backup_key"):
            owner = (row.get(field) or "").strip()
            if owner and owner not in person_keys:
                problems.append(f"{where}: unknown {field} '{owner}'")
        parse_date(row.get("decision_due", ""), f"{where} decision_due", problems)
    if not role_ids:
        problems.append("roles.csv: no roles found")

    unique_ids(bundle["risks"], "risk_id", "risks.csv", problems)
    for index, row in enumerate(bundle["risks"], start=2):
        where = f"risks.csv row {index}"
        if row.get("state") not in VALID_RISK_STATES:
            problems.append(f"{where}: invalid state '{row.get('state')}'")
        if row.get("owner_key") not in person_keys:
            problems.append(f"{where}: unknown owner '{row.get('owner_key')}'")
        parse_date(row.get("next_review", ""), f"{where} next_review", problems)

    unique_ids(bundle["decisions"], "decision_id", "decisions.csv", problems)
    for index, row in enumerate(bundle["decisions"], start=2):
        where = f"decisions.csv row {index}"
        if row.get("status") not in VALID_DECISION_STATUS:
            problems.append(f"{where}: invalid status '{row.get('status')}'")
        if row.get("owner_key") not in person_keys:
            problems.append(f"{where}: unknown owner '{row.get('owner_key')}'")
        parse_date(row.get("needed_by", ""), f"{where} needed_by", problems)

    unique_ids(bundle["onboarding"], "id", "onboarding.csv", problems)
    for index, row in enumerate(bundle["onboarding"], start=2):
        if row.get("mentor_key") not in person_keys:
            problems.append(f"onboarding.csv row {index}: unknown mentor '{row.get('mentor_key')}'")

    unique_ids(bundle["drivers"], "id", "strategic_drivers.csv", problems)
    for index, row in enumerate(bundle["drivers"], start=2):
        if row.get("owner_key") not in person_keys:
            problems.append(f"strategic_drivers.csv row {index}: unknown owner '{row.get('owner_key')}'")

    for key, link in bundle["links"].items():
        url = link.get("url", "")
        if re.search(r"(^|[\\/])[A-Za-z]:[\\/]", url) or url.lower().startswith("file:"):
            problems.append(f"links.json {key}: local file paths cannot be published")
        owner = link.get("owner", "")
        if owner and owner not in person_keys:
            problems.append(f"links.json {key}: unknown owner '{owner}'")

    for path in (ROOT / "docs").rglob("*"):
        if path.is_file() and path.suffix.lower() in SENSITIVE_EXTENSIONS:
            problems.append(f"docs/{path.relative_to(ROOT / 'docs')}: source/submission files cannot be published")

    marcom = next(p for p in people if p["key"] == "mar")
    for item in bundle["deliverables"]:
        if item["owner"] == "mar" and marcom["role"] == "UNFILLED":
            warnings.append(f"Ownership gap: {item['title']} is assigned to the unfilled MarCom role")

    return problems, warnings


def load_bundle():
    people_rows = read_csv("people.csv")
    people = {
        row["key"]: {"name": row["name"], "role": row["role"], "color": row["color"]}
        for row in people_rows
    }
    return {
        "site": read_json("site.json"),
        "people_rows": people_rows,
        "people": people,
        "tasks": read_csv("schedule.csv"),
        "details": read_json("details.json"),
        "deliverables": read_json("deliverables.json"),
        "statuses": read_csv("task_status.csv"),
        "roles": read_csv("roles.csv"),
        "onboarding": read_csv("onboarding.csv"),
        "drivers": read_csv("strategic_drivers.csv"),
        "risks": read_csv("risks.csv"),
        "decisions": read_csv("decisions.csv"),
        "links": read_json("links.json"),
    }


def build_payload(bundle):
    def clean_markup(value):
        return re.sub(r"<[^>]+>", "", html.unescape(str(value or ""))).strip()

    def with_gates(item):
        copy = dict(item)
        copy["gates"] = [
            {"label": "Content complete", "date": business_days_before(item["due"], 15)},
            {"label": "Peer review", "date": business_days_before(item["due"], 10)},
            {"label": "Freeze / red team", "date": business_days_before(item["due"], 5)},
            {"label": "Submission ready", "date": business_days_before(item["due"], 2)},
            {"label": "Official due", "date": item["due"]},
        ]
        return copy

    deliverables = [with_gates(item) for item in bundle["deliverables"]]
    linked_tasks = {item["schedule_id"] for item in bundle["deliverables"]}
    for task in bundle["tasks"]:
        detail = bundle["details"].get(task["id"], {})
        is_general_commitment = (
            task.get("lane") == "biz"
            and task.get("type") == "milestone"
            and (detail.get("org") or task["id"].endswith("-submission"))
        )
        if task["id"] in linked_tasks or not is_general_commitment:
            continue
        owner_keys = task.get("owners", "").split()
        due = task["start"]
        artifacts = []
        for artifact in detail.get("subs", []):
            artifacts.append(
                {
                    "name": clean_markup(artifact.get("a", "Submission artifact")),
                    "format": clean_markup(artifact.get("f", "Confirm with organizer")),
                    "limit": clean_markup(artifact.get("l", "Confirm current limits")),
                    "filename": clean_markup(artifact.get("fn", "Confirm current naming convention")),
                    "oem": clean_markup(artifact.get("oem", "Confirm")),
                }
            )
        if not artifacts:
            artifacts = [
                {
                    "name": "Controlled submission package",
                    "format": "Confirm current request",
                    "limit": "Confirm current limits",
                    "filename": "Confirm current naming convention",
                    "oem": "No unless explicitly permitted",
                }
            ]
        done = [clean_markup(value) for value in detail.get("content", [])]
        if not done:
            done = [
                "Re-open the latest controlled requirement and scorecard",
                "Complete the required content and supporting evidence",
                "Pass factual, compliance, naming, size, and submission review",
            ]
        deliverables.append(
            with_gates(
                {
                    "id": "general-" + task["id"],
                    "title": clean_markup(task["task"]),
                    "lane": task["lane"],
                    "due": due,
                    "due_time": clean_markup(detail.get("time") or task.get("label") or "Confirm time"),
                    "scoring": clean_markup(
                        " - ".join(value for value in (detail.get("size"), detail.get("dl")) if value)
                        or "Team leadership requirement"
                    ),
                    "owner": owner_keys[0],
                    "contributors": owner_keys[1:],
                    "schedule_id": task["id"],
                    "source": "General Deliverables Rev 2 or applicable Team Leadership Requirement; Team Dashboard 2026-08-28",
                    "purpose": clean_markup(detail.get("what") or "Complete the stated Year 1 commitment."),
                    "artifacts": artifacts,
                    "done": done,
                }
            )
        )
    deliverables.sort(key=lambda item: (item["due"], item["title"]))

    status_map = {row["task_id"]: row for row in bundle["statuses"]}
    task_counts = Counter()
    for task in bundle["tasks"]:
        for owner in task.get("owners", "").split():
            task_counts[owner] += 1

    return {
        "generated": dt.datetime.now().astimezone().isoformat(timespec="minutes"),
        "today": dt.date.today().isoformat(),
        "site": bundle["site"],
        "people": bundle["people"],
        "tasks": bundle["tasks"],
        "details": bundle["details"],
        "deliverables": deliverables,
        "statuses": status_map,
        "roles": bundle["roles"],
        "onboarding": bundle["onboarding"],
        "drivers": bundle["drivers"],
        "risks": bundle["risks"],
        "decisions": bundle["decisions"],
        "links": bundle["links"],
        "task_counts": dict(task_counts),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate data without writing HTML")
    args = parser.parse_args()

    bundle = load_bundle()
    problems, warnings = validate(bundle)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if problems:
        print("Build stopped. Fix these items:")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(1)

    if args.check:
        print(
            f"Validation passed: {len(bundle['tasks'])} tasks, "
            f"{len(bundle['deliverables'])} deliverables, {len(bundle['roles'])} roles."
        )
        return

    payload = build_payload(bundle)
    template = (ROOT / "template.html").read_text(encoding="utf-8")
    if "/*__DATA__*/" not in template:
        raise SystemExit("template.html is missing the data marker")
    html = template.replace(
        "/*__DATA__*/",
        "const DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";",
        1,
    )
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(
        f"Built {OUT.relative_to(ROOT)}: {len(bundle['tasks'])} tasks, "
        f"{len(payload['deliverables'])} deliverables/commitments, {len(bundle['roles'])} roles, "
        f"{len(bundle['onboarding'])} first wins."
    )
    if warnings:
        print(f"Review {len(warnings)} warning(s) above before publishing.")


if __name__ == "__main__":
    main()
