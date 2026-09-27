import streamlit as st
from google import genai
from pypdf import PdfReader

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Study Buddy")
st.write("Upload your notes or PDF and let AI help you study.")

# Gemini API
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("GEMINI_API_KEY is not configured in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)


def extract_pdf_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def ask_ai(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        st.error(f"Gemini error: {e}")
        return None


# Sidebar
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
    5,
    30,
    10
)


# PDF upload
uploaded_file = st.file_uploader(
    "📄 Upload your notes or PDF",
    type=["pdf"]
)

notes = ""

if uploaded_file:

    with st.spinner("Reading your notes..."):
        notes = extract_pdf_text(uploaded_file)

    if not notes.strip():
        st.error("I couldn't extract text from this PDF.")
        st.stop()

    # Limit prompt size
    notes = notes[:100000]

    st.success("✅ Your notes are ready!")


    # Explain notes
    if mode == "Explain my notes":

        if st.button("🧠 Explain My Notes"):

            prompt = f"""
You are an expert tutor.

Explain the following study material clearly and simply.

Use:
- Simple language
- Important definitions
- Examples
- Key ideas
- A short summary

Only use information supported by the study material.

STUDY MATERIAL:

{notes}
"""

            with st.spinner("Creating your explanation..."):
                answer = ask_ai(prompt)

            if answer:
                st.subheader("🧠 Explanation")
                st.markdown(answer)


    # Flashcards
    elif mode == "Make flashcards":

        if st.button("🃏 Generate Flashcards"):

            prompt = f"""
You are a study assistant.

Create useful flashcards from the study material.

Format them like this:

### Card 1
**Question:** ...
**Answer:** ...

### Card 2
**Question:** ...
**Answer:** ...

Focus on important concepts.

Only use information supported by the study material.

STUDY MATERIAL:

{notes}
"""

            with st.spinner("Creating flashcards..."):
                answer = ask_ai(prompt)

            if answer:
                st.subheader("🃏 Flashcards")
                st.markdown(answer)


    # Quiz
    elif mode == "Create a quiz":

        if st.button("❓ Generate Quiz"):

            prompt = f"""
You are an expert teacher.

Create a {num_questions}-question practice quiz
based ONLY on the study material.

Use a mixture of:
- Multiple choice
- True/false
- Short answer

Do not give the answer immediately after each question.

At the end, create:

ANSWER KEY

Then list the correct answers.

STUDY MATERIAL:

{notes}
"""

            with st.spinner("Creating your quiz..."):
                answer = ask_ai(prompt)

            if answer:
                st.subheader("❓ Practice Quiz")
                st.markdown(answer)


    # Study guide
    elif mode == "Study guide":

        if st.button("📖 Create Study Guide"):

            prompt = f"""
You are an expert study coach.

Turn the study material into a clear study guide.

Include:

1. Main topics
2. Important vocabulary
3. Important facts
4. Concepts students commonly confuse
5. Examples
6. Things to memorize
7. Final review

Only use information supported by the study material.

STUDY MATERIAL:

{notes}
"""

            with st.spinner("Creating your study guide..."):
                answer = ask_ai(prompt)

            if answer:
                st.subheader("📖 Study Guide")
                st.markdown(answer)


# General AI tutor
st.divider()

st.subheader("💬 Ask Your Study Buddy")

question = st.text_input(
    "Ask a question about your uploaded notes:"
)

if question:

    if not uploaded_file:
        st.warning("📄 Upload your notes first.")

    else:

        prompt = f"""
You are a helpful AI tutor.

Answer the student's question using ONLY the study
material below.

If the answer cannot be found in the material,
say that clearly instead of making something up.

STUDY MATERIAL:

{notes}

STUDENT QUESTION:

{question}
"""

        with st.spinner("Thinking..."):
            answer = ask_ai(prompt)

        if answer:
            st.subheader("🤖 Study Buddy")
            st.markdown(answer)


st.divider()

st.caption("📚 AI Study Buddy • Powered by Google Gemini")
