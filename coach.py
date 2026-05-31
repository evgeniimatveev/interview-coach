"""
DATA INTERVIEW COACH — CLI
===========================
Beautiful terminal interface for data interview practice.
Powered by Claude · Tracks progress in SQLite · Personalized to your portfolio.
"""

import re
import random
import os
from dotenv import load_dotenv
import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.columns import Columns
from rich.markdown import Markdown
from rich import box

import db
from questions import SQL_QUESTIONS, BEHAVIORAL_QUESTIONS, PROJECT_QUESTIONS, STATS_QUESTIONS

load_dotenv()

console = Console()
client  = anthropic.Anthropic()

FAST_MODEL = "claude-haiku-4-5-20251001"
EVAL_MODEL = "claude-sonnet-4-6"

THEME = {
    "title":    "bold cyan",
    "header":   "bold white",
    "category": "bold magenta",
    "good":     "bold green",
    "ok":       "bold yellow",
    "poor":     "bold red",
    "dim":      "dim white",
    "accent":   "bold blue",
}


# ── Score helpers ─────────────────────────────────────────────────────────────

def score_color(score: int) -> str:
    if score >= 8: return THEME["good"]
    if score >= 5: return THEME["ok"]
    return THEME["poor"]


def score_bar(score: int) -> Text:
    filled = "█" * score
    empty  = "░" * (10 - score)
    icon   = "🟢" if score >= 8 else "🟡" if score >= 5 else "🔴"
    t = Text()
    t.append(f"{icon} ")
    t.append(filled, style=score_color(score))
    t.append(empty,  style="dim")
    t.append(f"  {score}/10", style=score_color(score) + " bold")
    return t


def category_badge(cat: str) -> Text:
    colors = {"SQL": "cyan", "Behavioral": "magenta", "Project": "yellow", "Stats": "green"}
    t = Text()
    t.append(f" {cat} ", style=f"bold {colors.get(cat,'white')} on grey23")
    return t


# ── Evaluation ────────────────────────────────────────────────────────────────

_EVAL_SYSTEM = """You are an expert interviewer for Data Analyst / Analytics Engineer roles.
Score the answer 1-10 and give concise feedback. Use EXACTLY this format:

SCORE: <number>

✅ Strengths: <1-2 sentences>

⚠️ Gaps: <1-2 sentences>

💡 Tip: <one concrete improvement>

Scoring: 9-10 excellent (numbers+structure+depth), 7-8 good (minor gaps), 5-6 developing (vague),
3-4 needs work (key elements missing), 1-2 poor (wrong approach)."""


