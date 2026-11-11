---
name: review
description: Spaced-repetition review session for the vault. Finds concept notes that are due (next_review today or earlier, shaky first) and quizzes each with the quiz skill, then reports what's left. Use when the user says "review", "what's due", "/review", or "study session".
argument-hint: "[topic tag or course, optional] [max notes, default 5]"
---

# review

**First read `.claude/skills/learn/study-rules.md`.**

## 1. Find what's due

Get today's date (see `study-rules.md`, "After each quiz"). Scan frontmatter in `200 Concepts/*.md` for notes with a `streak:` property (that marks a studied note). Due means:

- `status` is `new` or `shaky`, or
- `next_review` is today or earlier.

If the user gave a tag or course, filter by `tags` or `course`. Order: `shaky` first, then `new`, then oldest `next_review`. Default cap: 5 notes per session.

A quick way to list them:

```bash
cd "200 Concepts" && for f in *.md; do
  grep -q '^streak:' "$f" || continue
  s=$(grep -m1 '^status:' "$f" | cut -d' ' -f2)
  d=$(grep -m1 '^next_review:' "$f" | cut -d' ' -f2)
  echo "$d|$s|$f"
done | sort
```

## 2. Show the queue

"5 due today: Two's Complement (shaky), Binary System (new), ..." If nothing is due, say when the next one is and offer a quiz on the weakest note anyway (lowest streak).

## 3. Run it

For each note, run the `quiz` skill flow (quiz-master → ask → strict-grader → debrief → update note). After a fail, offer a short `tutor` round before the next note. Keep each note's update separate.

Don't let the user skip a `shaky` note silently. If they want to skip, say it stays due tomorrow.

## 4. Report

```
Session: 4 quizzed · 3 passed · 1 failed
Mastered: Binary System
Still shaky: Two's Complement (next: tomorrow)
Coming up: Hexadecimal System (2026-11-14)
```

## 5. Commit

One commit for the session: `Study: review session (4 notes)`.
