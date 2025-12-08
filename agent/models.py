from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional, List


class Email(BaseModel):
    id: str
    subject: str
    sender: str
    received_at: Optional[datetime] = None
    body: str


class Task(BaseModel):
    id: str
    email_id: str
    title: str
    description: str
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = Field(default=3, ge=1, le=5)
    priority_reason: str = ""
    estimated_minutes: int = 60


class ScheduledTask(BaseModel):
    task_id: str
    start: datetime
    end: datetime
    title: str
    priority: int
    source_email_subject: str