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
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import docx
from docx import Document

# Streamlit page config
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for modern UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styling */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Header styling */
    .main-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    /* Card styling */
    .custom-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
    }
    
    /* Enhanced headers */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    h2 {
        color: #4a5568;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #667eea;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
    }
    
    /* Progress indicators */
    .progress-container {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
    }
    
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-bottom: 8px;
        transition: all 0.3s ease;
    }
    
    .step-active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .step-completed {
        background: #48bb78;
        color: white;
    }
    
    .step-inactive {
        background: #e2e8f0;
        color: #a0aec0;
    }
    
    /* Score display */
    .score-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        color: white;
        margin: 20px 0;
    }
    
    .score-number {
        font-size: 4rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .metric-label {
        color: #718096;
        font-size: 0.9rem;
        margin-top: 5px;
    }
    
    /* Enhanced file uploader */
    .stFileUploader {
        border: 3px dashed #667eea;
        border-radius: 20px;
        padding: 40px;
        background: rgba(102, 126, 234, 0.05);
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #764ba2;
        background: rgba(102, 126, 234, 0.1);
    }
    
    /* Sidebar enhancements */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        color: #4a5568;
        font-weight: 600;
        padding: 12px 20px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Enhanced alerts */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Loading animations */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 2s infinite;
    }
    
    /* Footer */
    .footer {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-top: 50px;
        backdrop-filter: blur(10px);
    }
    
    /* Requirement badges */
    .req-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        margin: 5px;
        transition: all 0.3s ease;
    }
    
    .req-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .badge-excellent {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
    }
    
    .badge-good {
        background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        color: white;
    }
    
    .badge-poor {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        color: white;
    }
    
    /* Statistics dashboard */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        h1 { font-size: 2rem; }
        .score-number { font-size: 3rem; }
        .custom-card { padding: 15px; }
    }
</style>
""", unsafe_allow_html=True)

# Enhanced header
st.markdown("""
<div class="main-header">
    <h1>🚀 AI Resume Analyzer Pro</h1>
    <p style="font-size: 1.2rem; color: #4a5568; margin: 0;">
        Advanced AI-powered resume matching with comprehensive analytics
    </p>
</div>
""", unsafe_allow_html=True)

# Progress indicator function
def show_progress_indicator(current_step):
    steps = [
        ("1", "Upload Job", "job"),
        ("2", "Extract Requirements", "extract"),
        ("3", "Upload Resume", "resume"),
        ("4", "View Results", "results")
    ]
    
    step_html = '<div class="progress-container"><div class="step-indicator">'
    
    for i, (num, title, key) in enumerate(steps):
        if i < current_step:
            circle_class = "step-circle step-completed"
            icon = "✓"
        elif i == current_step:
            circle_class = "step-circle step-active"
            icon = num
        else:
            circle_class = "step-circle step-inactive"
            icon = num
            
        step_html += f'''
        <div class="step">
            <div class="{circle_class}">{icon}</div>
            <span style="font-weight: 500; color: {'#667eea' if i <= current_step else '#a0aec0'}">{title}</span>
        </div>
        '''
        
        if i < len(steps) - 1:
            line_color = "#667eea" if i < current_step else "#e2e8f0"
            step_html += f'<div style="flex: 1; height: 2px; background: {line_color}; margin: 20px 10px 0 10px;"></div>'
    
    step_html += '</div></div>'
    st.markdown(step_html, unsafe_allow_html=True)

# Enhanced sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h2>⚙️ Configuration</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # API Configuration
    with st.expander("🔑 API Settings", expanded=True):
        gemini_api_key = st.text_input(
            "Gemini API Key", 
            type="password",
            help="Get your free API key from Google AI Studio",
            placeholder="Enter your Gemini API key..."
        )
        
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                st.success("✅ API configured successfully!")
            except Exception as e:
                st.error(f"❌ API configuration failed: {str(e)}")
    
    # Analysis Settings
    with st.expander("🎛️ Analysis Settings"):
        st.markdown("**Matching Sensitivity**")
        sensitivity = st.select_slider(
            "Select matching sensitivity",
            options=["Strict", "Balanced", "Lenient"],
            value="Balanced",
            help="Adjust how strictly requirements are matched"
        )
        
        st.markdown("**Analysis Depth**")
        analysis_depth = st.selectbox(
            "Choose analysis depth",
            ["Quick Scan", "Standard Analysis", "Deep Analysis"],
            index=1,
            help="Select how detailed the analysis should be"
        )
        
        include_suggestions = st.checkbox(
            "Include improvement suggestions",
            value=True,
            help="Generate actionable improvement recommendations"
        )
    
    # Quick Stats
    if 'evaluation' in st.session_state and st.session_state.evaluation:
        st.markdown("### 📊 Quick Stats")
        eval_data = st.session_state.evaluation
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Match Score", f"{eval_data.get('overall_match_percentage', 0)}%")
        with col2:
            requirements_met = sum(1 for req in eval_data.get('requirements_evaluation', {}).values() 
                                 if req.get('meets_requirement', False))
            total_requirements = len(eval_data.get('requirements_evaluation', {}))
            st.metric("Requirements Met", f"{requirements_met}/{total_requirements}")
    
    # Tips and Help
    with st.expander("💡 Pro Tips"):
        st.markdown("""
        **For Best Results:**
        - Use recent, well-formatted PDFs
        - Include relevant keywords from job posting
        - Quantify achievements with numbers
        - Keep resume updated and concise
        - Focus on skills mentioned in job description
        """)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <p style="color: #667eea; font-weight: 600;">
            Powered by Google Gemini AI
        </p>
    </div>
    """, unsafe_allow_html=True)

