# מערכת יצירת מאמרים מקצועיים — CrewAI Multi-Agent Orchestration

> מטלה אקדמית: יצירה והפעלה של אורקסטרציה של סוכנים באמצעות CrewAI

---

## תיאור המטלה

מערכת זו מממשת **אורקסטרציה של סוכנים (Agent Orchestration)** באמצעות ספריית CrewAI.
המערכת מפעילה pipeline סדרתי של 4 סוכנים AI שכל אחד מהם מבצע שלב אחד ביצירת מאמר מקצועי,
ומעביר את הפלט שלו לסוכן הבא דרך מנגנון ה-context.

**הנושא לדוגמה:** "The Impact of Artificial Intelligence on Modern Healthcare"

---

## ארכיטקטורת המערכת

```
קלט: נושא המאמר
         │
         ▼
┌─────────────────────┐
│   Research Agent    │  ← SerperDevTool (חיפוש אינטרנט)
│  (מחקר ואיסוף מידע) │
└────────┬────────────┘
         │ context: תקציר מחקר מובנה
         ▼
┌─────────────────────┐
│    Writer Agent     │
│   (כתיבת המאמר)    │
└────────┬────────────┘
         │ context: טיוטת מאמר
         ▼
┌─────────────────────┐
│    Editor Agent     │
│  (עריכה ושיפור)    │
└────────┬────────────┘
         │ context: מאמר ערוך
         ▼
┌─────────────────────┐
│  Publisher Agent    │
│  (עיצוב ופרסום)    │
└────────┬────────────┘
         │
         ▼
פלט: מאמר מוכן לפרסום (Markdown)
```

---

## הסבר על כל סוכן

### 1. Research Agent — Senior Research Analyst

| שדה       | ערך                                                                     |
|-----------|-------------------------------------------------------------------------|
| **role**  | Senior Research Analyst                                                 |
| **goal**  | לאסוף מידע מקיף, מדויק ורלוונטי על הנושא הנדרש                        |
| **tools** | `SerperDevTool` — חיפוש אינטרנטי בזמן אמת                             |

**תפקיד:** הסוכן הראשון בשרשרת. מחפש מידע עדכני, סטטיסטיקות, דעות מומחים ומגמות עדכניות.
מחזיר **תקציר מחקר מובנה** (500-700 מילים) עם כותרות ברורות.

---

### 2. Writer Agent — Professional Content Writer

| שדה       | ערך                                                                     |
|-----------|-------------------------------------------------------------------------|
| **role**  | Professional Content Writer                                             |
| **goal**  | להפוך את ממצאי המחקר למאמר מקצועי ומרתק                               |
| **tools** | ללא כלים חיצוניים — מסתמך אך ורק על ה-context מהמחקר                 |

**תפקיד:** מקבל את תקציר המחקר ויוצר ממנו **מאמר מלא** (800-1000 מילים)
עם מבנה ברור: הקדמה, גוף (3-4 פרקים) ומסקנה.

---

### 3. Editor Agent — Senior Content Editor

| שדה       | ערך                                                                     |
|-----------|-------------------------------------------------------------------------|
| **role**  | Senior Content Editor                                                   |
| **goal**  | לשפר ולחדד את המאמר לרמה מקצועית הגבוהה ביותר                        |
| **tools** | ללא כלים חיצוניים — עורך את הטיוטה שקיבל                             |

**תפקיד:** עורך את הטיוטה ב-6 שלבים: בדיקת עובדות, מבנה, בהירות, סגנון, דקדוק, עקביות.
מחזיר את **המאמר הערוך במלואו** + הערת עורך קצרה.

---

### 4. Publisher Agent — Content Publisher and Formatter

| שדה       | ערך                                                                     |
|-----------|-------------------------------------------------------------------------|
| **role**  | Content Publisher and Formatter                                         |
| **goal**  | לעצב את המאמר הסופי כמסמך Markdown מוכן לפרסום                       |
| **tools** | ללא כלים חיצוניים — מעצב את התוכן שקיבל                              |

**תפקיד:** מוסיף Metadata (כותרת SEO, תיאור, תגים, זמן קריאה), מבנה Markdown
(H1/H2/H3), תקציר מנהלים, Call to Action, ונושאים קשורים.

---

## זרימת המידע בין הסוכנים (Context Flow)

```python
# כל Task מקבל את פלט הקודמת דרך context=[]
research_task = Task(agent=research_agent, ...)          # אין context — ראשון בשרשרת
writing_task  = Task(agent=writer_agent,  context=[research_task])  # מקבל מחקר
editing_task  = Task(agent=editor_agent,  context=[writing_task])   # מקבל טיוטה
publish_task  = Task(agent=publisher_agent, context=[editing_task]) # מקבל ערוך
```

