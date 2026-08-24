"""
Seed the database with:
- the 14-week GenAI Engineer roadmap (skill tree)
- starter achievements
- today's default quest schedule (from the doc's example day)

Safe to re-run: only seeds if tables are empty.
"""
from datetime import date
from database.models import RoadmapItem, Achievement, Task

# Skill tree, mapped onto a 14-week plan.
# skill_area matches the tree in the project doc: Python, DSA, ML, PyTorch,
# Transformers, LLM, RAG, Fine-tuning, Agents, AI Systems
ROADMAP_SEED = [
    # Week 1-2: Python foundations
    ("Python", "OOP fundamentals", 1),
    ("Python", "Decorators", 1),
    ("Python", "Generators & iterators", 1),
    ("Python", "Async / await", 2),
    ("Python", "Building a REST API (FastAPI basics)", 2),
    ("Python", "Testing with pytest", 2),
    # Week 2-5: DSA (ongoing throughout, but core topics front-loaded)
    ("DSA", "Arrays & strings", 2),
    ("DSA", "Hashing", 2),
    ("DSA", "Trees", 3),
    ("DSA", "Graphs (BFS/DFS)", 3),
    ("DSA", "Dynamic programming", 4),
    ("DSA", "Heaps & priority queues", 4),
    # Week 3-5: ML foundations
    ("ML", "Statistics & probability refresher", 3),
    ("ML", "Linear & logistic regression", 3),
    ("ML", "Classic ML models (trees, SVM, boosting)", 4),
    ("ML", "Model evaluation & metrics", 4),
    ("ML", "Feature engineering", 5),
    # Week 5-7: Deep Learning / PyTorch
    ("PyTorch", "Tensors & autograd", 5),
    ("PyTorch", "Building a training loop", 5),
    ("PyTorch", "CNNs", 6),
    ("PyTorch", "RNNs / sequence models", 6),
    ("PyTorch", "Optimization & regularization", 7),
    # Week 7-9: Transformers
    ("Transformers", "Attention mechanism from scratch", 7),
    ("Transformers", "Transformer architecture", 8),
    ("Transformers", "Hugging Face ecosystem", 8),
    ("Transformers", "Tokenization deep dive", 9),
    # Week 9-11: LLMs
    ("LLM", "How LLMs are trained (pretraining/RLHF)", 9),
    ("LLM", "Prompt engineering", 9),
    ("LLM", "LLM APIs (OpenAI/Gemini)", 10),
    ("LLM", "Embeddings & vector search", 10),
    ("LLM", "Evaluation of LLM outputs", 11),
    # Week 11-12: RAG
    ("RAG", "Chunking strategies", 11),
    ("RAG", "Vector databases", 11),
    ("RAG", "Building a RAG pipeline end-to-end", 12),
    ("RAG", "RAG evaluation & retrieval quality", 12),
    # Week 12-13: Fine-tuning
    ("Fine-tuning", "LoRA / PEFT fundamentals", 12),
    ("Fine-tuning", "Dataset prep for fine-tuning", 13),
    ("Fine-tuning", "Fine-tuning a small open model", 13),
    # Week 13-14: Agents
    ("Agents", "Tool use / function calling", 13),
    ("Agents", "Agent planning loops (ReAct, etc.)", 14),
    ("Agents", "Multi-agent orchestration", 14),
    ("Agents", "Building a real agent project", 14),
    # Week 14: AI Systems / capstone
    ("AI Systems", "Deploying an LLM app to production", 14),
    ("AI Systems", "Monitoring & cost management", 14),
    ("AI Systems", "Capstone project polish + portfolio writeup", 14),
]

ACHIEVEMENTS_SEED = [
    ("First Steps", "Complete your first task", "🐣", "xp_total", 1),
    ("Century Club", "Earn 100 XP", "💯", "xp_total", 100),
    ("Rising Hunter", "Earn 1,000 XP", "⚔️", "xp_total", 1000),
    ("GenAI Grinder", "Earn 10,000 XP", "🔥", "xp_total", 10000),
    ("DSA Starter", "Solve 10 DSA problems", "🧮", "dsa_solved", 10),
    ("DSA Warrior", "Solve 50 DSA problems", "⚡", "dsa_solved", 50),
    ("DSA Master", "Solve 200 DSA problems", "🏆", "dsa_solved", 200),
    ("Consistency", "Hit a 3-day streak", "📅", "streak_days", 3),
    ("Discipline", "Hit a 7-day streak", "🗓️", "streak_days", 7),
    ("Iron Will", "Hit a 30-day streak", "🛡️", "streak_days", 30),
    ("Shipper", "Complete your first project", "🚀", "projects_complete", 1),
    ("Portfolio Builder", "Complete 5 projects", "📦", "projects_complete", 5),
]

# Default schedule from the example day in the project doc
DEFAULT_TODAY_TASKS = [
    dict(block="Learn", title="Understand Python decorators", category="python", xp_value=25,
         start_time="08:00", end_time="10:00"),
    dict(block="Learn", title="Implement 3 decorator examples", category="python", xp_value=25,
         start_time="08:00", end_time="10:00"),
    dict(block="Implementation", title="Build decorator-based logger", category="python", xp_value=50,
         start_time="10:30", end_time="12:00"),
    dict(block="Implementation", title="Write tests for logger", category="python", xp_value=25,
         start_time="10:30", end_time="12:00"),
    dict(block="DSA", title="Two Sum", category="dsa", xp_value=10, start_time="13:00", end_time="14:30"),
    dict(block="DSA", title="Group Anagrams", category="dsa", xp_value=20, start_time="13:00", end_time="14:30"),
    dict(block="DSA", title="Longest Substring Without Repeating Characters", category="dsa", xp_value=20,
         start_time="13:00", end_time="14:30"),
    dict(block="DSA", title="Valid Anagram", category="dsa", xp_value=10, start_time="13:00", end_time="14:30"),
    dict(block="Project", title="Build RAG ingestion pipeline", category="project", xp_value=100,
         start_time="15:00", end_time="17:00"),
    dict(block="Project", title="Test chunking strategy", category="project", xp_value=50,
         start_time="15:00", end_time="17:00"),
    dict(block="Research", title="Read a research paper", category="research", xp_value=100,
         start_time="17:30", end_time="18:30"),
    dict(block="Research", title="Write paper summary", category="research", xp_value=25,
         start_time="17:30", end_time="18:30"),
    dict(block="Career", title="Make a GitHub commit", category="career", xp_value=25,
         start_time="18:30", end_time="19:00"),
    dict(block="Career", title="Write a LinkedIn post", category="career", xp_value=25,
         start_time="18:30", end_time="19:00"),
]


def seed_all(db):
    if db.query(RoadmapItem).count() == 0:
        for area, topic, week in ROADMAP_SEED:
            db.add(RoadmapItem(skill_area=area, topic=topic, week=week))

    if db.query(Achievement).count() == 0:
        for name, desc, icon, cond_type, cond_val in ACHIEVEMENTS_SEED:
            db.add(Achievement(name=name, description=desc, icon=icon,
                                condition_type=cond_type, condition_value=cond_val))

    if db.query(Task).filter(Task.task_date == date.today()).count() == 0:
        for t in DEFAULT_TODAY_TASKS:
            db.add(Task(task_date=date.today(), **t))

    db.commit()
