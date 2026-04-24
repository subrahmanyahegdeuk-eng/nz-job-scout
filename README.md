 Global AI Job Scout — Autonomous Multi-Region Job Search Agent

An autonomous AI agent that searches job boards across 12 countries, scores each role against your background, detects visa and relocation packages, and returns a ranked digest — all in one click.

Live demo
[Add your Streamlit URL here]

Supported regions
| Region | Job Boards Searched |
|--------|-------------------|
| New Zealand | seek.co.nz, linkedin.com, careers.govt.nz |
| United Kingdom | linkedin.com, reed.co.uk, totaljobs.com |
| UAE | linkedin.com, bayt.com, naukrigulf.com |
| Saudi Arabia | linkedin.com, bayt.com, naukrigulf.com |
| Qatar | linkedin.com, bayt.com, naukrigulf.com |
| Germany | linkedin.com, stepstone.de, xing.com |
| Netherlands | linkedin.com, indeed.nl, monsterboard.nl |
| France | linkedin.com, indeed.fr, apec.fr |
| India | linkedin.com, naukri.com, shine.com |
| Singapore | linkedin.com, jobsdb.com, mycareersfuture.gov.sg |
| Australia | seek.com.au, linkedin.com, indeed.com.au |
| Canada | linkedin.com, indeed.ca, jobbank.gc.ca |

 What it does
1. You select a target country and job type
2. You paste a 2-3 sentence summary of your background
3. The AI agent autonomously searches region-specific job boards
4. For each job it extracts: title, company, location, salary, summary, requirements
5. It scores each job against your background out of 10 and explains why
6. It detects visa sponsorship or relocation packages
7. Results are ranked highest to lowest match score
8. Download results as a text file for your records

How it works (technical)
```
User input → smolagents CodeAgent → custom web search tool
→ DuckDuckGo HTML search → BeautifulSoup parsing
→ GPT-3.5 summarisation + scoring → ranked Streamlit output
```

This is a **ReAct agent** (Reason + Act loop):
- The agent receives your task
- It plans which searches to run
- It calls the search tool multiple times
- It reads and synthesises results
- It scores and ranks against your background
- It returns a structured final report

Tech stack
- Agent framework:** HuggingFace smolagents
- LLM:** OpenAI GPT-3.5-turbo
- Search:** Custom web search tool (requests + BeautifulSoup)
- UI: Streamlit
- Language: Python

Run locally

Prerequisites
- Python 3.9+
- OpenAI API key (get one at platform.openai.com — add $5 credit)

 Setup
bash
git clone https://github.com/subrahmanyahegdeuk-eng/nz-job-scout.git
cd nz-job-scout
pip install -r requirements.txt
streamlit run app.py
```

### Usage
1. Enter your OpenAI API key in the sidebar
2. Paste your background (2-3 sentences about your skills and target roles)
3. Select your target region
4. Choose a job type
5. Click Search — results appear in 30-60 seconds

## Requirements
```
streamlit
smolagents
openai
requests
beautifulsoup4
```

## Project background
Built as part of an AI engineering portfolio to demonstrate:
- Autonomous AI agent design with HuggingFace smolagents
- Prompt engineering for structured output
- Multi-region product thinking
- End-to-end deployment on Streamlit Cloud

**Author:** Subrahmanya Anant Hegde
MSc Computer Science, University of Strathclyde
github.com/subrahmanyahegdeuk-eng
