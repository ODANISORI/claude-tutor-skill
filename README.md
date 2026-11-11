# Claude Study Vault

An Obsidian vault plus a set of Claude Code skills that turn your course material into notes, **teach** you every concept, then **quiz you until you actually understand it**, with spaced repetition and a strict independent grader.

## What you get

| Command | What it does |
|---|---|
| `/learn <topic or file>` | Reads almost anything: PDF, PowerPoint, Word, Excel, e-books, photos of notes or whiteboards, Jupyter notebooks, code, transcripts, web links. Writes a full lecture note and a few broad concept notes, teaches each concept with worked examples, then quizzes you. |
| `/quiz <concept>` | 5-8 fresh questions from a **quiz-master** agent, graded by a separate **strict-grader** agent that can't be talked into a pass. Mistakes are logged in the note. |
| `/tutor <concept>` | Socratic tutoring: guiding questions and a hint ladder instead of answers, ending with an explain-it-back. |
| `/review` | Spaced repetition: quizzes everything that's due, weakest first. |
| `/canvas` | Pulls new lectures from **Canvas LMS** and runs `/learn` on them. Your token stays in your OS keychain, never in the vault. |

**The annoying part:** a concept only becomes `mastered` after 3 passed quizzes in a row, spread over at least 3 days, including an explain-it-back and an apply-it-to-something-new question, with no open mistakes. Fail once and it drops back to `shaky` and returns tomorrow.

Progress lives in each note's properties (`status`, `streak`, `next_review`), and the **Study Dashboard** (Dataview) shows what's due, shaky, learning and mastered.

## Vault structure

```
000 Unorganised/        inbox (new notes land here)
100 Courses/<Course>/   lecture notes, one folder per course
200 Concepts/           concept notes you get quizzed on
300 Outputs/            301 Assignments, 302 Projects, 303 Exam Prep (Study Dashboard), 304 Personal Projects
400 Life/               401 Cookbook, 402 Personal Context
900 System/             Templates, Canvas
Images/                 attachments (slides and PDFs get copied here)
.claude/                the skills and agents
CLAUDE.md               vault rules Claude follows
```

## Setup: the easy way

This repo is private: first accept the collaborator invite from GitHub (check your email or github.com/notifications). Then open **Claude Code** (desktop app or terminal) in any folder and paste:

> Set up the Claude Study Vault for me. Clone https://github.com/ODANISORI/claude-tutor-skill into a temporary folder, read SETUP.md from the clone, and walk me through it step by step. Ask me before creating, copying or changing anything, and never delete or overwrite my existing files.

If Claude can't download the repo (login problems), click **Code → Download ZIP** on this page, unzip it, and tell Claude where the folder is. It checks what you have installed, creates the vault (or adds it to your existing one), helps you install the two Obsidian plugins, and sets up your courses.

## Setup: by hand

1. Install [Obsidian](https://obsidian.md), [Claude Code](https://claude.com/claude-code), Git and Python 3.9+.
2. Copy everything inside `vault/` (including the hidden `.claude/` and `.obsidian/` folders) to a new folder, e.g. `~/Documents/Study Vault`.
3. In Obsidian: *Open folder as vault*, then Settings → Community plugins → turn them on → install and enable **Dataview** and **Templater**.
4. Start Claude Code **inside the vault folder** (skills only load there) and run `/learn <something you're studying>`.

## Notes

- **Canvas token safety:** never paste your token into Claude. `/canvas setup` tells you how to store it in the macOS Keychain or in a file outside the vault (Windows/Linux).
- **File support:** PDF, images, notebooks, text and code are read directly. `.docx/.pptx/.xlsx/.odt/.odp/.ods/.epub/.html` use the bundled Python script (standard library only, nothing to install). `.doc` and `.rtf` need macOS. Keynote/Pages/Numbers: export to PDF first. Audio/video: give it a transcript.
- **Git is optional.** If your vault is a Git repo, the skills commit after each study session. If you back it up to GitHub, keep the repo private.
- The skills ask before creating folders and list notes before writing more than 5 of them.

## License

MIT, see [LICENSE](LICENSE).
