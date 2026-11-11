---
type: index
category: uni
tags:
  - topic/learning
---

# 🎓 Study Dashboard

Run `/review` in Claude Code to work through what's due. `/learn <topic>` adds new concepts, `/quiz <concept>` and `/tutor <concept>` work on one.

## 🔥 Due Now
```dataview
TABLE
  status AS "Status",
  streak AS "Streak",
  next_review AS "Due",
  course AS "Course"
FROM "200 Concepts"
WHERE streak != null AND (status = "shaky" OR status = "new" OR next_review <= date(today))
SORT choice(status = "shaky", 0, choice(status = "new", 1, 2)) ASC, next_review ASC
```

## ⚠️ Shaky
```dataview
TABLE
  last_quizzed AS "Last Quiz",
  next_review AS "Due"
FROM "200 Concepts"
WHERE status = "shaky"
SORT last_quizzed ASC
```

## 📈 Learning
```dataview
TABLE
  streak AS "Streak",
  next_review AS "Next Review",
  course AS "Course"
FROM "200 Concepts"
WHERE status = "learning"
SORT next_review ASC
```

## ✅ Mastered
```dataview
TABLE
  last_quizzed AS "Last Quiz",
  next_review AS "Next Check"
FROM "200 Concepts"
WHERE status = "mastered"
SORT file.name ASC
```

## 🧩 Open Mistakes
```dataview
TASK
FROM "200 Concepts"
WHERE !completed AND meta(section).subpath = "Mistakes to Fix"
GROUP BY file.link
```

## 📊 Progress by Course
```dataview
TABLE WITHOUT ID
  course AS "Course",
  length(rows) AS "Concepts",
  length(filter(rows, (r) => r.status = "mastered")) AS "Mastered",
  length(filter(rows, (r) => r.status = "shaky")) AS "Shaky"
FROM "200 Concepts"
WHERE streak != null
GROUP BY course
```