def evaluate(question: str, answer: str, category: str, context: str = "") -> tuple[int, dict]:
    full_text = ""

    console.print()
    console.print(Rule("[dim]Claude is evaluating...[/dim]", style="dim cyan"))
    console.print()

    with client.messages.stream(
        model=EVAL_MODEL,
        max_tokens=400,
        system=[{"type": "text", "text": _EVAL_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{
            "role": "user",
            "content": (
                f"Category: {category}\n"
                f"Key concepts: {context}\n\n"
                f"Question: {question}\n\n"
                f"Answer: {answer}"
            ),
        }],
    ) as stream:
        for chunk in stream.text_stream:
            console.print(chunk, end="", markup=False)
            full_text += chunk

    console.print()

    score = 5
    m = re.search(r"SCORE:\s*(\d+)", full_text)
    if m:
        score = max(1, min(10, int(m.group(1))))

    def _section(marker: str) -> str:
        m2 = re.search(rf"{re.escape(marker)}\s*(.+?)(?=\n[✅⚠️💡]|\Z)", full_text, re.DOTALL)
        return m2.group(1).strip() if m2 else ""

    return score, {
        "score":     score,
        "strengths": _section("✅ Strengths:"),
        "gaps":      _section("⚠️ Gaps:"),
        "tip":       _section("💡 Tip:"),
    }


# ── Input guardrail ───────────────────────────────────────────────────────────

def check_input(text: str) -> bool:
    if len(text.strip()) < 5:
        return False
    r = client.messages.create(
        model=FAST_MODEL, max_tokens=20,
        system="Reply OK or BLOCK. BLOCK if not related to data/tech interviews.",
        messages=[{"role": "user", "content": text}],
    )
    return "BLOCK" not in r.content[0].text.upper()


# ── Question helpers ──────────────────────────────────────────────────────────

def category_of(q: dict) -> str:
    qid = q["id"]
    if qid.startswith("sql"):    return "SQL"
    if qid.startswith("beh"):    return "Behavioral"
    if qid.startswith("stats"):  return "Stats"
    return "Project"


def get_questions(mode: str, count: int) -> list:
    pools = {
        "sql":        SQL_QUESTIONS,
        "behavioral": BEHAVIORAL_QUESTIONS,
        "project":    PROJECT_QUESTIONS,
        "stats":      STATS_QUESTIONS,
        "mixed":      SQL_QUESTIONS + BEHAVIORAL_QUESTIONS + PROJECT_QUESTIONS + STATS_QUESTIONS,
    }
    pool = pools.get(mode, SQL_QUESTIONS)
    return random.sample(pool, min(count, len(pool)))


# ── Interview session ─────────────────────────────────────────────────────────

def run_session(conn, mode: str, count: int):
    session_id = db.start_session(conn, mode)
    questions  = get_questions(mode, count)
    scores     = []

    console.print()
    console.print(Panel(
        f"[bold cyan]🎯 {mode.upper()} MODE[/bold cyan]  ·  {len(questions)} questions\n"
        f"[dim]Type your answer and press Enter twice to submit. Type [bold]skip[/bold] to skip.[/dim]",
        border_style="cyan", box=box.DOUBLE_EDGE,
    ))

    for i, q in enumerate(questions, 1):
        cat = category_of(q)
        console.print()
        console.print(Rule(
            f"[bold]Q{i}/{len(questions)}[/bold]  {category_badge(cat)}  [dim]{q['topic']}[/dim]",
            style="dim"
        ))
        console.print()

        # Question panel
        console.print(Panel(
            q["question"],
            title=f"[bold]{cat} Question[/bold]",
            border_style={"SQL":"cyan","Behavioral":"magenta","Project":"yellow"}.get(cat,"white"),
            padding=(1, 2),
        ))

        # Optional hint
        if "hint" in q:
            if Confirm.ask("  [dim]Show hint?[/dim]", default=False):
                console.print(Panel(
                    f"[dim]💡 {q['hint']}[/dim]",
                    border_style="dim", box=box.MINIMAL,
                ))

        # Collect answer
        console.print("\n  [bold]Your answer[/bold] [dim](Enter twice when done):[/dim]\n")
        lines = []
        while True:
            try:
                line = input("  ")
            except EOFError:
                break
            if line.strip().lower() == "skip":
                console.print("  [dim]⏭ Skipped.[/dim]")
                break
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)

        answer = "\n".join(lines).strip()
        if not answer or answer.lower() == "skip":
            continue

        if not check_input(answer):
            console.print("[red]⚠ Answer seems off-topic. Try again.[/red]")
            continue

        # Stream evaluation live — feedback appears in real time
        context = q.get("hint", "") or str(q.get("concepts", q.get("elements", "")))
        score, result = evaluate(q["question"], answer, cat, context)

        scores.append(score)

        # Score panel
        console.print(Panel(
            score_bar(score),
            title="[bold]Score[/bold]",
            border_style=score_color(score).replace("bold ", ""),
            box=box.HEAVY,
            padding=(0, 2),
        ))

        feedback_str = f"Strengths: {result.get('strengths','')} | Gaps: {result.get('gaps','')} | Tip: {result.get('tip','')}"
        db.save_answer(conn, session_id, q["id"], q["topic"], cat,
                       q["question"], answer, score, feedback_str)

    # Session summary
    db.end_session(conn, session_id)

    if not scores:
        console.print("[dim]No answers recorded.[/dim]")
        return

    avg = sum(scores) / len(scores)
    best_idx = scores.index(max(scores))
    weak_idx = scores.index(min(scores))

    summary = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    summary.add_column("", style="dim")
    summary.add_column("")
    summary.add_row("Questions answered", f"[bold]{len(scores)}[/bold]")
    summary.add_row("Average score",      score_bar(round(avg)))
    summary.add_row("Best topic",         f"[green]{questions[best_idx]['topic']}[/green]  ({max(scores)}/10)")
    if len(scores) > 1:
        summary.add_row("Needs work",     f"[red]{questions[weak_idx]['topic']}[/red]  ({min(scores)}/10)")

    console.print()
    console.print(Panel(
        summary,
        title="[bold cyan]📊 Session Complete[/bold cyan]",
        border_style="cyan",
        box=box.DOUBLE_EDGE,
        padding=(1, 2),
    ))
    console.print(
        f"[dim]  Progress saved · View detailed dashboard: [cyan]streamlit run dashboard.py[/cyan][/dim]\n"
    )


# ── Progress report ───────────────────────────────────────────────────────────

