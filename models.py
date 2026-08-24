"""
SQLAlchemy models for GenAI Hunter System.
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Task(Base):
    """A single scheduled task/quest for a given day."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    task_date = Column(Date, default=date.today, index=True)
    block = Column(String, default="General")       # e.g. "Learn", "Implementation", "DSA", "Project", "Research", "Career"
    title = Column(String, nullable=False)
    category = Column(String, default="general")     # python / ml / dl / llm / agents / dsa / project / research / career
    xp_value = Column(Integer, default=25)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    start_time = Column(String, nullable=True)        # "08:00"
    end_time = Column(String, nullable=True)          # "10:00"


class DSAProblem(Base):
    """A DSA problem the user has logged (attempted or solved)."""
    __tablename__ = "dsa_problems"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, default="arrays")        # arrays, trees, graphs, dp, strings, etc.
    difficulty = Column(String, default="easy")         # easy / medium / hard
    solved = Column(Boolean, default=False)
    solved_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)


class Project(Base):
    """A portfolio project (RAG pipeline, fine-tuning, agent, etc.)."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="not_started")     # not_started / in_progress / complete
    features_total = Column(Integer, default=1)
    features_done = Column(Integer, default=0)
    github_url = Column(String, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class RoadmapItem(Base):
    """A node in the skill tree / 14-week roadmap."""
    __tablename__ = "roadmap_items"

    id = Column(Integer, primary_key=True)
    skill_area = Column(String, nullable=False)   # Python, DSA, ML, PyTorch, Transformers, LLM, RAG, Fine-tuning, Agents, AI Systems
    topic = Column(String, nullable=False)         # e.g. "Decorators", "Async/Await"
    week = Column(Integer, default=1)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    resource_url = Column(String, nullable=True)


class XPLog(Base):
    """Every XP-earning event, for analytics + level calc."""
    __tablename__ = "xp_log"

    id = Column(Integer, primary_key=True)
    logged_at = Column(DateTime, default=datetime.utcnow)
    amount = Column(Integer, nullable=False)
    source = Column(String, nullable=False)   # "study_hour", "easy_dsa", "project_complete", etc.
    description = Column(String, nullable=True)


class DailyStat(Base):
    """One row per day: rolled-up study hours / dsa counts / xp for streaks + charts."""
    __tablename__ = "daily_stats"

    id = Column(Integer, primary_key=True)
    stat_date = Column(Date, unique=True, default=date.today, index=True)
    hours_studied = Column(Float, default=0.0)
    dsa_solved = Column(Integer, default=0)
    xp_earned = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    tasks_total = Column(Integer, default=0)


class Achievement(Base):
    """Unlockable achievements / badges."""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    icon = Column(String, default="🏅")
    condition_type = Column(String, nullable=False)   # "xp_total", "dsa_solved", "streak_days", "projects_complete"
    condition_value = Column(Integer, nullable=False)
    unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, nullable=True)


class Session(Base):
    """A logged study/focus session (from the timer)."""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    label = Column(String, default="Study Session")
    started_at = Column(DateTime, default=datetime.utcnow)
    duration_minutes = Column(Float, default=0.0)
