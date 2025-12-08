from datetime import datetime, timedelta
from typing import List

from .models import Task


def score_task(task: Task) -> Task:
    """
    Simple heuristic priority:
    - base 3
    - +2 if contains 'urgent' or 'asap'
    - +1 if due within 1 day
    - +1 if due within 3 days
    Priority clamped between 1 and 5.
    """
    text = (task.title + " " + task.description).lower()
    score = 3
    reasons = []

    if "urgent" in text or "asap" in text or "high priority" in text:
        score += 2
        reasons.append("Marked as urgent/ASAP.")

    if task.due_date:
        now = datetime.now()
        delta = task.due_date - now
        if delta <= timedelta(days=1):
            score += 1
            reasons.append("Due within 1 day.")
        elif delta <= timedelta(days=3):
            score += 1
            reasons.append("Due within 3 days.")

    # clamp
    score = max(1, min(5, score))
    task.priority = score
    task.priority_reason = " ".join(reasons) if reasons else "Default priority."
    return task


def prioritize_tasks(tasks: List[Task]) -> List[Task]:
    """Score all tasks and return sorted list (high priority first)."""
    scored = [score_task(t) for t in tasks]
    # Higher priority number = more important
    return sorted(scored, key=lambda t: t.priority, reverse=True)