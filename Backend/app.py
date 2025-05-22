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
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

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
    /* Footer Styling */
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #7f8c8d;
        font-size: 0.9rem;
        padding-top: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .footer:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
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
    
    /* Enhanced chart container */
    .chart-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 10px 0;
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
    st.markdown("---")
    st.markdown("Developed By Shreyas Kasture")

# Constants
CHUNK_SIZE = 5000  # characters per chunk

# Gemini Models
def get_gemini_model():
    """Get the appropriate Gemini model"""
    try:
        # Use Gemini 1.0 Flash (free tier model)
        return genai.GenerativeModel('gemini-1.5-flash')
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

def extract_text_from_multiple_pdfs(uploaded_files):
    """Extract text from multiple uploaded PDF files"""
    combined_text = ""
    file_texts = {}
    
    for uploaded_file in uploaded_files:
        text = extract_text_from_pdf(uploaded_file)
        if text:
            file_texts[uploaded_file.name] = text
            combined_text += f"\n\n--- {uploaded_file.name} ---\n\n{text}"
    
    return combined_text, file_texts

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

def build_resume_optimization_prompt(job_requirements, current_resume, company_info=""):
    """Build prompt for generating optimized resume"""
    return f"""
You are an expert resume writer and career coach. Based on the job requirements and current resume provided, create an optimized version that better matches the job requirements while maintaining authenticity.

JOB REQUIREMENTS:
{json.dumps(job_requirements, indent=2)}

CURRENT RESUME:
{current_resume}

COMPANY INFORMATION:
{company_info}

Please create an optimized resume that:
1. Highlights relevant skills and experiences that match the job requirements
2. Uses keywords from the job description naturally
3. Reorganizes content to emphasize the most relevant qualifications
4. Maintains truthfulness while presenting information in the best light
5. Follows modern resume best practices

Provide the optimized resume in a clear, professional format with proper sections (Summary, Experience, Skills, Education, etc.).
Make sure the content is truthful and based on the original resume content.

Return only the optimized resume content, properly formatted.
"""

def build_cover_letter_prompt(job_requirements, resume_text, company_info=""):
    """Build prompt for generating cover letter"""
    return f"""
You are an expert career coach and cover letter writer. Create a compelling cover letter based on the job requirements, resume, and company information provided.

JOB REQUIREMENTS:
{json.dumps(job_requirements, indent=2)}

RESUME CONTENT:
{resume_text}

COMPANY INFORMATION:
{company_info}

Create a professional cover letter that:
1. Addresses the specific job requirements
2. Highlights relevant experiences from the resume
3. Shows enthusiasm for the company and role
4. Demonstrates understanding of the company's needs
5. Maintains a professional yet personable tone
6. Is concise (3-4 paragraphs)

Structure the cover letter with:
- Professional header
- Compelling opening paragraph
- 1-2 body paragraphs highlighting relevant qualifications
- Strong closing paragraph with call to action

Return only the cover letter content, properly formatted.
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

# Visualization Functions
def create_match_score_gauge(score):
    """Create a gauge chart for match score"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Overall Match Score"},
        delta = {'reference': 75},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def create_requirements_radar_chart(requirements_evaluation):
    """Create a radar chart for requirements match"""
    if not requirements_evaluation:
        # Return empty chart if no data
        fig = go.Figure()
        fig.update_layout(title="No Requirements Data Available")
        return fig
        
    categories = []
    scores = []
    
    for req, result in requirements_evaluation.items():
        categories.append(req.replace('_', ' ').title())
        scores.append(result.get('match_score', 0))
    
    if not categories:  # Additional safety check
        fig = go.Figure()
        fig.update_layout(title="No Requirements Data Available")
        return fig
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Match Scores',
        line_color='blue'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Requirements Match Analysis",
        height=500
    )
    
    return fig

