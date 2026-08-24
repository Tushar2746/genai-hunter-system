# ⚔️ GenAI Hunter System

Your personal, gamified tracker for becoming a GenAI Engineer — built with **Python + Streamlit + SQLite** (Phase 1 MVP from the project plan, plus core of the XP/level/achievement engine).

## What's included (this build)

- **Dashboard** — level, XP bar, streak, today's quest checklist, quick focus-session logger, roadmap snapshot
- **Today** — full daily schedule editor; regenerate the example 8-hour day; add/delete custom tasks
- **Roadmap** — 14-week skill tree (Python → DSA/ML → PyTorch → Transformers → LLM → RAG → Fine-tuning → Agents → AI Systems), pre-seeded with ~45 topics
- **DSA** — log problems by category/difficulty, track solved %, XP per difficulty
- **Projects** — track portfolio projects with feature-level progress bars
- **Analytics** — Plotly charts: study hours (30d), cumulative XP, DSA by category, roadmap progress by area, XP source breakdown
- **Achievements** — 12 starter badges that auto-unlock based on XP, DSA count, streaks, and completed projects

XP, levels (1–100, with titles from Novice → BIG TECH READY), and streak logic all live in `core/` so you can tune them freely.

## Setup

```bash
# 1. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

It will open at `http://localhost:8501`. A `genai_hunter.db` SQLite file is created automatically in the project root on first run, and the roadmap/achievements/today's schedule are auto-seeded.

## Project structure

```
genai_hunter/
├── app.py                  # Dashboard (Streamlit entrypoint)
├── database/
│   ├── models.py            # SQLAlchemy models (Task, DSAProblem, Project, RoadmapItem, XPLog, DailyStat, Achievement, Session)
│   ├── database.py          # Engine/session setup
│   └── seed.py               # 14-week roadmap, achievements, default day seed data
├── core/
│   ├── xp.py                 # XP_REWARDS table + award_xp()
│   ├── levels.py             # Level curve + titles
│   ├── progress.py           # Roadmap/DSA/project %, streaks
│   └── achievements.py       # Unlock-checking logic
├── pages/                    # Streamlit auto-discovers these as sidebar pages
│   ├── 1_📅_Today.py
│   ├── 2_🗺️_Roadmap.py
│   ├── 3_🧮_DSA.py
│   ├── 4_🚀_Projects.py
│   ├── 5_📊_Analytics.py
│   └── 6_🏆_Achievements.py
└── requirements.txt
```

## Tuning it to your own plan

- **Change the roadmap**: edit `ROADMAP_SEED` in `database/seed.py` (only runs on an empty table — delete `genai_hunter.db` to re-seed from scratch, or just add/edit rows via the Roadmap page).
- **Change XP values**: edit `XP_REWARDS` in `core/xp.py`.
- **Change level curve / titles**: edit `core/levels.py`. The curve is `XP_to_reach(level) = 125 * (level-1) * level`, so leveling gets progressively slower — tune `XP_PER_LEVEL_UNIT` to make it faster/slower.
- **Change today's default schedule**: edit `DEFAULT_TODAY_TASKS` in `database/seed.py`.
- **Add achievements**: append to `ACHIEVEMENTS_SEED` in `database/seed.py` (`condition_type` can be `xp_total`, `dsa_solved`, `streak_days`, or `projects_complete`).

## What's next (from the original roadmap doc)

This build covers **Phase 1 (MVP)** and most of **Phase 2 (Progress Engine)** and **Phase 3 (Roadmap)**. Natural next steps, in order:

1. **Phase 4 polish** — weekly PDF/email reports, more chart types
2. **Phase 5 — AI Coach**: wire up an LLM API (Gemini/OpenAI) in a new `ai/` module (`planner.py`, `coach.py`, `evaluator.py`) that reads your `DailyStat`/`DSAProblem`/`RoadmapItem` tables and (a) answers "what should I study today?" and (b) auto-adjusts tomorrow's schedule based on weak areas (e.g. low graph-DSA accuracy)
3. **Phase 6 — Production**: swap SQLite → PostgreSQL/Supabase, add FastAPI if you want a separate API layer, add real auth, deploy (Streamlit Community Cloud is the fastest path)

I'm happy to build any of these next — just say the word (e.g. "add the AI Coach page" or "help me deploy this").
