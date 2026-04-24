import streamlit as st
from smolagents import CodeAgent, OpenAIServerModel
from smolagents import tool
import requests
from bs4 import BeautifulSoup
import urllib.parse

# ============================================================
# CUSTOM SEARCH TOOL
# We build our own search tool instead of DuckDuckGoSearchTool
# because DuckDuckGo blocks cloud servers
# We use requests to fetch real job listings directly
# ============================================================

@tool
def search_nz_jobs(query: str) -> str:
    """
    Searches for jobs in New Zealand using web search.
    Args:
        query: the job search query string
    Returns:
        search results as text
    """
    try:
        # Use DuckDuckGo HTML version which is more reliable on servers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        encoded = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        # Extract search result snippets
        for result in soup.find_all("div", class_="result__body")[:8]:
            title = result.find("a", class_="result__a")
            snippet = result.find("a", class_="result__snippet")
            if title and snippet:
                results.append(f"Title: {title.get_text()}\nSnippet: {snippet.get_text()}\n")

        if results:
            return "\n---\n".join(results)
        else:
            return "No results found. Try a different search query."

    except Exception as e:
        return f"Search error: {str(e)}"


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(page_title="NZ Job Scout", layout="wide")
st.title("NZ Job Scout — AI Job Search Agent")
st.caption("Searches NZ job boards, summarises roles, and scores them against your background.")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("Setup")

    # Try to get API key from Streamlit secrets first
    # Falls back to text input if not set
    api_key = st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, "secrets") else ""
    if not api_key:
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    else:
        st.success("API key loaded from secrets")

    st.markdown("---")
    st.subheader("Your background")

    user_background = st.text_area(
        "Paste your background (2-3 sentences)",
        placeholder="e.g. MSc Computer Science from University of Strathclyde. "
                    "Built RAG apps and LLM agents with LangChain and HuggingFace. "
                    "Targeting AI consultant roles in New Zealand.",
        height=120
    )

    st.markdown("---")
    st.subheader("Search settings")

    job_role = st.selectbox(
        "Job type to search",
        [
            "AI consultant New Zealand",
            "AI product manager New Zealand",
            "AI engineer New Zealand",
            "AI implementation specialist New Zealand",
            "machine learning engineer New Zealand",
            "digital transformation consultant New Zealand",
        ]
    )

    num_jobs = st.slider("Number of jobs to find", min_value=3, max_value=6, value=4)
    st.caption("Get your API key at platform.openai.com")


# ============================================================
# BUILD THE AGENT
# ============================================================

@st.cache_resource(show_spinner="Setting up agent...")
def build_agent(api_key):
    model = OpenAIServerModel(
        model_id="gpt-3.5-turbo",
        api_key=api_key
    )
    # Use our custom search tool instead of DuckDuckGoSearchTool
    agent = CodeAgent(
        tools=[search_nz_jobs],
        model=model,
        max_steps=8
    )
    return agent


# ============================================================
# PROMPT
# ============================================================

def build_prompt(job_role, num_jobs, user_background):
    return f"""
You are a job search assistant helping someone find AI and tech jobs in New Zealand.

Use the search_nz_jobs tool to search for "{job_role} jobs" and "{job_role} seek.co.nz".

For each of the {num_jobs} jobs you find:
- Job title
- Company name  
- Location in New Zealand
- 2-3 sentence summary of the role
- Key requirements (3-4 bullet points)
- Visa sponsorship mentioned? (yes / no / not mentioned)
- Match score out of 10 based on this background: "{user_background}"
- One sentence explaining the score

Rank results from highest to lowest match score.
End with: which job to apply to first and why (2 sentences).

If search results are limited, use what you find and note that more roles may be on seek.co.nz directly.
"""


# ============================================================
# SESSION STATE
# ============================================================

if "results" not in st.session_state:
    st.session_state.results = None


# ============================================================
# MAIN UI
# ============================================================

if api_key and user_background:

    agent = build_agent(api_key)

    col1, col2 = st.columns([3, 1])
    with col1:
        search_clicked = st.button(
            f"Search for {num_jobs} {job_role} jobs",
            type="primary",
            use_container_width=True
        )
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.results = None
            st.rerun()

    if search_clicked:
        with st.spinner("Agent is searching... this takes 30-60 seconds"):
            try:
                prompt = build_prompt(job_role, num_jobs, user_background)
                result = agent.run(prompt)
                st.session_state.results = str(result)
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Try reducing the number of jobs or try again in a moment.")

    if st.session_state.results:
        st.markdown("---")
        st.subheader("Results")
        st.markdown(st.session_state.results)
        st.markdown("---")
        st.download_button(
            label="Download results",
            data=st.session_state.results,
            file_name="nz_jobs.txt",
            mime="text/plain"
        )
        st.success(
            "Next step: search these job titles directly on seek.co.nz to find live listings and apply."
        )

else:
    if not api_key:
        st.info("Enter your OpenAI API key in the sidebar to get started.")
    elif not user_background:
        st.info("Add your background in the sidebar so the agent can score job matches.")

with st.expander("How this agent works"):
    st.markdown("""
**What happens when you click Search:**

1. The agent receives your task — job type, how many, your background
2. It calls the search tool to find real NZ job listings on the web
3. It reads the results and extracts job details
4. It scores each job against your background out of 10
5. It ranks them and explains which to apply to first

This is a **ReAct agent** — it Reasons and Acts in a loop until the task is done.
Built with HuggingFace smolagents + OpenAI GPT-3.5.
""")
