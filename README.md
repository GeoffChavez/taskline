# Cal State LA EcoCAR — Year 1 Taskline

The public schedule for the EcoCAR Innovation Challenge, Stellantis track.
Live at **https://<org>.github.io/taskline/**

Anyone can read it without an account. Click any row for the full submission
requirements — file names, formats, size limits, required content, and the
Argonne organizer for that deliverable.

---

## To change a date

1. Open `data/schedule.csv` in Excel.
2. Change the date. Dates are `YYYY-MM-DD`, always.
3. **Save as CSV** (Excel will warn you about "features not compatible" — say yes, keep CSV).
4. Run `python build.py`
5. Commit and push. The site updates in about a minute.

That is the whole workflow. You never edit HTML.

---

## The three data files

| File | What it holds | How often it changes |
|---|---|---|
| `data/schedule.csv` | Every task: dates, owners, which lane | **Weekly.** This is the one you'll touch. |
| `data/people.csv` | Names, roles, avatar colours | When someone joins or a role is named |
| `data/details.json` | Submission requirements per deliverable | Twice a year, when a Rev drops |

### schedule.csv columns

| Column | Meaning |
|---|---|
| `id` | Unique, lowercase, no spaces. Links a row to its entry in `details.json`. Don't reuse. |
| `group` | The section heading it appears under. Rows are grouped in file order — keep rows of the same group together. |
| `lane` | Colour band: `vse` `vhi` `pcm` `hvb` `pgm` `biz` |
| `task` | What shows in bold |
| `label` | The small grey line underneath |
| `type` | `bar` = work over time · `milestone` = a single date · `freeze` = our T−5 review window · `tbd` = dashed, date not published |
| `start` / `end` | `YYYY-MM-DD`. Milestones only need `start`. |
| `owners` | Space-separated keys from `people.csv`, e.g. `fra dor jef` |

### Adding a person

Add a row to `data/people.csv` with a short `key` (3 letters), their name, their
role, and a hex colour. Then use that key in the `owners` column.

---

## Build checks

`build.py` refuses to build and tells you the Excel row number if:

- a date isn't `YYYY-MM-DD` (catches Excel silently writing `15/10/2026`)
- an `end` date is before its `start`
- a `bar`, `freeze` or `tbd` row has no end date
- `type` isn't one of the four valid values
- an owner key isn't in `people.csv`
- two rows share an `id`

If it builds, the site is correct. That's the point of the check.

---

## When a Rev drops

The competition republishes requirements a few times a year. When that happens:

1. Update the dates in `schedule.csv` from the **Team Dashboard** — that is the
   official source for due dates, not the requirement PDFs.
2. Update the changed submission requirements in `details.json`.
3. Rebuild, commit, push.
4. Send the team the link and say what moved.

Re-baseline **once**, the week the Rev lands. Editing twice is how a schedule
loses its authority.

---

## Repo layout

```
data/schedule.csv     the timeline           <- edit this
data/people.csv       who's who              <- edit this
data/details.json     submission specs       <- edit when a Rev drops
template.html         the renderer           <- don't edit unless changing design
build.py              the build              <- run this
docs/index.html       the generated site     <- never edit by hand, it gets overwritten
```

GitHub Pages is set to serve from the `docs/` folder on `main`.

---

## Two rules that keep this alive after we graduate

**This repo belongs to the organization, not to a person.** The next PM gets
added as an owner, not handed a password. That is the whole reason it's here
and not on somebody's laptop.

**`docs/index.html` is generated.** If you edit it directly, your change
disappears the next time anyone runs `build.py`. Change the CSV instead.

---

*Dates and organizer leads come from the EIC Team Dashboard. Submission
requirements come from the STLA Technical Deliverable Requirements and the
General Deliverable Requirements. Every deliverable is submitted to EcoCAR
Box — nothing goes by email, and ZIP files are prohibited on every submission.*
