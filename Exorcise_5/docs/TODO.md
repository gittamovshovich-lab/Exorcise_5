# TODO — רשימת משימות לביצוע
## מערכת יצירת מאמרים מקצועיים | CrewAI

**עודכן:** 2026-06-16

---

## שלב 0: הכנה והגדרת סביבה

- [x] הגדרת מבנה תיקיות הפרויקט
- [x] יצירת `requirements.txt`
- [x] יצירת `.env.example`
- [ ] **השג OPENAI_API_KEY** — יצירת חשבון ב-openai.com ← **מוקדם ביותר!**
- [ ] **השג SERPER_API_KEY** — הרשמה חינמית ב-serper.dev
- [ ] העתק `.env.example` → `.env` והכנס את המפתחות
- [ ] הרץ `pip install -r requirements.txt`

---

## שלב 1: קוד Python (main.py)

- [x] הגדרת `search_tool = SerperDevTool()`
- [x] כתיבת `research_agent` — role, goal, backstory, tools
- [x] כתיבת `writer_agent` — role, goal, backstory
- [x] כתיבת `editor_agent` — role, goal, backstory
- [x] כתיבת `publisher_agent` — role, goal, backstory
- [x] הגדרת `research_task` — description + expected_output
- [x] הגדרת `writing_task` עם `context=[research_task]`
- [x] הגדרת `editing_task` עם `context=[writing_task]`
- [x] הגדרת `publishing_task` עם `context=[editing_task]`
- [x] יצירת `Crew` עם `Process.sequential` ו-`verbose=True`
- [x] הרצה עם `crew.kickoff()`
- [x] שמירת פלט ל-`output_article.md`
- [x] הוספת `argparse` ל-`--topic`

---

## שלב 2: תיעוד

- [x] כתיבת `README.md` — תיאור, ארכיטקטורה, הסברים, הרצה
- [x] כתיבת `docs/PRD.md` — דרישות מוצר
- [x] כתיבת `docs/PLAN.md` — ארכיטקטורה ותכנון
- [x] כתיבת `docs/TODO.md` — רשימת משימות (זה הקובץ)

---

## שלב 3: בדיקות

- [ ] הרץ `python main.py` עם נושא ברירת מחדל
- [ ] ודא שכל 4 הסוכנים מופעלים בסדר הנכון (בדוק verbose output)
- [ ] ודא שה-context עובר: Research→Writer, Writer→Editor, Editor→Publisher
- [ ] פתח `output_article.md` — ודא שהוא מסמך Markdown תקין
- [ ] הרץ עם `--topic` מותאם אישית ובדוק שהנושא השתנה
- [ ] צלם מסכים לכל שלב (לצרכי הגשה)

---

## שלב 4: GitHub

- [ ] אתחל repository: `git init`
- [ ] הוסף `.gitignore` (ודא ש-`.env` בפנים!)
- [ ] הוסף את כל הקבצים: `git add .`
- [ ] Commit ראשוני: `git commit -m "feat: initial CrewAI multi-agent system"`
- [ ] צור remote repository ב-GitHub
- [ ] Push: `git push -u origin main`

---

## שלב 5: הגשה

- [ ] בדוק שה-repository ציבורי (Public)
- [ ] ודא שה-README.md מוצג כראוי ב-GitHub
- [ ] הוסף צילומי מסך ל-README (אם נדרש)
- [ ] שלח קישור ל-repository

---

## חשוב: `.gitignore` מינימלי

```gitignore
# Secrets
.env

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# Output (אופציונלי — אפשר לכלול לדוגמה)
# output_article.md
```

---

## הערות

> **אזהרה:** לעולם אל תעלה את קובץ `.env` ל-GitHub! וודא שהוא ב-`.gitignore` לפני כל Push.

> **עלות:** כל הרצה מלאה (4 Agents + SerperDevTool) עשויה לעלות כ-$0.05-0.20 ב-OpenAI API. מומלץ להריץ פעם אחת ולשמור את הפלט.

> **זמן ריצה:** צפה ל-2-5 דקות לריצה מלאה עם verbose=True.
