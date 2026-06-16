# PLAN — תכנון המערכת והארכיטקטורה
## מערכת יצירת מאמרים מקצועיים | CrewAI Multi-Agent Pipeline

**גרסה:** 1.0  
**תאריך:** 2026-06-16  

---

## 1. החלטות ארכיטקטורה

### 1.1 בחירת Framework — CrewAI

**החלטה:** CrewAI (ולא LangChain, AutoGen, או פתרון מותאם)

**נימוק:**
- API פשוט ומובנה: `Agent → Task → Crew → kickoff()`
- תמיכה נטיבית ב-`Process.sequential` ו-context passing
- `verbose=True` מספק שקיפות מלאה לצרכי הדגמה אקדמית
- תיעוד מצוין ו-community פעיל

### 1.2 בחירת מבנה Pipeline — Sequential

**החלטה:** `Process.sequential` (ולא `hierarchical` או parallel)

**נימוק:**
- כל שלב תלוי ב-output של השלב הקודם — חייב להיות sequential
- `hierarchical` מוסיף Manager Agent מיותר למקרה זה
- parallel לא רלוונטי — Writer לא יכול לכתוב לפני שהמחקר הסתיים

### 1.3 מנגנון העברת מידע — context parameter

**החלטה:** `Task(context=[previous_task])` לכל Task שאינה ראשונה

**נימוק:**
- זה הדרך הרשמית של CrewAI להעביר output בין Tasks
- CrewAI מזריק אוטומטית את `expected_output` של ה-Task הקודמת
- שומר על אנקפסולציה — כל Agent מקבל רק מה שצריך

### 1.4 כלים (Tools)

**החלטה:** SerperDevTool רק ל-Research Agent; שאר הסוכנים ללא כלים

**נימוק:**
- Writer, Editor, Publisher עובדים על תוכן שכבר קיים ב-context — אין צורך בחיפוש
- הפשטה מסייעת לבהירות הקוד ומצמצמת עלות API

---

## 2. ארכיטקטורת נתונים (Data Flow)

```
                         ┌─────────────────────────────────┐
                         │         CREW ORCHESTRATOR        │
                         │    (CrewAI Process.sequential)   │
                         └──────────────┬──────────────────┘
                                        │ kickoff(inputs={"topic": ...})
                    ┌───────────────────▼───────────────────┐
                    │           TASK 1: research_task        │
                    │  Agent: research_agent                 │
                    │  Tool:  SerperDevTool                  │
                    │  Input: topic string                   │
                    │  Output: research brief (500-700w)     │
                    └───────────────────┬───────────────────┘
                              context=[research_task]
                    ┌───────────────────▼───────────────────┐
                    │           TASK 2: writing_task         │
                    │  Agent: writer_agent                   │
                    │  Tool:  none                           │
                    │  Input: research brief (via context)   │
                    │  Output: draft article (800-1000w)     │
                    └───────────────────┬───────────────────┘
                              context=[writing_task]
                    ┌───────────────────▼───────────────────┐
                    │           TASK 3: editing_task         │
                    │  Agent: editor_agent                   │
                    │  Tool:  none                           │
                    │  Input: draft article (via context)    │
                    │  Output: polished article + note       │
                    └───────────────────┬───────────────────┘
                              context=[editing_task]
                    ┌───────────────────▼───────────────────┐
                    │          TASK 4: publishing_task       │
                    │  Agent: publisher_agent                │
                    │  Tool:  none                           │
                    │  Input: polished article (via context) │
                    │  Output: full markdown document        │
                    └───────────────────┬───────────────────┘
                                        │
                              output_article.md
```

---

## 3. מבנה הקוד

### 3.1 מבנה קובץ main.py

```
main.py
├── IMPORTS (crewai, dotenv, tools, argparse)
├── TOOL INITIALIZATION
│   └── search_tool = SerperDevTool()
├── AGENT DEFINITIONS (4 agents)
│   ├── research_agent  — role, goal, backstory, tools=[search_tool]
│   ├── writer_agent    — role, goal, backstory, tools=[]
│   ├── editor_agent    — role, goal, backstory, tools=[]
│   └── publisher_agent — role, goal, backstory, tools=[]
├── TASK DEFINITIONS (function create_tasks)
│   ├── research_task   — description, expected_output, agent
│   ├── writing_task    — description, expected_output, agent, context=[research_task]
│   ├── editing_task    — description, expected_output, agent, context=[writing_task]
│   └── publishing_task — description, expected_output, agent, context=[editing_task]
├── CREW ASSEMBLY (function run_article_creation_system)
│   ├── Crew(agents=[...], tasks=[...], process=Process.sequential, verbose=True)
│   └── result = crew.kickoff()
└── ENTRY POINT (__main__)
    ├── argparse (--topic)
    ├── run_article_creation_system(topic)
    └── write output_article.md
```

