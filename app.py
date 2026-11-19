import os
import streamlit as st
from dotenv import load_dotenv

from extractor import extract_text_from_upload
from analyzer import analyze_with_gemini, analyze_with_openai
from pdf_generator import generate_pdf_report

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Smart Resume & JD Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        border-left: 6px solid #4CAF50;
        margin-bottom: 20px;
    }
    .score-badge-high {
        font-size: 2.2rem;
        font-weight: bold;
        color: #2e7d32;
    }
    .score-badge-medium {
        font-size: 2.2rem;
        font-weight: bold;
        color: #ed6c02;
    }
    .score-badge-low {
        font-size: 2.2rem;
        font-weight: bold;
        color: #d32f2f;
    }
    .keyword-pill-matched {
        display: inline-block;
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 12px;
        border-radius: 16px;
        margin: 3px;
        font-size: 0.85rem;
        font-weight: 500;
        border: 1px solid #c8e6c9;
    }
    .keyword-pill-missing {
        display: inline-block;
        background-color: #ffebee;
        color: #c62828;
        padding: 4px 12px;
        border-radius: 16px;
        margin: 3px;
        font-size: 0.85rem;
        font-weight: 500;
        border: 1px solid #ffcdd2;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    provider = st.selectbox(
        "Select LLM Provider",
        options=["Google Gemini", "OpenAI"],
        index=0
    )
    
    if provider == "Google Gemini":
        default_key = os.getenv("GEMINI_API_KEY", "")
        api_key = st.text_input("Gemini API Key", value=default_key, type="password", help="Enter your Google AI Studio API key")
        gemini_model_display = st.selectbox(
            "Gemini Model",
            options=[
                "gemini-flash-lite-latest (Recommended - Fast & Stable)",
                "gemini-3-flash-preview",
                "gemini-flash-latest",
                "gemini-pro-latest"
            ],
            index=0
        )
        model_name = gemini_model_display.split(" ")[0]
    else:
        default_key = os.getenv("OPENAI_API_KEY", "")
        api_key = st.text_input("OpenAI API Key", value=default_key, type="password", help="Enter your OpenAI API key")
        model_name = st.selectbox(
            "OpenAI Model",
            options=["gpt-4o-mini", "gpt-4o"],
            index=0
        )
        
    st.divider()
    st.markdown("""
    ### 💡 Quick Tips:
    1. Upload your resume in **PDF** or **TXT** format.
    2. Paste the target **Job Description**.
    3. Click **Analyze Fit** to inspect match score, missing keywords, and tailored tips.
    """)

# Main Page Header
st.title("🎯 Smart Resume & Job Description Analyzer")
st.markdown("Compare candidate resumes against job descriptions with AI to extract missing keywords, compute match scores, and generate tailored resume improvements.")

# Input Section: 2 Columns
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📄 Candidate Resume")
    resume_mode = st.radio("Input method:", ["Upload File (PDF/TXT)", "Paste Raw Text"], horizontal=True)
    
    resume_text = ""
    if resume_mode == "Upload File (PDF/TXT)":
        uploaded_file = st.file_uploader("Upload resume file", type=["pdf", "txt"], help="Upload PDF or TXT resume")
        if uploaded_file is not None:
            try:
                with st.spinner("Extracting text from file..."):
                    resume_text = extract_text_from_upload(uploaded_file)
                st.success(f"Extracted {len(resume_text)} characters from {uploaded_file.name}")
                with st.expander("Preview Extracted Resume"):
                    st.text_area("Resume Content", resume_text, height=200, disabled=True)
            except Exception as e:
                st.error(f"Error parsing file: {e}")
    else:
        resume_text = st.text_area("Paste Resume Text Here", height=320, placeholder="Paste the candidate's resume content here...")

with col2:
    st.subheader("📋 Job Description")
    sample_jd_clicked = st.button("Load Sample Job Description", type="secondary")
    
    default_jd = ""
    if sample_jd_clicked:
        default_jd = """Senior Python / AI Engineer
Location: Remote
About the Role:
We are seeking an experienced Python Software Engineer with strong background in Generative AI, Large Language Models (LLMs), and cloud APIs.

Requirements:
- 3+ years experience with Python, FastAPI, and Streamlit.
- Proven experience building GenAI applications using LangChain, OpenAI API, or Google Gemini API.
- Deep understanding of Prompt Engineering, Retrieval-Augmented Generation (RAG), and vector databases (Pinecone, ChromaDB).
- Hands-on experience with Docker, CI/CD pipelines, and cloud platforms (AWS / GCP).
- Strong understanding of RESTful APIs, Git, and unit testing with pytest.
- Excellent communication and problem-solving skills."""

    job_description = st.text_area(
        "Paste Job Description Here",
        value=default_jd,
        height=320,
        placeholder="Paste full job posting details, requirements, and responsibilities..."
    )

st.write("")
analyze_btn = st.button("🚀 Analyze Fit & ATS Score", type="primary", use_container_width=True)