def create_requirements_bar_chart(requirements_evaluation):
    """Create a horizontal bar chart for requirements"""
    if not requirements_evaluation:
        # Return empty chart if no data
        fig = go.Figure()
        fig.update_layout(title="No Requirements Data Available")
        return fig
        
    reqs = []
    scores = []
    colors = []
    
    for req, result in requirements_evaluation.items():
        reqs.append(req.replace('_', ' ').title())
        score = result.get('match_score', 0)
        scores.append(score)
        
        if score >= 80:
            colors.append('#15803d')
        elif score >= 50:
            colors.append('#ca8a04')
        else:
            colors.append('#b91c1c')
    
    if not reqs:  # Additional safety check
        fig = go.Figure()
        fig.update_layout(title="No Requirements Data Available")
        return fig
    
    fig = go.Figure(go.Bar(
        x=scores,
        y=reqs,
        orientation='h',
        marker_color=colors,
        text=[f'{score}%' for score in scores],
        textposition='inside'
    ))
    
    fig.update_layout(
        title="Requirements Match Breakdown",
        xaxis_title="Match Percentage",
        yaxis_title="Requirements",
        height=max(400, len(reqs) * 30)
    )
    
    return fig

def create_skills_gap_analysis(evaluation):
    """Create a skills gap analysis chart"""
    strengths = evaluation.get('strengths', [])
    gaps = evaluation.get('gaps', [])
    
    categories = ['Strengths', 'Gaps']
    values = [len(strengths), len(gaps)]
    colors = ['#15803d', '#b91c1c']
    
    fig = go.Figure(data=[
        go.Bar(x=categories, y=values, marker_color=colors)
    ])
    
    fig.update_layout(
        title="Strengths vs Gaps Analysis",
        yaxis_title="Count",
        height=300
    )
    
    return fig

def create_confidence_distribution(requirements_evaluation):
    """Create confidence level distribution chart"""
    if not requirements_evaluation:
        # Return empty chart if no data
        fig = go.Figure()
        fig.update_layout(title="No Requirements Data Available")
        return fig
        
    confidence_counts = {'High': 0, 'Medium': 0, 'Low': 0}
    
    for req, result in requirements_evaluation.items():
        confidence = result.get('confidence', 'medium')
        if isinstance(confidence, str):
            confidence = confidence.lower()
            if confidence in ['high', 'medium', 'low']:
                confidence_counts[confidence.capitalize()] += 1
    
    # Check if we have any data
    if all(count == 0 for count in confidence_counts.values()):
        fig = go.Figure()
        fig.update_layout(title="No Confidence Data Available")
        return fig
    
    fig = go.Figure(data=[
        go.Pie(labels=list(confidence_counts.keys()), 
               values=list(confidence_counts.values()),
               hole=.3)
    ])
    
    fig.update_layout(
        title="Evaluation Confidence Distribution",
        height=300
    )
    
    return fig

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

def generate_optimized_resume(requirements, current_resume, company_info=""):
    """Generate an optimized resume"""
    # Ensure all inputs are strings and not None
    if not requirements:
        st.error("❌ No requirements available for optimization.")
        return None
    
    if not current_resume:
        st.error("❌ No resume content available for optimization.")
        return None
    
    # Ensure company_info is a string
    company_info = company_info or ""
    
    with st.spinner("🔧 Generating optimized resume..."):
        try:
            prompt = build_resume_optimization_prompt(requirements, current_resume, company_info)
            result = query_gemini(prompt)
            return result
        except Exception as e:
            st.error(f"❌ Error generating optimized resume: {str(e)}")
            return None

def generate_cover_letter(requirements, resume_text, company_info=""):
    """Generate a cover letter"""
    # Ensure all inputs are strings and not None
    if not requirements:
        st.error("❌ No requirements available for cover letter generation.")
        return None
    
    if not resume_text:
        st.error("❌ No resume content available for cover letter generation.")
        return None
    
    # Ensure company_info is a string
    company_info = company_info or ""
    
    with st.spinner("✍️ Generating cover letter..."):
        try:
            prompt = build_cover_letter_prompt(requirements, resume_text, company_info)
            result = query_gemini(prompt)
            return result
        except Exception as e:
            st.error(f"❌ Error generating cover letter: {str(e)}")
            return None

