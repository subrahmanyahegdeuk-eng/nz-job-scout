import streamlit as st
from smolagents import CodeAgent, DuckDuckGoSearchTool, OpenAIServerModel

st.set_page_config(page_title="NZ Job Scout", layout="wide")
st.title("NZ Job Scout — AI Job Search Agent")
st.caption("Searches NZ job boards, summarises roles, and scores them against your background.")

with st.sidebar:
    st.header("Setup")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    st.markdown("---")
    st.subheader("Your background")
    user_background = st.text_area(
        "Paste your background (2-3 sentences)",
        placeholder="e.g. MSc Computer Science graduate from University of Strathclyde. Built RAG applications and LLM agents. Targeting AI consultant roles in New Zealand.",
        height=120
    )
    st.markdown("---")
    st.subheader("Search settings")
    job_role = st.selectbox("Job type to search", [
        "AI consultant New Zealand",
        "AI product manager New Zealand",
        "AI engineer New Zealand",
        "AI implementation specialist New Zealand",
        "machine learning engineer New Zealand",
    ])
    num_jobs = st.slider("Number of jobs to find", min_value=3, max_value=8, value=5)
    st.caption("Get your API key at platform.openai.com")

@st.cache_resource(show_spinner="Setting up agent...")
def build_agent(api_key):
    model = OpenAIServerModel(model_id="gpt-3.5-turbo", api_key=api_key)
    search_tool = DuckDuckGoSearchTool()
    agent = CodeAgent(tools=[search_tool], model=model, max_steps=10)
    return agent

def build_prompt(job_role, num_jobs, user_background):
    return f"""
You are a job search assistant helping someone find AI and tech jobs in New Zealand.

Your task:
1. Search the web for "{job_role}" jobs posted recently
2. Find {num_jobs} real job listings from sites like seek.co.nz, linkedin.com, careers.govt.nz
3. For each job extract:
   - Job title
   - Company name
   - Location (city in NZ)
   - A 2-3 sentence summary of what the role involves
   - Key requirements (bullet points)
   - Whether visa sponsorship is mentioned (yes/no/not mentioned)
   - A match score out of 10 based on this background: "{user_background}"
   - One sentence explaining the match score
4. Present results ranked from highest to lowest match score
5. End with a 2-sentence recommendation on which job to apply to first and why

Format each job clearly with headers. Use real company names and real job details from search results.
"""

if "results" not in st.session_state:
    st.session_state.results = None

if api_key and user_background:
    agent = build_agent(api_key)
    col1, col2 = st.columns([3, 1])
    with col1:
        search_clicked = st.button(f"Search for {num_jobs} {job_role} jobs", type="primary", use_container_width=True)
    with col2:
        if st.button("Clear results", use_container_width=True):
            st.session_state.results = None
            st.rerun()

    if search_clicked:
        with st.spinner("Agent is searching NZ job boards... this takes 30-60 seconds"):
            try:
                prompt = build_prompt(job_role, num_jobs, user_background)
                result = agent.run(prompt)
                st.session_state.results = result
            except Exception as e:
                st.error(f"Search failed: {str(e)}")
                st.info("Try reducing the number of jobs or simplifying your search term.")

    if st.session_state.results:
        st.markdown("---")
        st.subheader("Job Search Results")
        st.markdown(st.session_state.results)
        st.markdown("---")
        st.download_button(
            label="Download results as text file",
            data=st.session_state.results,
            file_name=f"nz_jobs_{job_role.replace(' ', '_')}.txt",
            mime="text/plain"
        )
        st.success("Tip: Copy job titles into seek.co.nz to find the actual listings and apply directly.")

else:
    if not api_key:
        st.info("Enter your OpenAI API key in the sidebar to get started.")
    elif not user_background:
        st.info("Add your background in the sidebar so the agent can score job matches.")

with st.expander("How this agent works"):
    st.markdown("""
**Step 1** — You give it a task: job type, number of results, your background.

**Step 2** — The agent plans: GPT-3.5 decides what to search and how many times.

**Step 3** — The agent searches: DuckDuckGoSearchTool searches the web for free, no API key needed.

**Step 4** — The agent summarises: reads results, scores them against your background, ranks them.

**Step 5** — You get a ranked list: highest match score at the top.

This is a **ReAct agent** — it Reasons then Acts, repeating until the task is complete.
""")