if analyze_btn:
    if not api_key:
        st.error(f"⚠️ Please provide an API Key for {provider} in the sidebar.")
    elif not resume_text.strip():
        st.warning("⚠️ Please upload or paste a candidate resume.")
    elif not job_description.strip():
        st.warning("⚠️ Please provide a target job description.")
    else:
        with st.spinner(f"Analyzing resume against job description using {provider} ({model_name})..."):
            try:
                if provider == "Google Gemini":
                    result = analyze_with_gemini(resume_text, job_description, api_key, model_name)
                else:
                    result = analyze_with_openai(resume_text, job_description, api_key, model_name)
                
                st.session_state["analysis_result"] = result
                st.success("Analysis complete!")
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

# Display Results if present in session state
if "analysis_result" in st.session_state:
    result = st.session_state["analysis_result"]
    st.divider()
    
    score = result.get("match_score", 0)
    score_color_class = "score-badge-high" if score >= 80 else ("score-badge-medium" if score >= 60 else "score-badge-low")
    
    # Score & Summary Header
    score_col, summary_col = st.columns([1, 3], gap="medium")
    with score_col:
        st.markdown(f"""
        <div style="text-align: center; background: #fafafa; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px;">
            <div style="font-size: 1rem; color: #666; font-weight: 600;">ATS MATCH SCORE</div>
            <div class="{score_color_class}">{score}%</div>
            <div style="color: #888; font-size: 0.85rem;">Overall Requirement Alignment</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(max(0, min(100, score)) / 100.0)
        
    with summary_col:
        st.markdown("### Executive Fit Summary")
        st.info(result.get("summary", "No summary available."))
        st.markdown(f"**Experience & Seniority Fit:** {result.get('experience_alignment', 'N/A')}")
        
    st.write("")
    
    # Tabs for detailed breakdown
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Keyword & Skills Gap",
        "💪 Strengths & Weaknesses",
        "💡 Tailored Improvement Tips",
        "✍️ Suggested Resume Rewrites"
    ])
    
    with tab1:
        kw_col1, kw_col2 = st.columns(2, gap="large")
        with kw_col1:
            st.markdown("#### ✅ Matched Keywords & Competencies")
            matched = result.get("matched_keywords", [])
            if matched:
                pills = " ".join([f'<span class="keyword-pill-matched">✓ {k}</span>' for k in matched])
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.write("No exact keywords matched.")
                
        with kw_col2:
            st.markdown("#### ❌ Critical Missing Keywords / Skills")
            missing = result.get("missing_keywords", [])
            if missing:
                pills = " ".join([f'<span class="keyword-pill-missing">✕ {k}</span>' for k in missing])
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.write("No major keywords missing.")
                
    with tab2:
        str_col, weak_col = st.columns(2, gap="large")
        with str_col:
            st.markdown("#### 🌟 Candidate Strengths")
            for item in result.get("strengths", []):
                st.markdown(f"- **{item}**")
        with weak_col:
            st.markdown("#### ⚠️ Key Gaps / Improvement Areas")
            for item in result.get("areas_for_improvement", []):
                st.markdown(f"- {item}")
                
    with tab3:
        st.markdown("#### 🚀 Actionable Steps to Improve ATS & Recruiter Fit")
        for i, tip in enumerate(result.get("tailored_improvement_tips", []), 1):
            st.markdown(f"**{i}.** {tip}")
            
    with tab4:
        st.markdown("#### 📝 Tailored Bullet Points for this Job Description")
        st.caption("Incorporate these tailored phrasing examples into your work experience or projects section:")
        for bp in result.get("suggested_bullet_points", []):
            st.markdown(f"> • {bp}")
            
    # Export Report Section
    st.divider()
    st.subheader("📥 Export Analysis Report")
    
    # Generate PDF bytes
    try:
        pdf_data = generate_pdf_report(result)
    except Exception as e:
        pdf_data = None
        st.warning(f"Could not generate PDF: {e}")

    report_md = f"""# Resume & Job Description Analysis Report
**ATS Match Score:** {score}%

## Executive Summary
{result.get('summary', '')}

**Seniority / Experience Fit:** {result.get('experience_alignment', '')}

## Matched Keywords
{', '.join(result.get('matched_keywords', []))}

## Missing Keywords
{', '.join(result.get('missing_keywords', []))}

## Strengths
{chr(10).join(['- ' + s for s in result.get('strengths', [])])}

## Areas for Improvement
{chr(10).join(['- ' + w for w in result.get('areas_for_improvement', [])])}

## Tailored Improvement Tips
{chr(10).join([f"{i+1}. " + t for i, t in enumerate(result.get('tailored_improvement_tips', []))])}

## Suggested Bullet Points
{chr(10).join(['- ' + b for b in result.get('suggested_bullet_points', [])])}
"""
    dl_col1, dl_col2 = st.columns([1, 1], gap="medium")
    
    with dl_col1:
        if pdf_data:
            st.download_button(
                label="📄 Download Analysis Report (PDF)",
                data=pdf_data,
                file_name="Resume_Job_Fit_Report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
            
    with dl_col2:
        st.download_button(
            label="📝 Download Report (Markdown)",
            data=report_md,
            file_name="resume_analysis_report.md",
            mime="text/markdown",
            use_container_width=True
        )

