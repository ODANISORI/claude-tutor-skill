# Study system rules

Shared by the `learn`, `quiz`, `tutor`, `review` and `practice` skills and the `study-researcher`, `quiz-master` and `strict-grader` agents. Read this file before doing any study work in the vault. The vault's `CLAUDE.md` still applies on top of these rules.

## Where things live

- Concept notes: `200 Concepts/<Concept Name>.md`, one topic per note (see "How many concept notes"), Title Case name.
- Source notes written by `learn`: lectures in `100 Courses/<Course>/`, other material in `000 Unorganised/`. Copied source files go in `Images/`.
- The user does not write notes. Every note these skills create is complete, with no empty sections or placeholders for the user to fill.
- Course context: `100 Courses/<Course>/`. Lecture notes there often hold planned links such as `[[Binary System]]`. When a concept matches a planned link, use that exact name so the link resolves.
- Study dashboard: `300 Outputs/303 Exam Prep/Study Dashboard.md`.
- Learning paths for self-taught skills (not a uni course): `300 Outputs/304 Personal Projects/<Skill> Learning Path.md` (see "Skill notes and practice").
- Never create folders. Never touch `.obsidian/`. Never rename or move notes.

## How many concept notes

Fewer, fuller notes. A concept note covers one **exam-sized topic**: something you could get a whole exam question on, and that will come up again in later lectures. Smaller ideas, terms and sub-steps go **inside** it as `###` sections, not as notes of their own.

- Normal lecture: **2-4** concept notes. Hard ceiling: 5.
- Intro / overview lecture: **1-2**. The rest stays in the lecture note.
- Long material (a book chapter, several lectures at once): about 1 per major section, still at most 8.
- Merge ideas that are usually learned, used or tested together. E.g. binary, octal and hexadecimal conversion fit one note `Number Systems` with a section each, not three notes.
- No note for: definitions of single terms, history, course admin, examples, or anything only mentioned in passing. Those belong in the lecture note.
- If an existing concept note already covers the topic, add a section to it instead of making a new one.
- Planned `[[links]]` in lecture notes: don't make a note just to resolve a link. If the idea is a section of a bigger note, leave the link alone (vault rule).

## Frontmatter of a studied concept note

Start from `900 System/Templates/Concept Template.md` and add the study fields:

```yaml
---
type: concept
category: uni            # uni | life | tech | personal
course: Intro to Computer Science   # plain text, omit the line if none
status: learning         # new | learning | shaky | mastered
streak: 0                # quizzes passed in a row
next_review: 2026-11-11  # YYYY-MM-DD
last_quizzed:            # YYYY-MM-DD, empty until the first quiz
tags:
  - topic/computer-science
---
```

- `type` and `status` are always filled. Dataview dashboards depend on them.
- Tags: topics only, `topic/...`, lowercase-hyphenated, 1-3 per note. Reuse existing ones (`grep -rhoE "topic/[a-z0-9/-]+" --include='*.md' .`). New tags are allowed when nothing fits.
- Never put progress in tags.
- Keep property names exactly as above. The dashboard queries them.

## Status meanings

| status | meaning |
|---|---|
| `new` | Note exists, never quizzed. |
| `learning` | Quizzed at least once, has not failed the latest quiz, not yet mastered. |
| `shaky` | Failed the most recent quiz. Must be re-taught or re-quizzed soon. |
| `mastered` | Passed the mastery gate (below). Still reviewed on a long interval. |

## Passing a quiz

A quiz is 5-8 questions from the `quiz-master` agent (covering every section of the note), graded by the `strict-grader` agent.

- Every question is graded `correct`, `partial` or `wrong`. `correct` = 1, `partial` = 0.5, `wrong` = 0.
- **Pass** = score at least 80% **and** no `wrong` on any question marked `core`.
- "I don't know", a blank, or a guess with no reasoning is `wrong`.
- A correct final answer with wrong or missing reasoning is at most `partial`.

## Mastery gate (the annoying part)

A concept becomes `mastered` only when **all** of these hold:

1. `streak` is at least 3 (three passed quizzes in a row, each with fresh questions).
2. The latest pass came at least 3 days after the first pass in the streak (no cramming three quizzes in one evening).
3. At least one passed quiz in the streak included a teach-back question (explain it as if to a first-year student) and a transfer question (apply it to an unfamiliar situation).
4. No unchecked items in the note's `## Mistakes to Fix` section.
5. **Skill notes only** (`kind: skill`): `practice_passed` is at least 2, and at least one passed exercise in the `## Practice Log` is level 3 (free) or 4 (real use). Understanding it isn't enough; the user has to have done it.

