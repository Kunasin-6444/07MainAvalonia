---
name: update_requirements
description: >
  Automatically update requirement.md whenever a new feature is implemented,
  a bug is found or fixed, a requirement status changes, or scope changes.
  Triggers on phrases like "fix this", "it's not working", "add this feature",
  "mark as done", "it works now", "new bug", "scope change", or whenever the
  agent independently finds and fixes a bug or completes a feature during a session.
---

# update_requirements Skill

## Purpose

Keep `d:\SideProject\07MainAvalonia\docs\requirement.md` always up-to-date as the
single source of truth for Phase 1 feature/bug/infra status. 

## ⚠️ MANDATORY RULE: Ask Before Updating
Before creating or modifying `docs/requirement.md`, **you must ask the user for explicit permission first**. You should present the planned changes and only proceed once approval is given.

## File Location

```
d:\SideProject\07MainAvalonia\docs\requirement.md
```

## When to Trigger

Trigger this skill (read the file, update it) whenever **any** of the following happen:

1. **Bug found** — a new error, crash, or wrong behavior is reported or discovered.
2. **Bug fixed** — a fix is applied and confirmed working (by test, curl, or user confirmation).
3. **Feature completed** — a requirement row transitions from ❌/🚧 to ✅.
4. **Feature broken** — a previously working feature stops working (status → 🔴).
5. **Scope change** — a requirement is added, removed, or redefined.
6. **Infrastructure change** — a package is installed, a config is changed, a service status changes.
7. **User says it works / it doesn't work** — any confirmation from the user.

## Update Rules

### Status Emoji Reference

| Emoji | Meaning |
|-------|---------|
| ✅ Done | Fully implemented and confirmed working |
| 🚧 In Progress | Currently being worked on |
| 🔴 Bug / Open | Known issue, not yet fixed |
| ⚠️ Needs Action | Works but requires a manual step |
| ❌ Not Started | Not yet begun |

### How to Update

1. **Read** the current `requirement.md` using `view_file`.
2. **Identify** which row(s) need updating based on what just happened.
3. **Ask the user** for explicit permission to update the file by showing the planned modifications.
4. **Edit** the file using `replace_file_content` or `multi_replace_file_content` after receiving approval:
   - Change the Status emoji/text
   - Update the Notes column with a brief description of what changed
   - If a new bug is found, add a new row in the **Known Bugs** table with the next available `B##` number
   - If a bug is fixed, change its status to `✅ Fixed` and add the fix summary in Notes
5. **Update** the `*Last updated: YYYY-MM-DD*` line at the bottom with today's date.

### Adding a New Bug Row

```markdown
| B## | <short description> | 🔴 Open | <how it manifests> |
```

When fixed, change to:
```markdown
| B## | <short description> | ✅ Fixed | <fix applied> |
```

### Adding a New Requirement Row

In the appropriate section table:
```markdown
| #.# | <requirement description> | ❌ Not Started | <data source or notes> |
```

## Example Triggers and Actions

**User says:** *"The transaction feed is not showing"*
→ Find requirement 2.4, set status to `🔴 Bug`, add notes, add new Bug row if not already present.

**Agent fixes a bug and confirms with curl/test:**
→ Find the bug row, set to `✅ Fixed`, add fix description to Notes column.

**User says:** *"cryptography package installed, API works now"*
→ Find B10 / infrastructure row for cryptography, set to `✅ Fixed`.

**New feature is requested:**
→ Add a new row in the relevant section with `❌ Not Started`, then update to `🚧 In Progress` while working.

## Important Notes

- Always update `requirement.md` **after** making code changes, not before.
- Keep Notes column **brief** (one line max) — full details go in `troubleshooting_log.md`.
- Never delete rows — only change their status. History must be preserved.
- The file uses standard GitHub-Flavored Markdown tables — preserve column alignment.
