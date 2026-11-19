# Smart Resume & Job Description Analyzer (Generative AI)

A modern AI-powered web application built with **Python**, **Streamlit**, and **Google Gemini / OpenAI APIs** to evaluate candidate resumes against target job postings, compute ATS match scores, detect skill gaps, and provide actionable resume enhancement suggestions.

---

## 🌟 Key Features

- **Multi-Model LLM Support**: Seamlessly toggle between **Google Gemini** (`gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.0-flash`) and **OpenAI** (`gpt-4o-mini`, `gpt-4o`).
- **Flexible Resume Ingestion**: Supports direct **PDF parsing** (via `pypdf`), text document uploads (`.txt`), and direct raw text copy-paste.
- **ATS Match Score & Seniority Fit**: Computes an objective alignment score (0–100%) and evaluates candidate experience against role requirements.
- **Keyword & Skills Gap Analysis**:
  - Highlights matched keywords and competencies in green badges.
  - Pinpoints missing keywords and technical requirements in red badges.
- **Tailored Improvement Tips**: Generates strategic recommendations to optimize bullet points, keywords, and recruiter readability.
- **Targeted Bullet Point Rewrites**: Produces ready-to-use, tailored resume bullet points highlighting relevant achievements.
- **Robust JSON Parsing & Error Handling**: Structured prompt templates enforce schema compliance with regex fallback handling for consistent rendering.
- **Exportable Reports**: One-click download of the complete analysis report as a formatted Markdown file.

---

## 🏗️ Project Architecture

```
Job analyzer/
├── app.py                 # Streamlit UI & interactive dashboard
├── analyzer.py            # Prompt engineering, LLM API calls & JSON parsing
├── extractor.py           # PDF and TXT text extraction module
├── requirements.txt       # Project dependencies
├── .env.example           # Environment variables template
└── README.md              # Project documentation
```

---

## 🚀 Getting Started

### 1. Clone or Open Workspace
Ensure you are in the project directory:
```bash
cd "Job analyzer"
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your API key:
- [Google AI Studio (Gemini)](https://aistudio.google.com/): `GEMINI_API_KEY=AIzaSy...`
- or [OpenAI API](https://platform.openai.com/api-keys): `OPENAI_API_KEY=sk-...`

*(Alternatively, you can enter the API key directly into the application's sidebar at runtime).*

### 5. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📝 Resume Bullet Points (Ready to Copy)

If you are showcasing this project on your resume or portfolio:

```text
Smart Resume & Job Description Analyzer (Generative AI) | Python, Streamlit, Google Gemini & OpenAI API
• Engineered an interactive Generative AI application using Python and Streamlit to benchmark candidate resumes against job descriptions, achieving automated ATS match scoring and gap analysis.
• Designed structured few-shot prompt templates to reliably extract missing domain keywords, assess seniority fit, and generate tailored resume bullet point rewrites.
• Implemented robust JSON response parsing, schema validation, and PDF extraction with comprehensive fallback and error handling.
```

