# Jobby

## How to run this project

### Clone the repository

    git clone https://github.com/SuperTuggy/Jobby
    cd jobby

### Create a virtual environment

**Windows**

    python -m venv venv
    venv\Scripts\activate

**macOS / Linux**

    python3 -m venv venv
    source venv/bin/activate

### Install requirements

    pip install -r requirements.txt

### Set up API keys

This project requires API keys.

1. Create an account and generate an API key from:
   - Tavily (for job search)
   - Google (for the Gemini API)

2. Open the file `main.py`.

3. Find these lines near the top:

    TAVILY_API_KEY = "INSERT YOUR API KEY"
    
    GOOGLE_API_KEY = "INSERT YOUR API KEY"

4. Replace the placeholder strings with your actual API keys.

Do not commit your API keys to a public repository.

### Run the program

Run the resume generator:

    python main.py

Run the job tracker UI:

    python job_tracker_ui.py
