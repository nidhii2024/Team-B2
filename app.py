import streamlit as st
import PyPDF2
import google.generativeai as genai
import speech_recognition as sr
import os

# -----------------------------
# 1. Configure Gemini API key
# -----------------------------
genai.configure(api_key="AIzaSyBKFCkj7ViYQYKMMHGlXt3mQrB3L97ZIkQ")

# -----------------------------
# 2. App Title
# -----------------------------
st.title("🎓 StudyBuddy")
st.write("Upload a PDF → AI generates questions → Answer by voice or text → Get evaluated!")

# -----------------------------
# 3. Upload PDF
# -----------------------------
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
pdf_text = ""
if uploaded_file:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        if page.extract_text():
            pdf_text += page.extract_text()
    st.success("✅ PDF uploaded successfully!")

# -----------------------------
# 4. Generate Questions
# -----------------------------
questions = ""
if uploaded_file and st.button("Generate Questions"):
    with st.spinner("🤖 Generating questions..."):
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"""
            From the following text, generate ONLY 5 quiz questions.
            - Do NOT provide answers.
            - Do NOT provide hints or explanations.
            - Format output as plain numbered questions.
            
            Text: {pdf_text}
            """
        )
        questions = response.text.strip()
    st.subheader("📝 Questions:")
    st.write(questions)

# -----------------------------
# 5. Record Voice Answer
# -----------------------------
def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Speak your answer now...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except Exception as e:
        return f"⚠️ Could not recognize audio: {str(e)}"

user_answer = ""

if uploaded_file and st.button("Record Answer"):
    user_answer = record_audio()
    st.write("✅ You said:", user_answer)

# -----------------------------
# 6. Textbox for Manual Answer
# -----------------------------
if uploaded_file:
    text_input = st.text_area("✍️ Or type your answer here:")
    if text_input:
        user_answer = text_input

# -----------------------------
# 7. Evaluate Answer
# -----------------------------
if uploaded_file and user_answer:
    with st.spinner("📊 Evaluating answer..."):
        model = genai.GenerativeModel("gemini-1.5-flash")
        eval_response = model.generate_content(
            f"Compare this student answer: '{user_answer}' with the text: '{pdf_text}'. "
            "Give a similarity percentage (0-100) and a short feedback."
        )
        score = eval_response.text
    st.subheader("📊 Answer Evaluation:")
    st.write(score)
