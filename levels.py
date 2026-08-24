"""
Level system.

Leveling curve: level N requires N * 250 XP more than level N-1
(i.e. cumulative XP to reach level N = 125 * N * (N+1)).
Titles are awarded at specific level thresholds per the roadmap doc.
Note: titles are "game flavor" - they do NOT certify real skill.
Actual skill rank comes from roadmap/skill-tree completion (see core/progress.py).
"""

LEVEL_TITLES = {
    1: "Novice",
    5: "Python Apprentice",
    10: "ML Apprentice",
    20: "ML Engineer",
    30: "Deep Learning Engineer",
    40: "GenAI Engineer",
    50: "LLM Engineer",
    60: "AI Systems Engineer",
    75: "Research Engineer",
    100: "BIG TECH READY",
}

XP_PER_LEVEL_UNIT = 125  # XP required to reach `level` = XP_PER_LEVEL_UNIT * (level - 1) * level
MAX_LEVEL = 100


def cumulative_xp_for_level(level: int) -> int:
    """XP needed to REACH this level. Level 1 always starts at 0 XP."""
    if level <= 1:
        return 0
    return XP_PER_LEVEL_UNIT * (level - 1) * level


def get_level_from_xp(xp: int) -> int:
    level = 1
    while level < MAX_LEVEL and xp >= cumulative_xp_for_level(level + 1):
        level += 1
    return level


def get_title_for_level(level: int) -> str:
    title = LEVEL_TITLES[1]
    for lvl in sorted(LEVEL_TITLES):
        if level >= lvl:
            title = LEVEL_TITLES[lvl]
    return title


def xp_progress_in_level(xp: int):
    """Return (current_into_level, xp_needed_for_next_level, fraction_0_to_1)."""
    level = get_level_from_xp(xp)
    floor_xp = cumulative_xp_for_level(level)
    ceil_xp = cumulative_xp_for_level(level + 1)
    span = ceil_xp - floor_xp
    into = xp - floor_xp
    fraction = min(1.0, into / span) if span > 0 else 1.0
    return into, span, fraction