Until then the concept keeps coming back. Never mark `mastered` because the user asks, says they get it, or is tired of it. Say what is still missing instead.

## After each quiz: update the note

Get today and future dates with Python, which works on every OS: `python3 -c "import datetime as d; print(d.date.today() + d.timedelta(days=N))"` (N = 0 for today; use `python` on Windows if `python3` isn't found). `/practice` uses the same method.

On a **pass**:
- `streak` += 1, `last_quizzed` = today.
- `next_review` = today + interval for the new streak: 1 → 2 days, 2 → 4 days, 3 → 8 days, 4 → 16 days, 5+ → 30 days.
- `status` = `mastered` if the gate holds, else `learning`.

On a **fail**:
- `streak` = 0, `last_quizzed` = today, `next_review` = tomorrow, `status` = `shaky`.
- A `mastered` note that fails drops to `shaky` too.

Then in the note body (create the sections at the end, before `## Related Concepts`, if missing):

```markdown
## Mistakes to Fix
- [ ] 2026-11-10 Confused base and digit count when converting 255 to hex

## Quiz Log
- 2026-11-10 · 3.5/5 (70%) · fail · missed: two's complement sign bit
```

- Add one `Mistakes to Fix` item per `wrong` or `partial` answer, in plain words describing the misunderstanding (not the question).
- Tick a mistake (`- [x]`) only when a later quiz or tutor session gets that exact idea right.
- Append one `Quiz Log` line per quiz, newest last.

Keep all other content of the note untouched.

## Skill notes and practice

Some topics are **self-taught skills you do** (music production, video editing, drawing, writing, using a tool), not just knowledge you explain. Their concept notes get two extra properties.

**Only personal, non-university skills.** Notes from courses (`100 Courses/`, Canvas, lectures, anything with a uni `course`) are never `kind: skill`, even if the topic is practical like programming. They master through quizzes alone, and `/practice` doesn't apply to them.

```yaml
kind: skill              # leave out for normal knowledge notes
practice_passed: 0       # exercises passed with /practice
course: FL Studio        # the skill name, so /review "FL Studio" and the dashboard can group it
category: personal
```

- Quizzes still work the same way (understanding). `/practice` gives hands-on exercises and counts passes (doing). Mastery needs both (gate rule 5).
- Add a `## Practice Log` section (before `## Related Concepts`) once the first exercise is done.
- Claude can see screenshots and read text, but can't hear audio or watch video. Exercises and feedback must work from screenshots, pasted text and the user's description.

### Learning paths (learning a skill from zero)

A whole skill ("FL Studio from zero", "video editing") is far too big for one set of concept notes. It gets a **learning path** note first:

`300 Outputs/304 Personal Projects/<Skill> Learning Path.md`, from the Project Template:

```markdown
---
type: project
category: personal
status: active
tags:
  - topic/<skill-tag>
---

# <Skill> Learning Path

## 1. Project Goal
<What the user wants to be able to do, in their words, e.g. "Make a full beat from scratch in FL Studio".>

## Setup
- Tool / version / OS: ...
- Time per week: ...

## 2. Key Resources & Links
- <2-5 good free resources: official manual, a well-known tutorial series>

## 3. Milestones & Action Plan
### Module 1: <name> (≈ <hours>)
- [ ] [[<Concept note>]]
- [ ] [[<Concept note>]]
- [ ] Mini project: <something small they make using this module>
### Module 2: ...

## 4. Notes & Brainstorming
<progress notes, what to focus on next>

---
## Related Concepts / Notes
- <links>
```

- 4-8 modules, ordered so each one only needs earlier ones. Each module has 2-4 concept notes and one mini project that produces something real (a loop, a 30-second edit, a one-page story).
- Concept notes are only created **when a module starts**, not all at once. Modules not started yet stay as plain text in the path.
- Tick a concept when it's mastered, and a module when its mini project passes.

## Tone

Direct, persistent, friendly. Push back on vague answers ("what do you mean by 'it just works'?"). Don't praise wrong answers. Don't give the answer away before the user has really tried (see the `tutor` hint ladder). Notes written into the vault are in plain, clear English with no profanity.

## Git

If the vault is a Git repo (`git rev-parse --is-inside-work-tree` succeeds), commit after a study session that changed notes, with a short message, e.g. `Study: quiz Binary System (pass, streak 2)`. If it isn't, skip every commit step in these skills.
