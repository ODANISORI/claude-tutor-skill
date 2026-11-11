---
type: index
category: life
tags:
  - topic/cooking
---

# 🍳 Cookbook Dashboard

## 🌟 Top Rated Recipes
```dataview
TABLE 
  rating_taste AS "Taste (1-5)", 
  rating_difficulty AS "Diff (1-5)", 
  prep_time_min AS "Time (m)"
FROM #topic/cooking
WHERE status = "tested"
SORT rating_taste DESC
LIMIT 15
```
## ⏱️ Quick Meals (Under 30 Mins)
```dataview
TABLE 
  rating_taste AS "Taste (1-5)", 
  prep_time_min AS "Time (m)"
FROM #topic/cooking
WHERE status = "tested" AND number(prep_time_min) <= 30
SORT prep_time_min ASC
```
## 📝 Recipes To Try
```dataview
TABLE 
  rating_difficulty AS "Diff (1-5)", 
  prep_time_min AS "Time (m)"
FROM #topic/cooking
WHERE status = "untested"
```
