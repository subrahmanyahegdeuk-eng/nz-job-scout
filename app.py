import streamlit as st
from smolagents import CodeAgent, OpenAIServerModel, tool
import requests
from bs4 import BeautifulSoup
import urllib.parse

@tool
def search_nz_jobs(query: str) -> str:
    """
    Searches for jobs in New Zealand.
    Args:
        query: the job search query string
    Returns:
        search results as text
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        encoded = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for result in soup.find_all("div", class_="result__body")[:8]:
            title = result.find("a", class_="result__a")
            snippet = result.find("a", class_="result__snippet")
            if title and snippet:
                results.append(f"Title: {title.get_text()}\nSnippet: {snippet.get_text()}")
        return "\n---\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"

st.set_page_config(page_title="NZ Job Scout", layout="wide")
st.title("NZ Job Scout — AI Job Search Agent")
st.caption("Searches NZ job boards, summarises roles, and scores them against your background.")

with st.sidebar:
    st.header("Setup")
    api_key = ""
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", "")
    except:
        pass
    if not api_key:
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    else:
        st.success("API key loaded")
    st.markdown("---")
    st.subheader("Your background")
    user_background = st.text_area("Paste your background (2-3 sentences)",
        placeholder="e.g. MSc Computer Science from University of Strathclyde. Built RAG apps and LLM agents. Targeting AI consultant roles in New Zealand.",
        height=120)
    st.markdown("---")
    st.subheader("Search settings")
    job_role = st.selectbox("Job type to search", [
        "AI consultant New Zealand",
        "AI product manager New Zealand",
        "AI engineer New Zealand",
        "AI implementation specialist New Zealand",
        "machine learning engineer New Zealand",
        "digital transformation consultant New Zealand",
    ])
    num_jobs = st.slider("Number of jobs to find", min_value=3, max_value=6, value=3)

@st.cache_resource(show_spinner="Setting up agent...")
def build_agent(api_key):
    model = OpenAIServerModel(model_id="gpt-3.5-turbo", api_key=api_key)
    agent = CodeAgent(tools=[search_nz_jobs], model=model, max_steps=8)
    return agent

def build_prompt(job_role, num_jobs, user_background):
    return f"""
You are a job search assistant finding AI jobs in New Zealand.
Use the search_nz_jobs tool to search for "{job_role} jobs seek.co.nz".
Search at least twice with different queries to find more results.
For each of the {num_jobs} jobs provide:
- Job title
- Company name
- Location in NZ
- 2-3 sentence summary
- Key requirements (3 bullet points)
- Visa sponsorship mentioned? (yes/no/not mentioned)
- Match score out of 10 for this background: "{user_background}"
- One sentence explaining the score
Rank from highest to lowest score.
End with which job to apply to first and why.
"""

if "results" not in st.session_state:
    st.session_state.results = None

if api_key and user_background:
    agent = build_agent(api_key)
    col1, col2 = st.columns([3, 1])
    with col1:
        search_clicked = st.button(f"Search for {num_jobs} {job_role} jobs", type="primary", use_container_width=True)
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.results = None
            st.rerun()
    if search_clicked:
        with st.spinner("Agent searching NZ job boards... takes 30-60 seconds"):
            try:
                result = agent.run(build_prompt(job_role, num_jobs, user_background))
                st.session_state.results = str(result)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    if st.session_state.results:
        st.markdown("---")
        st.subheader("Results")
        st.markdown(st.session_state.results)
        st.download_button("Download results", data=st.session_state.results, file_name="nz_jobs.txt", mime="text/plain")
        st.success("Search these job titles on seek.co.nz to find live listings and apply.")
else:
    if not api_key:
        st.info("Enter your OpenAI API key in the sidebar to get started.")
    elif not user_background:
        st.info("Add your background in the sidebar so the agent can score job matches.")
