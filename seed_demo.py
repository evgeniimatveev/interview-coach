"""Seed realistic demo data for HF Spaces — runs once if DB is empty."""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "interview.db")

SESSIONS = [
    # (days_ago, mode, questions)
    (21, "sql",        [
        ("sql_01", "GROUP BY + aggregation",        "SQL",        6, "Good use of SUM/GROUP BY but missing ORDER BY DESC and LIMIT. | Forgot to alias columns and sort correctly. | Always alias aggregations for readability."),
        ("sql_04", "LAG — month-over-month",         "SQL",        5, "Knew LAG exists but couldn't write the OVER clause correctly. | Missing DATE_TRUNC and percent calculation. | Practice: LAG(val) OVER (ORDER BY month) then (cur-prev)/prev*100."),
        ("sql_03", "CTE",                            "SQL",        6, "Wrote a working CTE but used subquery instead where CTE is cleaner. | Didn't explain readability benefit. | Use CTEs when logic is reused or multi-step."),
    ]),
    (16, "behavioral", [
        ("beh_01", "Handling messy data",            "Behavioral", 7, "Good NYC 311 example with concrete fix. | Missing quantified outcome — how many rows fixed? | Add: '0 ingestion errors after fix, 100% pipeline reliability'."),
        ("beh_05", "Technical communication",        "Behavioral", 7, "Decent Streamlit dashboard example. | Didn't specify who the audience was or what decision resulted. | Name the stakeholder and the action taken."),
        ("beh_03", "Learning quickly",               "Behavioral", 8, "Strong DuckDB example with timeline and outcome. | Could add what specifically was hard to learn. | Great structure overall — keep this answer."),
    ]),
    (12, "sql",        [
        ("sql_02", "Window functions — ROW_NUMBER",  "SQL",        7, "Correct PARTITION BY usage. | Filtered rank in WHERE instead of subquery/CTE — risky with some engines. | Use CTE to wrap the ranked query, then filter."),
        ("sql_05", "FILTER clause",                  "SQL",        8, "Clean FILTER usage, correct DuckDB syntax. | Could mention performance benefit vs CASE WHEN. | FILTER is single-pass; CASE WHEN scans twice — mention this."),
        ("sql_07", "Running total + % of total",     "SQL",        7, "Correct SUM OVER but used subquery for total instead of SUM() OVER(). | Minor inefficiency. | SUM() OVER() with no ORDER BY gives grand total in one pass."),
        ("sql_06", "UNNEST + STRING_SPLIT",          "SQL",        8, "Solid UNNEST/STRING_SPLIT combo. | Forgot TRIM() to handle whitespace around semicolons. | Always TRIM(UNNEST(...)) to avoid ' Python' != 'Python'."),
    ]),
    (8,  "project",   [
        ("proj_01", "SO Survey Analytics",           "Project",    8, "Clear architecture and 51% remote premium stat. | Missing how CI failures are handled. | Add: 'smoke tests fail the GitHub Actions run and send email alert'."),
        ("proj_05", "Uber driver insights",          "Project",    9, "Excellent — 47% figure, 26.5K rows, window function path clearly explained. | Could mention surge pricing as confounder tested. | Near-perfect answer."),
        ("proj_03", "Weather Pipeline reliability",  "Project",    8, "Good retry + graceful skip design. | Didn't quantify uptime. | Add: '98% city success rate over 2 weeks of production runs'."),
    ]),
    (4,  "mixed",     [
        ("sql_08", "Anti-join",                      "SQL",        8, "Both LEFT JOIN/NULL and NOT EXISTS explained. | Performance comparison was vague. | Specify: NOT EXISTS short-circuits on first match; LEFT JOIN scans full table."),
        ("beh_02", "Business impact from data",      "Behavioral", 9, "Outstanding — 47% $/hr insight, Olist delivery delays, clear communication path. | Slightly long. | Trim to 90 seconds for live interview pacing."),
        ("proj_02", "Olist dbt architecture",        "Project",    8, "dbt staging/marts explained well. | Didn't mention ref() DAG lineage. | One sentence on ref() shows you understand dbt's core differentiator."),
        ("beh_04", "Automation + reliability",       "Behavioral", 9, "Weather Pipeline + Job Market Pulse automation quantified perfectly. | Nothing missing. | This is an A+ answer — use it verbatim."),
    ]),
    (1,  "sql",       [
        ("sql_01", "GROUP BY + aggregation",         "SQL",        9, "Perfect — aliases, ORDER BY DESC, LIMIT 10, all aggregations present. | No gaps. | Strong improvement from first attempt — keep drilling."),
        ("sql_04", "LAG — month-over-month",         "SQL",        9, "Correct LAG + DATE_TRUNC + percent formula with NULL handling for first row. | Excellent. | Add a note about NULLIF in denominator to avoid division by zero."),
        ("sql_03", "CTE",                            "SQL",        8, "Clean CTE with HAVING and MEDIAN. | readability argument was brief. | Expand: 'CTE is named and reusable; subquery is anonymous and harder to debug'."),
    ]),
]


def seed_if_empty():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mode TEXT, started_at TEXT, ended_at TEXT,
            q_count INTEGER DEFAULT 0, avg_score REAL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER, question_id TEXT, topic TEXT,
            category TEXT, question TEXT, answer TEXT,
            score INTEGER, feedback TEXT, answered_at TEXT
        );
    """)
    conn.commit()

    if conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] > 0:
        conn.close()
        return

    now = datetime.now()
    for days_ago, mode, questions in SESSIONS:
        base = now - timedelta(days=days_ago)
        cur = conn.execute(
            "INSERT INTO sessions (mode, started_at) VALUES (?,?)",
            (mode, base.isoformat()),
        )
        sid = cur.lastrowid
        scores = []
        for i, (qid, topic, cat, score, feedback) in enumerate(questions):
            ts = (base + timedelta(minutes=i * 4)).isoformat()
            conn.execute(
                """INSERT INTO answers
                   (session_id,question_id,topic,category,question,answer,score,feedback,answered_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (sid, qid, topic, cat,
                 f"Interview question about {topic}",
                 f"Demo answer for {topic} — scored {score}/10",
                 score, feedback, ts),
            )
            scores.append(score)
        avg = round(sum(scores) / len(scores), 1)
        conn.execute(
            "UPDATE sessions SET ended_at=?, q_count=?, avg_score=? WHERE id=?",
            ((base + timedelta(minutes=len(questions) * 4)).isoformat(), len(scores), avg, sid),
        )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_if_empty()
    print("Demo data seeded.")
