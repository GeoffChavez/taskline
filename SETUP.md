# First-time setup — publishing this to the web

You do this once. About 30 minutes. After that, updating the site is
"edit CSV → run build.py → push."

---

## 1. Make a GitHub Organization, not a personal repo

Go to github.com → your avatar → **Your organizations** → **New organization** →
Free plan.

Name it something the team will recognize: `calstatela-ecocar`.

**Why an organization and not your own account:** repos under a personal account
belong to that person forever. When you graduate, the next PM either gets your
password or loses the site. An organization has owners, and you add the next PM
as an owner. This is the single decision that determines whether this thing
survives you.

Add at least one faculty advisor as an owner on day one. Not later.

---

## 2. Create the repo

Inside the organization → **New repository**

- Name: `taskline`
- **Public** (this matters — GitHub Pages on private repos requires a paid plan)
- Don't add a README, we have one

---

## 3. Push what's in this folder

Install [GitHub Desktop](https://desktop.github.com) if you don't already use
git from the command line. It is genuinely easier for this and the team can use
it too.

**GitHub Desktop:** File → Add local repository → pick this folder → Publish.

**Command line:**

```
git init
git add .
git commit -m "Year 1 taskline"
git branch -M main
git remote add origin https://github.com/calstatela-ecocar/taskline.git
git push -u origin main
```

---

## 4. Turn on Pages

Repo → **Settings** → **Pages**

- Source: **Deploy from a branch**
- Branch: `main`
- Folder: **`/docs`**  ← not root
- Save

Wait about a minute. Your URL is:

```
https://calstatela-ecocar.github.io/taskline/
```

That link is public, needs no account, and works on a phone. Put it in the
Discord channel topic, in your email signature, and on the team webpage.

---

## 5. Check it

Open the URL on your phone. Scroll down — the month headers should stay pinned.
Tap a deliverable — the drawer should open with the submission requirements.
Tap a person's chip — their rows should highlight.

If it looks right, you're done.

---

## Updating from then on

```
1. Open data/schedule.csv in Excel
2. Change what changed
3. Save as CSV
4. python build.py
5. Commit and push (GitHub Desktop: "Commit to main" then "Push origin")
```

Roughly two minutes. Do it once a week, right after the leadership meeting,
so the site is never more than seven days behind reality.

---

## If you get stuck

**"python: command not found"** — install Python from python.org, check the
"Add Python to PATH" box during install.

**Build stops with errors** — that's the point. It tells you the Excel row
number and what's wrong. Fix that row, save, run again.

**Site didn't update** — GitHub takes 30–60 seconds. Then hard-refresh
(Ctrl+Shift+R). Check repo → Actions for a failed deploy.

**Excel mangled the dates** — Excel likes to rewrite `2026-10-15` as
`10/15/2026`. Format the start/end columns as **Text** before typing dates, or
use Google Sheets, which doesn't do this. `build.py` catches it either way and
refuses to build, so it can never reach the site.
