import streamlit as st
import PyPDF2
import textwrap
import json
import os
import re
import time
import pandas as pd
import google.generativeai as genai
from io import BytesIO
from typing import Dict, List, Any
import base64

# Streamlit page config
st.set_page_config(
    page_title="Resume Job Match Checker",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main app styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Custom card styling */
    div[data-testid="stVerticalBlock"] {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Header styling */
    h1 {
        color: #1e3a8a;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #1e3a8a;
        font-weight: 600;
    }
    
    h3 {
        color: #2563eb;
        font-weight: 500;
    }
    
    /* Button styling */
    button[kind="primary"] {
        background-color: #2563eb;
        border-radius: 12px;
    }
    
    button[kind="secondary"] {
        border-radius: 12px;
    }
    
    /* Tab styling */
    button[data-baseweb="tab"] {
        font-weight: 600;
        border-radius: 10px 10px 0px 0px;
    }
    
    div[role="tablist"] {
        background-color: #f1f5f9;
        border-radius: 10px 10px 0px 0px;
    }
    
    /* Expander styling */
    details {
        background-color: #f8fafc;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    summary {
        padding: 10px;
        font-weight: 500;
    }
    
    /* File uploader */
    div[data-testid="stFileUploader"] {
        border: 2px dashed #2563eb;
        border-radius: 12px;
        padding: 20px;
    }
    
    /* Success message */
    div[data-baseweb="notification"] {
        border-radius: 10px;
    }
    
    /* Progress bar */
    div[role="progressbar"] {
        border-radius: 10px;
        height: 8px;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Match score styling */
    .match-score {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: 500;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    
    .badge-green {
        background-color: #dcfce7;
        color: #15803d;
    }
    
    .badge-yellow {
        background-color: #fef9c3;
        color: #854d0e;
    }
    
    .badge-red {
        background-color: #fee2e2;
        color: #b91c1c;
    }
</style>
""", unsafe_allow_html=True)

# App title with emojis
st.title("🚀 Resume Job Match Checker 📝")

# App description with emojis
st.markdown("""
### 🔍 Find out if your resume matches the job requirements! 💯

This app extracts job requirements from job descriptions and evaluates 
whether your resume meets those requirements in seconds! 🎯
""")

# Sidebar for API configuration with emojis
with st.sidebar:
    st.markdown("### ⚙️ API Configuration")
    st.markdown("---")
    
    gemini_api_key = st.text_input("🔑 Gemini API Key", type="password", 
                                  help="Get a free API key from https://aistudio.google.com/app/apikey")
    
    if gemini_api_key:
        try:
            # Configure Gemini API
            genai.configure(api_key=gemini_api_key)
            st.success("✅ Gemini API configured successfully!")
        except Exception as e:
            st.error(f"❌ Error configuring Gemini API: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 💡 About")
    st.info(
        "🔎 This app uses AI to extract job requirements from job descriptions "
        "and evaluates if your resume matches those requirements! "
        "Increase your chances of getting an interview! 🏆"
    )
    
    # Tips section in sidebar
    st.markdown("### 📝 Tips for Best Results")
    st.markdown("""
    - 📄 Upload clear, searchable PDFs
    - 📋 Make sure your resume is up-to-date
    - 📊 Update your resume based on the results
    - 💼 Focus on improving low-match areas
    - 🔄 Re-run the check after updating your resume
    """)

# Constants
CHUNK_SIZE = 5000  # characters per chunk

# Gemini Models
def get_gemini_model():
    """Get the appropriate Gemini model"""
    try:
        # Use Gemini 1.0 Flash (free tier model)
        return genai.GenerativeModel('gemini-1.5-pro-latest')
    except:
        # Fall back to Gemini 1.0 (free tier model)
        return genai.GenerativeModel('gemini-1.0-pro')

# Utility Functions
def extract_text_from_pdf(uploaded_file):
    """Extract text from an uploaded PDF file"""
    text = ""
    try:
        pdf_file = BytesIO(uploaded_file.getvalue())
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"❌ Error extracting text from PDF: {str(e)}")
        return None

def split_text_into_chunks(text, chunk_size=CHUNK_SIZE):
    """Split text into manageable chunks"""
    return textwrap.wrap(text, chunk_size)

def build_extraction_prompt(chunk):
    """Build prompt for job requirements extraction"""
    return f"""
From the following job description content, extract only the key job requirements
(such as skills, experience, education, certifications, etc.).

Return a valid JSON object with clear key-value pairs. Do not include explanation or surrounding text.
Structure the JSON as:
{{
  "requirement_name_1": "detailed requirement description 1",
  "requirement_name_2": "detailed requirement description 2",
  ...
}}

Use clear, descriptive keys like "experience_requirements", "technical_skills", "education_requirements", etc.

Text:
{chunk}
"""

def build_evaluation_prompt(requirements_json, resume_text):
    """Build prompt for resume evaluation"""
    return f"""
You are an expert resume analyst. Your task is to evaluate whether a resume meets the job requirements.

JOB REQUIREMENTS:
{json.dumps(requirements_json, indent=2)}

RESUME CONTENT:
{resume_text}

Please analyze if the resume meets each of the job requirements. Pay special attention to:
1. Experience requirements (years of experience, specific domains)
2. Technical skills and competencies
3. Education requirements
4. Certifications and qualifications

For each requirement, determine if the resume meets it based on the content provided.
If there are specific numerical requirements (e.g., "5 years of experience"), check if the resume meets those exact requirements.

Provide your assessment in the following JSON format:
{{
  "overall_match_percentage": 85,  // A number between 0-100 representing the overall match
  "requirements_evaluation": {{
    "requirement_name_1": {{
      "meets_requirement": true/false,
      "explanation": "Detailed explanation of why the resume meets or doesn't meet this requirement",
      "confidence": "high/medium/low",
      "match_score": 90  // A number between 0-100 for this specific requirement
    }},
    "requirement_name_2": {{
      "meets_requirement": true/false,
      "explanation": "Detailed explanation of why the resume meets or doesn't meet this requirement",
      "confidence": "high/medium/low",
      "match_score": 70
    }},
    ...
  }},
  "strengths": ["Strength 1", "Strength 2", ...],  // List of resume strengths related to the job
  "gaps": ["Gap 1", "Gap 2", ...],  // List of gaps or missing requirements
  "improvement_suggestions": ["Suggestion 1", "Suggestion 2", ...],  // Actionable suggestions to improve match
  "summary": "A brief summary of the overall match assessment"
}}

Only respond with the JSON object, no additional text.
"""

def extract_valid_json(text):
    """Extract valid JSON from text response"""
    try:
        # Try direct JSON parsing first
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            # Try to find JSON within the text
            json_match = re.search(r'({.*})', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            else:
                st.error("❌ Could not extract valid JSON from response")
                return None
        except Exception as e:
            st.error(f"❌ JSON parsing failed: {str(e)}")
            return None

def extract_years_from_text(text):
    """Extract years of experience from text"""
    if not text:
        return None
        
    # Look for patterns like "X years" or "X-year" or "X yr"
    patterns = [
        r'(\d+)\s*(?:years|year)',
        r'(\d+)\s*(?:-|\s)year',
        r'(\d+)\s*(?:yrs|yr)',
        r'experience\s*(?:of|with)?\s*(\d+)',
        r'(\d+)\s*years?\s*(?:of)?\s*experience'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            return int(matches[0])
    
    return None

def query_gemini(prompt):
    """Query the Gemini API"""
    if not gemini_api_key:
        st.error("❌ Please configure your Gemini API key in the sidebar first.")
        return None
        
    try:
        model = get_gemini_model()
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"❌ Error querying Gemini API: {str(e)}")
        return None

# Main App Functions
def extract_job_requirements(job_desc_text):
    """Extract job requirements from job description text"""
    with st.spinner("🔍 Extracting job requirements from document..."):
        chunks = split_text_into_chunks(job_desc_text)
        
        # Progress bar for extraction
        progress_bar = st.progress(0)
        st.write(f"⏳ Processing {len(chunks)} text chunks...")
        
        all_requirements = {}
        
        for i, chunk in enumerate(chunks):
            # Update progress
            progress = int((i / len(chunks)) * 100)
            progress_bar.progress(progress)
            
            # Only process every second chunk to speed up and save API calls
            if i % 2 == 0 or i == len(chunks) - 1:
                prompt = build_extraction_prompt(chunk)
                result = query_gemini(prompt)
                
                if result:
                    json_result = extract_valid_json(result)
                    if json_result:
                        all_requirements.update(json_result)
        
        # Complete progress bar
        progress_bar.progress(100)
        
        return all_requirements

def evaluate_resume(requirements, resume_text):
    """Evaluate resume against job requirements"""
    with st.spinner("🔍 Analyzing your resume against job requirements..."):
        prompt = build_evaluation_prompt(requirements, resume_text)
        result = query_gemini(prompt)
        
        if result:
            return extract_valid_json(result)
        return None

def generate_summary(evaluation):
    """Generate a concise summary of the evaluation"""
    prompt = f"""
You are an expert at summarizing complex information. Please provide a concise, easy-to-understand summary of the following resume evaluation.

RESUME EVALUATION:
{json.dumps(evaluation, indent=2)}

Your summary should:
1. Be no more than 3-4 sentences
2. Clearly state the overall match percentage
3. Mention the key strengths and gaps
4. Use simple, direct language

Respond with only the summary text, no additional formatting or explanation.
"""
    
    return query_gemini(prompt)

# App Interface
tabs = st.tabs(["📤 Upload Job Description", "📋 Extract Requirements", "📝 Upload Resume", "📊 Results"])

# Session state initialization
if 'job_desc_text' not in st.session_state:
    st.session_state.job_desc_text = None
if 'requirements' not in st.session_state:
    st.session_state.requirements = None
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'evaluation' not in st.session_state:
    st.session_state.evaluation = None
if 'summary' not in st.session_state:
    st.session_state.summary = None

# Tab 1: Upload Job Description
with tabs[0]:
    st.header("📤 Upload Job Description")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📑 Step 1: Upload the job description
        
        Upload the job posting PDF to analyze the requirements.
        """)
        
        uploaded_file = st.file_uploader("Choose a Job Description PDF file", type="pdf", 
                                       help="Upload the job description PDF to extract requirements")
    
    with col2:
        st.markdown("### 🔍 Why This Matters")
        st.info("A clear job description helps us accurately identify what employers are looking for! 🎯")
    
    if uploaded_file:
        if st.button("🔍 Extract Text from PDF", type="primary"):
            with st.spinner("⏳ Extracting text from PDF..."):
                job_desc_text = extract_text_from_pdf(uploaded_file)
                if job_desc_text:
                    st.session_state.job_desc_text = job_desc_text
                    st.success("✅ Successfully extracted text from the job description!")
                    
                    # Preview in a collapsed section
                    with st.expander("👀 View extracted text preview"):
                        st.text_area("Job Description Preview", job_desc_text[:2000] + "...", height=300)
                    
                    st.info("👉 Proceed to the '📋 Extract Requirements' tab to continue.")
                else:
                    st.error("❌ Failed to extract text from the PDF.")

# Tab 2: Extract Requirements
with tabs[1]:
    st.header("📋 Extract Job Requirements")
    
    if st.session_state.job_desc_text is None:
        st.info("🔍 Please upload a job description PDF in the '📤 Upload Job Description' tab first.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 🧐 Step 2: Extract job requirements
            
            Let AI analyze the job description to identify key requirements.
            """)
            
            if st.button("🔍 Extract Job Requirements", type="primary"):
                requirements = extract_job_requirements(st.session_state.job_desc_text)
                if requirements:
                    st.session_state.requirements = requirements
                    st.success(f"✅ Successfully extracted {len(requirements)} job requirements!")
                    
                    # Display requirements in a nice format with emojis
                    st.markdown("### 📋 Extracted Job Requirements")
                    
                    req_categories = {
                        'experience': '⏱️',
                        'skill': '🛠️',
                        'education': '🎓',
                        'certification': '📜',
                        'technical': '💻',
                        'soft': '🤝',
                        'language': '🗣️',
                        'knowledge': '🧠',
                        'qualification': '🏆',
                        'degree': '📚'
                    }
                    
                    for req, description in requirements.items():
                        # Assign emoji based on requirement category
                        emoji = '📌'  # default
                        for category, cat_emoji in req_categories.items():
                            if category in req.lower():
                                emoji = cat_emoji
                                break
                                
                        with st.expander(f"{emoji} {req.replace('_', ' ').title()}"):
                            st.write(description)
                    
                    st.info("👉 Proceed to the '📝 Upload Resume' tab to check your match!")
                else:
                    st.error("❌ Failed to extract job requirements from the document.")
        
        with col2:
            st.markdown("### 🧩 What's Happening")
            st.info("Our AI is analyzing the job posting to identify specific skills, qualifications, and experience needed! 🔍")

# Tab 3: Upload Resume
with tabs[2]:
    st.header("📝 Upload Your Resume")
    
    if st.session_state.requirements is None:
        st.info("📋 Please extract job requirements in the '📋 Extract Requirements' tab first.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 📄 Step 3: Upload your resume
            
            Upload your resume to check how well it matches the job requirements.
            """)
            
            resume_file = st.file_uploader("Choose your Resume PDF file", type="pdf",
                                         help="Upload your resume to evaluate against the job requirements")
            
            if resume_file:
                if st.button("🔍 Process Resume", type="primary"):
                    with st.spinner("⏳ Processing your resume..."):
                        resume_text = extract_text_from_pdf(resume_file)
                        if resume_text:
                            st.session_state.resume_text = resume_text
                            
                            # Preview in a collapsed section
                            with st.expander("👀 View extracted resume text preview"):
                                st.text_area("Resume Preview", resume_text[:1000] + "...", height=200)
                            
                            # Proceed to evaluation
                            st.success("✅ Resume processed successfully!")
                            
                            # Automatic evaluation
                            st.markdown("### 🔍 Evaluating Your Resume")
                            with st.spinner("⏳ Comparing your resume to job requirements..."):
                                evaluation = evaluate_resume(st.session_state.requirements, resume_text)
                                if evaluation:
                                    st.session_state.evaluation = evaluation
                                    summary = generate_summary(evaluation)
                                    st.session_state.summary = summary
                                    
                                    st.success("✅ Resume evaluation completed!")
                                    st.info("👉 Proceed to the '📊 Results' tab to view your match results!")
                                else:
                                    st.error("❌ Failed to evaluate your resume.")
                        else:
                            st.error("❌ Failed to extract text from your resume.")
        
        with col2:
            st.markdown("### 📊 What We're Looking For")
            st.info("We'll compare your resume against the extracted job requirements and provide a detailed match analysis! 🔍")
            
            # Add tips for better resume matching
            st.markdown("### 💡 Resume Tips")
            st.markdown("""
            - Use relevant keywords from the job description
            - Quantify your achievements when possible
            - Focus on skills mentioned in the job posting
            - Update your resume for each application
            """)

# Tab 4: Results
with tabs[3]:
    st.header("📊 Match Results")
    
    if st.session_state.evaluation is None:
        st.info("📝 Please complete the resume evaluation in the '📝 Upload Resume' tab first.")
    else:
        evaluation = st.session_state.evaluation
        
        # Display match score with visual elements
        match_score = evaluation.get('overall_match_percentage', 0)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Create a visual match score display
            score_color = "#15803d" if match_score >= 75 else "#ca8a04" if match_score >= 50 else "#b91c1c"
            st.markdown(f"""
            <div style="background-color: white; border-radius: 15px; padding: 20px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="margin-bottom: 10px;">Match Score</h3>
                <div style="font-size: 72px; font-weight: bold; color: {score_color};">{match_score}%</div>
                <div style="font-size: 16px; color: #64748b; margin-top: 10px;">
                    {
                    "Great match! 🌟" if match_score >= 75 else 
                    "Good match with room for improvement 👍" if match_score >= 50 else 
                    "Needs significant improvement 🔧"
                    }
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display summary
            if st.session_state.summary:
                st.markdown("### 📝 Summary")
                st.info(st.session_state.summary)
        
        with col2:
            # Strengths and gaps
            col_strengths, col_gaps = st.columns(2)
            
            with col_strengths:
                st.markdown("### 💪 Strengths")
                strengths = evaluation.get('strengths', [])
                for strength in strengths:
                    st.markdown(f"✅ {strength}")
                    
            with col_gaps:
                st.markdown("### 🔍 Areas to Improve")
                gaps = evaluation.get('gaps', [])
                for gap in gaps:
                    st.markdown(f"⚠️ {gap}")
        
        # Improvement suggestions
        st.markdown("### 🚀 Improvement Suggestions")
        suggestions = evaluation.get('improvement_suggestions', [])
        for i, suggestion in enumerate(suggestions):
            st.markdown(f"💡 **Suggestion {i+1}**: {suggestion}")
        
        # Detailed evaluation for each requirement
        st.markdown("### 📊 Detailed Requirements Analysis")
        
        requirements_data = []
        for req, result in evaluation['requirements_evaluation'].items():
            match_score = result.get("match_score", 0)
            score_emoji = "✅" if match_score >= 80 else "⚠️" if match_score >= 50 else "❌"
            
            requirements_data.append({
                "Requirement": req.replace('_', ' ').title(),
                "Match": f"{score_emoji} {match_score}%",
                "Status": "Meets" if result["meets_requirement"] else "Does not meet",
                "Confidence": result.get("confidence", "N/A").capitalize(),
                "Details": result["explanation"]
            })
        
        df = pd.DataFrame(requirements_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Detailed explanation for each requirement
        st.markdown("### 🔎 Requirement Details")
        for req, result in evaluation['requirements_evaluation'].items():
            meets = result["meets_requirement"]
            match_score = result.get("match_score", 0)
            
            # Determine color based on match score
            if match_score >= 80:
                color = "#15803d"  # green
                icon = "✅"
            elif match_score >= 50:
                color = "#ca8a04"  # yellow
                icon = "⚠️"
            else:
                color = "#b91c1c"  # red
                icon = "❌"
            
            with st.expander(f"{icon} {req.replace('_', ' ').title()} - {match_score}%"):
                st.markdown(f"**Match Score**: <span style='color:{color};font-weight:bold;'>{match_score}%</span>", unsafe_allow_html=True)
                st.markdown(f"**Status**: {'Meets requirement ✓' if meets else 'Does not meet requirement ✗'}")
                st.markdown(f"**Confidence**: {result.get('confidence', 'N/A').capitalize()}")
                st.markdown(f"**Explanation**: {result['explanation']}")
        
        # Download results
        col1, col2 = st.columns(2)
        with col1:
            if st.download_button(
                "📊 Download Analysis as JSON",
                json.dumps(evaluation, indent=2),
                file_name="resume_evaluation.json",
                mime="application/json"
            ):
                st.success("✅ Successfully downloaded evaluation results!")
                
        with col2:
            # Generate a simplified text report
            report = f"""RESUME MATCH REPORT
            
Overall Match Score: {match_score}%

STRENGTHS:
{chr(10).join([f'• {s}' for s in strengths])}

AREAS TO IMPROVE:
{chr(10).join([f'• {g}' for g in gaps])}

IMPROVEMENT SUGGESTIONS:
{chr(10).join([f'• {s}' for s in suggestions])}

REQUIREMENTS ANALYSIS:
{chr(10).join([f'• {req.replace("_", " ").title()}: {result.get("match_score", 0)}% - {"Meets" if result["meets_requirement"] else "Does not meet"}' for req, result in evaluation['requirements_evaluation'].items()])}
            """
            
            if st.download_button(
                "📝 Download Text Report",
                report,
                file_name="resume_match_report.txt",
                mime="text/plain"
            ):
                st.success("✅ Successfully downloaded text report!")

if __name__ == "__main__":
    pass 
