"""Process a "[Claim]" GitHub issue against data/starter_tasks.csv.

Runs inside the claim-task GitHub Action. Reads the issue from environment
variables (never from the command line), applies the claim rules, rewrites the
CSV if the claim is valid, and writes a reply for the issue to claim_result.md.

Exit code 0 = claim accepted, 3 = claim rejected (the reply says why).

Rules (settings live in data/site.json under "claims"):
  * The task must exist and not be Done.
  * First come, first served: a task whose owner slots are full is refused.
    Slots come from the capacity column: "One owner" = 1, "Three owners" = 3,
    "Several owners ..." = no fixed limit.
  * One GitHub user cannot claim the same task twice.
  * A GitHub user can hold at most `limit_per_person` unfinished claims.
  * mode "members" accepts only repository owners, members and collaborators;
    mode "anyone" accepts any GitHub user.

Local test:  ISSUE_BODY="..." ISSUE_AUTHOR=octocat AUTHOR_ASSOCIATION=NONE \
             python tools/claim_task.py
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "starter_tasks.csv"
SITE_PATH = ROOT / "data" / "site.json"
RESULT_PATH = ROOT / "claim_result.md"

NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                "seven": 7, "eight": 8, "nine": 9, "ten": 10}
NAME_OK = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ .'\-]{1,59}$")
SEP = "; "


def section(body: str, heading: str) -> str:
    """Return the text under '### heading' in a rendered issue form."""
    match = re.search(rf"^###\s+{re.escape(heading)}\s*$(.*?)(?=^###\s|\Z)", body, re.M | re.S)
    if not match:
        return ""
    text = match.group(1).strip()
    return "" if text == "_No response_" else text


def split(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split(";") if x.strip()]


def slots(capacity: str) -> int | None:
    words = (capacity or "").strip().lower().split()
    if not words:
        return 1
    first = words[0]
    if first.isdigit():
        return int(first)
    if first in NUMBER_WORDS:
        return NUMBER_WORDS[first]
    return None  # "Several owners ..." -> no fixed limit


def finish(ok: bool, message: str) -> None:
    RESULT_PATH.write_text(message.strip() + "\n", encoding="utf-8")
    print(message)
    sys.exit(0 if ok else 3)


def main() -> None:
    body = os.environ.get("ISSUE_BODY", "")
    author = (os.environ.get("ISSUE_AUTHOR") or "").strip()
    association = (os.environ.get("AUTHOR_ASSOCIATION") or "NONE").strip().upper()
    site = json.loads(SITE_PATH.read_text(encoding="utf-8"))
    rules = site.get("claims", {})
    mode = rules.get("mode", "anyone")
    limit = int(rules.get("limit_per_person", 2))
    pages = site.get("pages_url", "")

    if mode == "members" and association not in {"OWNER", "MEMBER", "COLLABORATOR"}:
        finish(False, "Claims are limited to team members on this repository. Ask the project manager to add your GitHub account, then submit again.")

    task_id = section(body, "Task ID").upper().replace(" ", "")
    name = " ".join(section(body, "Your name").split())
    if not re.fullmatch(r"ST-\d{1,3}", task_id):
        finish(False, f"`{task_id[:20] or 'blank'}` is not a task ID. Use the ID on the card, for example `ST-17`.")
    if not NAME_OK.fullmatch(name):
        finish(False, "Please give your first and last name using letters, spaces, hyphens or apostrophes only (2-60 characters).")
    if not author:
        finish(False, "Could not read your GitHub username.")

    raw = CSV_PATH.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    fields = list(rows[0].keys()) if rows else []
    if "claimed_github" not in fields:
        fields.append("claimed_github")

    task = next((r for r in rows if r["id"].upper() == task_id), None)
    if task is None:
        finish(False, f"There is no task `{task_id}` on the site. Check the ID on the card.")
    if task["status"] == "Done":
        finish(False, f"`{task_id}` is already done.")

    handles = [h.lower() for h in split(task.get("claimed_github", ""))]
    names = split(task.get("claimed_by", ""))
    cap = slots(task.get("capacity", ""))
    if author.lower() in handles:
        finish(False, f"You already hold `{task_id}`.")
    if task["status"] == "Claimed" or (cap is not None and len(names) >= cap):
        finish(False, f"`{task_id}` is already taken by {', '.join(names) or 'someone else'}. Pick another open task on the site.")

    active = [r["id"] for r in rows if r["status"] != "Done"
              and author.lower() in [h.lower() for h in split(r.get("claimed_github", ""))]]
    if len(active) >= limit:
        finish(False, f"You already hold {len(active)} unfinished tasks ({', '.join(active)}); the limit is {limit}. Finish one first, or ask your mentor to mark it Done.")

    names.append(name)
    task["claimed_by"] = SEP.join(names)
    task["claimed_github"] = SEP.join(split(task.get("claimed_github", "")) + [author])
    if cap is not None and len(names) >= cap:
        task["status"] = "Claimed"

    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in fields})
    CSV_PATH.write_bytes(out.getvalue().encode("utf-8"))

    left = "" if cap is None else f" ({cap - len(names)} owner slot(s) left)" if len(names) < cap else ""
    finish(True, f"""
**{task_id} is yours, {name}.**{left}

- Task: {task['title']}
- Done when: {task['done_when']}
- Next step: message your mentor within one week, and show the result at a Friday meeting.

Your name appears on the site in about two minutes: {pages}
""")


if __name__ == "__main__":
    main()
