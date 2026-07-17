---
name: update_project_docs
description: >
  Automatically update the project's troubleshooting_log.md and/or
  dashboard_phase1_plan.md whenever a new bug is found and solved, an existing
  plan section changes, or a new implementation decision is made. Triggers on
  phrases like "update the log", "add to troubleshooting", "log this bug",
  "update the plan", "mark as done", "plan is complete", or whenever the agent
  independently finds and fixes a bug during a session.
---

# Skill: Update Project Docs

This skill keeps two markdown files in sync with the current project state:

| File | Purpose |
|---|---|
| `troubleshooting_log.md` | Running record of every bug found, its root cause, and how it was fixed |
| `dashboard_phase1_plan.md` | Implementation plan with completion status |

---

## When to Trigger

Invoke this skill automatically whenever:

1. **A bug is found and fixed** during any task — add a new numbered entry to `troubleshooting_log.md`.
2. **A plan section is completed** — update the relevant section in `dashboard_phase1_plan.md` with a checkmark or completion note.
3. **A new architectural decision is made** — add a note to the relevant plan section.
4. **The user explicitly asks** to "update the log", "log this bug", "mark as done", etc.

---

## Locating the Files

Both files live at the workspace root:

    d:\SideProject\07MainAvalonia\troubleshooting_log.md
    d:\SideProject\07MainAvalonia\dashboard_phase1_plan.md

Always read the current file content first before appending, to avoid duplicates
and to pick the correct next bug number.

---

## Troubleshooting Log Entry Format

Append new bugs to the BOTTOM of troubleshooting_log.md using this template:

    ---

    ## Bug N - Short descriptive title

    ### Symptom
    What the user saw or what error message appeared.

    ### Root Cause
    Technical explanation of why it happened.

    ### Fix
    What was changed and in which file(s). Include code snippets where helpful.

Rules:
- N = next sequential bug number (read existing file to determine).
- Keep Symptom short (1-3 lines). Use code blocks for error messages.
- Root Cause should explain WHY, not just WHAT.
- Fix should name the exact file(s) changed.
- Append a "Last updated: YYYY-MM-DD" line at the very bottom after each update.

---

## Plan File Update Format

When a task from dashboard_phase1_plan.md is completed:
- Change [ ] to [x] or prefix the section heading with a checkmark.
- Add a one-line note below the item: Completed YYYY-MM-DD - brief description.

When a plan item is partially done or blocked:
- Add a note below the item explaining the status.

---

## Execution Steps

1. READ the current troubleshooting_log.md to find the last bug number.
2. COMPOSE the new entry using the template above.
3. APPEND it using run_command with PowerShell Add-Content (UTF-8).
4. If a plan item was also completed, READ dashboard_phase1_plan.md and update it.
5. CONFIRM to the user: "Added Bug N to troubleshooting_log.md"

---

## Example PowerShell Append Command

    $entry = @"
    
    ---
    
    ## Bug N - Title here
    
    ### Symptom
    ...
    
    ### Root Cause
    ...
    
    ### Fix
    ...
    
    *Last updated: YYYY-MM-DD*
    "@
    Add-Content -Path "D:\SideProject\07MainAvalonia\troubleshooting_log.md" -Value $entry -Encoding UTF8
