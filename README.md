# Cal State LA EcoCAR - Year 1 Execution Hub

This repository generates a public, read-only execution hub for the Cal State LA EcoCAR Innovation Challenge team. It connects the Year 1 baseline to accountable owners, official deliverable summaries, internal review gates, onboarding work, roles, and public-safe project controls.

Live site: https://geoffchavez.github.io/taskline/

## What this system is

- **GitHub repository:** version-controlled team baseline and public-safe status.
- **GitHub Pages:** easy-to-read navigation and accountability view.
- **Planner or equivalent:** daily checklists, comments, and personal reminders.
- **Box or Teams:** controlled official requirements, scorecards, OEM-sensitive data, drafts, contact details, and final submissions.

Do not upload organizer source documents or submission artifacts to this public repository. The source documents include use restrictions, and several technical submissions permit OEM-sensitive information.

## Source-of-truth order

1. Latest EcoCAR revision and scorecard.
2. EIC Team Dashboard for official dates.
3. Approved team baseline in this repository.
4. Weekly execution status.

When a higher source changes, update affected cards and tasks, rebuild, and record the revision in the commit message.

## Normal update

1. In GitHub Desktop, **Fetch origin**, then **Pull origin** if offered.
2. Edit the smallest relevant file in `data/`.
3. Open **Repository -> Open in Command Prompt**.
4. Run `python build.py`.
5. Open `docs/index.html` and check the changed page.
6. Commit with a specific message and **Push origin**.

GitHub Pages updates after the pushed commit is processed.

## Data map

| Need to change | File |
|---|---|
| Baseline task, date, lane, or owner | `data/schedule.csv` |
| Weekly status, health, progress, or next action | `data/task_status.csv` |
| Official artifact summary and definition of done | `data/deliverables.json` |
| People | `data/people.csv` |
| Required and delivery-critical roles | `data/roles.csv` |
| Strategic drivers | `data/strategic_drivers.csv` |
| New-member first wins | `data/onboarding.csv` |
| Public-safe risks and decisions | `data/risks.csv`, `data/decisions.csv` |
| Controlled-system links | `data/links.json` |
| Site identity and source dates | `data/site.json` |
| Supporting task detail | `data/details.json` |

The first key in the `owners` field of `schedule.csv` is the accountable owner. Additional keys are contributors. Every key must exist in `data/people.csv`.

## Built-in quality controls

`python build.py` stops when it finds:

- duplicate IDs;
- invalid or reversed dates;
- unknown or missing owners;
- invalid task status, health, role, risk, or decision values;
- deliverable deadlines that disagree with the matching schedule milestone;
- missing deliverable artifacts or completion checks;
- local file paths in published links; or
- common sensitive file formats inside `docs/`.

It also calculates five deliverable gates: content complete at T-15 business days, peer review at T-10, freeze/red team at T-5, submission ready at T-2, and official due at T-0.

## Operating rules

- One accountable owner per result; contributors support the owner.
- No more than two active priority items per person without an explicit leadership tradeoff.
- A task is not done until its acceptance checks and evidence are complete.
- Yellow means a credible recovery plan exists. Red means intervention is needed. Neither is punished for being honest.
- New members receive a bounded first win within seven days.
- Any Senior Design overlap receives a one-page, faculty-approved boundary covering scope, ownership, evidence reuse, and acceptance criteria.
- Decisions, changed dates, and owners are recorded within 24 hours.

## Initial leadership decisions

Before expanding the task inventory, the team should:

1. confirm every required role and backup;
2. approve the five strategic drivers;
3. validate the draft risks and decisions;
4. add the approved controlled-system links;
5. confirm every lead's dates, dependencies, academic conflicts, and capacity;
6. define the Senior Design boundary for each overlapping work package; and
7. re-baseline within two business days of every new official revision.

See [SETUP.md](SETUP.md) for first-time setup and [CONTRIBUTING.md](CONTRIBUTING.md) for the change workflow.
