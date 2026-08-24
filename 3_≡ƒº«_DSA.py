import streamlit as st
from datetime import datetime
import pandas as pd

from database.database import init_db, get_session
from database.models import DSAProblem
from core.progress import dsa_progress, dsa_progress_by_category
from core.xp import award_xp, xp_for_dsa
from core.achievements import check_and_unlock

st.set_page_config(page_title="DSA Tracker", page_icon="🧮", layout="wide")
init_db()
db = get_session()

st.title("🧮 DSA Tracker")

done, total, pct = dsa_progress(db)
st.progress(pct / 100 if total else 0, text=f"{pct}% solved ({done}/{total})")

by_cat = dsa_progress_by_category(db)
if by_cat:
    cols = st.columns(min(4, len(by_cat)) or 1)
    for i, (cat, (c_done, c_total, c_pct)) in enumerate(sorted(by_cat.items())):
        with cols[i % len(cols)]:
            st.metric(cat.title(), f"{c_done}/{c_total}", f"{c_pct}%")

st.divider()

with st.expander("➕ Log a new problem", expanded=True):
    with st.form("dsa_add", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        name = c1.text_input("Problem name")
        category = c2.selectbox("Category", ["arrays", "strings", "hashing", "trees", "graphs", "dp",
                                               "heaps", "linked-list", "backtracking", "greedy", "other"])
        difficulty = c3.selectbox("Difficulty", ["easy", "medium", "hard"])
        solved_now = c4.checkbox("Solved?", value=True)
        notes = st.text_area("Notes (optional)")
        if st.form_submit_button("Add") and name.strip():
            p = DSAProblem(
                name=name.strip(), category=category, difficulty=difficulty,
                solved=solved_now, notes=notes or None,
                solved_at=datetime.utcnow() if solved_now else None,
            )
            db.add(p)
            db.commit()
            if solved_now:
                award_xp(db, xp_for_dsa(difficulty), f"{difficulty}_dsa", name.strip())
                for ach in check_and_unlock(db):
                    st.toast(f"{ach.icon} Achievement unlocked: {ach.name}!", icon="🏆")
            st.rerun()

st.divider()
st.subheader("Problem Log")

problems = db.query(DSAProblem).order_by(DSAProblem.id.desc()).all()
if not problems:
    st.info("No problems logged yet.")
else:
    filter_cat = st.selectbox("Filter by category", ["All"] + sorted(by_cat.keys()))
    filtered = [p for p in problems if filter_cat == "All" or p.category == filter_cat]

    for p in filtered:
        cols = st.columns([4, 1, 1, 1])
        cols[0].write(f"**{p.name}**  ·  {p.category}  ·  _{p.difficulty}_")
        newly_solved = cols[1].checkbox("Solved", value=p.solved, key=f"dsa_{p.id}")
        if newly_solved and not p.solved:
            p.solved = True
            p.solved_at = datetime.utcnow()
            db.commit()
            award_xp(db, xp_for_dsa(p.difficulty), f"{p.difficulty}_dsa", p.name)
            for ach in check_and_unlock(db):
                st.toast(f"{ach.icon} Achievement unlocked: {ach.name}!", icon="🏆")
            st.rerun()
        elif not newly_solved and p.solved:
            p.solved = False
            p.solved_at = None
            db.commit()
            st.rerun()
        if cols[2].button("🗑️", key=f"dsa_del_{p.id}"):
            db.delete(p)
            db.commit()
            st.rerun()

db.close()