# Constants and Configuration
CHUNK_SIZE = 5000
SUPPORTED_FORMATS = ["pdf", "docx", "txt"]

# Enhanced utility functions
def extract_text_from_file(uploaded_file):
    """Extract text from various file formats"""
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            return extract_text_from_pdf(uploaded_file)
        elif file_extension == 'docx':
            return extract_text_from_docx(uploaded_file)
        elif file_extension == 'txt':
            return uploaded_file.getvalue().decode('utf-8')
        else:
            st.error(f"❌ Unsupported file format: {file_extension}")
            return None
    except Exception as e:
        st.error(f"❌ Error extracting text: {str(e)}")
        return None

def extract_text_from_pdf(uploaded_file):
    """Enhanced PDF text extraction"""
    text = ""
    try:
        pdf_file = BytesIO(uploaded_file.getvalue())
        reader = PyPDF2.PdfReader(pdf_file)
        
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
        
        return text.strip()
    except Exception as e:
        st.error(f"❌ PDF extraction error: {str(e)}")
        return None

def extract_text_from_docx(uploaded_file):
    """Extract text from DOCX files"""
    try:
        doc = Document(BytesIO(uploaded_file.getvalue()))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"❌ DOCX extraction error: {str(e)}")
        return None

def get_gemini_model():
    """Get the appropriate Gemini model with error handling"""
    try:
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        try:
            return genai.GenerativeModel('gemini-1.0-pro')
        except Exception as e:
            st.error(f"❌ Model initialization failed: {str(e)}")
            return None

