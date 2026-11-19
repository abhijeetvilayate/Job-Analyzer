import json
import re
from typing import Dict, Any, Optional

PROMPT_TEMPLATE = """You are an expert Executive Recruiter, ATS (Applicant Tracking System) Specialist, and Career Coach.
Analyze the following Candidate Resume against the target Job Description with deep scrutiny.

Candidate Resume:
```
{resume_text}
```

Target Job Description:
```
{job_description}
```

Instructions:
1. Objectively evaluate the match between the resume and the job requirements.
2. Calculate a realistic ATS Match Score between 0 and 100 based on core skills, experience level, tools, and domain requirements.
3. Identify matched keywords (skills/qualifications present in both).
4. Identify critical missing keywords and skills (required or preferred in the job description but absent or weak in the resume).
5. Categorize strengths and gaps.
6. Provide specific, high-impact, actionable improvement tips to increase the candidate's chances.
7. Provide tailored resume bullet points or rephrasings demonstrating how the candidate could better frame their actual background for this role.

You MUST respond ONLY with a valid JSON object strictly matching this schema. Do not include markdown code block formatting or preamble text if possible, or keep it as pure JSON:
{{
  "match_score": <integer from 0 to 100>,
  "summary": "<2-3 sentence executive summary of candidate fit>",
  "matched_keywords": ["<keyword1>", "<keyword2>", "..."],
  "missing_keywords": ["<keyword1>", "<keyword2>", "..."],
  "experience_alignment": "<Evaluation of years of experience and seniority fit>",
  "strengths": [
    "<Key strength 1>",
    "<Key strength 2>",
    "<Key strength 3>"
  ],
  "areas_for_improvement": [
    "<Weakness or gap 1>",
    "<Weakness or gap 2>"
  ],
  "tailored_improvement_tips": [
    "<Actionable step 1 to tailor the resume>",
    "<Actionable step 2>",
    "<Actionable step 3>"
  ],
  "suggested_bullet_points": [
    "<Tailored bullet point phrasing 1 tailored to the JD>",
    "<Tailored bullet point phrasing 2 tailored to the JD>"
  ]
}}
"""

def clean_json_response(raw_text: str) -> Dict[str, Any]:
    """
    Cleans and extracts JSON payload from model output, handling markdown blocks,
    preambles, or unescaped characters.
    """
    text = raw_text.strip()
    
    # Strip markdown backticks if present
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # Attempt direct parse
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return validate_and_normalize(data)
    except json.JSONDecodeError:
        pass

    # Regex search for JSON object if surrounded by chatty text
    match = re.search(r'(\{[\s\S]*\})', text)
    if match:
        try:
            data = json.loads(match.group(1))
            if isinstance(data, dict):
                return validate_and_normalize(data)
        except json.JSONDecodeError:
            pass

    raise ValueError("The AI model returned a response that could not be parsed as valid JSON. Response preview:\n" + text[:300])

def validate_and_normalize(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensures expected keys exist with valid fallback values."""
    return {
        "match_score": int(data.get("match_score", 0)),
        "summary": str(data.get("summary", "Analysis completed.")),
        "matched_keywords": list(data.get("matched_keywords", [])),
        "missing_keywords": list(data.get("missing_keywords", [])),
        "experience_alignment": str(data.get("experience_alignment", "Not specified")),
        "strengths": list(data.get("strengths", [])),
        "areas_for_improvement": list(data.get("areas_for_improvement", [])),
        "tailored_improvement_tips": list(data.get("tailored_improvement_tips", [])),
        "suggested_bullet_points": list(data.get("suggested_bullet_points", []))
    }

def analyze_with_gemini(resume_text: str, job_description: str, api_key: str, model_name: str = "gemini-flash-lite-latest") -> Dict[str, Any]:
    """
    Call Google Gemini API using fast REST endpoints with automatic failover
    to prevent hanging on overloaded models.
    """
    import requests

    prompt = PROMPT_TEMPLATE.format(
        resume_text=resume_text.strip(),
        job_description=job_description.strip()
    )

    clean_name = model_name.replace("models/", "")
    # Prioritize responsive models; avoid getting stuck on 503 high-demand models
    models_to_try = [clean_name]
    fallback_chain = ["gemini-flash-lite-latest", "gemini-3-flash-preview", "gemini-flash-latest"]
    for fb in fallback_chain:
        if fb not in models_to_try:
            models_to_try.append(fb)

    last_error = None
    clean_key = api_key.strip()

    # Step 1: Direct REST call with tight timeout (fastest and most reliable)
    for m in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={clean_key}"
            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": clean_key
            }
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }
            res = requests.post(url, headers=headers, json=payload, timeout=25)
            
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return clean_json_response(parts[0]["text"])
            
            # If model is 503 (high demand), 429 (rate-limited), or 404 (not found), failover immediately
            if res.status_code in (404, 429, 503):
                continue
            else:
                err_msg = res.json().get("error", {}).get("message", res.text)
                last_error = RuntimeError(f"Gemini API Error ({res.status_code}): {err_msg}")
        except Exception as e:
            last_error = e
            continue

    # Step 2: Fallback to google.genai SDK if REST loop encountered issues
    try:
        from google import genai
        client = genai.Client(api_key=clean_key)
        for m in models_to_try:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=prompt
                )
                if response and response.text:
                    return clean_json_response(response.text)
            except Exception as e:
                last_error = e
                continue
    except Exception as e:
        last_error = e

    if last_error:
        raise last_error
    raise RuntimeError("Unable to complete analysis. Please verify your API key and network connection.")

def analyze_with_openai(resume_text: str, job_description: str, api_key: str, model_name: str = "gpt-4o-mini") -> Dict[str, Any]:
    """Call OpenAI API to analyze resume."""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai package not installed. Run 'pip install openai'.")

    client = OpenAI(api_key=api_key)
    
    prompt = PROMPT_TEMPLATE.format(
        resume_text=resume_text.strip(),
        job_description=job_description.strip()
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are an expert ATS & Resume Analyzer that only outputs valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.2
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty response received from OpenAI API.")

    return clean_json_response(content)
