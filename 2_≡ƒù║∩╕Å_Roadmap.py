import streamlit as st
from datetime import datetime

from database.database import init_db, get_session
from database.models import RoadmapItem
from core.progress import roadmap_progress_by_area, overall_roadmap_progress
from core.xp import award_xp, XP_REWARDS
from core.achievements import check_and_unlock

st.set_page_config(page_title="Roadmap", page_icon="🗺️", layout="wide")
init_db()
db = get_session()

st.title("🗺️ 14-Week Roadmap / Skill Tree")

done, total, pct = overall_roadmap_progress(db)
st.progress(pct / 100, text=f"Overall: {pct}% ({done}/{total} topics)")
st.caption("XP determines your game level. **These skill-tree completions determine your actual rank.**")
st.divider()

by_area = roadmap_progress_by_area(db)

# preserve a sensible skill-tree order
AREA_ORDER = ["Python", "DSA", "ML", "PyTorch", "Transformers", "LLM", "RAG", "Fine-tuning", "Agents", "AI Systems"]
areas_sorted = sorted(by_area.keys(), key=lambda a: AREA_ORDER.index(a) if a in AREA_ORDER else 999)

for area in areas_sorted:
    a_done, a_total, a_pct = by_area[area]
    with st.expander(f"**{area}** — {a_pct}% ({a_done}/{a_total})", expanded=False):
        st.progress(a_pct / 100)
        items = (
            db.query(RoadmapItem)
            .filter(RoadmapItem.skill_area == area)
            .order_by(RoadmapItem.week)
            .all()
        )
        for item in items:
            checked = st.checkbox(
                f"Week {item.week} — {item.topic}",
                value=item.completed,
                key=f"roadmap_{item.id}",
            )
            if checked and not item.completed:
                item.completed = True
                item.completed_at = datetime.utcnow()
                db.commit()
                award_xp(db, XP_REWARDS["roadmap_topic"], "roadmap_topic", item.topic)
                for ach in check_and_unlock(db):
                    st.toast(f"{ach.icon} Achievement unlocked: {ach.name}!", icon="🏆")
                st.rerun()
            elif not checked and item.completed:
                item.completed = False
                item.completed_at = None
                db.commit()
                st.rerun()

db.close()
