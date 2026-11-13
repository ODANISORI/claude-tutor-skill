---
name: practice
description: Hands-on practice for self-taught, non-university skills in the vault (music production, video editing, drawing, writing for fun, any tool). Only works on skill notes (kind: skill) and learning paths, never on course notes. Gives one small, concrete exercise with a clear checklist, the user does it in their own tool and shows the result (pasted text, screenshots, or a description), then gets specific feedback and a pass or redo. Tracks passed exercises in the note, which skill notes need for mastery. Use when the user says "/practice X", "give me an exercise", "let me try it", or after learning a skill concept.
argument-hint: <concept note, skill topic, or learning path>
---

# practice

Quizzes check that the user understands a skill. This checks that they can **do** it. **First read `.claude/skills/learn/study-rules.md`**, especially "Skill notes and practice".

## 1. Find what to practise

**Only for self-taught skills.** `/practice` works only on concept notes with `kind: skill` and on learning paths in `300 Outputs/304 Personal Projects/`. If the user points it at a university/course note (no `kind: skill`, e.g. anything with a `course` that has a folder in `100 Courses/`), don't set an exercise: say `/practice` is for personal skills, and offer `/quiz` or `/tutor` for that note instead. Never add `kind: skill` to a course note.

- A skill concept note in `200 Concepts/` → practise that.
- A learning path (`300 Outputs/304 Personal Projects/<Skill> Learning Path.md`) or a skill name → pick the first concept in the path that isn't mastered and has the fewest passed exercises; say which.
- Nothing in the vault yet → offer `/learn <topic>` first. Don't set exercises for something never taught.

Read the note: how it works, `## Practice Log`, `## Mistakes to Fix`. Ask once, if you don't know yet: which tool and version (e.g. FL Studio 2024 Producer Edition, DaVinci Resolve 19), and the OS. Remember the answer in the learning path note (`## Setup`).

## 2. Set one exercise

Exactly one exercise at a time, sized to **10-30 minutes**. Pick the level from the Practice Log:

| Level | When | Example (beatmaking) |
|---|---|---|
| 1. Guided | first exercise on this concept | "Recreate this exact 4-on-the-floor kick pattern: steps 1, 5, 9, 13." |
| 2. Variation | after a level 1 pass | "Make a hi-hat pattern with a swing feel and two open hats per bar." |
| 3. Free | after a level 2 pass | "Make an 8-bar drum loop for a lo-fi track; you choose the pattern." |
| 4. Real use | after a level 3 pass | "Use this in a short track idea of your own." |

Write the exercise like this:

```
Exercise: <name>  (level 2, ~15 min)
Goal: <one sentence: what you'll be able to do after>
Steps:
1. ...
2. ...
Done when (checklist):
- [ ] ...
- [ ] ...
Show me: <exactly what to send: a screenshot of the piano roll + mixer, the paragraph as text, the timeline screenshot...>
```

Rules:
- Steps for levels 1-2 are concrete, with the real menu names and shortcuts for the user's tool and version. If you're not sure a menu path is right for their version, say so and describe what to look for instead of guessing. Check current docs with a web search when it matters.
- Every checklist item must be **checkable from what the user sends**. You can see images and text; you **cannot hear audio or watch video**. So for sound, ask for screenshots (piano roll, channel rack, mixer, EQ curve, arrangement/timeline) plus the user's own description ("what did you hear when you turned the cutoff down?").
- Aim exercises at open items in `## Mistakes to Fix`.
- Never repeat an exercise from the Practice Log; change the material, tempo, genre, text or constraint.

## 3. Wait for the result

The user does it in their own tool. Don't give extra hints unless they ask; if they're stuck, use the `tutor` hint ladder (smallest hint first). If they say they skipped it or "basically did it", ask for the evidence anyway.

## 4. Give feedback

Look at exactly what they sent (open screenshots with care, zoom in mentally on labels and values):

- Go through the checklist: ✅ / ❌ for each item, with the evidence ("kick on steps 1, 5, 9, 13 ✅", "the hats are all the same velocity, so no swing feel ❌").
- One thing that's good, specifically. Then the **most important** fix, with how to do it. Don't drown them in ten notes.
- For writing: quote their sentences and show a rewritten version of one or two.
- **Pass** = every checklist item met. Otherwise **redo**: they fix the ❌ items and send again (a redo of the same exercise is fine; it doesn't count as repeating).
- Be honest about limits: "I can see the notes are on the right steps, but I can't hear whether the mix is balanced. Compare it to your reference track."

## 5. Update the note

Get today's date as `study-rules.md` describes. Then:

- On a **pass**: `practice_passed` += 1 (add the property, starting at 0, if missing). If the mastery gate now holds, set `status: mastered`.
- On a **redo**: add one item to `## Mistakes to Fix` for the underlying problem (not the exercise), in plain words.
- Append to `## Practice Log` (create it before `## Related Concepts` if missing):
  ```markdown
  ## Practice Log
  - 2026-11-13 · L1 Four-on-the-floor kick · pass
  - 2026-11-14 · L2 Swung hi-hats · redo: all hats same velocity
  ```
- Tick `## Mistakes to Fix` items the exercise showed are fixed.
- If there's a learning path note, tick the concept there once it's mastered.
- Don't touch `streak`; only quizzes change it.

## 6. Keep going

- After a pass, offer the next level (or the next concept in the path if this one has 2+ passes including level 3).
- Suggest saving their work file with a name like `<concept> L2` so they can see their progress later.
- Commit the note change as `study-rules.md` describes: `Practice: <Concept> L2 (pass)`.