def show_progress(conn):
    stats = db.get_stats(conn)
    sessions = db.get_recent_sessions(conn, limit=5)
    rows = db.get_progress(conn)

    if not stats or not stats[0]:
        console.print(Panel("[dim]No sessions yet. Start practicing![/dim]", border_style="dim"))
        return

    total_s, total_q, avg, best, best_t, weak_t = stats

    # Top stats
    stat_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    stat_table.add_column("", style="dim")
    stat_table.add_column("", justify="right")
    stat_table.add_row("Total sessions",   f"[bold cyan]{total_s}[/bold cyan]")
    stat_table.add_row("Total questions",  f"[bold cyan]{total_q}[/bold cyan]")
    stat_table.add_row("Overall average",  score_bar(round(avg or 0)))
    if best_t:
        stat_table.add_row("Strongest topic", f"[green]{best_t}[/green]")
    if weak_t:
        stat_table.add_row("Focus area",       f"[red]{weak_t}[/red]")

    console.print()
    console.print(Panel(stat_table, title="[bold cyan]📈 Your Progress[/bold cyan]",
                        border_style="cyan", box=box.DOUBLE_EDGE))

    # Recent sessions
    if sessions:
        t = Table(title="Recent Sessions", box=box.SIMPLE_HEAD,
                  title_style="bold", header_style="dim")
        t.add_column("Date",   style="dim", width=12)
        t.add_column("Mode",   width=12)
        t.add_column("Qs",     justify="right", width=4)
        t.add_column("Score",  width=30)
        for _, mode, started, q_count, avg_s in sessions:
            t.add_row(
                started[:10] if started else "?",
                f"[bold]{mode}[/bold]",
                str(q_count),
                score_bar(round(avg_s or 0)),
            )
        console.print(t)

    # By topic
    if rows:
        t2 = Table(title="Performance by Topic (weakest first)",
                   box=box.SIMPLE_HEAD, title_style="bold", header_style="dim")
        t2.add_column("Topic",    width=30)
        t2.add_column("Category", width=12)
        t2.add_column("Attempts", justify="right", width=8)
        t2.add_column("Avg Score", width=30)
        for topic, cat, attempts, avg_s in rows:
            t2.add_row(topic, category_badge(cat), str(attempts), score_bar(round(avg_s or 0)))
        console.print(t2)

    console.print()


# ── Main menu ─────────────────────────────────────────────────────────────────

def main():
    conn = db.get_conn()

    console.print()
    console.print(Panel(
        "[bold cyan]🎓 DATA INTERVIEW COACH[/bold cyan]\n"
        "[dim]Powered by Claude · Personalized to your portfolio · Progress tracked in SQLite[/dim]",
        border_style="cyan",
        box=box.DOUBLE_EDGE,
        padding=(1, 4),
    ))

    MODES = {
        "1": ("sql",        "SQL Drill",         "12 questions · Window fn, CTEs, UNNEST, LAG, Cohort"),
        "2": ("behavioral", "Behavioral",         "9 questions · STAR stories + Tell me about yourself"),
        "3": ("project",    "Project Deep",       "8 questions · Olist, Uber, Weather, MCP, SO Survey, Coach"),
        "4": ("stats",      "Stats & A/B Testing","6 questions · p-value, Type I/II, test design, pitfalls"),
        "5": ("mixed",      "Mixed",              "All categories — real interview feel"),
    }

    while True:
        console.print()
        menu = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        menu.add_column("", style="bold cyan", width=4)
        menu.add_column("", style="bold", width=20)
        menu.add_column("", style="dim")
        for key, (_, label, desc) in MODES.items():
            menu.add_row(f"[{key}]", label, desc)
        menu.add_row("[6]", "Progress",   "See your scores and weak areas")
        menu.add_row("[0]", "Exit",       "")
        console.print(menu)

        choice = Prompt.ask("\n  [bold]Choose[/bold]", choices=["0","1","2","3","4","5","6"])

        if choice == "0":
            console.print("\n  [bold cyan]Good practice! See you next time. 💪[/bold cyan]\n")
            break
        elif choice == "6":
            show_progress(conn)
        elif choice in MODES:
            mode, label, _ = MODES[choice]
            max_q = {"sql": 12, "behavioral": 9, "project": 8, "stats": 6, "mixed": 12}[mode]
            n = Prompt.ask(f"  Questions? (1–{max_q})", default="3")
            n = int(n) if n.isdigit() and 1 <= int(n) <= max_q else 3
            run_session(conn, mode, n)

    conn.close()


if __name__ == "__main__":
    main()
