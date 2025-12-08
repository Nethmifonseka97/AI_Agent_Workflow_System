import streamlit as st
from datetime import datetime, date
from typing import List, Dict

import faiss
import numpy as np
from fastembed import TextEmbedding

from agent import (
    load_emails_from_folder,
    extract_tasks_from_emails,
    prioritize_tasks,
    schedule_tasks_for_day,
    Email,
    Task,
)

# --- Embedding model for semantic task search ---
embedder = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")


@st.cache_data(show_spinner=False)
def load_emails() -> List[Email]:
    return load_emails_from_folder("emails")


@st.cache_data(show_spinner=False)
def run_agent_pipeline() -> tuple[List[Email], List[Task]]:
    emails = load_emails()
    tasks = extract_tasks_from_emails(emails)
    tasks = prioritize_tasks(tasks)
    return emails, tasks


def build_task_index(tasks: List[Task]):
    """Build FAISS index over task titles+descriptions."""
    if not tasks:
        return None, None

    texts = [f"{t.title}. {t.description}" for t in tasks]
    vectors = list(embedder.embed(texts))
    vectors = np.array(vectors, dtype="float32")

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    return index, vectors


def semantic_task_search(query: str, tasks: List[Task], index, top_k: int = 5):
    if not tasks or index is None:
        return []

    q_vec = list(embedder.embed([query]))
    q_vec = np.array(q_vec, dtype="float32")

    distances, indices = index.search(q_vec, min(top_k, len(tasks)))
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        results.append((dist, tasks[idx]))
    return results


def main():
    st.set_page_config(
        page_title="AI Agent Workflow System",
        layout="wide",
        page_icon="🤖",
    )

    st.title("🤖 AI Agent Workflow System")
    st.write(
        "Local AI that reads emails → extracts tasks → prioritizes them → creates a daily plan."
    )

    with st.sidebar:
        st.header("⚙️ Controls")
        if st.button("Run Agent Pipeline"):
            st.session_state["run_agent"] = True

        schedule_date = st.date_input("Schedule for date", value=date.today())
        st.session_state["schedule_date"] = schedule_date

    # Run or load pipeline
    if "run_agent" not in st.session_state:
        st.info("Click **Run Agent Pipeline** in the sidebar to start.")
        return

    with st.spinner("Loading emails and running agent..."):
        emails, tasks = run_agent_pipeline()

    st.success(f"Loaded {len(emails)} emails and extracted {len(tasks)} tasks.")

    # Build semantic search index
    index, _ = build_task_index(tasks)

    # Create tabs
    tab_inbox, tab_tasks, tab_schedule, tab_search = st.tabs(
        ["📥 Inbox", "✅ Tasks", "🗓 Schedule", "🔍 Search Tasks"]
    )

    # --- Inbox tab ---
    with tab_inbox:
        st.subheader("Inbox")
        for email in emails:
            with st.expander(f"{email.subject} — {email.sender}"):
                if email.received_at:
                    st.caption(email.received_at.strftime("%Y-%m-%d %H:%M"))
                st.text(email.body)

    # --- Tasks tab ---
    with tab_tasks:
        st.subheader("Extracted Tasks")
        if not tasks:
            st.write("No tasks were extracted.")
        else:
            for task in tasks:
                with st.expander(f"[P{task.priority}] {task.title}"):
                    st.write(f"**From email ID:** {task.email_id}")
                    st.write(f"**Description:** {task.description}")
                    if task.due_date:
                        st.write(
                            f"**Due date:** {task.due_date.strftime('%Y-%m-%d %H:%M')}"
                        )
                    st.write(f"**Estimated minutes:** {task.estimated_minutes}")
                    st.write(f"**Priority reason:** {task.priority_reason}")

    # --- Schedule tab ---
    with tab_schedule:
        st.subheader("Daily Schedule")
        day = datetime.combine(st.session_state["schedule_date"], datetime.min.time())

        emails_by_id: Dict[str, Email] = {e.id: e for e in emails}
        scheduled = schedule_tasks_for_day(tasks, emails_by_id, day)

        if not scheduled:
            st.write("No tasks could be scheduled for this day.")
        else:
            for s in scheduled:
                st.markdown(
                    f"**{s.start.strftime('%H:%M')}–{s.end.strftime('%H:%M')}** "
                    f"[P{s.priority}] {s.title}  \n"
                    f"<span style='font-size: 0.9em; color: #666;'>Source: {s.source_email_subject}</span>",
                    unsafe_allow_html=True,
                )

    # --- Search tab ---
    with tab_search:
        st.subheader("Semantic Task Search")
        query = st.text_input("Search tasks by meaning (e.g. 'client presentation', 'prepare report')")
        if query and index:
            results = semantic_task_search(query, tasks, index, top_k=5)
            if not results:
                st.write("No matching tasks found.")
            else:
                for dist, task in results:
                    st.markdown(
                        f"**[P{task.priority}] {task.title}**  \n"
                        f"<span style='font-size: 0.9em; color: #666;'>Distance: {dist:.4f}</span>",
                        unsafe_allow_html=True,
                    )
                    st.write(task.description)
                    st.markdown("---")
        elif query:
            st.write("No tasks available to search yet.")


if __name__ == "__main__":
    main()