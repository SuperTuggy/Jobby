# Jobby

A local tool for generating tailored resumes from job postings and tracking applications.

---

## Requirements

- Python 3.10+
- pip
- A PDF resume
- API keys for:
  - Tavily
  - Google Generative AI (Gemini)

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/SuperTuggy/Jobby.git
cd Jobby
2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Set API keys
export TAVILY_API_KEY="your_tavily_key"
export GOOGLE_API_KEY="your_google_key"

Running the generator

This step searches for jobs and generates tailored resumes.

python generator.py


You will be prompted for:

Job titles (comma-separated)

Remote vs in-person preference

Location (if in-person)

A base resume PDF

Generated resumes are saved under the resumes/ directory.
Job state is saved in processed_jobs.json.

Running the tracker UI

This step launches a simple GUI for tracking jobs.

python main.py


You can:

Open job postings in your browser

Open generated resumes

Mark jobs as applied

Archive jobs (hidden from view)

State is saved automatically.
