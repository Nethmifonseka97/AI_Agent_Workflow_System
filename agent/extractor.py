import re
import uuid
from pathlib import Path
from typing import List

from dateutil import parser as date_parser

from .models import Email, Task


HEADER_PATTERN = re.compile(r"^(Subject|From|Date):", re.IGNORECASE)


def load_emails_from_folder(folder: str = "emails") -> List[Email]:
    """Load plain-text emails from a folder of .txt files."""
    emails: List[Email] = []
    for path in sorted(Path(folder).glob("*.txt")):
        content = path.read_text(encoding="utf-8")
        email = parse_email_file(content, file_name=path.name)
        emails.append(email)
    return emails


def parse_email_file(raw: str, file_name: str) -> Email:
    """Very simple parser: looks for Subject/From/Date headers, rest is body."""
    lines = raw.splitlines()
    subject = "No subject"
    sender = "unknown@example.com"
    received_at = None
    body_lines = []
    header_done = False

    for line in lines:
        if not header_done and HEADER_PATTERN.match(line):
            if line.lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
            elif line.lower().startswith("from:"):
                sender = line.split(":", 1)[1].strip()
            elif line.lower().startswith("date:"):
                text_date = line.split(":", 1)[1].strip()
                try:
                    received_at = date_parser.parse(text_date, fuzzy=True)
                except Exception:
                    received_at = None
            continue

        # blank line typically separates headers from body
        if not header_done and line.strip() == "":
            header_done = True
            continue

        if header_done:
            body_lines.append(line)

    body = "\n".join(body_lines).strip()
    return Email(
        id=str(uuid.uuid4()),
        subject=subject,
        sender=sender,
        received_at=received_at,
        body=body,
    )


# --- Task extraction logic ---


TASK_CUE_PATTERNS = [
    r"\bplease\b",
    r"\bcan you\b",
    r"\bcould you\b",
    r"\bkindly\b",
    r"\bwe need to\b",
    r"\bwe need\b",
    r"\baction required\b",
    r"\bto-do\b",
    r"\btodo\b",
    r"\bnext steps\b",
]

DUE_CUE_PATTERNS = [
    r"\bby\b",
    r"\bbefore\b",
    r"\btoday\b",
    r"\btomorrow\b",
    r"\bend of day\b",
    r"\bEOD\b",
]


def is_potential_task_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False

    # bullet points are often tasks
    if stripped.startswith(("-", "*", "•")):
        return True

    lowered = stripped.lower()
    for pat in TASK_CUE_PATTERNS:
        if re.search(pat, lowered):
            return True

    return False


def extract_due_date_from_line(line: str):
    lowered = line.lower()
    # Very simple heuristics
    if "today" in lowered:
        from datetime import datetime, timedelta

        return datetime.now().replace(hour=23, minute=59, second=0, microsecond=0)
    if "tomorrow" in lowered:
        from datetime import datetime, timedelta

        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.replace(hour=17, minute=0, second=0, microsecond=0)

    # Look for 'by ...' or 'before ...'
    m = re.search(r"\b(by|before)\b(.+)", lowered)
    if m:
        candidate = m.group(2).strip()
        # limit to some length
        candidate = " ".join(candidate.split()[:5])
        try:
            return date_parser.parse(candidate, fuzzy=True)
        except Exception:
            return None

    return None


def extract_tasks_from_email(email: Email) -> List[Task]:
    tasks: List[Task] = []
    lines = email.body.splitlines()

    for line in lines:
        if not is_potential_task_line(line):
            continue

        title = line.strip().lstrip("-*•").strip()
        if not title:
            continue

        due = extract_due_date_from_line(line)

        task = Task(
            id=str(uuid.uuid4()),
            email_id=email.id,
            title=title,
            description=line.strip(),
            assignee=None,  # could infer from greeting or sender in future
            due_date=due,
        )
        tasks.append(task)

    return tasks


def extract_tasks_from_emails(emails: List[Email]) -> List[Task]:
    all_tasks: List[Task] = []
    for email in emails:
        tasks = extract_tasks_from_email(email)
        all_tasks.extend(tasks)
    return all_tasks