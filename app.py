"""
ClaimAssist AI - minimum viable product (MVP)

One user : an individual policyholder whose health claim was rejected or partly paid
One job  : understand the rejection and prepare an appeal
One AI   : explains the rejection in plain English + drafts an appeal letter

Run locally:  streamlit run app.py
"""

import os

import streamlit as st
from google import genai

# ---------------------------------------------------------------------------
# 1. SETTINGS  (change these in one place)
# ---------------------------------------------------------------------------
# If Google retires this model name, open Google AI Studio, pick a current
# Gemini "flash" model and paste its name here.
MODEL_NAME = "gemini-3.5-flash-lite"

POLICY_TYPES = [
    "Individual health insurance",
    "Family floater",
    "Senior citizen policy",
    "Corporate / group health insurance",
    "Parent's policy that I manage",
]

LETTER_MARKER = "---APPEAL LETTER---"  # the AI puts this line between the two parts

# ---------------------------------------------------------------------------
# 2. THE INSTRUCTIONS WE GIVE THE AI (the "prompt")
#    Each rule here comes from something users told us in the survey/interview.
# ---------------------------------------------------------------------------
INSTRUCTIONS = f"""
You help an ordinary health-insurance policyholder in India who received a claim
rejection or partial settlement. The reader is NOT an expert.

Use ONLY the details the user gives you. Never invent policy clause numbers,
court cases, regulation section numbers, amounts or dates. If something needed
is missing, say so and tell the user what to look for in their policy document.

Write your answer in TWO parts.

PART 1 - use these four headings exactly, in simple English (school-level words,
short sentences, explain any jargon in brackets):
## 1. What the insurer is saying
## 2. Why the claim was rejected
(State the main reason category: waiting period, pre-existing disease,
policy exclusion, missing documents, medical necessity, non-disclosure, or other.
Then say, as possible grounds and NOT as a promise, whether the doctor's advice
gives a reasonable basis to question it.)
## 3. Documents to collect for the appeal
(A checklist, using "- [ ]" for each item, based on the rejection reason.)
## 4. Things to keep in mind
(2-3 short points: appeal to the insurer first, then Insurance Ombudsman / IRDAI
grievance route if unresolved. Mention these only in general terms. Say this is
guidance, not legal advice.)

Then write this exact line on its own line:
{LETTER_MARKER}

PART 2 - a formal appeal letter to the insurer's grievance officer:
- Use square-bracket placeholders such as [Your Name], [Policy Number], [Claim Number],
  [Date] for anything the user did not give. Do not guess them.
- Clear subject line, short polite paragraphs, state the facts given, state why
  the rejection should be reconsidered using the doctor's advice, ask for a
  written, clause-wise explanation and a review within the timeline required by
  IRDAI rules (do not quote a number of days), and mention the right to approach
  the Insurance Ombudsman if unresolved.
- Do not make threats or accusations. Do not claim anything the user did not state.
"""


# ---------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# ---------------------------------------------------------------------------
def get_api_key():
    """Read the Gemini key from Streamlit secrets (or an environment variable)."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.environ.get("GEMINI_API_KEY")


def ask_ai(user_details: str) -> str:
    """Send the instructions + the user's details to Gemini and return its text."""
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=INSTRUCTIONS + "\n\nUSER DETAILS:\n" + user_details,
    )
    return response.text


# ---------------------------------------------------------------------------
# 4. THE SCREEN
# ---------------------------------------------------------------------------
st.set_page_config(page_title="ClaimAssist AI", page_icon="🩺", layout="centered")
st.title("🩺 ClaimAssist AI")
st.caption("Understand your health insurance claim rejection and prepare an appeal letter.")

with st.sidebar:
    st.header("Before you start")
    st.write(
        "- Do **not** type your name, phone number, policy number or Aadhaar. "
        "The letter will have [placeholders] for you to fill in later.\n"
        "- Your text is sent to Google's Gemini AI to generate the answer. "
        "This app does not store it.\n"
        "- The result is a **draft to review and edit**. It is guidance, "
        "not legal advice, and cannot guarantee your appeal succeeds."
    )

if not get_api_key():
    st.error("The app is missing its AI key. Add GEMINI_API_KEY in the app's secrets (see README).")
    st.stop()

# Step 1 - the form where the user gives us the information
with st.form("claim_form"):
    st.subheader("Step 1: Tell us about your claim")
    policy_type = st.selectbox("Policy type", POLICY_TYPES)
    col1, col2 = st.columns(2)
    claim_amount = col1.number_input("Amount you claimed (₹)", min_value=0, step=1000)
    rejected_amount = col2.number_input("Amount rejected / deducted (₹)", min_value=0, step=1000)
    rejection_text = st.text_area(
        "Paste the rejection or deduction reason from the insurer's letter *",
        height=160,
        placeholder="Copy the paragraph or clause the insurer used to reject or reduce your claim.",
    )
    doctor_advice = st.text_area(
        "What did your doctor advise or write? (diagnosis, why treatment was needed)",
        height=120,
        placeholder="Example: Surgery was advised after medicines did not work; admission was medically necessary.",
    )
    submitted = st.form_submit_button("Explain my rejection and draft my appeal")

# Step 2 - when the button is pressed, call the AI and show the result
if submitted:
    if len(rejection_text.strip()) < 20:
        st.warning("Please paste the rejection reason from your letter (at least a sentence).")
        st.stop()

    details = (
        f"Policy type: {policy_type}\n"
        f"Amount claimed: Rs {claim_amount}\n"
        f"Amount rejected or deducted: Rs {rejected_amount}\n"
        f"Insurer's rejection / deduction text: {rejection_text}\n"
        f"Doctor's advice: {doctor_advice or 'Not provided'}"
    )

    with st.spinner("Reading your letter and preparing your explanation..."):
        try:
            result = ask_ai(details)
        except Exception as error:
            st.error(
                "Sorry, something went wrong while contacting the AI. "
                "Please wait a minute and try again."
            )
            st.caption(f"Technical detail: {error}")
            st.stop()

    if LETTER_MARKER in result:
        explanation, letter = result.split(LETTER_MARKER, 1)
    else:  # safety net if the AI forgot the marker
        explanation, letter = result, ""

    st.subheader("Step 2: Your explanation")
    st.markdown(explanation.strip())

    if letter.strip():
        st.subheader("Step 3: Your draft appeal letter")
        st.caption("Edit the text below, fill in the [placeholders], then copy or download it.")
        edited = st.text_area("Appeal letter", value=letter.strip(), height=420)
        st.download_button("Download letter (.txt)", data=edited, file_name="appeal_letter.txt")

    st.info("Always check the draft against your policy document before sending it.")
