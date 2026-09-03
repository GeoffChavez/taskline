# Contributing

## Before editing

1. Pull the latest version in GitHub Desktop.
2. Confirm the request with the accountable owner.
3. Check the latest controlled requirement revision and Team Dashboard date.
4. Decide whether the change is public-safe.

## Make a focused change

- Change status in `data/task_status.csv`, not in the generated HTML.
- Change baseline dates and owners in `data/schedule.csv`.
- Change official deliverable summaries only after comparing a new source revision.
- Use `YYYY-MM-DD` dates.
- Use people keys from `data/people.csv`.
- Keep one accountable owner first in a task's `owners` field.
- Do not manually edit `docs/index.html`; it is generated.

## Verify

Run:

```text
python build.py
```

Then open `docs/index.html` and verify the affected section. If a deadline changed, also open the matching deliverable card and timeline row.

## Commit

Good commit messages describe the controlled change:

- `Update PCM tool-check status and next action`
- `Rebaseline CAD readiness from Rev 1`
- `Assign interim MarCom owner`

Avoid vague messages such as `update` or `changes`.

## Review expectations

Changes to official requirements, milestone dates, accountable owners, RYG health, role assignments, or public visibility require review by the affected lead and Project Manager. Safety-related changes also require the appropriate faculty or safety approval.
