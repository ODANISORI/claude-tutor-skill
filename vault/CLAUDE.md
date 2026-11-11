# Vault rules for Claude

## Structure
- `000 Unorganised`: inbox, where new notes land by default
- `100 Courses`: lectures and exercises, one subfolder per course
- `200 Concepts`: concept notes (a few broad notes per lecture, not one per term)
- `300 Outputs`: assignments (301), projects (302), exam prep (303), personal projects (304)
- `400 Life`: personal notes; recipes in `401 Cookbook`, personal context in `402 Personal Context`
- `900 System`: templates, canvases
- Images and attachments go in `Images/` (Obsidian's attachment folder setting).

## Making notes
- Create new notes from the matching template in `900 System/Templates`.
- Replace Templater code (`<% tp.file.title %>`, `<% tp.date.now(...) %>` etc.) with real values. It only runs inside Obsidian.
- Always fill in `type` and `status`; for lectures also `course`. Dataview dashboards depend on them.

## Tags and properties
- Tags are for topics only: `topic/...`, lowercase with hyphens (e.g. `topic/computer-science`), nested where useful (`topic/maths/probability`).
- 1-3 tags per note. Reuse existing tags where they fit; new topic tags are fine.
- Progress goes in the `status` property, never in a tag.
- Don't add tags that repeat the folder or `type`.
- After changing a property, check that the Dataview queries in the dashboards (`300 Outputs/Dashboard.md`, `300 Outputs/303 Exam Prep/Study Dashboard.md`, `400 Life/Cooking Dashboard.md`) still work.

## Study system
- Skills `/learn`, `/quiz`, `/tutor`, `/review`, `/canvas` and agents `study-researcher`, `quiz-master`, `strict-grader` live in `.claude/`.
- Rules (statuses, `streak`, `next_review`, mastery gate) are in `.claude/skills/learn/study-rules.md`. Studied concept notes use those properties; the Study Dashboard queries them.
- `/canvas` pulls lectures from Canvas LMS. The Canvas token lives only in the OS keychain or a file outside the vault, never in the vault, a note, or the chat.

## Safety
- Never rename or move notes without asking. Renaming on disk does not update links the way renaming inside Obsidian does.
- Never touch `.obsidian/`.
- Ask before creating new folders. Delete only when asked, and move to the Trash instead of deleting permanently.
- Before changing more than ~5 notes, list the files that will change.
- Leave unresolved `[[links]]` alone; they are planned notes.
- If the vault is a Git repo, commit after a batch of changes with a short message saying what changed.
