"""
⚔️ GENAI HUNTER SYSTEM — Dashboard (main entrypoint)
Run with: streamlit run app.py
"""
import streamlit as st
from datetime import datetime, date, timedelta

from database.database import init_db, get_session
from database.seed import seed_all
from database.models import Task
from core.xp import award_xp, total_xp, XP_REWARDS
from core.levels import get_level_from_xp, get_title_for_level, xp_progress_in_level
from core.progress import (
    overall_roadmap_progress, dsa_progress, project_progress,
    today_task_progress, current_streak, weekly_hours,
)
from core.achievements import check_and_unlock
from database.models import DailyStat

st.set_page_config(page_title="GenAI Hunter System", page_icon="⚔️", layout="wide")

# ---------- init ----------
init_db()
db = get_session()
seed_all(db)

# ---------- header / level bar ----------
xp = total_xp(db)
level = get_level_from_xp(xp)
title = get_title_for_level(level)
into, span, frac = xp_progress_in_level(xp)
streak = current_streak(db)

st.title("⚔️ GENAI HUNTER SYSTEM")

col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
with col1:
    st.metric("Level", f"{level}", title)
with col2:
    st.metric("Total XP", f"{xp:,}")
with col3:
    st.metric("Streak", f"🔥 {streak}d")
with col4:
    st.metric("Today", date.today().strftime("%b %d"))

st.progress(frac, text=f"{into}/{span} XP to Level {level + 1}")
st.divider()

# ---------- today's quest ----------
left, right = st.columns([2, 1])

with left:
    st.subheader("🎯 Today's Quest")

    today_tasks = (
        db.query(Task)
        .filter(Task.task_date == date.today())
        .order_by(Task.start_time)
        .all()
    )

    if not today_tasks:
        st.info("No tasks scheduled for today yet. Add some below, or generate a default day on the **Today** page.")
    else:
        blocks = {}
        for t in today_tasks:
            blocks.setdefault(t.block, []).append(t)

        for block_name, tasks in blocks.items():
            time_range = ""
            if tasks[0].start_time and tasks[0].end_time:
                time_range = f"  `{tasks[0].start_time}–{tasks[0].end_time}`"
            st.markdown(f"**{block_name}**{time_range}")
            for t in tasks:
                checked = st.checkbox(
                    f"{t.title}  *(+{t.xp_value} XP)*",
                    value=t.completed,
                    key=f"task_{t.id}",
                )
                if checked and not t.completed:
                    t.completed = True
                    t.completed_at = datetime.utcnow()
                    db.commit()
                    award_xp(db, t.xp_value, "task_complete", t.title)

                    stat = db.query(DailyStat).filter(DailyStat.stat_date == date.today()).first()
                    if stat:
                        stat.tasks_completed = (stat.tasks_completed or 0) + 1
                        db.commit()

                    newly = check_and_unlock(db)
                    for ach in newly:
                        st.toast(f"{ach.icon} Achievement unlocked: {ach.name}!", icon="🏆")
                    st.rerun()
                elif not checked and t.completed:
                    t.completed = False
                    t.completed_at = None
                    db.commit()
                    st.rerun()

    with st.expander("➕ Add a quick task for today"):
        with st.form("add_task_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            new_title = c1.text_input("Task")
            new_block = c2.selectbox("Block", ["Learn", "Implementation", "DSA", "Project", "Research", "Career", "General"])
            new_xp = c3.number_input("XP", min_value=5, max_value=500, value=25, step=5)
            submitted = st.form_submit_button("Add task")
            if submitted and new_title.strip():
                db.add(Task(task_date=date.today(), block=new_block, title=new_title.strip(), xp_value=new_xp))
                stat = db.query(DailyStat).filter(DailyStat.stat_date == date.today()).first()
                if not stat:
                    db.add(DailyStat(stat_date=date.today(), tasks_total=0))
                    db.flush()
                    stat = db.query(DailyStat).filter(DailyStat.stat_date == date.today()).first()
                stat.tasks_total = (stat.tasks_total or 0) + 1
                db.commit()
                st.rerun()

    st.divider()
    st.subheader("⏱️ Focus Session")
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    label = fc1.text_input("What are you working on?", value="Deep work session", key="focus_label")
    minutes = fc2.number_input("Minutes", min_value=5, max_value=240, value=25, step=5, key="focus_minutes")
    if fc3.button("✅ Log session"):
        from database.models import Session as StudySession
        db.add(StudySession(label=label, duration_minutes=minutes, started_at=datetime.utcnow()))
        stat = db.query(DailyStat).filter(DailyStat.stat_date == date.today()).first()
        if not stat:
            db.add(DailyStat(stat_date=date.today()))
            db.flush()
            stat = db.query(DailyStat).filter(DailyStat.stat_date == date.today()).first()
        stat.hours_studied = (stat.hours_studied or 0) + minutes / 60
        db.commit()
        hours = minutes / 60
        award_xp(db, round(hours * XP_REWARDS["study_hour"]), "study_hour", label)
        newly = check_and_unlock(db)
        for ach in newly:
            st.toast(f"{ach.icon} Achievement unlocked: {ach.name}!", icon="🏆")
        st.success(f"Logged {minutes} min — +{round(hours * XP_REWARDS['study_hour'])} XP")
        st.rerun()

with right:
    st.subheader("📊 Roadmap Snapshot")
    r_done, r_total, r_pct = overall_roadmap_progress(db)
    d_done, d_total, d_pct = dsa_progress(db)
    p_done, p_total, p_pct = project_progress(db)
    t_done, t_total = today_task_progress(db)

    st.progress(r_pct / 100, text=f"14-Week Roadmap — {r_pct}% ({r_done}/{r_total})")
    st.progress(d_pct / 100, text=f"DSA — {d_pct}% ({d_done}/{d_total})")
    st.progress(p_pct / 100, text=f"Projects — {p_pct}% ({p_done}/{p_total})")
    st.progress((t_done / t_total) if t_total else 0, text=f"Today's Tasks — {t_done}/{t_total}")

    st.divider()
    st.subheader("📈 This Week")
    st.metric("Hours studied (7d)", f"{weekly_hours(db, 1)}h")

    st.divider()
    st.caption("Use the sidebar to jump to **Roadmap**, **DSA**, **Projects**, **Analytics**, or **Achievements**.")

db.close()
