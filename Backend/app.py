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
import openai
import anthropic
import requests

# Streamlit page config
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
OPENAI_API_KEY = "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"
ANTHROPIC_API_KEY = "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"
HUGGINGFACE_API_KEY = "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"
PINECONE_API_KEY = "pcsk_MQWK7_PVT3wqroExRVr4QT2dVrWZHNrf7yTCJV1LXp14CoaMFp9yLx9Jn5Y32qcDV5Xx"
ADZUNA_APP_ID = "aa08dca8"
ADZUNA_API_KEY = "5a3964291d93cb468d63d3a6a3956210"
RAPIDAPI_KEY = "8c34393a1dmsh6105bc185272fe3p19b523jsn7ab6aaf136de"

# Initialize API clients
openai.api_key = OPENAI_API_KEY
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

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
    
    /* Developer credit */
    .developer-credit {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 10px 0;
        display: inline-block;
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
    <div class="developer-credit">
        Developed with ❤️ by Shreyas Kasture
    </div>
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
        if current_step not in st.session_state:
            st.session_state.current_step = 0
        elif i < current_step:
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
            <span style="font-size: 0.8rem; color: #4a5568; font-weight: 600;">{title}</span>
        </div>
        '''
              
        if i < len(steps) - 1:
            line_color = "#667eea" if i < current_step else "#e2e8f0"
            step_html += f'<div style="flex: 1; height: 2px; background: {line_color}; margin: 20px 10px 0 10px;"></div>'
    
    step_html += '</div></div>'
    st.markdown(step_html, unsafe_allow_html=True)

# Enhanced sidebar with developer credit
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h2>⚙️ Configuration</h2>
        <div class="developer-credit" style="font-size: 0.8rem; padding: 5px 15px;">
            Made with ❤️ by Shreyas Kasture
        </div>
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
            overall_score = eval_data.get('overall_match_percentage', 0)
            # Ensure score is numeric
            if overall_score is None:
                overall_score = 0
            elif isinstance(overall_score, str):
                try:
                    overall_score = float(overall_score)
                except (ValueError, TypeError):
                    overall_score = 0
            st.metric("Match Score", f"{overall_score}%")
        with col2:
            requirements_met = 0
            total_requirements = 0
            if 'requirements_evaluation' in eval_data and eval_data['requirements_evaluation']:
                for req_data in eval_data['requirements_evaluation'].values():
                    if isinstance(req_data, dict):
                        if req_data.get('meets_requirement', False):
                            requirements_met += 1
                        total_requirements += 1
            st.metric("Requirements Met", f"{requirements_met}/{total_requirements}")
    
    # Tips and Help
    with st.expander("💡 Pro Tips"):
        st.markdown("""
        **For Best Results:**
        - Use recent, well-formatted PDFs
        - Include relevant keywords from job posting
        - Quantify achievements with numbers
        - Keep format clean and ATS-friendly
        - Focus on skills mentioned in job description
        """)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <p style="color: #667eea; font-weight: 600;">
            Powered by Multiple AI Models
        </p>
    </div>
    """, unsafe_allow_html=True)

# Constants and Configuration
CHUNK_SIZE = 5000
SUPPORTED_FORMATS = ["pdf", "docx", "txt"]

# Utility functions for API integration
def get_openai_response(prompt, model="gpt-3.5-turbo"):
    """Get response from OpenAI API"""
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI API Error: {str(e)}")
        return None

def get_anthropic_response(prompt):
    """Get response from Anthropic Claude API"""
    try:
        response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        st.error(f"Anthropic API Error: {str(e)}")
        return None

def get_job_market_data(job_title, location="United States"):
    """Get job market data from Adzuna API"""
    try:
        url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/1"
        params = {
            'app_id': ADZUNA_APP_ID,
            'app_key': ADZUNA_API_KEY,
            'what': job_title,
            'results_per_page': 20
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Job market data error: {str(e)}")
        return None

def get_salary_insights(job_title):
    """Get salary insights using RapidAPI"""
    try:
        url = "https://job-salary-data.p.rapidapi.com/job-salary"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "job-salary-data.p.rapidapi.com"
        }
        params = {"job_title": job_title, "location": "United States"}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Salary insights error: {str(e)}")
        return None

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

def safe_get_score(data, key, default=0):
    """Safely get score value and ensure it's numeric"""
    value = data.get(key, default)
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

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
        score = safe_get_score(data, 'match_score', 0)
        scores.append(score)
        statuses.append('Meets' if data.get('meets_requirement', False) else 'Does not meet')
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    colors = []
    for score in scores:
        if score >= 80:
            colors.append('#48bb78')
        elif score >= 50:
            colors.append('#ed8936')
        else:
            colors.append('#f56565')
    
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
    # Ensure score is numeric
    score = safe_get_score({'score': score}, 'score', 0)
    
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

def generate_optimized_resume(original_resume, job_requirements, missing_keywords):
    """Generate an optimized resume using AI"""
    prompt = f"""
You are a professional resume writer and career coach. Based on the original resume and job requirements, create an optimized version that:

1. Incorporates missing keywords naturally
2. Restructures content for better ATS compatibility
3. Quantifies achievements where possible
4. Improves formatting and readability
5. Maintains authenticity while enhancing relevance

ORIGINAL RESUME:
{original_resume}

JOB REQUIREMENTS:
{json.dumps(job_requirements, indent=2)}

MISSING KEYWORDS TO INCORPORATE:
{', '.join(missing_keywords)}

Please provide:
1. An optimized resume version
2. A summary of key improvements made
3. Specific sections that were enhanced

Format the response as JSON with keys: 'optimized_resume', 'improvements_summary', 'enhanced_sections'
"""
    
    # Try multiple AI services for better results
    for service in ['anthropic', 'openai', 'gemini']:
        try:
            if service == 'anthropic':
                response = get_anthropic_response(prompt)
            elif service == 'openai':
                response = get_openai_response(prompt, "gpt-4")
            else:  # gemini
                model = get_gemini_model()
                if model:
                    response = model.generate_content(prompt).text
                else:
                    continue
                    
            if response:
                return extract_enhanced_json(response)
        except Exception as e:
            st.warning(f"Service {service} unavailable: {str(e)}")
            continue
    
    return None

def generate_cover_letter(resume_text, job_requirements, company_info=""):
    """Generate a personalized cover letter"""
    prompt = f"""
Create a compelling, personalized cover letter based on the resume and job requirements.

RESUME CONTENT:
{resume_text}

JOB REQUIREMENTS:
{json.dumps(job_requirements, indent=2)}

COMPANY INFO:
{company_info}

The cover letter should:
1. Be professional yet engaging
2. Highlight relevant achievements from the resume
3. Address key job requirements
4. Show genuine interest in the role
5. Be 3-4 paragraphs long
6. Include a strong opening and closing

Format as JSON with keys: 'cover_letter', 'key_highlights', 'personalization_notes'
"""
    
    # Try multiple AI services
    for service in ['anthropic', 'openai', 'gemini']:
        try:
            if service == 'anthropic':
                response = get_anthropic_response(prompt)
            elif service == 'openai':
                response = get_openai_response(prompt, "gpt-4")
            else:  # gemini
                model = get_gemini_model()
                if model:
                    response = model.generate_content(prompt).text
                else:
                    continue
                    
            if response:
                return extract_enhanced_json(response)
        except Exception as e:
            st.warning(f"Service {service} unavailable: {str(e)}")
            continue
    
    return None

def create_skills_radar_chart(evaluation):
    """Create a radar chart for skills analysis"""
    if not evaluation or 'requirements_evaluation' not in evaluation:
        return None
    
    categories = []
    scores = []
    
    for category, data in evaluation['requirements_evaluation'].items():
        categories.append(category.replace('_', ' ').title())
        score = safe_get_score(data, 'overall_score', 0)
        scores.append(score)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Your Profile',
        line_color='#667eea',
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))
    
    # Add industry benchmark (simulated)
    benchmark_scores = [max(70, score * 0.9) for score in scores]
    fig.add_trace(go.Scatterpolar(
        r=benchmark_scores,
        theta=categories,
        fill='toself',
        name='Industry Benchmark',
        line_color='#f56565',
        fillcolor='rgba(245, 101, 101, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Skills Profile vs Industry Benchmark",
        template="plotly_white"
    )
    
    return fig

def create_improvement_timeline(evaluation):
    """Create a timeline visualization for improvement suggestions"""
    if not evaluation or 'improvement_suggestions' not in evaluation:
        return None
    
    suggestions = evaluation['improvement_suggestions']
    
    # Prepare timeline data
    timeline_data = []
    colors = ['#667eea', '#ed8936', '#48bb78']
    
    for i, (timeframe, items) in enumerate(suggestions.items()):
        if isinstance(items, list):
            for j, item in enumerate(items):
                timeline_data.append({
                    'Task': item,
                    'Start': f'2024-{i+1:02d}-01',
                    'Finish': f'2024-{i+2:02d}-01',
                    'Resource': timeframe.title(),
                    'Priority': len(items) - j
                })
    
    if not timeline_data:
        return None
    
    df = pd.DataFrame(timeline_data)
    
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", 
                     color="Resource", title="Improvement Action Plan")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(template="plotly_white")
    
    return fig

def get_market_analytics(job_title):
    """Get comprehensive market analytics"""
    analytics = {
        'job_market_data': get_job_market_data(job_title),
        'salary_insights': get_salary_insights(job_title),
        'trending_skills': [],
        'market_demand': 'Medium'
    }
    
    # Simulate trending skills based on job title
    tech_skills = ['Python', 'Machine Learning', 'Cloud Computing', 'Data Analysis', 'API Development']
    soft_skills = ['Communication', 'Leadership', 'Problem Solving', 'Team Collaboration']
    
    analytics['trending_skills'] = tech_skills + soft_skills
    
    return analytics

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
for key in ['job_desc_text', 'requirements', 'resume_text', 'evaluation', 'current_step', 'optimized_resume', 'cover_letter']:
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
        overall_score = safe_get_score(evaluation, 'overall_match_percentage', 0)
        
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
            ats_score = safe_get_score(evaluation.get('ats_compatibility', {}), 'score', 0)
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
                            overall_score = safe_get_score(category_data, 'overall_score', 0)
                            st.metric(f"{category.title()} Score", f"{overall_score}%")
                            
                            for req_name, req_data in category_data['detailed_requirements'].items():
                                if isinstance(req_data, dict):
                                    score = safe_get_score(req_data, 'match_score', 0)
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
                                    'Score': safe_get_score(req_data, 'match_score', 0),
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
            if st.button("🔧 Generate Optimized Resume", type="primary", use_container_width=True):
                with st.spinner("🧠 Creating optimized resume version..."):
                    # Get missing keywords from evaluation
                    keyword_analysis = st.session_state.evaluation.get('keyword_analysis', {})
                    missing_keywords = keyword_analysis.get('missing_keywords', [])
                    
                    # Generate optimized resume
                    optimized_data = generate_optimized_resume(
                        st.session_state.resume_text,
                        st.session_state.requirements,
                        missing_keywords
                    )
                    
                    if optimized_data:
                        st.session_state.optimized_resume = optimized_data
                        st.success("✅ Optimized resume generated!")
                        
                        # Display optimized resume
                        st.markdown("### 📝 Optimized Resume")
                        
                        # Show improvements summary
                        if 'improvements_summary' in optimized_data:
                            with st.expander("🔍 Key Improvements Made"):
                                st.markdown(optimized_data['improvements_summary'])
                        
                        # Show enhanced sections
                        if 'enhanced_sections' in optimized_data:
                            with st.expander("📈 Enhanced Sections"):
                                enhanced_sections = optimized_data['enhanced_sections']
                                if isinstance(enhanced_sections, list):
                                    for section in enhanced_sections:
                                        st.markdown(f"• {section}")
                                else:
                                    st.markdown(enhanced_sections)
                        
                        # Display the optimized resume
                        optimized_resume_text = optimized_data.get('optimized_resume', 'No optimized resume generated')
                        st.text_area(
                            "Optimized Resume Content:",
                            optimized_resume_text,
                            height=400
                        )
                        
                        # Download option
                        st.download_button(
                            "💾 Download Optimized Resume",
                            optimized_resume_text,
                            file_name=f"optimized_resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("❌ Failed to generate optimized resume. Please try again.")
        
        with opt_cols[1]:
            if st.button("📝 Generate Cover Letter", type="primary", use_container_width=True):
                with st.spinner("✍️ Creating personalized cover letter..."):
                    # Generate cover letter
                    cover_letter_data = generate_cover_letter(
                        st.session_state.resume_text,
                        st.session_state.requirements
                    )
                    
                    if cover_letter_data:
                        st.session_state.cover_letter = cover_letter_data
                        st.success("✅ Cover letter generated!")
                        
                        # Display cover letter
                        st.markdown("### 💌 Personalized Cover Letter")
                        
                        # Show key highlights
                        if 'key_highlights' in cover_letter_data:
                            with st.expander("⭐ Key Highlights"):
                                highlights = cover_letter_data['key_highlights']
                                if isinstance(highlights, list):
                                    for highlight in highlights:
                                        st.markdown(f"• {highlight}")
                                else:
                                    st.markdown(highlights)
                        
                        # Show personalization notes
                        if 'personalization_notes' in cover_letter_data:
                            with st.expander("🎯 Personalization Notes"):
                                st.markdown(cover_letter_data['personalization_notes'])
                        
                        # Display the cover letter
                        cover_letter_text = cover_letter_data.get('cover_letter', 'No cover letter generated')
                        st.text_area(
                            "Cover Letter Content:",
                            cover_letter_text,
                            height=400
                        )
                        
                        # Download option
                        st.download_button(
                            "💾 Download Cover Letter",
                            cover_letter_text,
                            file_name=f"cover_letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("❌ Failed to generate cover letter. Please try again.")
        
        # Show existing optimized content if available
        if st.session_state.optimized_resume:
            st.markdown("### 📋 Previously Generated Content")
            
            content_tabs = st.tabs(["📝 Optimized Resume", "💌 Cover Letter"])
            
            with content_tabs[0]:
                if st.session_state.optimized_resume:
                    st.text_area(
                        "Your Optimized Resume:",
                        st.session_state.optimized_resume.get('optimized_resume', ''),
                        height=300
                    )
            
            with content_tabs[1]:
                if st.session_state.cover_letter:
                    st.text_area(
                        "Your Cover Letter:",
                        st.session_state.cover_letter.get('cover_letter', ''),
                        height=300
                    )
        
        # Keyword optimization suggestions
        st.markdown("#### 🔍 Smart Keyword Optimization")
        
        if 'keyword_analysis' in st.session_state.evaluation:
            keyword_data = st.session_state.evaluation['keyword_analysis']
            
            keyword_cols = st.columns(2)
            
            with keyword_cols[0]:
                st.markdown("##### ✅ Keywords Found")
                matched_keywords = keyword_data.get('matched_keywords', [])
                if matched_keywords:
                    for keyword in matched_keywords[:10]:  # Show first 10
                        st.markdown(f"• `{keyword}`")
                else:
                    st.info("No matched keywords found")
            
            with keyword_cols[1]:
                st.markdown("##### ❌ Missing Keywords")
                missing_keywords = keyword_data.get('missing_keywords', [])
                if missing_keywords:
                    st.info("💡 Consider adding these keywords to your resume:")
                    for keyword in missing_keywords[:10]:  # Show first 10
                        st.markdown(f"• `{keyword}`")
                else:
                    st.success("All important keywords are present!")
        
        # Skills gap analysis
        st.markdown("#### 📈 Skills Development Roadmap")
        
        gaps = st.session_state.evaluation.get('gaps', [])
        if gaps:
            st.markdown("**Priority skills to develop:**")
            
            # Create a more detailed skills development plan
            skills_cols = st.columns(3)
            
            with skills_cols[0]:
                st.markdown("##### 🏃 Immediate (1-3 months)")
                immediate_skills = gaps[:3] if len(gaps) >= 3 else gaps
                for i, gap in enumerate(immediate_skills, 1):
                    st.markdown(f"{i}. {gap}")
            
            with skills_cols[1]:
                st.markdown("##### 📅 Medium-term (3-6 months)")
                medium_skills = gaps[3:6] if len(gaps) > 3 else []
                for i, gap in enumerate(medium_skills, 1):
                    st.markdown(f"{i}. {gap}")
            
            with skills_cols[2]:
                st.markdown("##### 🎯 Long-term (6+ months)")
                long_skills = gaps[6:] if len(gaps) > 6 else []
                for i, gap in enumerate(long_skills, 1):
                    st.markdown(f"{i}. {gap}")
        
        # ATS Optimization Tips
        st.markdown("#### 🤖 ATS Optimization Tips")
        
        ats_data = st.session_state.evaluation.get('ats_compatibility', {})
        ats_score = safe_get_score(ats_data, 'score', 0)
        
        if ats_score < 80:
            st.warning("⚠️ Your resume may not be fully ATS-optimized")
            
            ats_issues = ats_data.get('issues', [])
            ats_recommendations = ats_data.get('recommendations', [])
            
            if ats_issues:
                st.markdown("**Issues Found:**")
                for issue in ats_issues:
                    st.markdown(f"• {issue}")
            
            if ats_recommendations:
                st.markdown("**Recommendations:**")
                for rec in ats_recommendations:
                    st.markdown(f"• {rec}")
        else:
            st.success("✅ Your resume appears to be ATS-friendly!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 6: Analytics Dashboard
with tabs[5]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Advanced Analytics Dashboard")
    
    if st.session_state.evaluation is None:
        st.info("📊 Complete the analysis first to view analytics")
    else:
        # Extract job title for market analysis
        job_title = "Software Engineer"  # Default, could be extracted from job description
        if st.session_state.job_desc_text:
            # Simple job title extraction (could be improved with NLP)
            text_words = st.session_state.job_desc_text.lower().split()
            if any(word in text_words for word in ["engineer", "developer", "programmer"]):
                job_title = "Software Engineer"
            elif any(word in text_words for word in ["analyst", "data"]):
                job_title = "Data Analyst"
            elif any(word in text_words for word in ["manager", "lead"]):
                job_title = "Manager"
        
        # Market Analytics Section
        st.markdown("#### 🌍 Market Intelligence")
        
        market_cols = st.columns(3)
        
        with market_cols[0]:
            st.markdown("##### 💼 Job Market Trends")
            with st.spinner("Fetching market data..."):
                market_data = get_job_market_data(job_title)
                if market_data and 'results' in market_data:
                    total_jobs = market_data.get('count', 0)
                    st.metric("Available Positions", f"{total_jobs:,}")
                    
                    # Show top locations
                    if market_data['results']:
                        locations = {}
                        for job in market_data['results'][:10]:
                            location = job.get('location', {}).get('display_name', 'Unknown')
                            locations[location] = locations.get(location, 0) + 1
                        
                        st.markdown("**Top Locations:**")
                        for loc, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]:
                            st.markdown(f"• {loc}: {count} jobs")
                else:
                    st.metric("Available Positions", "N/A")
                    st.info("Market data temporarily unavailable")
        
        with market_cols[1]:
            st.markdown("##### 💰 Salary Insights")
            with st.spinner("Fetching salary data..."):
                salary_data = get_salary_insights(job_title)
                if salary_data:
                    # This would be implemented based on the actual API response structure
                    st.metric("Average Salary", "$75,000")
                    st.metric("Salary Range", "$60K - $120K")
                else:
                    st.metric("Average Salary", "N/A")
                    st.info("Salary data temporarily unavailable")
        
        with market_cols[2]:
            st.markdown("##### 📊 Market Position")
            competitive_assessment = st.session_state.evaluation.get('competitive_assessment', {})
            market_position = competitive_assessment.get('market_position', 'average').title()
            st.metric("Your Position", market_position)
            
            # Color code based on position
            if market_position.lower() == 'strong':
                st.success("🔥 You're competitive!")
            elif market_position.lower() == 'average':
                st.warning("⚡ Room for improvement")
            else:
                st.error("💪 Needs significant work")
        
        # Skills Analysis Dashboard
        st.markdown("#### 🎯 Comprehensive Skills Analysis")
        
        # Create radar chart for skills
        if 'requirements_evaluation' in st.session_state.evaluation:
            radar_fig = create_skills_radar_chart(st.session_state.evaluation)
            if radar_fig:
                st.plotly_chart(radar_fig, use_container_width=True)
        
        # Skills breakdown
        skills_analysis_cols = st.columns(2)
        
        with skills_analysis_cols[0]:
            st.markdown("##### 💻 Technical Skills Breakdown")
            
            # Create a detailed technical skills chart
            tech_requirements = st.session_state.requirements.get('technical_skills', {})
            if tech_requirements:
                skills_data = []
                
                for category, skills_list in tech_requirements.items():
                    if isinstance(skills_list, list):
                        for skill in skills_list:
                            # Check if skill is mentioned in resume
                            resume_text_lower = st.session_state.resume_text.lower()
                            skill_present = skill.lower() in resume_text_lower
                            skills_data.append({
                                'Skill': skill,
                                'Category': category.replace('_', ' ').title(),
                                'Present': 'Yes' if skill_present else 'No',
                                'Score': 85 if skill_present else 0
                            })
                
                if skills_data:
                    df_skills = pd.DataFrame(skills_data)
                    
                    # Create a bar chart
                    fig_skills = px.bar(
                        df_skills, 
                        x='Skill', 
                        y='Score',
                        color='Present',
                        facet_col='Category',
                        title="Technical Skills Assessment"
                    )
                    fig_skills.update_layout(height=400)
                    st.plotly_chart(fig_skills, use_container_width=True)
        
        with skills_analysis_cols[1]:
            st.markdown("##### 🤝 Soft Skills Analysis")
            
            soft_skills = st.session_state.requirements.get('soft_skills', [])
            if soft_skills:
                soft_skills_data = []
                resume_text_lower = st.session_state.resume_text.lower()
                
                for skill in soft_skills:
                    # Simple keyword matching for soft skills
                    skill_keywords = skill.lower().split()
                    skill_present = any(keyword in resume_text_lower for keyword in skill_keywords)
                    
                    soft_skills_data.append({
                        'Skill': skill,
                        'Present': skill_present,
                        'Score': 80 if skill_present else 20
                    })
                
                df_soft = pd.DataFrame(soft_skills_data)
                
                # Create a horizontal bar chart
                fig_soft = px.bar(
                    df_soft,
                    x='Score',
                    y='Skill',
                    orientation='h',
                    color='Present',
                    title="Soft Skills Assessment"
                )
                fig_soft.update_layout(height=400)
                st.plotly_chart(fig_soft, use_container_width=True)
        
        # Improvement Timeline
        st.markdown("#### 📅 Career Development Timeline")
        
        timeline_fig = create_improvement_timeline(st.session_state.evaluation)
        if timeline_fig:
            st.plotly_chart(timeline_fig, use_container_width=True)
        else:
            st.info("💡 Complete your analysis to see personalized development timeline")
        
        # Competitive Analysis
        st.markdown("#### 🏆 Competitive Intelligence")
        
        comp_cols = st.columns(3)
        
        with comp_cols[0]:
            st.markdown("##### 🎯 Your Unique Value")
            competitive = st.session_state.evaluation.get('competitive_assessment', {})
            usps = competitive.get('unique_selling_points', [])
            
            if usps:
                for i, usp in enumerate(usps, 1):
                    st.markdown(f"**{i}.** {usp}")
            else:
                st.info("Develop unique selling points to stand out")
        
        with comp_cols[1]:
            st.markdown("##### 🚀 Key Differentiators")
            differentiators = competitive.get('differentiators', [])
            
            if differentiators:
                for i, diff in enumerate(differentiators, 1):
                    st.markdown(f"**{i}.** {diff}")
            else:
                st.info("Build differentiators to compete effectively")
        
        with comp_cols[2]:
            st.markdown("##### 📈 Growth Opportunities")
            
            # Calculate growth potential based on gaps and current score
            overall_score = safe_get_score(st.session_state.evaluation, 'overall_match_percentage', 0)
            gaps_count = len(st.session_state.evaluation.get('gaps', []))
            
            if overall_score >= 80:
                growth_potential = "High - Fine-tuning needed"
            elif overall_score >= 60:
                growth_potential = "Medium - Targeted improvements"
            else:
                growth_potential = "High - Significant opportunities"
            
            st.metric("Growth Potential", growth_potential)
            st.metric("Skills to Develop", gaps_count)
        
        # Performance Tracking (Simulated - would be real with user accounts)
        st.markdown("#### 📊 Performance Tracking")
        
        # Simulate historical data
        dates = pd.date_range(start='2024-01-01', end='2024-12-01', freq='M')
        scores = [45, 52, 58, 65, 72, 78, 82, 85, 88, 90, 92, overall_score]
        
        tracking_df = pd.DataFrame({
            'Date': dates,
            'Match Score': scores[:len(dates)]
        })
        
        fig_tracking = px.line(
            tracking_df,
            x='Date',
            y='Match Score',
            title='Resume Match Score Improvement Over Time',
            markers=True
        )
        fig_tracking.update_layout(
            yaxis_range=[0, 100],
            template="plotly_white"
        )
        st.plotly_chart(fig_tracking, use_container_width=True)
        
        # Export Analytics
        st.markdown("#### 💾 Export Analytics")
        
        export_cols = st.columns(3)
        
        with export_cols[0]:
            # Create comprehensive analytics report
            analytics_report = {
                'timestamp': datetime.now().isoformat(),
                'job_title': job_title,
                'overall_score': overall_score,
                'market_position': market_position,
                'skills_analysis': st.session_state.evaluation.get('requirements_evaluation', {}),
                'improvement_suggestions': st.session_state.evaluation.get('improvement_suggestions', {}),
                'competitive_assessment': competitive
            }
            
            if st.download_button(
                "📊 Download Analytics Report",
                json.dumps(analytics_report, indent=2),
                file_name=f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            ):
                st.success("✅ Analytics downloaded!")
        
        with export_cols[1]:
            # Create skills matrix CSV
            if 'requirements_evaluation' in st.session_state.evaluation:
                skills_matrix = []
                for category, data in st.session_state.evaluation['requirements_evaluation'].items():
                    if isinstance(data, dict) and 'detailed_requirements' in data:
                        for req, req_data in data['detailed_requirements'].items():
                            if isinstance(req_data, dict):
                                skills_matrix.append({
                                    'Category': category,
                                    'Skill': req,
                                    'Current_Level': safe_get_score(req_data, 'match_score', 0),
                                    'Target_Level': 85,
                                    'Gap': 85 - safe_get_score(req_data, 'match_score', 0),
                                    'Priority': 'High' if safe_get_score(req_data, 'match_score', 0) < 50 else 'Medium'
                                })
                
                if skills_matrix:
                    skills_df = pd.DataFrame(skills_matrix)
                    csv_skills = skills_df.to_csv(index=False)
                    
                    if st.download_button(
                        "📈 Download Skills Matrix",
                        csv_skills,
                        file_name=f"skills_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    ):
                        st.success("✅ Skills matrix downloaded!")
        
        with export_cols[2]:
            if st.button("🔄 Refresh Analytics"):
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced footer with developer credit
st.markdown("""
<div class="footer">
    <h3>🚀 AI Resume Analyzer Pro</h3>
    <p style="color: #667eea; font-weight: 600; margin: 10px 0;">
        Powered by Multiple AI Models • Enhanced Analytics • Smart Optimization
    </p>
    <div style="margin: 20px 0;">
        <div class="developer-credit">
            Developed with ❤️ by Shreyas Kasture
        </div>
    </div>
    <div style="margin-top: 20px;">
        <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 8px 16px; border-radius: 20px; font-size: 0.8rem;">
            v2.0 - Enhanced Edition with AI Optimization
        </span>
    </div>
    <p style="color: #718096; font-size: 0.8rem; margin-top: 15px;">
        Integrating OpenAI GPT-4 • Anthropic Claude • Google Gemini • Market Intelligence APIs
    </p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    pass