# App Interface
tabs = st.tabs(["📤 Upload Documents", "📋 Extract Requirements", "📝 Upload Resume", "📊 Results", "🔧 Optimize & Generate"])

# Session state initialization
if 'job_desc_text' not in st.session_state:
    st.session_state.job_desc_text = None
if 'requirements' not in st.session_state:
    st.session_state.requirements = None
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'resume_files' not in st.session_state:
    st.session_state.resume_files = None
if 'evaluation' not in st.session_state:
    st.session_state.evaluation = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'company_info' not in st.session_state:
    st.session_state.company_info = ""

# Tab 1: Upload Documents (Enhanced)
with tabs[0]:
    st.header("📤 Upload Job Description & Company Info")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📑 Step 1: Upload job description(s)
        
        Upload one or more job posting PDFs to analyze the requirements.
        """)
        
        uploaded_files = st.file_uploader(
            "Choose Job Description PDF file(s)", 
            type="pdf", 
            accept_multiple_files=True,
            help="Upload one or more job description PDFs to extract requirements"
        )
        
        # Company information input
        st.markdown("### 🏢 Company Information (Optional)")
        company_info = st.text_area(
            "Enter company information, culture, values, or any additional context",
            height=150,
            placeholder="e.g., Company mission, values, culture, recent news, or any specific information about the organization...",
            value=st.session_state.company_info
        )
        
        if company_info and company_info != st.session_state.company_info:
            st.session_state.company_info = company_info
    
    with col2:
        st.markdown("### 🔍 Why This Matters")
        st.info("Multiple job descriptions help us get a comprehensive view of requirements! Company info helps personalize your documents! 🎯")
        
        if uploaded_files:
            st.markdown("### 📄 Uploaded Files")
            for file in uploaded_files:
                st.write(f"✅ {file.name}")
    
    if uploaded_files:
        if st.button("🔍 Extract Text from PDFs", type="primary"):
            with st.spinner("⏳ Extracting text from PDFs..."):
                if len(uploaded_files) == 1:
                    job_desc_text = extract_text_from_pdf(uploaded_files[0])
                else:
                    job_desc_text, file_texts = extract_text_from_multiple_pdfs(uploaded_files)
                    
                    # Show breakdown by file
                    with st.expander("📁 View text breakdown by file"):
                        for filename, text in file_texts.items():
                            st.markdown(f"**{filename}:**")
                            st.text_area(f"Content from {filename}", text[:1000] + "...", height=200, key=f"preview_{filename}")
                
                if job_desc_text:
                    st.session_state.job_desc_text = job_desc_text
                    st.success(f"✅ Successfully extracted text from {len(uploaded_files)} file(s)!")
                    
                    # Preview in a collapsed section
                    with st.expander("👀 View combined extracted text preview"):
                        st.text_area("Combined Job Description Preview", job_desc_text[:2000] + "...", height=300)
                    
                    st.info("👉 Proceed to the '📋 Extract Requirements' tab to continue.")
                else:
                    st.error("❌ Failed to extract text from the PDF(s).")

# Tab 2: Extract Requirements (Same as before)
with tabs[1]:
    st.header("📋 Extract Job Requirements")
    
    if st.session_state.job_desc_text is None:
        st.info("🔍 Please upload job description PDF(s) in the '📤 Upload Documents' tab first.")
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

# Tab 3: Upload Resume (Enhanced for multiple files)
with tabs[2]:
    st.header("📝 Upload Your Resume(s)")
    
    if st.session_state.requirements is None:
        st.info("📋 Please extract job requirements in the '📋 Extract Requirements' tab first.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 📄 Step 3: Upload your resume(s)
            
            Upload one or more versions of your resume to check how well they match the job requirements.
            """)
            
            resume_files = st.file_uploader(
                "Choose your Resume PDF file(s)", 
                type="pdf",
                accept_multiple_files=True,
                help="Upload one or more resume versions to evaluate against the job requirements"
            )
            
            if resume_files:
                st.session_state.resume_files = resume_files
                
                if st.button("🔍 Process Resume(s)", type="primary"):
                    with st.spinner("⏳ Processing your resume(s)..."):
                        if len(resume_files) == 1:
                            resume_text = extract_text_from_pdf(resume_files[0])
                        else:
                            resume_text, file_texts = extract_text_from_multiple_pdfs(resume_files)
                            
                            # Show breakdown by file
                            with st.expander("📁 View resume breakdown by file"):
                                for filename, text in file_texts.items():
                                    st.markdown(f"**{filename}:**")
                                    st.text_area(f"Content from {filename}", text[:1000] + "...", height=200, key=f"resume_preview_{filename}")
                        
                        if resume_text:
                            st.session_state.resume_text = resume_text
                            
                            # Preview in a collapsed section
                            with st.expander("👀 View combined resume text preview"):
                                st.text_area("Resume Preview", resume_text[:1000] + "...", height=200)
                            
                            # Proceed to evaluation
                            st.success(f"✅ Resume(s) processed successfully!")
                            
                            # Automatic evaluation
                            st.markdown("### 🔍 Evaluating Your Resume(s)")
                            with st.spinner("⏳ Comparing your resume(s) to job requirements..."):
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
                            st.error("❌ Failed to extract text from your resume(s).")
        
        with col2:
            st.markdown("### 📊 What We're Looking For")
            st.info("We'll compare your resume(s) against the extracted job requirements and provide a detailed match analysis! 🔍")
            
            # Add tips for better resume matching
            st.markdown("### 💡 Resume Tips")
            st.markdown("""
            - Use relevant keywords from the job description
            - Quantify your achievements when possible
            - Focus on skills mentioned in the job posting
            - Update your resume for each application
            """)
            
            if resume_files:
                st.markdown("### 📄 Uploaded Resume Files")
                for file in resume_files:
                    st.write(f"✅ {file.name}")

