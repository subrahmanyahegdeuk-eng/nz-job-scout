import streamlit as st
from smolagents import CodeAgent, OpenAIServerModel, tool
import requests
from bs4 import BeautifulSoup
import urllib.parse

@tool
def search_jobs(query: str) -> str:
    """
    Searches for jobs using web search.
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

st.set_page_config(page_title="Global AI Job Scout", layout="wide")
st.title("Global AI Job Scout")
st.caption("Searches AI job boards worldwide, summarises roles, and scores them against your background.")

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
    user_background = st.text_area(
        "Paste your background (2-3 sentences)",
        placeholder="e.g. MSc Computer Science from University of Strathclyde. Built RAG apps and LLM agents. Targeting AI consultant roles internationally.",
        height=120
    )

    st.markdown("---")
    st.subheader("Search settings")

    # REGION SELECTOR — the main new feature
    region = st.selectbox("Target region", [
        "New Zealand",
        "United Kingdom",
        "United Arab Emirates",
        "Saudi Arabia",
        "Qatar",
        "Germany",
        "Netherlands",
        "France",
        "India",
        "Singapore",
        "Australia",
        "Canada",
    ])

    # Job boards change depending on region
    job_boards = {
        "New Zealand": "seek.co.nz, linkedin.com, careers.govt.nz",
        "United Kingdom": "linkedin.com, reed.co.uk, totaljobs.com, cv-library.co.uk",
        "United Arab Emirates": "linkedin.com, bayt.com, naukrigulf.com, dubizzle.com",
        "Saudi Arabia": "linkedin.com, bayt.com, naukrigulf.com, jobs.sa",
        "Qatar": "linkedin.com, bayt.com, naukrigulf.com, qatarliving.com/jobs",
        "Germany": "linkedin.com, xing.com, stepstone.de, indeed.de",
        "Netherlands": "linkedin.com, indeed.nl, nationalevacaturebank.nl, monsterboard.nl",
        "France": "linkedin.com, indeed.fr, pole-emploi.fr, apec.fr",
        "India": "linkedin.com, naukri.com, indeed.co.in, shine.com",
        "Singapore": "linkedin.com, jobsdb.com, mycareersfuture.gov.sg, jobstreet.com",
        "Australia": "seek.com.au, linkedin.com, indeed.com.au, jora.com",
        "Canada": "linkedin.com, indeed.ca, jobbank.gc.ca, workopolis.com",
    }

    # Visa sponsorship context per region
    visa_context = {
        "New Zealand": "Check for Accredited Employer Work Visa (AEWV) sponsorship",
        "United Kingdom": "Check for Skilled Worker visa sponsorship",
        "United Arab Emirates": "Most roles include visa and relocation package — note this",
        "Saudi Arabia": "Most roles include visa, accommodation, and relocation — note this",
        "Qatar": "Most roles include visa and relocation package — note this",
        "Germany": "Check for EU Blue Card or work visa sponsorship",
        "Netherlands": "Check for highly skilled migrant permit (kennismigrant) sponsorship",
        "France": "Check for work visa or EU Blue Card sponsorship",
        "India": "Visa not required for Indian nationals — note salary in INR",
        "Singapore": "Check for Employment Pass (EP) sponsorship",
        "Australia": "Check for Employer Nomination Scheme (ENS) or TSS visa sponsorship",
        "Canada": "Check for LMIA-backed work permit or Express Entry sponsorship",
    }

    job_role = st.selectbox("Job type to search", [
        "AI consultant",
        "AI implementation specialist",
        "AI solutions architect",
        "machine learning engineer",
        "AI engineer",
        "digital transformation consultant",
        "LLM engineer",
        "data scientist",
    ])

    num_jobs = st.slider("Number of jobs to find", min_value=3, max_value=6, value=3)
    st.caption("Get your API key at platform.openai.com")

@st.cache_resource(show_spinner="Setting up agent...")
def build_agent(api_key):
    model = OpenAIServerModel(model_id="gpt-3.5-turbo", api_key=api_key)
    agent = CodeAgent(tools=[search_jobs], model=model, max_steps=8)
    return agent

def build_prompt(job_role, region, num_jobs, user_background, boards, visa_note):
    return f"""
You are a job search assistant finding AI jobs in {region}.

Use the search_jobs tool to search for "{job_role} jobs {region}" and "{job_role} {region} {boards.split(',')[0].strip()}".
Search at least twice with different queries to find more results.

For each of the {num_jobs} jobs provide:
- Job title
- Company name
- Location (city in {region})
- Salary if mentioned
- 2-3 sentence summary of what the role involves
- Key requirements (3 bullet points)
- Visa/relocation: {visa_note}
- Match score out of 10 based on this background: "{user_background}"
- One sentence explaining the score

Rank results from highest to lowest match score.
End with which job to apply to first and why (2 sentences).
Note: if salary is in local currency, mention the currency clearly.
"""

if "results" not in st.session_state:
    st.session_state.results = None
if "last_region" not in st.session_state:
    st.session_state.last_region = None

if api_key and user_background:
    agent = build_agent(api_key)

    # Show which region and boards are being searched
    st.info(f"Searching for **{job_role}** roles in **{region}**\nJob boards: {job_boards[region]}")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_clicked = st.button(
            f"Search for {num_jobs} {job_role} jobs in {region}",
            type="primary",
            use_container_width=True
        )
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.results = None
            st.rerun()

    if search_clicked:
        with st.spinner(f"Agent searching {region} job boards... takes 30-60 seconds"):
            try:
                prompt = build_prompt(
                    job_role, region, num_jobs, user_background,
                    job_boards[region], visa_context[region]
                )
                result = agent.run(prompt)
                st.session_state.results = str(result)
                st.session_state.last_region = region
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Try reducing the number of jobs or try again in a moment.")

    if st.session_state.results:
        st.markdown("---")
        st.subheader(f"Results — {st.session_state.last_region}")
        st.markdown(st.session_state.results)
        st.markdown("---")
        st.download_button(
            "Download results",
            data=st.session_state.results,
            file_name=f"jobs_{region.replace(' ', '_')}.txt",
            mime="text/plain"
        )
        st.success(f"Next step: search these job titles directly on {job_boards[region].split(',')[0]} to find live listings.")

else:
    if not api_key:
        st.info("Enter your OpenAI API key in the sidebar to get started.")
    elif not user_background:
        st.info("Add your background in the sidebar so the agent can score job matches.")

with st.expander("Supported regions and job boards"):
    for r, boards in job_boards.items():
        st.write(f"**{r}:** {boards}")
