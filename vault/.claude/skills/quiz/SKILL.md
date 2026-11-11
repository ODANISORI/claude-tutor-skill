---
name: quiz
description: Quiz the user on a vault concept note with fresh questions from the quiz-master agent, graded independently by the strict-grader agent, then update the note's status, streak, review date, mistakes and quiz log. Enforces the mastery gate. Use when the user says "quiz me on X", "/quiz X", or after a learn or tutor session.
argument-hint: <concept note name or topic>
---

# quiz

**First read `.claude/skills/learn/study-rules.md`.** It defines passing, the mastery gate and how to update the note.

## 1. Find the note

Resolve the argument to a file in `200 Concepts/`. If it is a topic with several notes, pick the one most due (`status: shaky` first, then earliest `next_review`) and say which. If no note exists, offer to run `learn` instead.

Read the note: frontmatter, `## Mistakes to Fix`, `## Quiz Log`.

## 2. Get questions

Work out what the mastery gate still needs (e.g. "streak 2, no teach-back passed yet"). Launch the `quiz-master` agent with the note path, that gate status, and any questions already asked in this session.

Keep the RUBRIC to yourself. Never show it, hint at it, or paraphrase it before grading.

## 3. Ask

- Ask one question at a time. Wait for each answer.
- Do not give hints, confirm or correct during the quiz. If the user asks for help: "Give it your best try, we'll go through it after." If they say "I don't know", record that and move on.
- If an answer is vague, ask once for more: "Can you be more specific?" Then record what they gave.
- Keep the user's answers verbatim.

## 4. Grade

Launch the `strict-grader` agent with the note path, the questions, the rubric and the verbatim answers. Use its grades as final. Don't round up, and don't let "but I meant..." change a grade after the fact. They can show it on the next quiz.

## 5. Debrief

- Show score and pass/fail.
- For each `partial` / `wrong`: what the right idea is and why their answer missed it. Then make them redo that one in their own words right now (not graded, but required before moving on).
- State the mastery gate plainly: "Streak 2/3. Still need: a passed teach-back question, and the next pass must be on or after 2026-11-13."

## 6. Update the note

Apply the "After each quiz" rules from `study-rules.md`: frontmatter (`status`, `streak`, `next_review`, `last_quizzed`), `## Mistakes to Fix`, `## Quiz Log`. Touch nothing else.

## 7. Don't let go

- On a **fail**: offer `/tutor <concept>` now, then a retest. Be persistent: "This one isn't solid yet. 10 minutes with the tutor now, then a retest?"
- On a **pass** that isn't mastery yet: say when it comes back.
- If several concepts are due, offer the next one.

## 8. Commit

Commit the changed note(s): `Study: quiz <Concept> (<pass|fail>, streak <n>)`.