### 3.2 מבנה תיקיות הפרויקט

```
Exorcise_5/
├── main.py              ← קוד מלא (single-script requirement)
├── requirements.txt     ← תלויות
├── .env.example         ← תבנית משתני סביבה
├── output_article.md    ← נוצר בזמן ריצה
├── README.md            ← תיעוד ראשי
└── docs/
    ├── PRD.md           ← מסמך דרישות מוצר (זה הקובץ)
    ├── PLAN.md          ← ארכיטקטורה ותכנון
    └── TODO.md          ← רשימת משימות
```

---

## 4. הגדרות Agents — ניתוח System Prompts

### פילוסופיית ה-backstory

ה-backstory של כל Agent פועל כ-**system prompt** המגדיר:
1. **זהות** — "מי אתה?" (שנות ניסיון, רקע)
2. **מתודולוגיה** — "איך אתה עובד?" (תהליכים, גישות)
3. **ערכים** — "מה חשוב לך?" (דיוק, יצירתיות, קפדנות)
4. **פלט צפוי** — "מה אתה מייצר?" (פורמט וסוג התוצר)

### research_agent — Senior Research Analyst
- **אישיות:** אנליטי, קפדני, שיטתי
- **מתודולוגיה:** מאמת עובדות ממקורות מרובים, מתעדף תוכן סמכותי
- **ערך מרכזי:** דיוק מעל הכל — "לא ממציא עובדות"
- **פלט:** brief מובנה עם כותרות ברורות

### writer_agent — Professional Content Writer
- **אישיות:** יצירתי, מרתק, מותאם לקהל
- **מתודולוגיה:** שלושה עמודות — clarity, credibility, compelling narrative
- **ערך מרכזי:** בסיס על ראיות בלבד — "לא ממציא עובדות"
- **פלט:** מאמר עם מבנה ברור ועקבי

### editor_agent — Senior Content Editor
- **אישיות:** קפדני, בלתי מתפשר, משמר קול הכותב
- **מתודולוגיה:** 6-step process: accuracy → structure → clarity → style → grammar → consistency
- **ערך מרכזי:** "עריכה טובה היא בלתי נראית"
- **פלט:** מאמר מלא ערוך + הערת עורך

### publisher_agent — Content Publisher and Formatter
- **אישיות:** מדוקדק, מכיר פלטפורמות, מונחה SEO
- **מתודולוגיה:** checklist publish מוגדר היטב
- **ערך מרכזי:** "הצגה חשובה לא פחות מתוכן"
- **פלט:** מסמך Markdown מלא מוכן לפרסום

---

## 5. תרשים רצף (Sequence Diagram)

```
User        Crew            Research        Writer          Editor          Publisher
 │           │                │               │               │               │
 │──topic──►│                │               │               │               │
 │           │──Task 1──────►│               │               │               │
 │           │               │──SerperSearch►│               │               │
 │           │               │◄──results────│               │               │
 │           │               │──brief──────►│               │               │
 │           │◄──output 1───│               │               │               │
 │           │──Task 2──────────────────────►               │               │
 │           │               │           [context: brief]   │               │
 │           │               │               │──article────►│               │
 │           │◄──output 2────────────────────               │               │
 │           │──Task 3──────────────────────────────────────►               │
 │           │               │            [context: draft]  │               │
 │           │               │               │               │──polished───►│
 │           │◄──output 3─────────────────────────────────────              │
 │           │──Task 4──────────────────────────────────────────────────────►
 │           │               │         [context: polished article]          │
 │           │◄──output 4──────────────────────────────────────────────────
 │◄──final──│
 │           │
[output_article.md]
```

---

## 6. החלטות עיצוב נוספות

### למה `allow_delegation=False`?

מונע מסוכן לפנות לסוכן אחר ישירות. בפרויקט זה, כל תקשורת עוברת דרך ה-Crew
ומנגנון ה-context. זה מבטיח שה-pipeline הוא sequential אמיתי.

### למה `create_tasks(topic)` כ-function?

כדי לאפשר קריאה עם נושאים שונים ללא שינוי קוד. ה-topic מוזרק לתיאורי ה-Tasks
בזמן ריצה.

### למה לשמור ל-`output_article.md`?

הפלט בזמן ריצה (verbose) הוא ל-debugging. ה-output הסופי נשמר לקובץ
כדי לאפשר בדיקה, שיתוף והגשה.
