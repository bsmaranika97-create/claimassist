# ClaimAssist AI

Helps an individual policyholder in India understand a health insurance claim
rejection or partial settlement, and prepare a draft appeal letter.

**Live app:** [paste your Streamlit link here]

## What it does
1. The user picks a policy type, enters claimed and rejected amounts, pastes the insurer's rejection reason, and adds the doctor's advice.
2. The AI explains the rejection in plain English, lists documents to collect, and drafts an appeal letter with [placeholders] for personal details.
3. The user edits the letter and downloads it.

## Scope of this version (MVP)
- One user: individual retail policyholder
- One problem: cannot understand a rejection or write an appeal
- One AI capability: explain + draft
- No login, no database, nothing stored

## Tech
Python, Streamlit, Google Gemini API (google-genai), deployed on Streamlit Community Cloud.

## Run locally
1. `pip install -r requirements.txt`
2. Create `.streamlit/secrets.toml` containing: `GEMINI_API_KEY = "your-key"`
3. `streamlit run app.py`

## Deploy
Push to GitHub, create the app on Streamlit Community Cloud, and add `GEMINI_API_KEY` under Settings > Secrets.
The key is never committed to GitHub.

## AI use disclosure
- Gemini API: powers the in-app explanation and letter drafting.
- [Add: which tools you used to help write code, and what for.]

## Limits
Output is a draft for review, not legal advice. It may contain errors. Do not enter personal identifiers.

## Team
[Names and roles]
