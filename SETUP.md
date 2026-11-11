# Setup instructions (for Claude Code)

You are setting up the Claude Study Vault for the user. Follow these steps in order. Talk to the user in plain, friendly language: they may not be technical. **Ask before creating, copying, moving or deleting anything**, and never delete or overwrite the user's existing files.

This repository's `vault/` folder is a ready-made Obsidian vault: folder structure, note templates, Dataview dashboards, and the study skills in `vault/.claude/`.

## 1. Check the basics

Run these and tell the user what's missing (don't install anything without asking):

- `git --version`: needed to download the repo. If missing, point them to https://git-scm.com/downloads.
- `python3 --version` (Windows: `python --version`): needs **3.9 or newer**. Used by the Canvas and file-reading helpers. If missing, point them to https://www.python.org/downloads/ (Windows: tick "Add python.exe to PATH" in the installer).
- Obsidian: ask if it's installed. If not: https://obsidian.md/download.

## 2. Get the files

If the user already downloaded the repo (e.g. as a ZIP from GitHub, unzipped), ask for that folder's path and use it as `<clone>`. Otherwise clone it into a temporary folder (not into a vault):

```bash
git clone --depth 1 https://github.com/ODANISORI/claude-tutor-skill.git "<temp folder>/claude-tutor-skill"
```

The repo is **private**: cloning only works if the owner invited the user (GitHub → the invite email or github.com/notifications → Accept) and git is logged in to GitHub. If the clone fails with an authentication error or "Repository not found":
- Don't keep retrying and never ask for their GitHub password or token in chat.
- Tell them to either (a) accept the invite, then run the same `git clone` command themselves in a terminal (it opens a GitHub login in the browser), or (b) open https://github.com/ODANISORI/claude-tutor-skill in the browser while logged in, click **Code → Download ZIP**, unzip it, and tell you the folder path.

Read `README.md` from `<clone>` so you know what's in it.

## 3. Choose where the vault goes

Ask the user which they want:

- **A. A new vault** (recommended). Suggest `~/Documents/Study Vault` (Windows: `C:\Users\<name>\Documents\Study Vault`), or let them pick. If that folder already exists and isn't empty, don't use it; ask for another name.
- **B. Add to an existing vault.** Ask for its path. Their structure is different, so explain the plan first: the numbered folders (`000 Unorganised` ... `900 System`) are added next to their existing folders, existing files are never overwritten, and their own notes stay where they are (step 6 can sort them later). If the vault already has a `CLAUDE.md` or `.claude/` folder, show them what's there and ask how to merge; don't replace it.

## 4. Copy the vault

Copy **the contents** of `vault/` (including the hidden `.claude/`, `.obsidian/` and `.gitignore`) into the chosen folder.

- Copy without overwriting: on macOS/Linux `cp -Rn "<clone>/vault/." "<target>/"`; on Windows PowerShell use `robocopy "<clone>\vault" "<target>" /E /XC /XN /XO`.
- For option B, skip `.obsidian/` if the vault already has one (their Obsidian settings stay), and tell them to set the attachment folder (`Images`) and the Templater template folder (`900 System/Templates`) themselves in Obsidian's settings.
- Remove the `.gitkeep` files only if the user asks; they're harmless (Obsidian doesn't show them).
- Then list what was created.

## 5. Obsidian plugins

Tell the user to:

1. Open Obsidian → **Open folder as vault** → choose the vault folder.
2. Settings → **Community plugins** → **Turn on community plugins** (leaves Restricted mode).
3. **Browse** and install + enable **Dataview** and **Templater**. The dashboards need Dataview; the templates use Templater. Templater is already pointed at `900 System/Templates`.
4. Open `000 Unorganised/Start Here.md`.

## 6. Personalise

Ask, one at a time:

1. **Which courses are you taking?** Create one folder per course in `100 Courses/` (after they confirm the list).
2. **Do you want to keep your notes in Git?** If yes and the vault isn't a repo yet: `git init`, then commit everything with the message `Set up Claude Study Vault`. Mention the Obsidian Git plugin for automatic backups, and that if they push to GitHub the repo should be **private**.
3. **(Option B only) Sort existing notes?** If they want, propose where each existing note should go (lectures → `100 Courses/<course>/`, ideas/definitions → `200 Concepts/`, etc.). List the moves and wait for a yes. **Move notes inside Obsidian** (drag in the file list), not on disk, so links update; or, if they want you to do it, warn first that links to moved notes may break. Never delete anything.
4. **Do you use Canvas LMS?** If yes, tell them to run `/canvas setup` after the restart (step 7). It walks them through the token safely. **Never** ask for or accept a Canvas token in chat.

## 7. Finish

- The study skills only load when Claude Code starts **inside the vault folder**. Tell the user to close this session and start Claude Code again from the vault folder (in the desktop app: open the vault folder as the project).
- Then they can try:
  - `/learn <topic or file>`: notes, teaching, then a quiz
  - `/review`: quiz whatever is due
  - `/canvas setup`: connect Canvas
- Offer to delete the temporary clone from step 2 (move it to the Trash).

Summarise what was set up and where the vault is.
