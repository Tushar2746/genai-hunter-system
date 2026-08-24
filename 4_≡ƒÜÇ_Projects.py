import streamlit as st
from datetime import datetime

from database.database import init_db, get_session
from database.models import Project
from core.progress import project_progress
from core.xp import award_xp, XP_REWARDS
from core.achievements import check_and_unlock

st.set_page_config(page_title="Projects", page_icon="🚀", layout="wide")
init_db()
db = get_session()

st.title("🚀 Portfolio Projects")

done, total, pct = project_progress(db)
st.progress(pct / 100 if total else 0, text=f"{pct}% complete ({done}/{total} projects)")
st.divider()

with st.expander("➕ Add a new project", expanded=False):
    with st.form("proj_add", clear_on_submit=True):
        name = st.text_input("Project name")
        desc = st.text_area("Description")
        features_total = st.number_input("Total planned features", min_value=1, max_value=50, value=5)
        github_url = st.text_input("GitHub URL (optional)")
        if st.form_submit_button("Add project") and name.strip():
            db.add(Project(name=name.strip(), description=desc, features_total=features_total,
                            github_url=github_url or None, status="not_started"))
            db.commit()
            st.rerun()

st.divider()

projects = db.query(Project).order_by(Project.id.desc()).all()
if not projects:
    st.info("No projects yet — add your first one above (e.g. 'RAG Ingestion Pipeline').")

for p in projects:
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"### {p.name}")
            if p.description:
                st.caption(p.description)
            if p.github_url:
                st.markdown(f"[GitHub ↗]({p.github_url})")
        with c2:
            status_badge = {"not_started": "⚪ Not started", "in_progress": "🟡 In progress", "complete": "🟢 Complete"}
            st.markdown(f"**{status_badge.get(p.status, p.status)}**")

        feat_pct = round(100 * p.features_done / p.features_total, 1) if p.features_total else 0
        st.progress(feat_pct / 100, text=f"Features: {p.features_done}/{p.features_total} ({feat_pct}%)")

        fc1, fc2, fc3, fc4 = st.columns(4)
        if fc1.button("➕ Feature done", key=f"feat_{p.id}", disabled=p.features_done >= p.features_total):
            p.features_done += 1
            if p.status == "not_started":
                p.status = "in_progress"
            db.commit()
            award_xp(db, XP_REWARDS["project_feature"], "project_feature", f"{p.name} — feature")

            if p.features_done >= p.features_total and p.status != "complete":
                p.status = "complete"
                p.completed_at = datetime.utcnow()
                db.commit()
                award_xp(db, XP_REWARDS["project_complete"], "project_complete", p.name)

            for ach in check_and_unlock(db):
                st.toast(f"{ach.icon} Achievement unlocked: {ach.name}!", icon="🏆")
            st.rerun()

        if fc2.button("↩️ Undo feature", key=f"undo_{p.id}", disabled=p.features_done <= 0):
            p.features_done -= 1
            if p.features_done < p.features_total:
                p.status = "in_progress"
            db.commit()
            st.rerun()

        if fc3.button("✅ Mark complete", key=f"complete_{p.id}", disabled=p.status == "complete"):
            was_complete = p.status == "complete"
            p.status = "complete"
            p.features_done = p.features_total
            p.completed_at = datetime.utcnow()
            db.commit()
            if not was_complete:
                award_xp(db, XP_REWARDS["project_complete"], "project_complete", p.name)
                for ach in check_and_unlock(db):
                    st.toast(f"{ach.icon} Achievement unlocked: {ach.name}!", icon="🏆")
            st.rerun()

        if fc4.button("🗑️ Delete", key=f"del_proj_{p.id}"):
            db.delete(p)
            db.commit()
            st.rerun()

db.close()
