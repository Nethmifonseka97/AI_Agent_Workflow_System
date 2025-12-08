from datetime import datetime, timedelta
from typing import List

from .models import Task, ScheduledTask, Email


def schedule_tasks_for_day(
    tasks: List[Task],
    emails_by_id: dict[str, Email],
    day: datetime,
    work_start_hour: int = 9,
    work_end_hour: int = 17,
) -> List[ScheduledTask]:
    """
    Very simple greedy scheduler:
    - Sort tasks by priority, then due date
    - Fill the workday sequentially with estimated_minutes
    """
    # normalize day
    day = day.replace(hour=0, minute=0, second=0, microsecond=0)
    start = day.replace(hour=work_start_hour, minute=0)
    end_of_day = day.replace(hour=work_end_hour, minute=0)

    # sort tasks
    tasks_sorted = sorted(
        tasks,
        key=lambda t: (
            -t.priority,
            t.due_date or datetime.max,
        ),
    )

    scheduled: List[ScheduledTask] = []
    cursor = start

    for task in tasks_sorted:
        duration = timedelta(minutes=task.estimated_minutes)
        slot_end = cursor + duration
        if slot_end > end_of_day:
            break  # no more time in the day

        email = emails_by_id.get(task.email_id)

        scheduled.append(
            ScheduledTask(
                task_id=task.id,
                start=cursor,
                end=slot_end,
                title=task.title,
                priority=task.priority,
                source_email_subject=email.subject if email else "",
            )
        )
        cursor = slot_end

    return scheduled