import streamlit as st

from database.database import init_db, get_session
from database.models import Achievement
from core.achievements import check_and_unlock

st.set_page_config(page_title="Achievements", page_icon="🏆", layout="wide")
init_db()
db = get_session()

check_and_unlock(db)

st.title("🏆 Achievements")

achievements = db.query(Achievement).order_by(Achievement.unlocked.desc(), Achievement.condition_value).all()
unlocked = [a for a in achievements if a.unlocked]
locked = [a for a in achievements if not a.unlocked]

st.metric("Unlocked", f"{len(unlocked)}/{len(achievements)}")
st.divider()

cols = st.columns(3)
for i, ach in enumerate(unlocked):
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"## {ach.icon}")
            st.markdown(f"**{ach.name}**")
            st.caption(ach.description)
            if ach.unlocked_at:
                st.caption(f"Unlocked {ach.unlocked_at.strftime('%b %d, %Y')}")

if locked:
    st.divider()
    st.subheader("Locked")
    cols2 = st.columns(3)
    for i, ach in enumerate(locked):
        with cols2[i % 3]:
            with st.container(border=True):
                st.markdown("## 🔒")
                st.markdown(f"**{ach.name}**")
                st.caption(ach.description)

db.close()
