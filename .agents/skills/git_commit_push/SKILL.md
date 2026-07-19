---
name: git_commit_push
description: >
  Automatically commit and push the current changes to git whenever the user confirms that the changes are ok or working. Triggers on phrases like "code is ok", "looks good", "it works", "commit and push", or after a successful manual verification.
---

# Skill: Git Commit & Push

This skill automates git version control operations to capture working changes and upload them to the remote repository.

---

## When to Trigger

Invoke this skill whenever:
1. **The user confirms changes are correct** by saying phrases like:
   - "code is ok"
   - "it works"
   - "looks good"
   - "commit and push"
2. **After a successful walkthrough and manual verification** where the code compiles and works as expected, and the user approves committing it.

---

## Execution Steps

1. **Check Status**: Run `git status` to see what files are untracked, modified, or staged.
2. **Verify Walkthrough**: Double check that `walkthrough.md` is updated with correct details.
3. **Ask for Commit Message**: Present the list of changed files and ask the user for a commit message, or suggest one based on the recent walkthrough.
4. **Stage Files**: Stage the files for commit:
   ```powershell
   git add .
   ```
5. **Commit Changes**: Commit the staged changes with the message:
   ```powershell
   git commit -m "Your commit message"
   ```
6. **Push Changes**: Push the commit to the remote repository:
   ```powershell
   git push
   ```
7. **Notify the User**: Once completed successfully, notify the user with the commit hash or message.

---

## Example Sequence

### Step 1: User Confirmation
**User says:** *"Everything works now, commit and push it"*

### Step 2: Propose git commands
Run `git status` to see changes:
```powershell
git status
```
Show the summary of files and ask for commit message:
> I will stage all files, commit them with message: `feat: modularize queries and group documents into docs/`, and push to the remote. Do you want to modify this message?

### Step 3: Execute git commands
```powershell
git add .
git commit -m "feat: modularize queries and group documents into docs/"
git push
```
