---
type: index
status: done
tags:
  - topic/learning
---

# 👋 Start Here

This vault comes with a study system for Claude Code. Open Claude Code in this vault's folder and use:

| Command | What it does |
|---|---|
| `/learn <topic or file>` | Too broad a topic? It asks a few questions to narrow it down first. Reads a topic, PDF, slides, Word file, photo of notes, link... Writes the lecture note and a few concept notes, teaches you every concept, then quizzes you. |
| `/quiz <concept>` | Fresh questions, graded by a separate strict grader. Updates the note's status and review date. |
| `/tutor <concept>` | Socratic help when you're stuck: questions and hints instead of answers. |
| `/review` | Spaced repetition: quizzes whatever is due today. |
| `/practice <skill>` | Hands-on exercises for personal skills (music production, video editing, drawing...). You send screenshots or text, it gives feedback. Not used for course material. |
| `/canvas` | Pulls new lectures from Canvas LMS and runs `/learn` on them (one-time setup needed). |

A concept only counts as **mastered** after 3 passed quizzes in a row, spread over several days, including an explain-it-back and an apply-it question. Until then it keeps coming back.

## Where things go
- `100 Courses/<Course>/`: lecture notes (one folder per course)
- `200 Concepts/`: concept notes you get quizzed on
- `300 Outputs/`: assignments, projects, exam prep. [[Study Dashboard]] shows what's due.
- `900 System/Templates/`: note templates

You can delete this note once you're set up.
