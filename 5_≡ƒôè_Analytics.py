import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

from database.database import init_db, get_session
from database.models import DailyStat, DSAProblem, XPLog, Project
from core.progress import dsa_progress_by_category, roadmap_progress_by_area, current_streak, weekly_hours
from core.xp import total_xp
from core.levels import get_level_from_xp, get_title_for_level

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")
init_db()
db = get_session()

st.title("📊 Analytics")

xp = total_xp(db)
level = get_level_from_xp(xp)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Level", level, get_title_for_level(level))
c2.metric("Total XP", f"{xp:,}")
c3.metric("Streak", f"{current_streak(db)} days")
c4.metric("Hours (7d)", f"{weekly_hours(db, 1)}h")

st.divider()

# ---------- Study hours over last 30 days ----------
st.subheader("Study Hours — Last 30 Days")
start = date.today() - timedelta(days=29)
stats = db.query(DailyStat).filter(DailyStat.stat_date >= start).order_by(DailyStat.stat_date).all()
date_range = [start + timedelta(days=i) for i in range(30)]
stat_map = {s.stat_date: s for s in stats}
hours_data = [stat_map[d].hours_studied if d in stat_map else 0 for d in date_range]

df_hours = pd.DataFrame({"date": date_range, "hours": hours_data})
if df_hours["hours"].sum() > 0:
    fig = px.bar(df_hours, x="date", y="hours", title=None)
    fig.update_layout(margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Log a focus session on the Dashboard to start seeing your study-hours chart.")

# ---------- XP over time ----------
st.subheader("XP Earned Over Time")
xp_logs = db.query(XPLog).order_by(XPLog.logged_at).all()
if xp_logs:
    df_xp = pd.DataFrame([{"date": x.logged_at.date(), "amount": x.amount} for x in xp_logs])
    df_xp = df_xp.groupby("date", as_index=False)["amount"].sum()
    df_xp["cumulative"] = df_xp["amount"].cumsum()
    fig2 = px.area(df_xp, x="date", y="cumulative", title=None)
    fig2.update_layout(margin=dict(t=10))
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Complete tasks or log DSA problems to start earning XP.")

col_a, col_b = st.columns(2)

# ---------- DSA by category ----------
with col_a:
    st.subheader("DSA by Category")
    by_cat = dsa_progress_by_category(db)
    if by_cat:
        df_cat = pd.DataFrame([
            {"category": cat, "solved": d, "total": t} for cat, (d, t, pct) in by_cat.items()
        ])
        fig3 = px.bar(df_cat, x="category", y=["solved", "total"], barmode="overlay", title=None)
        fig3.update_layout(margin=dict(t=10))
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No DSA problems logged yet.")

# ---------- Roadmap progress by skill area ----------
with col_b:
    st.subheader("Roadmap Progress by Skill Area")
    by_area = roadmap_progress_by_area(db)
    if by_area:
        df_area = pd.DataFrame([
            {"area": area, "pct": pct} for area, (d, t, pct) in by_area.items()
        ])
        fig4 = px.bar(df_area, x="area", y="pct", range_y=[0, 100], title=None)
        fig4.update_layout(margin=dict(t=10))
        st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ---------- XP source breakdown ----------
st.subheader("Where Your XP Comes From")
if xp_logs:
    df_source = pd.DataFrame([{"source": x.source, "amount": x.amount} for x in xp_logs])
    df_source = df_source.groupby("source", as_index=False)["amount"].sum()
    fig5 = px.pie(df_source, names="source", values="amount", title=None)
    st.plotly_chart(fig5, use_container_width=True)

db.close()
