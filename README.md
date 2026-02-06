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
git clone [https://github.com/SuperTuggy/Jobby.git](https://github.com/SuperTuggy/Jobby.git)
cd Jobby
```

2. Create and activate a virtual environment
Bash

python -m venv venv
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

3. Install dependencies
Bash

pip install -r requirements.txt

4. Set API keys
Bash

export TAVILY_API_KEY="your_tavily_key"
export GOOGLE_API_KEY="your_google_key"

Running the Generator

This step searches for jobs and generates tailored resumes.
Bash

python generator.py

You will be prompted for:

    Job titles (comma-separated)

    Remote vs in-person preference

    Location (if in-person)

    A base resume PDF

Generated resumes are saved under the resumes/ directory. Job state is saved in processed_jobs.json.
Running the Tracker UI

This step launches a simple GUI for tracking jobs.
Bash

python main.py

In the UI, you can:

    Open job postings in your browser

    Open generated resumes

    Mark jobs as applied

    Archive jobs (hidden from view)

State is saved automatically.