CrewAI מזריק אוטומטית את **`expected_output`** של כל Task לתוך ה-prompt של ה-Task הבאה.
כך כל סוכן עובד על הפלט של קודמו — זהו context passing אמיתי.

---

## למה זה נחשב Orchestration?

**Orchestration** = תיאום של מספר סוכנים עצמאיים לביצוע מטרה מורכבת.

במערכת זו:
- כל סוכן הוא **יחידה עצמאית** עם role, goal, backstory וtools משלו
- ה-**Crew** הוא ה-Orchestrator שמנהל את הסדר, ה-context וה-execution
- התהליך הוא **Sequential Pipeline** — כל שלב חייב להסתיים לפני הבא
- אף סוכן לא יכול לדלג, להחליף תפקידים, או לבצע מספר שלבים

זה שונה מ**סוכן בודד** שעושה הכל — כאן יש **חלוקת עבודה ברורה** ו**העברת אחריות** ממשית.

---

## למה זה תהליך סדרתי (Sequential)?

```python
article_crew = Crew(
    agents=[...],
    tasks=[...],
    process=Process.sequential,  # ← מפתח!
    verbose=True,
)
```

`Process.sequential` אומר ל-CrewAI להריץ את ה-Tasks אחת אחרי השנייה.
Task 2 לא מתחילה לפני ש-Task 1 סיימה ויצרה פלט מלא.
זה מבטיח שכל שלב מבוסס על עבודה מוגמרת של השלב הקודם — לא על הנחות.

---

## איך להריץ את הפרויקט

### דרישות מוקדמות

```bash
pip install -r requirements.txt
```

### הגדרת API Keys

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

ערוך את `.env` והכנס את המפתחות שלך:
- `OPENAI_API_KEY` — ממשק openai.com
- `SERPER_API_KEY` — מפתח חינמי מ-serper.dev

### הרצה

```bash
# נושא ברירת מחדל (AI in Healthcare)
python main.py

# נושא מותאם אישית
python main.py --topic "The Future of Renewable Energy in Urban Cities"
```

### פלט

הפלט מודפס live לקונסול (verbose=True) ונשמר אוטומטית ל-`output_article.md`.

---

## דוגמת קלט/פלט

### קלט

```
--topic "The Impact of Artificial Intelligence on Modern Healthcare"
```

### פלט (חלק מ-output_article.md)

```markdown
---
title: "How AI is Revolutionizing Healthcare: From Diagnosis to Drug Discovery"
date: 2026-06-16
reading_time: "5 min read"
author: "[Author Name]"
tags: [artificial-intelligence, healthcare, machine-learning, medical-diagnosis, digital-health]
description: "Explore how artificial intelligence is transforming modern healthcare..."
---

## Executive Summary
AI is reshaping healthcare at an unprecedented pace, improving diagnostic accuracy by up to 40%...

# How AI is Revolutionizing Healthcare: From Diagnosis to Drug Discovery

## Introduction
In the operating rooms of leading hospitals today, algorithms are achieving what...

## The Diagnostic Revolution
...

## Call to Action
Found this article valuable? Share it with your network and join the conversation...
```

---

## צילומי מסך (Screenshot Placeholders)

המיקומים המומלצים לצילומי מסך בדוח/הגשה:

1. **`[SCREENSHOT 1]`** — הרצת `python main.py` בטרמינל, רגע לפני kick-off
2. **`[SCREENSHOT 2]`** — פלט verbose של Research Agent בפעולה (חיפוש SerperDevTool)
3. **`[SCREENSHOT 3]`** — פלט verbose של Writer Agent (כתיבת המאמר)
4. **`[SCREENSHOT 4]`** — תחילת Editor Agent וסיום Publisher Agent
5. **`[SCREENSHOT 5]`** — הקובץ `output_article.md` פתוח בעורך (VS Code / Notepad++)

---

## מבנה הפרויקט

```
Exorcise_5/
├── main.py              # קוד מלא — הגדרת Agents, Tasks, Crew והרצה
├── requirements.txt     # תלויות Python
├── .env.example         # תבנית משתני סביבה
├── output_article.md    # פלט המאמר (נוצר בזמן ריצה)
├── README.md            # מסמך זה
└── docs/
    ├── PRD.md           # Product Requirements Document
    ├── PLAN.md          # ארכיטקטורה ותכנון
    └── TODO.md          # רשימת משימות
```

---

## תלויות עיקריות

| ספרייה          | גרסה      | שימוש                              |
|-----------------|-----------|-------------------------------------|
| `crewai`        | ≥0.80.0   | Framework לאורקסטרציה של סוכנים    |
| `crewai-tools`  | ≥0.17.0   | SerperDevTool לחיפוש אינטרנטי      |
| `python-dotenv` | ≥1.0.0    | טעינת API keys מקובץ .env          |

---

*נוצר כחלק ממטלה אקדמית בנושא Multi-Agent Orchestration | CrewAI Framework*
