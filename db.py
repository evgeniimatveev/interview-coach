"""SQLite operations for interview history."""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "interview.db")


def get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            mode       TEXT,
            started_at TEXT,
            ended_at   TEXT,
            q_count    INTEGER DEFAULT 0,
            avg_score  REAL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS answers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER,
            question_id TEXT,
            topic       TEXT,
            category    TEXT,
            question    TEXT,
            answer      TEXT,
            score       INTEGER,
            feedback    TEXT,
            answered_at TEXT
        );
    """)
    conn.commit()
    return conn


def start_session(conn, mode: str) -> int:
    cur = conn.execute(
        "INSERT INTO sessions (mode, started_at) VALUES (?,?)",
        (mode, datetime.now().isoformat()),
    )
    conn.commit()
    return cur.lastrowid


def end_session(conn, session_id: int):
    row = conn.execute(
        "SELECT COUNT(*), AVG(score) FROM answers WHERE session_id=?",
        (session_id,),
    ).fetchone()
    conn.execute(
        "UPDATE sessions SET ended_at=?, q_count=?, avg_score=? WHERE id=?",
        (datetime.now().isoformat(), row[0], round(row[1] or 0, 1), session_id),
    )
    conn.commit()


def save_answer(conn, session_id, q_id, topic, category, question, answer, score, feedback):
    conn.execute(
        """INSERT INTO answers
           (session_id, question_id, topic, category, question, answer, score, feedback, answered_at)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (session_id, q_id, topic, category, question, answer, score, feedback,
         datetime.now().isoformat()),
    )
    conn.commit()


def get_progress(conn):
    return conn.execute("""
        SELECT topic, category, COUNT(*) attempts, ROUND(AVG(score),1) avg_score
        FROM answers GROUP BY topic, category ORDER BY avg_score ASC
    """).fetchall()


def get_recent_sessions(conn, limit=10):
    return conn.execute("""
        SELECT id, mode, started_at, q_count, avg_score
        FROM sessions WHERE q_count > 0
        ORDER BY id DESC LIMIT ?
    """, (limit,)).fetchall()


def get_all_answers(conn):
    return conn.execute("""
        SELECT answered_at, category, topic, score, feedback, question, answer
        FROM answers ORDER BY id
    """).fetchall()


def get_stats(conn):
    return conn.execute("""
        SELECT
            COUNT(DISTINCT s.id)            as total_sessions,
            COUNT(a.id)                     as total_questions,
            ROUND(AVG(a.score), 1)          as overall_avg,
            MAX(a.score)                    as best_score,
            (SELECT topic FROM answers ORDER BY score DESC LIMIT 1) as best_topic,
            (SELECT topic FROM answers ORDER BY score ASC  LIMIT 1) as weak_topic
        FROM sessions s LEFT JOIN answers a ON s.id = a.session_id
        WHERE s.q_count > 0
    """).fetchone()
