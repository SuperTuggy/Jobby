import os
import re
import json
import time
from datetime import datetime

import pdfplumber
from weasyprint import HTML
from tavily import TavilyClient
from google import genai
from tkinter import Tk, filedialog, simpledialog, messagebox

# =====================================================
# CONFIG (NO PERSONAL DATA)
# =====================================================

TAVILY_API_KEY = "INSERT YOUR API KEY"
GOOGLE_API_KEY = "INSERT YOUR API KEY"

OUTPUT_ROOT = "resumes"
LOG_FILE = "generation.log"
PROCESSED_JOBS_FILE = "processed_jobs.json"

MAX_JOBS_PER_RUN = 1
SLEEP_BETWEEN_CALLS = 15  # seconds

# =====================================================
# PERSISTENT MEMORY (WASTE PREVENTION)
# =====================================================

def load_processed_jobs():
    if not os.path.exists(PROCESSED_JOBS_FILE):
        return {}
    with open(PROCESSED_JOBS_FILE, "r") as f:
        return json.load(f)

def save_processed_jobs(data):
    with open(PROCESSED_JOBS_FILE, "w") as f:
        json.dump(data, f, indent=2)

processed_jobs = load_processed_jobs()
today = datetime.now().strftime("%Y-%m-%d")

# =====================================================
# CLOSED JOB FILTER
# =====================================================

CLOSED_JOB_PHRASES = [
    "no longer accepting applications",
    "position has been filled",
    "job posting has expired",
    "applications are closed",
    "role is no longer open",
]

def is_job_closed(text: str) -> bool:
    if not text:
        return False
    text = text.lower()
    return any(p in text for p in CLOSED_JOB_PHRASES)

# =====================================================
# CONFIDENCE SCORING
# =====================================================

BAD_URL_PATTERNS = [
    "/hire/",
    "/job-description",
    "/career-advice",
    "/companies/",
    "/salary",
]

GOOD_DOMAINS = [
    "greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "smartrecruiters.com",
    "indeed.com/viewjob",
    "linkedin.com/jobs/view",
]

def compute_confidence(url: str, text: str, title: str) -> int:
    score = 0
    u = url.lower()
    t = (text or "").lower()

    if any(bad in u for bad in BAD_URL_PATTERNS):
        score -= 30
    if any(d in u for d in GOOD_DOMAINS):
        score += 30
    if title.lower() in t:
        score += 20
    if len(t) > 1000:
        score += 10
    elif len(t) < 400:
        score -= 10

    return max(0, min(100, score))

# =====================================================
# HELPERS
# =====================================================

