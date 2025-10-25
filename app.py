import streamlit as st
import google.generativeai as genai
import json
from pypdf import PdfReader
import io
import markdown2
from weasyprint import HTML, CSS
import os  # Weasyprint might need this, good to keep

# --- 1. Page Configuration & API Key ---
# Set the page configuration as the very first Streamlit command
st.set_page_config(
    page_title="AI Resume Optimizer",
    page_icon="🧑‍💼",
    layout="wide"
)

try:
    api_key = "AIzaSyDamqBNeAPRv4EhQcn3PCKX8iE9xni3DPE"
    if not api_key:
        raise KeyError
    genai.configure(api_key=api_key)
except KeyError:
    st.error("ERROR: GOOGLE_API_KEY not found. Please add it to your .streamlit/secrets.toml file.")
    st.stop()  # Stop the app if the key is not found

# --- 2. Model, Config, and CSS Definitions ---

# System instruction for the model
system_instruction = "You are a helpful assistant and an expert in career coaching specializing in tailoring resumes."

# Setting up the model
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash-lite',  # Using a specific, reliable model
    system_instruction=system_instruction
)

# Configuration for the generation call
generation_config = genai.GenerationConfig(
    temperature=0.25,
    response_mime_type="application/json",
    response_schema={
        "type": "OBJECT",
        "properties": {
            "explanation": {"type": "STRING"},
            "resume": {"type": "STRING"}
        },
        "required": ["explanation", "resume"]
    }
)

# Professional CSS for PDF styling
resume_style = """
body {
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #2c3e50;
    background-color: #fff;
    margin: 40px;
    font-size: 11pt;
}
h1 {
    font-size: 24pt;
    color: #1a1a1a;
    text-align: center;
    margin-bottom: 5px;
    font-weight: 400;
    letter-spacing: 0.5px;
}
/* Contact info under name */
.contact-info {
    text-align: center;
    font-size: 10pt;
    color: #555;
    margin-bottom: 20px;
}
h2 {
    font-size: 13pt;
    color: #ffffff;
    background-color: #2c3e50;
    padding: 6px 10px;
    margin-top: 28px;
    margin-bottom: 12px;
    border-radius: 4px;
    font-weight: 500;
}
ul {
    padding-left: 18px;
    margin-top: 5px;
    margin-bottom: 10px;
    list-style-type: disc;
}
li {
    margin-bottom: 6px;
}
p {
    margin: 0 0 6px 0;
}
b {
    color: #2c3e50;
}
"""

# --- 3. Build the User Interface (UI) ---

st.title("🤖 AI Resume Optimizer")
st.markdown("Upload your resume (PDF) and paste the job description to get a tailored version in seconds.")

# Create two columns for inputs
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

with col2:
    job_description = st.text_area("Paste the Job Description", height=300,
                                   placeholder="Paste the full job description here...")

# Submit button
submit_button = st.button("Optimize My Resume")

# --- 4. Main Application Logic ---
if submit_button:
    # Validate inputs
    if uploaded_file is None:
        st.error("⚠️ Please upload your resume PDF.")
    elif not job_description:
        st.error("⚠️ Please paste the job description.")
    else:
        with st.spinner("Analyzing job description and your resume... This may take a moment."):
            try:
                # --- PDF Reading Logic ---
                # Use uploaded_file.getvalue() which returns bytes
                reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))

                all_text = ""
                for page in reader.pages:
                    text = page.extract_text()
                    if text:  # Ensure text was extracted
                        if text not in all_text:  # Simple de-dupe
                            all_text += text

                md_resume = all_text  # This is the extracted text

                # --- Prompt Creation Logic ---
                prompt = f"""
                I am providing you a markdown resume and a job description \
                I want you to optimize the resume according to the job role and job description \
                Make relevent changes to the resume in sections such as skills, projects, achievments, etc \
                while keeping the unique qualifications and strengths. \
                Return a JSON object containing two keys:
                1. The output should state in depth about the changes you made to the resume and why you made them in bullet points. \
                2. Then return the optimized resume in markdown format.

                ### Here is the resume in Markdown:
                {md_resume}

                ### Here is the job description:
                {job_description}

                If the text does not match the following criteria, is probably not a resume:
                - If it is longer than 3 pages, the new pages begin after //........//
                - Absence of sections such as Education, Experience, Skills, Projects, Certifications,etc.
                In this case return ---Not a valid resume--- without any further explanation in the explanation key and return an empty string in the resume key.

                Please modify the resume to:
                - Contain keywords and phrases relevent to the job description
                - Make sure the experiences are presented in a way that match the job description requirements.
                - Maintain clarity, conciseness, and professionalism throughout.
                - There should be no --implied-- or --likely--, everything should be a statement
                - The Markdown format MUST follow semantic structure so it renders cleanly in PDF:
                  * `#` for the name
                  * `##` for main sections (Summary, Education, Skills, Experience, Projects, Achievements, Certifications, Languages, etc.)
                  * `###` for sub-sections (e.g., each job or project title)
                  * Use bullet points (`-`) for responsibilities, skills, and achievements,etc
                  * Avoid inline formatting hacks (like mixing emojis or excessive bolding for section headers)
                  * Ensure consistent spacing and formatting throughout
                """

                # --- API Call Logic ---
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )

                # Directly parse the JSON response text
                output_data = json.loads(response.text)

                # --- Extract and Validate Response ---
                explanation = output_data.get("explanation", "")
                updated_resume = output_data.get("resume", "")

                if "---Not a valid resume---" in explanation or not updated_resume:
                    st.error(
                        "The uploaded file does not appear to be a valid resume, or the text could not be extracted properly. Please try a different PDF.")
                else:
                    # --- 5. Display Results ---
                    st.success("✅ Your resume has been optimized!")

                    # Create two columns for outputs
                    out_col1, out_col2 = st.columns(2)

                    with out_col1:
                        st.subheader("Changes Explained")
                        st.markdown(explanation)  # Display formatted markdown

                    with out_col2:
                        st.subheader("Optimized Resume (Markdown)")
                        # Use st.code to show the raw markdown
                        st.code(updated_resume, language="markdown")

                    # --- 6. PDF Generation and Download Logic ---
                    st.subheader("Download Your New Resume")

                    # Convert Markdown -> HTML
                    html_content = markdown2.markdown(updated_resume)

                    # Generate PDF in memory
                    pdf_bytes = HTML(string=html_content).write_pdf(stylesheets=[CSS(string=resume_style)])

                    st.download_button(
                        label="Click to Download PDF",
                        data=pdf_bytes,
                        file_name=f"{uploaded_file.name.split('.')[0]}_Optimized.pdf",
                        mime="application/pdf"
                    )

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.exception(e)  # Provides a full traceback for debugging