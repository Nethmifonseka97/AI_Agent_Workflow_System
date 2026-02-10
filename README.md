
# AI Agent Workflow System (Fully Local)

A fully local AI-powered workflow automation system that reads emails, extracts tasks, prioritizes them, and generates a daily work schedule—**without any API keys, internet, or heavy AI frameworks**.

This project demonstrates practical AI automation using:
- Semantic task extraction
- Heuristic priority scoring
- A lightweight scheduler
- Vector search using FAISS + FastEmbed
- A Streamlit dashboard

Perfect for showcasing **AI engineering, NLP, automation pipelines, and workflow logic** in your GitHub portfolio.

---

## Features

### Email Processing
- Load and parse plain-text email files
- Extract headers (Subject, From, Date)
- Analyze body content for task-relevant lines

### AI Task Extraction
Uses cue-based semantic analysis to identify task sentences:
- “Please…”
- “Can you…”
- “We need to…”
- Bullet points
- Action words & heuristics

Automatically extracts:
- Task title
- Description  
- Due date (if mentioned)
- Email source link

# Priority Engine
Each task receives a priority score (1–5) based on:
- Urgency cues (e.g., "ASAP", "urgent")
- Estimated due date proximity
- Email importance patterns  

# Smart Scheduler
Creates a daily plan based on:
- Priority
- Due dates
- Task duration estimates
- Workday boundaries (default 9am–5pm)

# Semantic Search
Search extracted tasks by meaning, not keywords.  
Uses:
- **FastEmbed** for dense embeddings  
- **FAISS** for fast vector similarity

# Streamlit UI
Four interactive tabs:
- **Inbox**
- **Extracted Tasks**
- **Daily Schedule**
- **Semantic Task Search**

---

# Tech Stack

| Component | Technology |
|----------|-------------|
| UI | Streamlit |
| Embeddings | FastEmbed |
| Vector Search | FAISS |
| Date Parsing | python-dateutil |
| Data Models | Pydantic |
| Environment | Python venv (recommended) |

---

# Project Structure

```
ai_agent_workflow/
│
├── app.py                      # Streamlit dashboard
│
├── agent/
│   ├── models.py               # Email, Task, Schedule models
│   ├── extractor.py            # Task extraction logic
│   ├── priority.py             # Priority scoring engine
│   ├── scheduler.py            # Daily scheduling logic
│   └── __init__.py
│
├── emails/
│   ├── email1.txt
│   ├── email2.txt
│   └── email3.txt
│
└── data/
    └── (optional persistence)
```

---

# Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/ai_agent_workflow.git
cd ai_agent_workflow
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install "numpy<2.0.0" streamlit faiss-cpu fastembed python-dateutil pydantic
```

---

# Running the App

```bash
python -m streamlit run app.py
```

Then open the URL shown in the terminal (usually http://localhost:8501).

---

# Adding More Emails

Add plain `.txt` files to the `emails/` folder with patterns like:

```
Subject: ...
From: ...
Date: ...

Body text here...
Tasks might appear as:
- Bullet points
- "Please do X"
- "We need to..."
```

The system will automatically extract tasks during the next run.



# License
MIT License

---

# Author
**Nethmi Fonseka**  
AI / Automation / Workflow Developer  
GitHub: https://github.com/Nethmifonseka97

---

Thank you for checking out this project!  
If you'd like enhancements or deployment instructions (Streamlit Cloud, Docker, etc.), feel free to contribute or open an issue.