def log_event(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def safe_folder_name(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]", "_", text)

# =====================================================
# FIXED RESUME TEMPLATE (USER-AGNOSTIC)
# =====================================================

def structured_resume_to_pdf(data: dict, output_path: str):
    header = data.get("header", {})
    name = header.get("name", "")
    email = header.get("email", "")
    phone = header.get("phone", "")
    location = header.get("location", "")

    def bullets(items):
        return "".join(f"<li>{i}</li>" for i in items)

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: "Times New Roman", serif;
                margin: 40px;
                font-size: 11pt;
                line-height: 1.35;
            }}
            h1 {{
                text-align: center;
                font-size: 16pt;
                margin-bottom: 4px;
            }}
            .contact {{
                text-align: center;
                font-size: 10pt;
                margin-bottom: 12px;
            }}
            h2 {{
                border-bottom: 1px solid #000;
                font-size: 12pt;
                margin-top: 14px;
            }}
            .row {{
                display: flex;
                justify-content: space-between;
                font-weight: bold;
            }}
            ul {{
                margin-top: 4px;
            }}
        </style>
    </head>
    <body>

    <h1>{name}</h1>
    <div class="contact">
        {email}{(" · " + phone) if phone else ""}{(" · " + location) if location else ""}
    </div>

    <h2>EDUCATION</h2>
    {"".join(
        f"<div class='row'><span>{e['institution']}</span><span>{e['dates']}</span></div>"
        f"<div>{e['degree']} — {e['location']}</div>"
        for e in data.get("education", [])
    )}

    <h2>EXPERIENCE</h2>
    {"".join(
        f"<div class='row'><span>{x['company']} — {x['role']}</span><span>{x['dates']}</span></div>"
        f"<div>{x['location']}</div>"
        f"<ul>{bullets(x['bullets'])}</ul>"
        for x in data.get("experience", [])
    )}

    <h2>PROJECTS</h2>
    {"".join(
        f"<div><b>{p['title']}</b></div><ul>{bullets(p['bullets'])}</ul>"
        for p in data.get("projects", [])
    )}

    <h2>SKILLS</h2>
    <ul>{bullets(data.get("skills", []))}</ul>

    </body>
    </html>
    """

    HTML(string=html).write_pdf(output_path)

# =====================================================
# UI INPUT
# =====================================================

root = Tk()
root.withdraw()

job_titles_input = simpledialog.askstring(
    "Job Targets",
    "Enter job titles (comma-separated)"
)

if not job_titles_input:
    raise SystemExit("No job titles provided.")

job_titles = [j.strip() for j in job_titles_input.split(",") if j.strip()]

# -------- REMOTE vs IN-PERSON (CITY + STATE) --------

job_type = messagebox.askquestion(
    title="Job Type",
    message="Are you looking for REMOTE jobs?\n\nYes = Remote only\nNo = In-person / Hybrid"
)

is_remote = (job_type == "yes")

city = None
state = None

if not is_remote:
    city = simpledialog.askstring("City", "Enter your city (e.g. Boston)")
    state = simpledialog.askstring("State", "Enter your state (e.g. MA)")
    if not city or not state:
        raise SystemExit("City and state are required for in-person jobs.")

location_clause = "remote" if is_remote else f"{city} {state}"

# -------- RESUME FILE --------

resume_path = filedialog.askopenfilename(
    title="Select Resume (PDF)",
    filetypes=[("PDF files", "*.pdf")]
)

if not resume_path:
    raise SystemExit("No resume selected.")

# =====================================================
# READ RESUME
# =====================================================

with pdfplumber.open(resume_path) as pdf:
    resume_text = "\n".join(p.extract_text() or "" for p in pdf.pages)

# =====================================================
# SEARCH JOBS (TAVILY DOES LOCATION FILTERING)
# =====================================================

SITES = [
    "site:boards.greenhouse.io",
    "site:jobs.lever.co",
    "site:jobs.ashbyhq.com",
    "site:smartrecruiters.com",
    "site:indeed.com/viewjob",
    "site:linkedin.com/jobs/view",
]

tavily = TavilyClient(TAVILY_API_KEY)
jobs = []
seen = set()

for title in job_titles:
    query = f"{title} {location_clause} ({' OR '.join(SITES)})"
    res = tavily.search(query=query, search_depth="advanced")

    for r in res.get("results", []):
        url = r.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        jobs.append({
            "url": url,
            "content": r.get("content", ""),
            "target_title": title
        })

# =====================================================
# AI SETUP
# =====================================================

genai_client = genai.Client(api_key=GOOGLE_API_KEY)
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# =====================================================
# PROCESS JOBS
# =====================================================

count = 0

for job in jobs:
    if count >= MAX_JOBS_PER_RUN:
        break

    url = job["url"]
    desc = job["content"]
    title = job["target_title"]

    if url in processed_jobs or is_job_closed(desc):
        continue

    confidence = compute_confidence(url, desc, title)
    if confidence < 50:
        continue

    prompt = f"""
Return VALID JSON ONLY.

Schema:
{{
  "header": {{
    "name": "",
    "email": "",
    "phone": "",
    "location": ""
  }},
  "education": [],
  "experience": [],
  "projects": [],
  "skills": []
}}

Extract header info from the resume if present.
Rewrite content to better match the job.
Do NOT invent facts.

RESUME:
{resume_text}

JOB DESCRIPTION:
{desc}
"""

    ai = genai_client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    try:
        data = json.loads(ai.text)
    except json.JSONDecodeError:
        log_event(f"FAILED_JSON | {url}")
        continue

    folder = os.path.join(OUTPUT_ROOT, safe_folder_name(url))
    os.makedirs(folder, exist_ok=True)
    output_pdf = os.path.join(folder, "Resume.pdf")

    structured_resume_to_pdf(data, output_pdf)

    processed_jobs[url] = {
        "job_title": title,
        "job_type": "remote" if is_remote else "in_person",
        "location": None if is_remote else f"{city}, {state}",
        "confidence": confidence,
        "resume_path": output_pdf,
        "date": today
    }

    save_processed_jobs(processed_jobs)
    log_event(f"GENERATED | {url}")
    count += 1
    time.sleep(SLEEP_BETWEEN_CALLS)

print("Done.")
