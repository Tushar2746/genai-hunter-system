"""
XP system: reward table + functions to award and log XP.
"""
from datetime import datetime, date
from database.models import XPLog, DailyStat

XP_REWARDS = {
    "study_hour": 50,
    "easy_dsa": 10,
    "medium_dsa": 20,
    "hard_dsa": 40,
    "task_complete": 25,
    "project_feature": 100,
    "project_complete": 500,
    "paper": 100,
    "certificate": 250,
    "github_commit": 25,
    "roadmap_topic": 30,
}


def award_xp(db, amount: int, source: str, description: str = None):
    """Log an XP event and roll it up into today's DailyStat row."""
    entry = XPLog(amount=amount, source=source, description=description, logged_at=datetime.utcnow())
    db.add(entry)

    today = date.today()
    stat = db.query(DailyStat).filter(DailyStat.stat_date == today).first()
    if not stat:
        stat = DailyStat(stat_date=today, xp_earned=0)
        db.add(stat)
        db.flush()
    stat.xp_earned = (stat.xp_earned or 0) + amount

    db.commit()
    return entry


def total_xp(db) -> int:
    from sqlalchemy import func
    result = db.query(func.sum(XPLog.amount)).scalar()
    return int(result or 0)


def xp_for_dsa(difficulty: str) -> int:
    key = f"{difficulty.lower()}_dsa"
    return XP_REWARDS.get(key, 10)
