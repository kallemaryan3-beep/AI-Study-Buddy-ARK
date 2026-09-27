import streamlit as st
import time
from google import genai
from pypdf import PdfReader

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Study Buddy")
st.write("Upload your notes or PDF and let AI help you study.")


# ============================================================
# GEMINI SETUP
# ============================================================

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("GEMINI_API_KEY is not configured in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(pdf_file):
    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ============================================================
# GEMINI AI FUNCTION
# ============================================================

def ask_ai(prompt):

    models = [
        "gemini-3.8-flash",
        "gemini-3.8-flash-lite"
    ]

    last_error = None

    for model in models:

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response.text:
                    return response.text

            except Exception as e:

                last_error = e

                error_text = str(e)

                if "503" in error_text or "UNAVAILABLE" in error_text:

                    if attempt < 2:
                        time.sleep(2 ** attempt)
                        continue

                    break

                break

    if last_error:
        st.error(
            "Gemini is temporarily unavailable. "
            "Please wait a moment and try again."
        )

    return None


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("📚 Study Settings")

mode = st.sidebar.selectbox(
    "What do you want to do?",
    [
        "Explain my notes",
        "Make flashcards",
        "Create a quiz",
        "Study guide"
    ]
)

num_questions = st.sidebar.slider(
    "Number of quiz questions",
    min_value=5,
    max_value=30,
    value=10
)


# ============================================================
# PDF UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "📄 Upload your notes or PDF",
    type=["pdf"]
)

notes = ""


# ============================================================
# PROCESS PDF
# ============================================================

if uploaded_file:

    with st.spinner("📖 Reading your notes..."):
        notes = extract_pdf_text(uploaded_file)

    if not notes.strip():

        st.error(
            "I couldn't extract text from this PDF. "
            "Try a text-based PDF instead."
        )

        st.stop()

    # Prevent extremely large prompts
    notes = notes[:100000]

    st.success("✅ Your notes are ready!")


    # ========================================================
    # EXPLAIN NOTES
    # ========================================================

    if mode == "Explain my notes":

        if st.button("🧠 Explain My Notes"):

            prompt = f"""
You are an expert tutor helping a student understand
their study material.

Explain the following study material clearly and simply.

Use:

- Simple language
- Important definitions
- Examples
- Key ideas
- A short summary at the end

Do not invent information that isn't supported by
the study material.

STUDY MATERIAL:

{notes}
"""

            with st.spinner("🧠 Creating your explanation..."):

                answer = ask_ai(prompt)

            if answer:

                st.subheader("🧠 Explanation")

                st.markdown(answer)


    # ========================================================
    # FLASHCARDS
    # ========================================================

    elif mode == "Make flashcards":

        if st.button("🃏 Generate Flashcards"):

            prompt = f"""
You are a study assistant.

Create useful flashcards from the following study
material.

Format every card like this:

### Card 1
**Question:** ...
**Answer:** ...

### Card 2
**Question:** ...
**Answer:** ...

Focus on important concepts rather than tiny details.

Only use information supported by the study material.

STUDY MATERIAL:

{notes}
"""

            with st.spinner("🃏 Creating flashcards..."):

                answer = ask_ai(prompt)

            if answer:

                st.subheader("🃏 Flashcards")

                st.markdown(answer)


    # ========================================================
    # QUIZ
    # ========================================================

    elif mode == "Create a quiz":

        if st.button("❓ Generate Quiz"):

            prompt = f"""
You are an expert teacher.

Create a {num_questions}-question practice quiz
based ONLY on the following study material.

Use a mixture of:

- Multiple choice
- True/false
- Short answer

Do not provide the answers immediately after each
question.

After all questions, create a section called:

ANSWER KEY

Put the correct answers in that section.

Only use information supported by the study material.

STUDY MATERIAL:

{notes}
"""

            with st.spinner("❓ Creating your quiz..."):

                answer = ask_ai(prompt)

            if answer:

                st.subheader("❓ Practice Quiz")

                st.markdown(answer)


    # ========================================================
    # STUDY GUIDE
    # ========================================================

    elif mode == "Study guide":

        if st.button("📖 Create Study Guide"):

            prompt = f"""
You are an expert study coach.

Turn the following study material into a clear,
organized study guide.

Include:

1. Main topics
2. Important vocabulary
3. Important facts
4. Concepts students commonly confuse
5. Examples
6. Things to memorize
7. A short final review

Only use information supported by the material.

STUDY MATERIAL:

{notes}
"""

            with st.spinner("📖 Creating your study guide..."):

                answer = ask_ai(prompt)

            if answer:

                st.subheader("📖 Study Guide")

                st.markdown(answer)


# ============================================================
# GENERAL AI STUDY BUDDY
# ============================================================

st.divider()

st.subheader("💬 Ask Your Study Buddy")

question = st.text_input(
    "Ask a question about your uploaded notes:"
)


if question:

    if not uploaded_file:

        st.warning(
            "📄 Please upload your notes or a PDF first."
        )

    else:

        prompt = f"""
You are a helpful AI tutor.

Answer the student's question using ONLY the study
material provided below.

If the answer cannot be found in the material,
say that clearly instead of making something up.

Give a clear and student-friendly explanation.

STUDY MATERIAL:

{notes}

STUDENT QUESTION:

{question}
"""

        with st.spinner("🤔 Thinking..."):

            answer = ask_ai(prompt)

        if answer:

            st.subheader("🤖 Study Buddy")

            st.markdown(answer)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "📚 AI Study Buddy • Powered by Google Gemini"
)
