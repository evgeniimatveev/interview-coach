"""
DATA INTERVIEW COACH — Dashboard
==================================
Streamlit visualization of interview practice progress.
Reads from local SQLite DB (data/interview.db).
"""

import sqlite3
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "interview.db")

st.set_page_config(
    page_title="Data Interview Coach",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .metric-label  { font-size: 0.85rem; color: #888; }
    .metric-value  { font-size: 2rem; font-weight: 700; }
    [data-testid="stMetricValue"] { font-size: 2rem; }
</style>
""", unsafe_allow_html=True)

TEAL   = "#2a9d8f"
ORANGE = "#e76f51"
BLUE   = "#264653"
YELLOW = "#e9c46a"
GREEN  = "#52b788"
RED    = "#e63946"


# ── Data loading ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def load_data():
    if not os.path.exists(DB_PATH):
        return None, None, None

    conn = sqlite3.connect(DB_PATH)

    answers = pd.read_sql("""
        SELECT a.*, s.mode
        FROM answers a JOIN sessions s ON a.session_id = s.id
        ORDER BY a.id
    """, conn)

    sessions = pd.read_sql("""
        SELECT * FROM sessions WHERE q_count > 0 ORDER BY id
    """, conn)

    conn.close()
    return answers, sessions


answers, sessions = load_data()

# ── Header ────────────────────────────────────────────────────────────────────

st.title("🎓 Data Interview Coach")
st.caption("Track your progress · Identify weak spots · Get interview-ready")

if answers is None or answers.empty:
    st.info("No practice sessions yet. Run `python coach.py` to start practicing!")
    st.stop()

# ── Top KPIs ──────────────────────────────────────────────────────────────────

total_sessions  = len(sessions)
total_questions = len(answers)
overall_avg     = round(answers["score"].mean(), 1)
best_score      = int(answers["score"].max())
best_topic      = answers.groupby("topic")["score"].mean().idxmax()
weak_topic      = answers.groupby("topic")["score"].mean().idxmin()
weak_avg        = round(answers.groupby("topic")["score"].mean().min(), 1)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📅 Sessions",    total_sessions)
c2.metric("❓ Questions",   total_questions)
c3.metric("📊 Avg Score",   f"{overall_avg}/10")
c4.metric("🏆 Best Topic",  best_topic[:20])
c5.metric("🎯 Focus Area",  f"{weak_topic[:22]}… ({weak_avg})" if len(weak_topic) > 22 else f"{weak_topic} ({weak_avg})")

st.divider()

# ── Interview Readiness + Practice Next ───────────────────────────────────────

gauge_col, next_col = st.columns([1, 1])

with gauge_col:
    weights = {"SQL": 0.40, "Behavioral": 0.35, "Project": 0.25}
    cat_scores = answers.groupby("category")["score"].mean()
    avail_w = sum(weights[c] for c in cat_scores.index if c in weights)
    readiness = round(
        sum(cat_scores[c] * weights[c] for c in cat_scores.index if c in weights)
        / avail_w * 10, 1
    ) if avail_w else round(overall_avg * 10, 1)

    gauge_color = GREEN if readiness >= 80 else YELLOW if readiness >= 60 else RED
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=readiness,
        number={"suffix": "%", "font": {"size": 52, "color": gauge_color}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"size": 11}},
            "bar":  {"color": gauge_color, "thickness": 0.25},
            "bgcolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0,  60], "color": "rgba(230,57,70,0.15)"},
                {"range": [60, 80], "color": "rgba(233,196,106,0.15)"},
                {"range": [80,100], "color": "rgba(82,183,136,0.15)"},
            ],
            "threshold": {
                "line": {"color": GREEN, "width": 3},
                "thickness": 0.8,
                "value": 80,
            },
        },
        title={"text": "Interview Readiness", "font": {"size": 15}},
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        height=240,
        margin=dict(l=20, r=20, t=30, b=10),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
    missing = [c for c in ["SQL","Behavioral","Project"] if c not in cat_scores.index]
    if missing:
        st.caption(f"⚠️ Missing data for: {', '.join(missing)} — practice these to get a full score")

with next_col:
    st.subheader("📌 Practice Next")
    topic_df_sorted = (
        answers.groupby(["category","topic"])["score"]
        .mean().round(1).reset_index()
        .sort_values("score")
    )
    mode_map = {"SQL": "[1] SQL Drill", "Behavioral": "[2] Behavioral", "Project": "[3] Project Deep"}
    for _, row in topic_df_sorted.head(3).iterrows():
        icon  = "🔴" if row["score"] < 5 else "🟡" if row["score"] < 8 else "🟢"
        badge = mode_map.get(row["category"], "[4] Mixed")
        st.markdown(
            f"{icon} **{row['topic']}** &nbsp; `{row['score']}/10`",
            unsafe_allow_html=True,
        )
        st.caption(f"{row['category']} · Run {badge} in coach.py")
    st.markdown("")
    st.info("💡 Tip: aim for 3 attempts per topic — score stabilizes after repetition.")

st.divider()

# ── Score trend over time ─────────────────────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Score Trend Over Time")

    answers["answered_at"] = pd.to_datetime(answers["answered_at"])
    answers["q_num"] = range(1, len(answers) + 1)

    # Rolling average
    answers["rolling_avg"] = answers["score"].rolling(window=5, min_periods=1).mean().round(1)

    fig = go.Figure()
    fig.add_scatter(
        x=answers["q_num"], y=answers["score"],
        mode="markers", name="Score",
        marker=dict(color=answers["score"],
                    colorscale=[[0,"#e63946"],[0.5,"#e9c46a"],[1,"#52b788"]],
                    size=8, showscale=False),
    )
    fig.add_scatter(
        x=answers["q_num"], y=answers["rolling_avg"],
        mode="lines", name="Rolling avg (5)",
        line=dict(color=TEAL, width=2.5),
    )
    fig.add_hline(y=8, line_dash="dot", line_color=GREEN,
                  annotation_text="Target 8+", annotation_position="right")
    fig.update_layout(
        xaxis_title="Question #", yaxis_title="Score",
        yaxis=dict(range=[0, 10.5]),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏷️ Score by Category")

    cat_df = answers.groupby("category")["score"].agg(["mean","count"]).reset_index()
    cat_df.columns = ["Category", "Avg Score", "Questions"]
    cat_df["Avg Score"] = cat_df["Avg Score"].round(1)
    cat_df["Color"] = cat_df["Category"].map(
        {"SQL": TEAL, "Behavioral": ORANGE, "Project": YELLOW}
    )

    fig2 = go.Figure(go.Bar(
        x=cat_df["Category"],
        y=cat_df["Avg Score"],
        marker_color=cat_df["Color"],
        text=cat_df["Avg Score"],
        textposition="outside",
        width=0.5,
    ))
    fig2.add_hline(y=8, line_dash="dot", line_color=GREEN,
                   annotation_text="Target 8+")
    fig2.update_layout(
        yaxis=dict(range=[0, 11], title="Avg Score"),
        xaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True)

    if len(cat_df) >= 3:
        st.subheader("🎯 Skills Radar")
        cats = cat_df["Category"].tolist()
        vals = cat_df["Avg Score"].tolist()
        fig_radar = go.Figure(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=cats + [cats[0]],
            fill="toself",
            fillcolor="rgba(42,157,143,0.2)",
            line=dict(color=TEAL, width=2.5),
            name="Score",
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=10)),
                bgcolor="rgba(0,0,0,0)",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            height=280,
            margin=dict(l=30, r=30, t=20, b=20),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# ── Topic heatmap ─────────────────────────────────────────────────────────────

st.subheader("📊 Performance by Topic")

topic_df = (
    answers.groupby(["category", "topic"])["score"]
    .agg(["mean", "count"])
    .reset_index()
)
topic_df.columns = ["Category", "Topic", "Avg Score", "Attempts"]
topic_df["Avg Score"] = topic_df["Avg Score"].round(1)
topic_df = topic_df.sort_values("Avg Score", ascending=True)

col3, col4 = st.columns([2, 1])

with col3:
    fig3 = px.bar(
        topic_df, x="Avg Score", y="Topic", orientation="h",
        color="Avg Score",
        color_continuous_scale=[[0,"#e63946"],[0.5,"#e9c46a"],[0.8,"#52b788"],[1,"#2a9d8f"]],
        text="Avg Score",
        range_color=[0, 10],
        hover_data={"Attempts": True, "Category": True},
    )
    fig3.add_vline(x=8, line_dash="dot", line_color=GREEN,
                   annotation_text="Target 8+")
    fig3.update_layout(
        xaxis=dict(range=[0, 11], title="Avg Score"),
        yaxis_title="",
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=max(300, len(topic_df) * 35),
    )
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("**Topic Summary**")
    display_df = topic_df[["Topic","Category","Avg Score","Attempts"]].sort_values("Avg Score")
    display_df["Status"] = display_df["Avg Score"].apply(
        lambda s: "🔴 Focus" if s < 5 else "🟡 Develop" if s < 8 else "🟢 Good"
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── Session history ───────────────────────────────────────────────────────────

st.divider()
st.subheader("📅 Session History")

sessions["started_at"] = pd.to_datetime(sessions["started_at"]).dt.strftime("%Y-%m-%d %H:%M")
sessions_display = sessions[["started_at", "mode", "q_count", "avg_score"]].copy()
sessions_display.columns = ["Date", "Mode", "Questions", "Avg Score"]
sessions_display["Avg Score"] = sessions_display["Avg Score"].round(1)
sessions_display["Grade"] = sessions_display["Avg Score"].apply(
    lambda s: "🟢 Good" if s >= 8 else "🟡 Developing" if s >= 5 else "🔴 Needs Work"
)

st.dataframe(
    sessions_display.sort_values("Date", ascending=False),
    use_container_width=True, hide_index=True,
)

# ── Recent answers ────────────────────────────────────────────────────────────

with st.expander("📝 Recent Answers & Feedback"):
    recent = answers.tail(10)[
        ["answered_at","category","topic","score","question","feedback"]
    ].copy()
    recent["answered_at"] = recent["answered_at"].dt.strftime("%H:%M")
    recent.columns = ["Time","Category","Topic","Score","Question","Feedback"]
    recent = recent.sort_values("Score", ascending=True)

    for _, row in recent.iterrows():
        color = "🟢" if row["Score"] >= 8 else "🟡" if row["Score"] >= 5 else "🔴"
        st.markdown(f"**{color} {row['Score']}/10** · [{row['Category']}] {row['Topic']}")
        st.caption(f"Q: {row['Question'][:120]}...")
        if row["Feedback"]:
            st.caption(f"Feedback: {str(row['Feedback'])[:200]}...")
        st.divider()

# ── Footer ────────────────────────────────────────────────────────────────────

st.caption("🎓 Data Interview Coach · Built with Claude API + Streamlit · evgeniimatveev")
