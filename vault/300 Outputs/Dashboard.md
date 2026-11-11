---
type: index
category: uni
tags:
  - topic/learning
---

# 📋 Dashboard

## To-Do
```dataview
TASK
FROM "100 Courses"
WHERE !completed
```

## Deadlines
```dataview
TABLE
  course AS "Course",
  due AS "Due",
  status AS "Status"
FROM "300 Outputs/301 Assignments"
WHERE type = "assignment" AND status != "done"
SORT due ASC
```

## Active Projects
```dataview
TABLE
  category AS "Category",
  status AS "Status"
FROM "300 Outputs/302 Projects" OR "300 Outputs/304 Personal Projects"
WHERE type = "project" AND status = "active"
```

## Studying
See [[Study Dashboard]].
