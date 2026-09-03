# First-time setup

## 1. Get the repository

In GitHub Desktop, choose **File -> Clone repository**, select `GeoffChavez/taskline`, and choose a local folder. If this repository is already open and shows the `main` branch, skip this step.

## 2. Confirm Python

Choose **Repository -> Open in Command Prompt**, then run:

```text
python --version
```

Python 3.10 or newer is recommended. The build uses only Python's standard library.

## 3. Build the site

In the same window, run:

```text
python build.py
```

A successful build writes `docs/index.html` and reports the number of tasks, deliverables, roles, and onboarding choices. Warnings are intentional review items; errors must be fixed before publishing.

## 4. Preview

In File Explorer, open the repository folder, then open `docs/index.html`. Test the section tabs, owner filters, a deliverable card, and a timeline task.

## 5. Publish an update

Return to GitHub Desktop. Review the changed files, enter a specific summary, click **Commit to main**, then click **Push origin**.

## 6. Keep private material private

Never copy official PDFs, Word requirements, scorecards, OEM data, raw vehicle logs, submission drafts, contact lists, or private links into this public repository. Store those in the approved Box or Teams location and add only a safe label or controlled link in `data/links.json`.
