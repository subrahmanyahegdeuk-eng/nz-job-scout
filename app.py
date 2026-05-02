import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from groq import Groq

st.set_page_config(page_title="Global AI Job Scout", page_icon="🌍", layout="wide")

st.markdown("""
<style>
    .stApp { background: #f8f9fe; }
    section[data-testid="stSidebar"] { background: #1a1a2e !important; }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] caption { color: #e2e8f0 !important; }
    section[data-testid="stSidebar"] input {
        background: #2d2d4e !important; color: white !important;
        border: 1px solid #4a4a7a !important; border-radius: 8px !important;
    }
    .sb-head {
        color: #a78bfa; font-size: 12px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1.5px;
        margin: 20px 0 10px 0; padding-bottom: 6px;
        border-bottom: 1px solid #2d2d4e;
    }
    .scout-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 28px 32px; border-radius: 16px; margin-bottom: 28px;
    }
    .scout-title { font-size: 30px; font-weight: 700; color: white; margin: 0 0 6px 0; }
    .scout-sub { font-size: 15px; color: rgba(255,255,255,0.85); margin: 0 0 14px 0; }
    .region-badge {
        display: inline-block; background: rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.35); border-radius: 20px;
        padding: 4px 14px; font-size: 12px; color: white; margin: 3px;
    }
    .stat-card {
        background: white; border-radius: 14px; padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #eeeeee; text-align: center; margin-bottom: 8px;
    }
    .stat-number { font-size: 36px; font-weight: 700; color: #667eea; margin: 0; }
    .stat-label { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin: 4px 0 0 0; }
    .feature-card {
        background: white; border-radius: 14px; padding: 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #eeeeee; margin-bottom: 8px;
    }
    .results-card {
        background: white; border-radius: 14px; padding: 20px 24px;
        margin-bottom: 20px; border: 1px solid #eeeeee;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .job-card {
        background: white; border-radius: 12px; padding: 18px 20px;
        margin-bottom: 14px; border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

REGIONS = {
    "🇳🇿 New Zealand": {"boards": "seek.co.nz, linkedin.com", "visa": "Check for AEWV sponsorship"},
    "🇬🇧 United Kingdom": {"boards": "linkedin.com, reed.co.uk, totaljobs.com", "visa": "Check for Skilled Worker visa"},
    "🇦🇪 UAE": {"boards": "linkedin.com, bayt.com, naukrigulf.com", "visa": "Most roles include visa package"},
    "🇸🇦 Saudi Arabia": {"boards": "linkedin.com, bayt.com", "visa": "Most roles include visa and relocation"},
    "🇶🇦 Qatar": {"boards": "linkedin.com, bayt.com", "visa": "Most roles include visa package"},
    "🇩🇪 Germany": {"boards": "linkedin.com, stepstone.de, xing.com", "visa": "Check for EU Blue Card"},
    "🇳🇱 Netherlands": {"boards": "linkedin.com, indeed.nl", "visa": "Check for kennismigrant permit"},
    "🇫🇷 France": {"boards": "linkedin.com, indeed.fr", "visa": "Check for EU Blue Card"},
    "🇮🇳 India": {"boards": "linkedin.com, naukri.com, shine.com", "visa": "No visa needed for Indian nationals"},
    "🇸🇬 Singapore": {"boards": "linkedin.com, jobsdb.com", "visa": "Check for Employment Pass"},
    "🇦🇺 Australia": {"boards": "seek.com.au, linkedin.com", "visa": "Check for TSS visa sponsorship"},
    "🇨🇦 Canada": {"boards": "linkedin.com, indeed.ca", "visa": "Check for LMIA work permit"},
}

JOB_ROLES = [
    "AI consultant", "AI implementation specialist",
    "AI solutions architect", "machine learning engineer",
    "AI engineer", "digital transformation consultant",
    "LLM engineer", "automation specialist",
    "data analyst", "data analyst AI",
    "healthcare data analyst", "business intelligence analyst",
    "data engineer",
]

region_badges = "".join([
    f'<span class="region-badge">{r}</span>'
    for r in list(REGIONS.keys())[:6]
])
st.markdown(f"""
<div class="scout-header">
    <p class="scout-title">🌍 Global AI Job Scout</p>
    <p class="scout-sub">Searches job boards across 12 countries and scores matches against your background — powered by Groq LLaMA, completely free</p>
    <div>{region_badges} <span class="region-badge">+6 more</span></div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<p class="sb-head">🔑 API Key</p>', unsafe_allow_html=True)
    api_key = st.text_input("Groq API Key", type="password",
        placeholder="gsk_...", label_visibility="collapsed")
    st.caption("Free key at console.groq.com")

    st.markdown('<p class="sb-head">👤 Your Background</p>', unsafe_allow_html=True)
    user_background = st.text_area("Background",
        placeholder="e.g. MSc Computer Science from University of Strathclyde. Built RAG apps and LLM agents. Targeting AI consultant or data analyst roles.",
        height=130, label_visibility="collapsed")

    st.markdown('<p class="sb-head">🔍 Search Settings</p>', unsafe_allow_html=True)
    selected_region = st.selectbox("Region", list(REGIONS.keys()),
        label_visibility="collapsed")
    job_role = st.selectbox("Job Type", JOB_ROLES,
        label_visibility="collapsed")
    num_jobs = st.slider("Results to find", 3, 6, 3)

    st.markdown('<p class="sb-head">📊 Coverage</p>', unsafe_allow_html=True)
    st.caption(f"🌍 {len(REGIONS)} countries")
    st.caption(f"💼 {len(JOB_ROLES)} job types")
    st.caption("🤖 Powered by Groq LLaMA — free")

def search_web(query):
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
                results.append(
                    f"Title: {title.get_text()}\n"
                    f"Snippet: {snippet.get_text()}"
                )
        return "\n---\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"

def run_job_search(api_key, job_role, region_name,
                   num_jobs, user_background, region_config):
    client = Groq(api_key=api_key)
    boards = region_config['boards'].split(',')[0].strip()

    query1 = f"{job_role} jobs {region_name} 2025"
    query2 = f"{job_role} {boards} hiring now"

    results1 = search_web(query1)
    results2 = search_web(query2)
    combined = f"Search 1 results:\n{results1}\n\nSearch 2 results:\n{results2}"

    prompt = f"""
You are a job search assistant. Based on the search results below,
find and summarise {num_jobs} real {job_role} job listings in {region_name}.

For each job provide:
- Job title and company name
- Location in {region_name}
- Salary if mentioned
- 2-3 sentence summary of the role
- Key requirements (3 bullet points)
- Visa/sponsorship: {region_config['visa']}
- Match score out of 10 for this background: "{user_background}"
- One sentence explaining the score

Rank from highest to lowest match score.
End with: which job to apply to first and why (2 sentences).

Search results:
{combined}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    return response.choices[0].message.content

if "results" not in st.session_state:
    st.session_state.results = None
if "search_meta" not in st.session_state:
    st.session_state.search_meta = None

if api_key and user_background:
    region_config = REGIONS[selected_region]

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"""
<div class="stat-card">
    <p class="stat-number">{num_jobs}</p>
    <p class="stat-label">Jobs to find</p>
</div>""", unsafe_allow_html=True)
    col2.markdown(f"""
<div class="stat-card">
    <p class="stat-number">{len(REGIONS)}</p>
    <p class="stat-label">Countries</p>
</div>""", unsafe_allow_html=True)
    col3.markdown("""
<div class="stat-card">
    <p class="stat-number">Free</p>
    <p class="stat-label">Groq powered</p>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_btn, col_clear = st.columns([4, 1])
    with col_btn:
        search_clicked = st.button(
            f"🔍 Search {num_jobs} {job_role} jobs in {selected_region}",
            type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.results = None
            st.rerun()

    if search_clicked:
        with st.spinner(f"🤖 Searching {selected_region} job boards... 15-30 seconds"):
            try:
                result = run_job_search(
                    api_key, job_role, selected_region,
                    num_jobs, user_background, region_config)
                st.session_state.results = result
                st.session_state.search_meta = {
                    "region": selected_region, "role": job_role}
            except Exception as e:
                st.error(f"Search failed: {str(e)}")
                st.info("Check your Groq API key and try again.")

    if st.session_state.results:
        meta = st.session_state.search_meta
        st.markdown(f"""
<div class="results-card">
    <div style="font-size:13px;color:#888;margin-bottom:4px">
        Results for</div>
    <div style="font-size:18px;font-weight:600;color:#1a1a2e">
        {meta['role']} · {meta['region']}</div>
</div>""", unsafe_allow_html=True)

        st.markdown(st.session_state.results)
        st.markdown("<br>", unsafe_allow_html=True)

        boards = region_config['boards'].split(',')[0].strip()
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "💾 Download results",
                data=st.session_state.results,
                file_name=f"jobs_{selected_region.split()[-1].lower()}.txt",
                mime="text/plain",
                use_container_width=True)
        with col2:
            st.success(f"Search on {boards} to apply directly")

else:
    col1, col2, col3, col4 = st.columns(4)
    features = [
        ("🤖", "AI powered", "Groq LLaMA analyses search results and scores every job"),
        ("🎯", "Match scoring", "Every job scored 1-10 against your specific background"),
        ("✈️", "Visa detection", "Automatically flags visa and relocation packages"),
        ("📥", "Download", "Export your ranked job list as a text file"),
    ]
    for col, (icon, title, desc) in zip(
            [col1, col2, col3, col4], features):
        col.markdown(f"""
<div class="feature-card">
    <div style="font-size:28px;margin-bottom:10px">{icon}</div>
    <strong style="color:#1a1a2e;font-size:14px">{title}</strong>
    <p style="color:#888;font-size:12px;margin:6px 0 0;line-height:1.5">
        {desc}</p>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if not api_key:
        st.info("🔑 Enter your Groq API key in the sidebar — free at console.groq.com")
    elif not user_background:
        st.info("👤 Add your background in the sidebar so the AI can score job matches")