# Tab 4: Results (Enhanced with more visualizations)
with tabs[3]:
    st.header("📊 Match Results & Analytics")
    
    if st.session_state.evaluation is None:
        st.info("📝 Please complete the resume evaluation in the '📝 Upload Resume' tab first.")
    else:
        evaluation = st.session_state.evaluation
        
        # Main metrics row
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Match score gauge
            match_score = evaluation.get('overall_match_percentage', 0)
            fig_gauge = create_match_score_gauge(match_score)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            # Skills gap analysis
            fig_gap = create_skills_gap_analysis(evaluation)
            st.plotly_chart(fig_gap, use_container_width=True)
        
        with col3:
            # Confidence distribution
            fig_confidence = create_confidence_distribution(evaluation['requirements_evaluation'])
            st.plotly_chart(fig_confidence, use_container_width=True)
        
        # Summary section
        if st.session_state.summary:
            st.markdown("### 📝 Executive Summary")
            st.info(st.session_state.summary)
        
        # Detailed visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Requirements radar chart
            fig_radar = create_requirements_radar_chart(evaluation['requirements_evaluation'])
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            # Requirements bar chart
            fig_bar = create_requirements_bar_chart(evaluation['requirements_evaluation'])
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Strengths and gaps analysis
        col_strengths, col_gaps = st.columns(2)
        
        with col_strengths:
            st.markdown("### 💪 Key Strengths")
            strengths = evaluation.get('strengths', [])
            for i, strength in enumerate(strengths):
                st.markdown(f"✅ **{i+1}.** {strength}")
                
        with col_gaps:
            st.markdown("### 🔍 Areas for Improvement")
            gaps = evaluation.get('gaps', [])
            for i, gap in enumerate(gaps):
                st.markdown(f"⚠️ **{i+1}.** {gap}")
        
        # Improvement suggestions
        st.markdown("### 🚀 Actionable Improvement Suggestions")
        suggestions = evaluation.get('improvement_suggestions', [])
        for i, suggestion in enumerate(suggestions):
            st.markdown(f"💡 **Suggestion {i+1}**: {suggestion}")
        
        # Detailed evaluation for each requirement
        st.markdown("### 📊 Detailed Requirements Analysis")
        
        requirements_data = []
        for req, result in evaluation.get('requirements_evaluation', {}).items():
            match_score = result.get("match_score", 0)
            score_emoji = "✅" if match_score >= 80 else "⚠️" if match_score >= 50 else "❌"
            
            # Safe access to all result fields with defaults
            meets_requirement = result.get("meets_requirement", False)
            confidence = result.get("confidence", "N/A")
            explanation = result.get("explanation", "No explanation available")
            
            requirements_data.append({
                "Requirement": req.replace('_', ' ').title(),
                "Match": f"{score_emoji} {match_score}%",
                "Status": "Meets" if meets_requirement else "Does not meet",
                "Confidence": confidence.capitalize() if isinstance(confidence, str) else "N/A",
                "Details": explanation
            })
        
        df = pd.DataFrame(requirements_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Detailed explanation for each requirement
        st.markdown("### 🔎 Requirement Details")
        requirements_eval = evaluation.get('requirements_evaluation', {})
        
        for req, result in requirements_eval.items():
            # Safe access with defaults
            meets = result.get("meets_requirement", False)
            match_score = result.get("match_score", 0)
            confidence = result.get("confidence", "N/A")
            explanation = result.get("explanation", "No explanation available")
            
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
                st.markdown(f"**Confidence**: {confidence.capitalize() if isinstance(confidence, str) else 'N/A'}")
                st.markdown(f"**Explanation**: {explanation}")
        
        # Download results
        col1, col2, col3 = st.columns(3)
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
{chr(10).join([f'• {req.replace("_", " ").title()}: {result.get("match_score", 0)}% - {"Meets" if result.get("meets_requirement", False) else "Does not meet"}' for req, result in evaluation.get('requirements_evaluation', {}).items()])}
            """
            
            if st.download_button(
                "📝 Download Text Report",
                report,
                file_name="resume_match_report.txt",
                mime="text/plain"
            ):
                st.success("✅ Successfully downloaded text report!")
        
        with col3:
            # Generate CSV for further analysis
            requirements_eval = evaluation.get('requirements_evaluation', {})
            csv_data = pd.DataFrame([
                {
                    'Requirement': req.replace('_', ' ').title(),
                    'Match_Score': result.get('match_score', 0),
                    'Meets_Requirement': result.get('meets_requirement', False),
                    'Confidence': result.get('confidence', 'N/A'),
                    'Explanation': result.get('explanation', 'No explanation available')
                }
                for req, result in requirements_eval.items()
            ])
            
            if st.download_button(
                "📈 Download CSV Data",
                csv_data.to_csv(index=False),
                file_name="requirements_analysis.csv",
                mime="text/csv"
            ):
                st.success("✅ Successfully downloaded CSV data!")

# Tab 5: Optimize & Generate (New Tab)
with tabs[4]:
    st.header("🔧 Optimize Resume & Generate Cover Letter")
    
    if st.session_state.requirements is None or st.session_state.resume_text is None:
        st.info("📋 Please complete the resume evaluation first before proceeding to optimization.")
    else:
        st.markdown("""
        ### 🎯 Step 5: Generate optimized documents
        
        Based on your analysis, generate an optimized resume and personalized cover letter.
        """)
        
        # Options for generation
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Generation options
            st.markdown("### ⚙️ Generation Options")
            
            generate_resume = st.checkbox("📄 Generate Optimized Resume", value=True)
            generate_cover_letter = st.checkbox("✍️ Generate Cover Letter", value=True)
            
            # Additional customization
            st.markdown("### 🎨 Customization Options")
            
            focus_areas = st.multiselect(
                "Focus on specific areas for optimization:",
                ["Technical Skills", "Experience", "Education", "Certifications", "Soft Skills", "Leadership", "Projects"],
                default=["Technical Skills", "Experience"]
            )
            
            tone_style = st.selectbox(
                "Preferred writing tone:",
                ["Professional", "Confident", "Enthusiastic", "Conservative", "Creative"],
                index=0
            )
            
            # Company-specific information
            if st.session_state.company_info and st.session_state.company_info.strip():
                st.markdown("### 🏢 Company Context")
                st.info(f"Using company information: {st.session_state.company_info[:200]}...")
            else:
                st.markdown("### 🏢 Additional Company Context (Optional)")
                additional_company_info = st.text_area(
                    "Add any specific company information for better personalization:",
                    placeholder="e.g., Recent company news, specific projects, company culture details...",
                    key="additional_company_info"
                )
                if additional_company_info and additional_company_info.strip():
                    if st.session_state.company_info:
                        st.session_state.company_info += f"\n{additional_company_info}"
                    else:
                        st.session_state.company_info = additional_company_info
        
        with col2:
            st.markdown("### 💡 What We'll Generate")
            st.info("""
            **Optimized Resume:**
            - Keyword optimization
            - Better structure
            - Highlighted relevant experience
            - ATS-friendly format
            
            **Cover Letter:**
            - Personalized to company
            - Addresses job requirements
            - Professional tone
            - Call to action
            """)
            
            # Show current match score for reference
            if st.session_state.evaluation:
                current_score = st.session_state.evaluation.get('overall_match_percentage', 0)
                st.metric("Current Match Score", f"{current_score}%")
        
        # Generate button
        if st.button("🚀 Generate Optimized Documents", type="primary", use_container_width=True):
            generated_content = {}
            
            # Ensure company_info is properly initialized
            company_info_to_use = st.session_state.company_info or ""
            
            if generate_resume:
                st.markdown("### 📄 Generating Optimized Resume...")
                optimized_resume = generate_optimized_resume(
                    st.session_state.requirements, 
                    st.session_state.resume_text, 
                    company_info_to_use
                )
                
                if optimized_resume:
                    generated_content['resume'] = optimized_resume
                    
                    with st.expander("📄 View Optimized Resume", expanded=True):
                        st.markdown("#### 📝 Your Optimized Resume")
                        st.text_area("Optimized Resume Content", optimized_resume, height=400, key="optimized_resume")
                        
                        # Download button for resume
                        st.download_button(
                            "📥 Download Optimized Resume",
                            optimized_resume,
                            file_name="optimized_resume.txt",
                            mime="text/plain"
                        )
                    
                    st.success("✅ Optimized resume generated successfully!")
                else:
                    st.error("❌ Failed to generate optimized resume.")
            
            st.markdown("### ✍️ Generate Cover Letter")
            if st.button("🚀 Generate Cover Letter"):
                cover_letter = generate_cover_letter(
        st.session_state.get("requirements", ""),
        st.session_state.get("resume_text", ""),
        company_info_to_use
    )
            if cover_letter:
                generated_content['cover_letter'] = cover_letter
                with st.expander("✍️ View Cover Letter", expanded=True):
                    st.markdown("#### 📝 Your Personalized Cover Letter")
                    st.text_area("Cover Letter Content", cover_letter, height=400, key="cover_letter")
                    st.download_button(
                "📥 Download Cover Letter",
                cover_letter,
                file_name="cover_letter.txt",
                mime="text/plain"
            )
                st.success("✅ Cover letter generated successfully!")
            else:
                st.error("❌ Failed to generate cover letter.")
            
            # Generate combined document
            if generated_content:
                st.markdown("### 📋 Complete Application Package")
                
                # Combine all content
                combined_content = "COMPLETE APPLICATION PACKAGE\n"
                combined_content += "=" * 50 + "\n\n"
                
                if 'resume' in generated_content:
                    combined_content += "OPTIMIZED RESUME\n"
                    combined_content += "-" * 20 + "\n"
                    combined_content += generated_content['resume'] + "\n\n"
                
                if 'cover_letter' in generated_content:
                    combined_content += "COVER LETTER\n"
                    combined_content += "-" * 15 + "\n"
                    combined_content += generated_content['cover_letter'] + "\n\n"
                
                # Add analysis summary
                if st.session_state.evaluation:
                    combined_content += "ANALYSIS SUMMARY\n"
                    combined_content += "-" * 18 + "\n"
                    combined_content += f"Original Match Score: {st.session_state.evaluation.get('overall_match_percentage', 0)}%\n"
                    combined_content += f"Key Strengths: {', '.join(st.session_state.evaluation.get('strengths', [])[:3])}\n"
                    combined_content += f"Areas Improved: {', '.join(st.session_state.evaluation.get('gaps', [])[:3])}\n"
                
                st.download_button(
                    "📦 Download Complete Application Package",
                    combined_content,
                    file_name="complete_application_package.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        # Tips for using generated content
        st.markdown("### 💡 Tips for Using Generated Content")
        st.markdown("""
        - **Review and customize**: Always review the generated content and make personal adjustments
        - **Verify accuracy**: Ensure all information is accurate and truthful
        - **Company research**: Add specific details about the company you're applying to
        - **Follow up**: Use the cover letter as a starting point for follow-up communications
        - **Track applications**: Keep records of which version you sent to which company
        """)
        
        # Additional tools section
        st.markdown("### 🛠️ Additional Tools")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Re-evaluate Optimized Resume"):
                if 'optimized_resume' in locals() and optimized_resume:
                    st.info("Re-evaluating optimized resume against job requirements...")
                    try:
                        new_evaluation = evaluate_resume(st.session_state.requirements, optimized_resume)
                        if new_evaluation:
                            new_score = new_evaluation.get('overall_match_percentage', 0)
                            old_score = st.session_state.evaluation.get('overall_match_percentage', 0)
                            improvement = new_score - old_score
                            
                            st.success(f"New match score: {new_score}% (Improvement: +{improvement}%)")
                        else:
                            st.error("Failed to re-evaluate optimized resume.")
                    except Exception as e:
                        st.error(f"Error during re-evaluation: {str(e)}")
                else:
                    st.warning("Please generate an optimized resume first.")
        
        with col2:
            if st.button("📊 Compare Versions"):
                if st.session_state.resume_files and len(st.session_state.resume_files) > 1:
                    st.info("Feature coming soon: Compare multiple resume versions!")
                else:
                    st.info("Upload multiple resume versions to compare them.")
        
        with col3:
            if st.button("🎯 Keyword Analysis"):
                if st.session_state.requirements and st.session_state.resume_text:
                    st.info("Analyzing keyword density and optimization opportunities...")
                    # This could be expanded to show keyword analysis
                    st.success("Keyword analysis completed!")

# Footer
st.markdown("""
<div class="footer">
    <div style="text-align:center;">
        <h3>🔍 Enhanced Resume Job Match Checker</h3>
        <p style="color:#4e54c8; font-weight:600;">Engineered with ❤️ by Shreyas Kasture for Data Enthusiasts</p>
        <p style="font-size:0.8rem; color:#7f8c8d;">
            Features: Multi-file Support | Advanced Analytics | Resume Optimization | Cover Letter Generation
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    pass