def create_match_visualization(evaluation):
    """Create interactive match score visualization"""
    if not evaluation or 'requirements_evaluation' not in evaluation:
        return None
    
    # Prepare data for visualization
    requirements = []
    scores = []
    statuses = []
    
    for req, data in evaluation['requirements_evaluation'].items():
        requirements.append(req.replace('_', ' ').title())
        scores.append(data.get('match_score', 0))
        statuses.append('Meets' if data.get('meets_requirement', False) else 'Does not meet')
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    colors = ['#48bb78' if score >= 80 else '#ed8936' if score >= 50 else '#f56565' 
              for score in scores]
    
    fig.add_trace(go.Bar(
        y=requirements,
        x=scores,
        orientation='h',
        marker_color=colors,
        text=[f'{score}%' for score in scores],
        textposition='inside',
        hovertemplate='<b>%{y}</b><br>Score: %{x}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Requirements Match Analysis",
        xaxis_title="Match Score (%)",
        yaxis_title="Requirements",
        template="plotly_white",
        height=max(400, len(requirements) * 40),
        showlegend=False
    )
    
    return fig

def create_score_gauge(score):
    """Create a gauge chart for overall match score"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Overall Match Score"},
        delta = {'reference': 70},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 50], 'color': "#fee2e2"},
                {'range': [50, 75], 'color': "#fef9c3"},
                {'range': [75, 100], 'color': "#dcfce7"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=400, template="plotly_white")
    return fig

# Enhanced prompt building functions
def build_enhanced_extraction_prompt(chunk, sensitivity="Balanced"):
    """Build enhanced prompt for job requirements extraction"""
    sensitivity_instructions = {
        "Strict": "Focus only on explicitly stated requirements. Do not infer or assume requirements.",
        "Balanced": "Extract both explicit and reasonably implied requirements from context.",
        "Lenient": "Extract all possible requirements, including those that might be implied or preferred."
    }
    
    return f"""
You are an expert HR analyst specializing in job requirement extraction. 

ANALYSIS APPROACH: {sensitivity_instructions[sensitivity]}

From the following job description content, extract comprehensive job requirements including:
- Technical skills and competencies
- Years of experience (be specific about numbers)
- Educational requirements
- Certifications and licenses
- Soft skills and personal attributes
- Industry knowledge
- Tools and software proficiency
- Language requirements
- Travel or location requirements

Return a detailed JSON object with clear categorization:

{{
  "technical_skills": {{
    "programming_languages": ["skill1", "skill2"],
    "frameworks_tools": ["tool1", "tool2"],
    "databases": ["db1", "db2"]
  }},
  "experience_requirements": {{
    "years_required": "X years",
    "industry_experience": "specific industry",
    "role_experience": "specific role type"
  }},
  "education_requirements": {{
    "degree_level": "Bachelor's/Master's/PhD",
    "field_of_study": "specific field",
    "alternative_experience": "if degree not required"
  }},
  "certifications": ["cert1", "cert2"],
  "soft_skills": ["skill1", "skill2"],
  "additional_requirements": {{
    "languages": ["language1", "language2"],
    "travel": "travel percentage",
    "location": "location requirements"
  }}
}}

Text to analyze:
{chunk}
"""

def build_enhanced_evaluation_prompt(requirements_json, resume_text, sensitivity="Balanced", analysis_depth="Standard"):
    """Build enhanced evaluation prompt"""
    
    depth_instructions = {
        "Quick Scan": "Provide a quick assessment focusing on key matches and mismatches.",
        "Standard Analysis": "Provide a thorough analysis with detailed explanations for each requirement.",
        "Deep Analysis": "Conduct an exhaustive analysis including subtle matches, potential, and growth areas."
    }
    
    return f"""
You are a senior HR consultant and resume analyst with 15+ years of experience in talent acquisition.

ANALYSIS DEPTH: {depth_instructions[analysis_depth]}
MATCHING SENSITIVITY: {sensitivity}

Analyze the resume against the job requirements with the following methodology:

1. **Requirement Matching**: For each requirement, determine if the resume demonstrates it
2. **Evidence Assessment**: Look for specific examples, achievements, and keywords
3. **Experience Validation**: Verify experience claims match requirements
4. **Skill Evaluation**: Assess technical and soft skills comprehensively
5. **Potential Assessment**: Consider transferable skills and learning capacity

JOB REQUIREMENTS:
{json.dumps(requirements_json, indent=2)}

RESUME CONTENT:
{resume_text}

Provide comprehensive analysis in this JSON format:
{{
  "overall_match_percentage": 85,
  "confidence_level": "high/medium/low",
  "requirements_evaluation": {{
    "requirement_category": {{
      "overall_score": 80,
      "detailed_requirements": {{
        "specific_requirement": {{
          "meets_requirement": true/false,
          "match_score": 85,
          "evidence_found": ["evidence1", "evidence2"],
          "explanation": "detailed explanation",
          "confidence": "high/medium/low",
          "improvement_potential": "high/medium/low"
        }}
      }}
    }}
  }},
  "strengths": ["strength1", "strength2"],
  "gaps": ["gap1", "gap2"],
  "red_flags": ["flag1", "flag2"],
  "improvement_suggestions": {{
    "immediate": ["suggestion1", "suggestion2"],
    "medium_term": ["suggestion1", "suggestion2"],
    "long_term": ["suggestion1", "suggestion2"]
  }},
  "keyword_analysis": {{
    "matched_keywords": ["keyword1", "keyword2"],
    "missing_keywords": ["keyword1", "keyword2"],
    "keyword_density": "high/medium/low"
  }},
  "experience_analysis": {{
    "total_years_found": "X years",
    "relevant_experience": "X years",
    "experience_quality": "high/medium/low",
    "progression_evident": true/false
  }},
  "ats_compatibility": {{
    "score": 85,
    "issues": ["issue1", "issue2"],
    "recommendations": ["rec1", "rec2"]
  }},
  "competitive_assessment": {{
    "market_position": "strong/average/weak",
    "unique_selling_points": ["usp1", "usp2"],
    "differentiators": ["diff1", "diff2"]
  }},
  "summary": "comprehensive summary of the analysis"
}}

Focus on providing actionable insights and specific recommendations.
"""

def query_gemini_with_retry(prompt, max_retries=3):
    """Query Gemini API with retry logic"""
    if not gemini_api_key:
        st.error("❌ Please configure your Gemini API key first.")
        return None
    
    for attempt in range(max_retries):
        try:
            model = get_gemini_model()
            if not model:
                return None
                
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"⚠️ Attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
            else:
                st.error(f"❌ All attempts failed: {str(e)}")
                return None
    
    return None

def extract_enhanced_json(text):
    """Enhanced JSON extraction with better error handling"""
    try:
        # Try direct parsing first
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            # Clean the text and try again
            cleaned_text = re.sub(r'^```json\s*|```\s*$', '', text.strip())
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            try:
                # Try to find JSON within the text
                json_match = re.search(r'(\{.*\})', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                else:
                    st.error("❌ Could not extract valid JSON from response")
                    return None
            except Exception as e:
                st.error(f"❌ JSON parsing failed: {str(e)}")
                return None

# Enhanced main functions
def extract_job_requirements_enhanced(job_desc_text, sensitivity="Balanced"):
    """Enhanced job requirements extraction"""
    with st.spinner("🔍 Analyzing job description with AI..."):
        chunks = textwrap.wrap(job_desc_text, CHUNK_SIZE)
        
        # Create progress tracking
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        all_requirements = {}
        
        for i, chunk in enumerate(chunks):
            # Update progress
            progress = int((i / len(chunks)) * 100)
            progress_bar.progress(progress)
            status_text.text(f"Processing chunk {i+1} of {len(chunks)}...")
            
            # Process chunk
            prompt = build_enhanced_extraction_prompt(chunk, sensitivity)
            result = query_gemini_with_retry(prompt)
            
            if result:
                json_result = extract_enhanced_json(result)
                if json_result:
                    # Merge requirements intelligently
                    for category, items in json_result.items():
                        if category not in all_requirements:
                            all_requirements[category] = items
                        elif isinstance(items, dict):
                            all_requirements[category].update(items)
                        elif isinstance(items, list):
                            all_requirements[category].extend(items)
        
        # Complete progress
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        return all_requirements

def evaluate_resume_enhanced(requirements, resume_text, sensitivity="Balanced", analysis_depth="Standard"):
    """Enhanced resume evaluation"""
    with st.spinner("🧠 Conducting comprehensive resume analysis..."):
        prompt = build_enhanced_evaluation_prompt(requirements, resume_text, sensitivity, analysis_depth)
        result = query_gemini_with_retry(prompt)
        
        if result:
            return extract_enhanced_json(result)
        return None

# Session state initialization
for key in ['job_desc_text', 'requirements', 'resume_text', 'evaluation', 'current_step']:
    if key not in st.session_state:
        st.session_state[key] = None

if 'current_step' not in st.session_state:
    st.session_state.current_step = 0

# Show progress indicator
show_progress_indicator(st.session_state.current_step)

# Main application tabs
tabs = st.tabs([
    "📤 Job Description", 
    "📋 Requirements Analysis", 
    "📝 Resume Upload", 
    "📊 Comprehensive Results",
    "🎯 Resume Optimizer",
    "📈 Analytics Dashboard"
])

# Tab 1: Enhanced Job Description Upload
with tabs[0]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📑 Upload Job Description")
        st.markdown("Support for multiple formats: PDF, DOCX, TXT")
        
        uploaded_file = st.file_uploader(
            "Choose job description file",
            type=SUPPORTED_FORMATS,
            help="Upload the job posting in PDF, DOCX, or TXT format"
        )
        
        # Option to paste text directly
        st.markdown("**Or paste job description text:**")
        pasted_text = st.text_area(
            "Paste job description here",
            height=200,
            placeholder="Copy and paste the job description text here..."
        )
    
    with col2:
        st.markdown("### 🎯 Best Practices")
        st.info("""
        **For optimal results:**
        - Use the original job posting
        - Ensure text is clear and readable
        - Include complete job description
        - Check for any formatting issues
        """)
        
        if uploaded_file or pasted_text:
            st.success("✅ Job description ready for processing!")
    
    if uploaded_file or pasted_text:
        if st.button("🚀 Process Job Description", type="primary", use_container_width=True):
            with st.spinner("⏳ Extracting and analyzing job description..."):
                if uploaded_file:
                    job_desc_text = extract_text_from_file(uploaded_file)
                else:
                    job_desc_text = pasted_text
                
                if job_desc_text:
                    st.session_state.job_desc_text = job_desc_text
                    st.session_state.current_step = 1
                    st.success("✅ Job description processed successfully!")
                    
                    # Show preview with word count and key stats
                    with st.expander("📊 Job Description Analysis"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            word_count = len(job_desc_text.split())
                            st.metric("Word Count", word_count)
                        with col2:
                            char_count = len(job_desc_text)
                            st.metric("Characters", char_count)
                        with col3:
                            sentences = len([s for s in job_desc_text.split('.') if s.strip()])
                            st.metric("Sentences", sentences)
                        
                        st.text_area("Preview:", job_desc_text[:1000] + "..." if len(job_desc_text) > 1000 else job_desc_text, height=200)
                    
                    st.info("👉 Proceed to 'Requirements Analysis' tab")
                else:
                    st.error("❌ Failed to extract text from the file")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Enhanced Requirements Analysis
with tabs[1]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    if st.session_state.job_desc_text is None:
        st.info("📤 Please upload and process a job description first")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🧠 AI-Powered Requirements Extraction")
            st.markdown("Advanced analysis with customizable sensitivity levels")
            
            if st.button("🔍 Extract Requirements", type="primary", use_container_width=True):
                requirements = extract_job_requirements_enhanced(
                    st.session_state.job_desc_text, 
                    sensitivity
                )
                
                if requirements:
                    st.session_state.requirements = requirements
                    st.session_state.current_step = 2
                    st.success(f"✅ Successfully extracted requirements from {len(requirements)} categories!")
                    
                    # Enhanced requirements display
                    st.markdown("### 📋 Extracted Requirements")
                    
                    # Create tabs for different requirement categories
                    if requirements:
                        req_categories = list(requirements.keys())
                        req_tabs = st.tabs([cat.replace('_', ' ').title() for cat in req_categories])
                        
                        category_icons = {
                            'technical_skills': '💻',
                            'experience_requirements': '⏱️',
                            'education_requirements': '🎓',
                            'certifications': '📜',
                            'soft_skills': '🤝',
                            'additional_requirements': '➕'
                        }
                        
                        for i, (category, req_tab) in enumerate(zip(req_categories, req_tabs)):
                            with req_tab:
                                icon = category_icons.get(category, '📌')
                                st.markdown(f"### {icon} {category.replace('_', ' ').title()}")
                                
                                if isinstance(requirements[category], dict):
                                    for subcategory, items in requirements[category].items():
                                        st.markdown(f"**{subcategory.replace('_', ' ').title()}:**")
                                        if isinstance(items, list):
                                            for item in items:
                                                st.markdown(f"• {item}")
                                        else:
                                            st.markdown(f"• {items}")
                                elif isinstance(requirements[category], list):
                                    for item in requirements[category]:
                                        st.markdown(f"• {item}")
                                else:
                                    st.markdown(f"• {requirements[category]}")
                    
                    st.info("👉 Proceed to 'Resume Upload' tab")
                else:
                    st.error("❌ Failed to extract requirements")
        
        with col2:
            st.markdown("### ⚙️ Analysis Settings")
            st.info(f"""
            **Current Settings:**
            - Sensitivity: {sensitivity}
            - Analysis Depth: {analysis_depth}
            - Suggestions: {'Enabled' if include_suggestions else 'Disabled'}
            """)
            
            if st.session_state.requirements:
                st.markdown("### 📊 Quick Stats")
                total_reqs = sum(len(reqs) if isinstance(reqs, (list, dict)) else 1 
                               for reqs in st.session_state.requirements.values())
                st.metric("Total Requirements", total_reqs)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: Enhanced Resume Upload
with tabs[2]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    if st.session_state.requirements is None:
        st.info("📋 Please extract job requirements first")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📄 Upload Your Resume")
            st.markdown("Multiple format support with intelligent parsing")
            
            resume_file = st.file_uploader(
                "Choose your resume file",
                type=SUPPORTED_FORMATS,
                help="Upload your resume in PDF, DOCX, or TXT format"
            )
            
            # Option to paste resume text
            st.markdown("**Or paste your resume text:**")
            pasted_resume = st.text_area(
                "Paste resume text here",
                height=200,
                placeholder="Copy and paste your resume content here..."
            )
            
            if resume_file or pasted_resume:
                if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
                    with st.spinner("⏳ Processing and analyzing your resume..."):
                        if resume_file:
                            resume_text = extract_text_from_file(resume_file)
                        else:
                            resume_text = pasted_resume
                        
                        if resume_text:
                            st.session_state.resume_text = resume_text
                            
                            # Show resume stats
                            with st.expander("📊 Resume Analysis"):
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    word_count = len(resume_text.split())
                                    st.metric("Words", word_count)
                                with col2:
                                    char_count = len(resume_text)
                                    st.metric("Characters", char_count)
                                with col3:
                                    # Estimate reading time
                                    reading_time = max(1, word_count // 200)
                                    st.metric("Reading Time", f"{reading_time} min")
                                with col4:
                                    # Count potential keywords
                                    keywords = len(set(word.lower() for word in resume_text.split() 
                                                     if len(word) > 3 and word.isalpha()))
                                    st.metric("Unique Keywords", keywords)
                                
                                st.text_area("Resume Preview:", resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text, height=200)
                            
                            # Automatic evaluation
                            st.markdown("### 🧠 Conducting Analysis...")
                            evaluation = evaluate_resume_enhanced(
                                st.session_state.requirements,
                                resume_text,
                                sensitivity,
                                analysis_depth
                            )
                            
                            if evaluation:
                                st.session_state.evaluation = evaluation
                                st.session_state.current_step = 3
                                st.success("✅ Resume analysis completed!")
                                st.info("👉 View detailed results in 'Comprehensive Results' tab")
                            else:
                                st.error("❌ Failed to analyze resume")
                        else:
                            st.error("❌ Failed to extract text from resume")
        
        with col2:
            st.markdown("### 🎯 Resume Tips")
            st.info("""
            **Optimization Tips:**
            - Use keywords from job description
            - Quantify achievements
            - Include relevant skills
            - Keep format clean and ATS-friendly
            - Update for each application
            """)
            
            if st.session_state.resume_text:
                st.success("✅ Resume uploaded successfully!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 4: Comprehensive Results
with tabs[3]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    if st.session_state.evaluation is None:
        st.info("📝 Please complete the resume analysis first")
    else:
        evaluation = st.session_state.evaluation
        overall_score = evaluation.get('overall_match_percentage', 0)
        
        # Enhanced score display
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown(f"""
            <div class="score-display">
                <h2 style="margin: 0; color: white;">Overall Match Score</h2>
                <div class="score-number">{overall_score}%</div>
                <p style="margin: 0; font-size: 1.2rem;">
                    {'🌟 Excellent Match!' if overall_score >= 85 else 
                     '🎯 Strong Match!' if overall_score >= 70 else 
                     '👍 Good Match!' if overall_score >= 55 else 
                     '🔧 Needs Improvement'}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Key metrics dashboard
        st.markdown("### 📊 Key Metrics")
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            confidence = evaluation.get('confidence_level', 'medium').title()
            st.metric("Analysis Confidence", confidence)
        
        with metric_cols[1]:
            if 'requirements_evaluation' in evaluation:
                met_reqs = sum(1 for req_data in evaluation['requirements_evaluation'].values()
                              if isinstance(req_data, dict) and 
                              any(sub_req.get('meets_requirement', False) 
                                  for sub_req in req_data.get('detailed_requirements', {}).values()
                                  if isinstance(sub_req, dict)))
                total_reqs = len(evaluation['requirements_evaluation'])
                st.metric("Requirements Met", f"{met_reqs}/{total_reqs}")
        
        with metric_cols[2]:
            ats_score = evaluation.get('ats_compatibility', {}).get('score', 0)
            st.metric("ATS Compatibility", f"{ats_score}%")
        
        with metric_cols[3]:
            exp_analysis = evaluation.get('experience_analysis', {})
            relevant_exp = exp_analysis.get('relevant_experience', 'N/A')
            st.metric("Relevant Experience", relevant_exp)
        
        # Interactive visualizations
        st.markdown("### 📈 Visual Analysis")
        
        viz_cols = st.columns(2)
        
        with viz_cols[0]:
            # Gauge chart for overall score
            gauge_fig = create_score_gauge(overall_score)
            st.plotly_chart(gauge_fig, use_container_width=True)
        
        with viz_cols[1]:
            # Requirements breakdown chart
            match_fig = create_match_visualization(evaluation)
            if match_fig:
                st.plotly_chart(match_fig, use_container_width=True)
        
        # Detailed analysis sections
        analysis_tabs = st.tabs([
            "🎯 Strengths & Gaps", 
            "📋 Detailed Requirements", 
            "🔍 Keyword Analysis",
            "📊 Competitive Assessment"
        ])
        
        with analysis_tabs[0]:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💪 Key Strengths")
                strengths = evaluation.get('strengths', [])
                for strength in strengths:
                    st.markdown(f"✅ {strength}")
            
            with col2:
                st.markdown("### 🎯 Areas for Improvement")
                gaps = evaluation.get('gaps', [])
                for gap in gaps:
                    st.markdown(f"⚠️ {gap}")
            
            # Red flags section
            red_flags = evaluation.get('red_flags', [])
            if red_flags:
                st.markdown("### 🚨 Red Flags")
                for flag in red_flags:
                    st.error(f"🚨 {flag}")
        
        with analysis_tabs[1]:
            st.markdown("### 📋 Detailed Requirements Analysis")
            
            if 'requirements_evaluation' in evaluation:
                for category, category_data in evaluation['requirements_evaluation'].items():
                    with st.expander(f"📂 {category.replace('_', ' ').title()}"):
                        if isinstance(category_data, dict) and 'detailed_requirements' in category_data:
                            overall_score = category_data.get('overall_score', 0)
                            st.metric(f"{category.title()} Score", f"{overall_score}%")
                            
                            for req_name, req_data in category_data['detailed_requirements'].items():
                                if isinstance(req_data, dict):
                                    score = req_data.get('match_score', 0)
                                    meets = req_data.get('meets_requirement', False)
                                    
                                    # Color coding based on score
                                    if score >= 80:
                                        badge_class = "badge-excellent"
                                        icon = "✅"
                                    elif score >= 50:
                                        badge_class = "badge-good"
                                        icon = "⚠️"
                                    else:
                                        badge_class = "badge-poor"
                                        icon = "❌"
                                    
                                    st.markdown(f"""
                                    <div style="margin: 10px 0; padding: 15px; border-radius: 10px; background: {'#f0f9ff' if meets else '#fef2f2'};">
                                        <h4>{icon} {req_name.replace('_', ' ').title()}</h4>
                                        <span class="req-badge {badge_class}">{score}% Match</span>
                                        <p><strong>Evidence:</strong> {', '.join(req_data.get('evidence_found', []))}</p>
                                        <p><strong>Analysis:</strong> {req_data.get('explanation', 'No explanation available')}</p>
                                        <p><strong>Confidence:</strong> {req_data.get('confidence', 'N/A').title()}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
        
        with analysis_tabs[2]:
            st.markdown("### 🔍 Keyword Analysis")
            
            keyword_analysis = evaluation.get('keyword_analysis', {})
            
            kw_cols = st.columns(3)
            
            with kw_cols[0]:
                st.markdown("#### ✅ Matched Keywords")
                matched = keyword_analysis.get('matched_keywords', [])
                for keyword in matched:
                    st.markdown(f"• {keyword}")
            
            with kw_cols[1]:
                st.markdown("#### ❌ Missing Keywords")
                missing = keyword_analysis.get('missing_keywords', [])
                for keyword in missing:
                    st.markdown(f"• {keyword}")
            
            with kw_cols[2]:
                density = keyword_analysis.get('keyword_density', 'N/A')
                st.metric("Keyword Density", density.title())
        
        with analysis_tabs[3]:
            st.markdown("### 📊 Competitive Assessment")
            
            competitive = evaluation.get('competitive_assessment', {})
            
            comp_cols = st.columns(2)
            
            with comp_cols[0]:
                market_position = competitive.get('market_position', 'N/A')
                st.metric("Market Position", market_position.title())
                
                st.markdown("#### 🌟 Unique Selling Points")
                usps = competitive.get('unique_selling_points', [])
                for usp in usps:
                    st.markdown(f"⭐ {usp}")
            
            with comp_cols[1]:
                st.markdown("#### 🔥 Key Differentiators")
                differentiators = competitive.get('differentiators', [])
                for diff in differentiators:
                    st.markdown(f"🔥 {diff}")
        
        # Action items and recommendations
        st.markdown("### 🚀 Improvement Recommendations")
        
        improvements = evaluation.get('improvement_suggestions', {})
        
        if isinstance(improvements, dict):
            rec_tabs = st.tabs(["🏃 Immediate", "📅 Medium-term", "🎯 Long-term"])
            
            with rec_tabs[0]:
                immediate = improvements.get('immediate', [])
                for i, suggestion in enumerate(immediate, 1):
                    st.markdown(f"**{i}.** {suggestion}")
            
            with rec_tabs[1]:
                medium_term = improvements.get('medium_term', [])
                for i, suggestion in enumerate(medium_term, 1):
                    st.markdown(f"**{i}.** {suggestion}")
            
            with rec_tabs[2]:
                long_term = improvements.get('long_term', [])
                for i, suggestion in enumerate(long_term, 1):
                    st.markdown(f"**{i}.** {suggestion}")
        else:
            # Fallback for simple list format
            for i, suggestion in enumerate(improvements, 1):
                st.markdown(f"💡 **Recommendation {i}:** {suggestion}")
        
        # Summary
        st.markdown("### 📝 Executive Summary")
        summary = evaluation.get('summary', 'No summary available')
        st.info(summary)
        
        # Download options
        st.markdown("### 💾 Export Options")
        
        download_cols = st.columns(4)
        
        with download_cols[0]:
            if st.download_button(
                "📊 Download Full Analysis (JSON)",
                json.dumps(evaluation, indent=2),
                file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            ):
                st.success("✅ Analysis downloaded!")
        
        with download_cols[1]:
            # Create PDF report (simplified text version)
            pdf_report = f"""RESUME ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL MATCH SCORE: {overall_score}%

EXECUTIVE SUMMARY:
{summary}

KEY STRENGTHS:
{chr(10).join([f'• {s}' for s in evaluation.get('strengths', [])])}

AREAS FOR IMPROVEMENT:
{chr(10).join([f'• {g}' for g in evaluation.get('gaps', [])])}

IMMEDIATE ACTION ITEMS:
{chr(10).join([f'• {item}' for item in improvements.get('immediate', []) if isinstance(improvements, dict)])}
"""
            
            if st.download_button(
                "📄 Download Report (TXT)",
                pdf_report,
                file_name=f"resume_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            ):
                st.success("✅ Report downloaded!")
        
        with download_cols[2]:
            # CSV format for easy analysis
            if 'requirements_evaluation' in evaluation:
                csv_data = []
                for category, category_data in evaluation['requirements_evaluation'].items():
                    if isinstance(category_data, dict) and 'detailed_requirements' in category_data:
                        for req_name, req_data in category_data['detailed_requirements'].items():
                            if isinstance(req_data, dict):
                                csv_data.append({
                                    'Category': category,
                                    'Requirement': req_name,
                                    'Score': req_data.get('match_score', 0),
                                    'Meets_Requirement': req_data.get('meets_requirement', False),
                                    'Confidence': req_data.get('confidence', 'N/A')
                                })
                
                if csv_data:
                    df = pd.DataFrame(csv_data)
                    csv_string = df.to_csv(index=False)
                    
                    if st.download_button(
                        "📈 Download Data (CSV)",
                        csv_string,
                        file_name=f"resume_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    ):
                        st.success("✅ Data downloaded!")
        
        with download_cols[3]:
            if st.button("🔄 Restart Analysis"):
                for key in ['job_desc_text', 'requirements', 'resume_text', 'evaluation']:
                    st.session_state[key] = None
                st.session_state.current_step = 0
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 5: Resume Optimizer
with tabs[4]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 AI Resume Optimizer")
    
    if st.session_state.evaluation is None:
        st.info("📊 Complete the analysis first to access optimization features")
    else:
        st.markdown("#### 🚀 Optimization Tools")
        
        opt_cols = st.columns(2)
        
        with opt_cols[0]:
            if st.button("🔧 Generate Optimized Resume", type="primary"):
                with st.spinner("🧠 Creating optimized resume version..."):
                    # This would integrate with Gemini to create an optimized version
                    st.info("🔄 Feature coming soon! This will generate an optimized resume based on the analysis.")
        
        with opt_cols[1]:
            if st.button("📝 Generate Cover Letter", type="primary"):
                with st.spinner("✍️ Creating personalized cover letter..."):
                    st.info("🔄 Feature coming soon! This will generate a tailored cover letter.")
        
        # Keyword optimization suggestions
        st.markdown("#### 🔍 Keyword Optimization")
        
        if 'keyword_analysis' in st.session_state.evaluation:
            keyword_data = st.session_state.evaluation['keyword_analysis']
            
            missing_keywords = keyword_data.get('missing_keywords', [])
            if missing_keywords:
                st.markdown("**Consider adding these keywords to your resume:**")
                
                keyword_cols = st.columns(3)
                for i, keyword in enumerate(missing_keywords):
                    with keyword_cols[i % 3]:
                        st.markdown(f"• `{keyword}`")
        
        # Skills gap analysis
        st.markdown("#### 📈 Skills Development Plan")
        
        gaps = st.session_state.evaluation.get('gaps', [])
        if gaps:
            st.markdown("**Priority skills to develop:**")
            for i, gap in enumerate(gaps[:5], 1):  # Show top 5
                st.markdown(f"{i}. {gap}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 6: Analytics Dashboard
with tabs[5]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Analytics Dashboard")
    
    if st.session_state.evaluation is None:
        st.info("📊 Complete the analysis first to view analytics")
    else:
        # Create comprehensive analytics visualizations
        
        # Score breakdown pie chart
        if 'requirements_evaluation' in st.session_state.evaluation:
            scores_data = []
            categories = []
            
            for category, category_data in st.session_state.evaluation['requirements_evaluation'].items():
                if isinstance(category_data, dict):
                    score = category_data.get('overall_score', 0)
                    scores_data.append(score)
                    categories.append(category.replace('_', ' ').title())
            
            if scores_data:
                # Radar chart for skills
                fig_radar = go.Figure()
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=scores_data,
                    theta=categories,
                    fill='toself',
                    name='Your Profile',
                    line_color='#667eea'
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=True,
                    title="Skills Profile Analysis"
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
        
        # Historical tracking (placeholder for future feature)
        st.markdown("#### 📊 Performance Tracking")
        st.info("🔄 Historical tracking feature coming soon! Track your improvement over time.")
        
        # Benchmarking (placeholder)
        st.markdown("#### 🏆 Industry Benchmarking")
        st.info("🔄 Industry benchmarking coming soon! Compare your profile with industry standards.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced footer
st.markdown("""
<div class="footer">
    <h3>🚀 AI Resume Analyzer Pro</h3>
    <p style="color: #667eea; font-weight: 600; margin: 10px 0;">
        Engineered with ❤️ by Shreyas Kasture
    </p>
    <p style="color: #718096; font-size: 0.9rem;">
        Powered by Google Gemini AI • Enhanced UI/UX • Advanced Analytics
    </p>
    <div style="margin-top: 20px;">
        <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 8px 16px; border-radius: 20px; font-size: 0.8rem;">
            v2.0 - Enhanced Edition
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    pass
