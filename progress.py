"""
Progress calculations: roadmap %, DSA %, project %, streaks.
"""
from datetime import date, timedelta
from database.models import RoadmapItem, DSAProblem, Project, DailyStat, Task


def roadmap_progress_by_area(db):
    """Return {skill_area: (done, total, pct)} for every area in the roadmap."""
    items = db.query(RoadmapItem).all()
    areas = {}
    for item in items:
        areas.setdefault(item.skill_area, [0, 0])
        areas[item.skill_area][1] += 1
        if item.completed:
            areas[item.skill_area][0] += 1
    return {
        area: (done, total, round(100 * done / total, 1) if total else 0)
        for area, (done, total) in areas.items()
    }


def overall_roadmap_progress(db):
    items = db.query(RoadmapItem).all()
    total = len(items)
    done = sum(1 for i in items if i.completed)
    pct = round(100 * done / total, 1) if total else 0
    return done, total, pct


def dsa_progress(db):
    total = db.query(DSAProblem).count()
    done = db.query(DSAProblem).filter(DSAProblem.solved == True).count()  # noqa: E712
    pct = round(100 * done / total, 1) if total else 0
    return done, total, pct


def dsa_progress_by_category(db):
    problems = db.query(DSAProblem).all()
    cats = {}
    for p in problems:
        cats.setdefault(p.category, [0, 0])
        cats[p.category][1] += 1
        if p.solved:
            cats[p.category][0] += 1
    return {
        cat: (done, total, round(100 * done / total, 1) if total else 0)
        for cat, (done, total) in cats.items()
    }


def project_progress(db):
    projects = db.query(Project).all()
    total = len(projects)
    done = sum(1 for p in projects if p.status == "complete")
    pct = round(100 * done / total, 1) if total else 0
    return done, total, pct


def today_task_progress(db, the_date=None):
    the_date = the_date or date.today()
    tasks = db.query(Task).filter(Task.task_date == the_date).all()
    total = len(tasks)
    done = sum(1 for t in tasks if t.completed)
    return done, total


def current_streak(db) -> int:
    """Count consecutive days (ending today or yesterday) with tasks_completed > 0."""
    stats = db.query(DailyStat).order_by(DailyStat.stat_date.desc()).all()
    stat_map = {s.stat_date: s for s in stats}

    streak = 0
    cursor = date.today()
    # allow today to be "in progress" without breaking the streak
    if cursor not in stat_map or (stat_map[cursor].tasks_completed or 0) == 0:
        cursor -= timedelta(days=1)

    while cursor in stat_map and (stat_map[cursor].tasks_completed or 0) > 0:
        streak += 1
        cursor -= timedelta(days=1)

    return streak


def weekly_hours(db, weeks_back: int = 1) -> float:
    start = date.today() - timedelta(days=7 * weeks_back)
    stats = db.query(DailyStat).filter(DailyStat.stat_date >= start).all()
    return round(sum(s.hours_studied or 0 for s in stats), 1)
