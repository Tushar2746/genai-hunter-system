import streamlit as st
from datetime import date, timedelta, datetime

from database.database import init_db, get_session
from database.models import Task, DailyStat
from database.seed import DEFAULT_TODAY_TASKS
from core.xp import award_xp
from core.achievements import check_and_unlock

st.set_page_config(page_title="Today's Schedule", page_icon="📅", layout="wide")
init_db()
db = get_session()

st.title("📅 Today's Schedule")

selected_date = st.date_input("Date", value=date.today())

c1, c2 = st.columns([1, 3])
if c1.button("🔁 Generate default day for this date"):
    existing = db.query(Task).filter(Task.task_date == selected_date).count()
    if existing:
        st.warning("Tasks already exist for this date. Delete them below first if you want to regenerate.")
    else:
        for t in DEFAULT_TODAY_TASKS:
            db.add(Task(task_date=selected_date, **t))
        db.commit()
        st.rerun()

tasks = db.query(Task).filter(Task.task_date == selected_date).order_by(Task.start_time).all()

if not tasks:
    st.info("No tasks for this date yet.")
else:
    blocks = {}
    for t in tasks:
        blocks.setdefault(t.block, []).append(t)

    for block_name, block_tasks in blocks.items():
        time_range = ""
        if block_tasks[0].start_time and block_tasks[0].end_time:
            time_range = f"  `{block_tasks[0].start_time}–{block_tasks[0].end_time}`"
        st.subheader(f"{block_name}{time_range}")
        for t in block_tasks:
            row = st.columns([6, 1])
            with row[0]:
                checked = st.checkbox(f"{t.title}  *(+{t.xp_value} XP)*", value=t.completed, key=f"pg_task_{t.id}")
            with row[1]:
                if st.button("🗑️", key=f"del_{t.id}"):
                    db.delete(t)
                    db.commit()
                    st.rerun()

            if checked and not t.completed:
                t.completed = True
                t.completed_at = datetime.utcnow()
                db.commit()
                if selected_date == date.today():
                    award_xp(db, t.xp_value, "task_complete", t.title)
                    stat = db.query(DailyStat).filter(DailyStat.stat_date == date.today()).first()
                    if stat:
                        stat.tasks_completed = (stat.tasks_completed or 0) + 1
                        db.commit()
                    for ach in check_and_unlock(db):
                        st.toast(f"{ach.icon} Achievement unlocked: {ach.name}!", icon="🏆")
                st.rerun()
            elif not checked and t.completed:
                t.completed = False
                t.completed_at = None
                db.commit()
                st.rerun()

st.divider()
with st.expander("➕ Add a custom task"):
    with st.form("today_add_task", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        title = c1.text_input("Task title")
        block = c2.selectbox("Block", ["Learn", "Implementation", "DSA", "Project", "Research", "Career", "General"])
        cat = c3.selectbox("Category", ["python", "ml", "dl", "llm", "agents", "dsa", "project", "research", "career", "general"])
        xp_val = c4.number_input("XP", min_value=5, max_value=500, value=25, step=5)
        start_t = st.text_input("Start time (optional, e.g. 09:00)")
        end_t = st.text_input("End time (optional, e.g. 10:30)")
        if st.form_submit_button("Add") and title.strip():
            db.add(Task(
                task_date=selected_date, block=block, title=title.strip(),
                category=cat, xp_value=xp_val,
                start_time=start_t or None, end_time=end_t or None,
            ))
            db.commit()
            st.rerun()

db.close()
