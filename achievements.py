"""
Check and unlock achievements based on current stats.
Returns a list of newly-unlocked Achievement objects (for toast/celebration UI).
"""
from datetime import datetime
from database.models import Achievement, DSAProblem, Project
from core.xp import total_xp
from core.progress import current_streak


def check_and_unlock(db):
    newly_unlocked = []
    achievements = db.query(Achievement).filter(Achievement.unlocked == False).all()  # noqa: E712
    if not achievements:
        return newly_unlocked

    xp = total_xp(db)
    dsa_solved = db.query(DSAProblem).filter(DSAProblem.solved == True).count()  # noqa: E712
    streak = current_streak(db)
    projects_done = db.query(Project).filter(Project.status == "complete").count()

    metric_map = {
        "xp_total": xp,
        "dsa_solved": dsa_solved,
        "streak_days": streak,
        "projects_complete": projects_done,
    }

    for ach in achievements:
        current_value = metric_map.get(ach.condition_type, 0)
        if current_value >= ach.condition_value:
            ach.unlocked = True
            ach.unlocked_at = datetime.utcnow()
            newly_unlocked.append(ach)

    if newly_unlocked:
        db.commit()

    return newly_unlocked
