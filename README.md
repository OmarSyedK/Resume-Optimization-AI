
# Resume Optimization AI

Changing you resume according to different job applications and roles is a tedious task. This tool fixes that for you. All you have to do is upload your existing resume and the required job title (and extra details if you want) and the model will generate a clean, ready to download resume in pdf form.
It also provides a detailed explanation of every change made so you know how your resume was optimized.


## How it works & Techniques

This project uses a combination of file processing and advanced prompt engineering to deliver its results.

* **PDF Parsing:** The uploaded resume is read and its text is extracted using the pypdf library.

* **Prompt Engineering:** A detailed system prompt instructs the Google Gemini model to act as an expert career coach. The prompt commands the AI to make specific, relevant changes and maintain a professional tone.

* **Structured JSON Output:** The Gemini API's response_schema is used to force the model to return its answer in a reliable JSON format. This ensures the application doesn't break and can easily parse the explanation and resume fields.

* **PDF Generation:** The optimized resume, which is generated in markdown, is converted to HTML using markdown2 and then styled with a custom CSS sheet. The weasyprint library renders the HTML into a clean, professional PDF available for download.

## Tech Stack

* **Core:** Python

* **Web Framework:** Streamlit

* **AI Model:** Google Gemini (via google-generativeai)

* **PDF Handling:**

    **Reading:** pypdf

    **Writing:** weasyprint

* **Text Conversion:** markdown2

* **Deployment:** Streamlit Cloud


## Link

https://resumeopt.streamlit.app/

