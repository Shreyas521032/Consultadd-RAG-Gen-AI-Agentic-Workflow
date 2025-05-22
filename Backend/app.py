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
import docx
from docx import Document

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
    
    /* Sample documents section */
    .sample-docs {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
    }
    
    .sample-docs h4 {
        color: white;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# App title with emojis
st.title("🚀 Enhanced Resume Job Match Checker 📝")

# App description with emojis
st.markdown("""
### 🔍 Find out if your resume matches the job requirements! 💯

This enhanced app supports **PDF, DOC, DOCX, and TXT** files and evaluates 
whether your resume meets job requirements with advanced AI analysis! 🎯

**New Features**: Multi-format support | Sample documents | Enhanced analytics
""")

# Sample Documents Data
SAMPLE_JOB_DESCRIPTIONS = {
    "Software Engineer - Tech Startup": """
Job Title: Senior Software Engineer
Company: TechFlow Innovations

Job Description:
We are seeking a passionate Senior Software Engineer to join our dynamic team at TechFlow Innovations. As a key member of our engineering team, you will be responsible for designing, developing, and maintaining scalable web applications and services.

Key Responsibilities:
• Design and develop high-quality, scalable web applications using modern technologies
• Collaborate with cross-functional teams including product managers, designers, and other engineers
• Write clean, maintainable, and well-documented code
• Participate in code reviews and provide constructive feedback
• Mentor junior developers and contribute to team knowledge sharing
• Troubleshoot and debug applications to optimize performance
• Stay updated with latest technology trends and best practices

Required Qualifications:
• Bachelor's degree in Computer Science, Software Engineering, or related field
• 5+ years of professional software development experience
• Strong proficiency in JavaScript, Python, or Java
• Experience with modern web frameworks (React, Angular, Vue.js, Django, or Spring)
• Solid understanding of database design and SQL
• Experience with cloud platforms (AWS, Azure, or GCP)
• Knowledge of containerization technologies (Docker, Kubernetes)
• Experience with version control systems (Git)
• Strong problem-solving and analytical skills
• Excellent communication and teamwork abilities

Preferred Qualifications:
• Master's degree in Computer Science or related field
• Experience with microservices architecture
• Knowledge of DevOps practices and CI/CD pipelines
• Experience with NoSQL databases (MongoDB, Redis)
• Familiarity with machine learning frameworks
• Agile/Scrum development experience
• Open source contributions

What We Offer:
• Competitive salary and equity package
• Comprehensive health, dental, and vision insurance
• Flexible work arrangements and remote work options
• Professional development opportunities
• Modern office environment with latest technology
• Team building events and company retreats

Location: San Francisco, CA (Hybrid)
Employment Type: Full-time
Salary Range: $120,000 - $180,000 annually
""",

    "Data Scientist - Healthcare": """
Job Title: Senior Data Scientist - Healthcare Analytics
Company: MedAnalytics Solutions

Job Description:
MedAnalytics Solutions is looking for an experienced Data Scientist to join our healthcare analytics team. You will work on cutting-edge projects that directly impact patient outcomes and healthcare efficiency.

Key Responsibilities:
• Develop and implement machine learning models for healthcare predictive analytics
• Analyze large-scale healthcare datasets to identify patterns and insights
• Collaborate with clinical teams to understand business requirements
• Design and execute A/B tests to measure intervention effectiveness
• Build automated reporting and dashboard solutions
• Present findings to stakeholders including C-level executives
• Ensure compliance with healthcare data privacy regulations (HIPAA)

Required Qualifications:
• PhD or Master's degree in Data Science, Statistics, Computer Science, or related quantitative field
• 4+ years of experience in data science or analytics roles
• Strong proficiency in Python and R for data analysis
• Experience with machine learning libraries (scikit-learn, TensorFlow, PyTorch)
• Expertise in SQL and database management
• Experience with statistical analysis and hypothesis testing
• Knowledge of healthcare data standards (HL7, FHIR)
• Strong data visualization skills (Tableau, Power BI, or similar)
• Experience with cloud platforms (AWS, Azure, GCP)
• Understanding of healthcare regulations and compliance requirements

Preferred Qualifications:
• Experience in healthcare or life sciences industry
• Knowledge of clinical workflows and electronic health records (EHR)
• Experience with big data technologies (Spark, Hadoop)
• Publications in peer-reviewed journals
• Experience with natural language processing (NLP)
• Familiarity with clinical trial design and analysis
• Knowledge of epidemiology and biostatistics

What We Offer:
• Competitive salary: $130,000 - $200,000
• Comprehensive benefits package
• Opportunity to make a real impact on healthcare outcomes
• Conference attendance and continuing education support
• Collaborative research environment
• Flexible work arrangements

Location: Boston, MA / Remote
Employment Type: Full-time
""",

    "Marketing Manager - E-commerce": """
Job Title: Digital Marketing Manager
Company: ShopSmart E-commerce

Job Description:
ShopSmart E-commerce is seeking a dynamic Digital Marketing Manager to drive our online marketing strategy and accelerate business growth. You'll lead multi-channel marketing campaigns and optimize customer acquisition strategies.

Key Responsibilities:
• Develop and execute comprehensive digital marketing strategies across multiple channels
• Manage paid advertising campaigns (Google Ads, Facebook, Instagram, TikTok)
• Optimize conversion funnels and improve customer acquisition costs
• Lead email marketing campaigns and marketing automation
• Analyze marketing metrics and ROI to optimize campaign performance
• Collaborate with content team to create engaging marketing materials
• Manage marketing budget and allocate resources effectively
• Stay current with digital marketing trends and emerging platforms
• A/B test marketing campaigns and landing pages
• Work with cross-functional teams including sales, product, and customer service

Required Qualifications:
• Bachelor's degree in Marketing, Business, Communications, or related field
• 3+ years of digital marketing experience, preferably in e-commerce
• Proven experience with Google Ads, Facebook Ads Manager, and other paid platforms
• Strong analytical skills and experience with marketing analytics tools
• Experience with email marketing platforms (Mailchimp, Klaviyo, SendGrid)
• Knowledge of SEO/SEM best practices
• Proficiency in Google Analytics, Google Tag Manager
• Experience with A/B testing and conversion optimization
• Strong project management and organizational skills
• Excellent written and verbal communication skills

Preferred Qualifications:
• Google Ads and Facebook Blueprint certifications
• Experience with marketing automation platforms (HubSpot, Marketo)
• Knowledge of customer segmentation and personalization strategies
• Experience with influencer marketing and affiliate programs
• Familiarity with e-commerce platforms (Shopify, WooCommerce, Magento)
• Basic knowledge of HTML/CSS and web development
• Experience with customer retention strategies
• Data visualization skills (Tableau, Power BI)

What We Offer:
• Salary: $70,000 - $95,000 plus performance bonuses
• Health, dental, and vision insurance
• Employee discount on all products
• Professional development budget
• Flexible PTO policy
• Remote work options
• Modern office with game room and free snacks

Location: Austin, TX / Hybrid
Employment Type: Full-time
"""
}

SAMPLE_RESUMES = {
    "Software Engineer Resume": """
JOHN SMITH
Senior Software Engineer
Email: john.smith@email.com | Phone: (555) 123-4567
LinkedIn: linkedin.com/in/johnsmith | GitHub: github.com/johnsmith
Location: San Francisco, CA

PROFESSIONAL SUMMARY
Experienced Senior Software Engineer with 6+ years of expertise in full-stack web development, cloud architecture, and team leadership. Proven track record of building scalable applications serving millions of users and mentoring development teams. Passionate about clean code, modern technologies, and delivering high-quality software solutions.

TECHNICAL SKILLS
Programming Languages: JavaScript, Python, Java, TypeScript, Go
Frontend: React, Angular, Vue.js, HTML5, CSS3, Redux, Next.js
Backend: Node.js, Django, Spring Boot, Express.js, FastAPI
Databases: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch
Cloud & DevOps: AWS (EC2, S3, Lambda, RDS), Docker, Kubernetes, Jenkins, GitLab CI/CD
Tools & Technologies: Git, Linux, REST APIs, GraphQL, Microservices, Agile/Scrum

PROFESSIONAL EXPERIENCE

Senior Software Engineer | TechCorp Solutions | March 2021 - Present
• Lead development of customer-facing web applications serving 2M+ daily active users
• Architected and implemented microservices infrastructure reducing system downtime by 40%
• Mentored team of 4 junior developers, improving code quality and delivery speed by 30%
• Collaborated with product managers and designers to define technical requirements
• Implemented automated testing strategies increasing code coverage from 60% to 95%
• Optimized database queries and caching strategies, improving application performance by 50%

Software Engineer | StartupFlow Inc. | June 2019 - February 2021
• Developed RESTful APIs and frontend components for B2B SaaS platform
• Built real-time data processing pipelines using Python and Apache Kafka
• Integrated third-party payment systems and authentication services
• Participated in code reviews and contributed to engineering best practices
• Worked in Agile environment with 2-week sprint cycles
• Reduced API response times by 35% through code optimization and caching

Junior Software Developer | WebSolutions LLC | August 2018 - May 2019
• Developed responsive web applications using React and Node.js
• Worked with senior developers to implement new features and fix bugs
• Participated in daily standups and sprint planning meetings
• Contributed to open-source projects and internal tool development
• Learned modern development practices including TDD and continuous integration

EDUCATION
Bachelor of Science in Computer Science | University of California, Berkeley | 2018
Relevant Coursework: Data Structures, Algorithms, Database Systems, Software Engineering

PROJECTS
E-Commerce Platform (Personal Project)
• Built full-stack e-commerce application using React, Node.js, and PostgreSQL
• Implemented user authentication, payment processing, and order management
• Deployed on AWS with automated CI/CD pipeline using GitHub Actions

Open Source Contributions
• Contributor to React Router with 3 merged pull requests
• Maintainer of popular npm package with 10k+ weekly downloads
• Active participant in local tech meetups and hackathons

CERTIFICATIONS
• AWS Certified Solutions Architect - Associate (2022)
• Certified Kubernetes Administrator (CKA) (2021)
• Google Cloud Professional Cloud Architect (2020)

ACHIEVEMENTS
• Led team that won "Best Innovation" award at company hackathon
• Increased application performance by 60% through architectural improvements
• Reduced deployment time from 2 hours to 15 minutes through automation
""",

    "Data Scientist Resume": """
DR. SARAH CHEN
Senior Data Scientist - Healthcare Analytics
Email: sarah.chen@email.com | Phone: (555) 987-6543
LinkedIn: linkedin.com/in/sarahchen | Portfolio: sarahchen-portfolio.com
Location: Boston, MA

PROFESSIONAL SUMMARY
Experienced Data Scientist with 5+ years specializing in healthcare analytics and machine learning. PhD in Biostatistics with proven expertise in predictive modeling, clinical data analysis, and regulatory compliance. Published researcher with strong background in statistical analysis and healthcare domain knowledge.

TECHNICAL SKILLS
Programming: Python, R, SQL, SAS, MATLAB
Machine Learning: scikit-learn, TensorFlow, PyTorch, XGBoost, Keras
Data Analysis: pandas, NumPy, SciPy, dplyr, ggplot2
Visualization: Tableau, Power BI, Matplotlib, Seaborn, Plotly
Databases: PostgreSQL, MySQL, MongoDB, Snowflake
Cloud Platforms: AWS (SageMaker, EC2, S3), Azure Machine Learning, GCP
Healthcare Standards: HL7, FHIR, DICOM, ICD-10, CPT
Other: Git, Docker, Jupyter, Apache Spark, Hadoop

PROFESSIONAL EXPERIENCE

Senior Data Scientist | HealthTech Analytics | January 2022 - Present
• Developed predictive models for patient readmission risk, achieving 87% accuracy and reducing readmissions by 15%
• Built automated reporting dashboards for clinical teams using Tableau and Python
• Led cross-functional team of 6 members on $2M population health management project
• Implemented HIPAA-compliant data processing pipelines for 500K+ patient records
• Collaborated with physicians and nurses to translate clinical needs into data solutions
• Published 3 peer-reviewed papers on healthcare predictive analytics

Data Scientist | MedResearch Institute | June 2020 - December 2021
• Analyzed electronic health records (EHR) data for clinical trial optimization
• Developed natural language processing models for clinical note analysis
• Created statistical models for drug efficacy studies and FDA submissions
• Designed and executed A/B tests for digital health interventions
• Mentored 2 junior data scientists and established best practices for team
• Reduced data processing time by 50% through automation and optimization

Biostatistician | Clinical Trials Corp | August 2019 - May 2020
• Performed statistical analysis for Phase II and Phase III clinical trials
• Designed sample size calculations and randomization schemes
• Created regulatory-compliant statistical analysis plans (SAPs)
• Collaborated with biostatistics team on FDA and EMA submissions
• Developed R packages for internal statistical analysis workflows

Research Assistant | Harvard Medical School | September 2017 - July 2019
• Conducted biostatistical analysis for epidemiological studies
• Published research on healthcare disparities and population health
• Presented findings at American Statistical Association conferences
• Mentored undergraduate students in statistical methods

EDUCATION
PhD in Biostatistics | Harvard School of Public Health | 2019
Dissertation: "Machine Learning Approaches for Precision Medicine in Cardiovascular Disease"
GPA: 3.9/4.0

Master of Science in Statistics | Stanford University | 2017
Bachelor of Science in Mathematics | UC Berkeley | 2015, Magna Cum Laude

PUBLICATIONS & RESEARCH
• "Predictive Modeling for Hospital Readmission Risk" - Journal of Medical Internet Research (2023)
• "Machine Learning in Clinical Decision Support" - Healthcare Management Review (2022)
• "Natural Language Processing for Clinical Documentation" - AMIA Conference Proceedings (2021)
• h-index: 12, Total citations: 450+

CERTIFICATIONS & TRAINING
• Certified Clinical Data Manager (CCDM) - 2021
• AWS Certified Machine Learning - Specialty - 2022
• SAS Certified Clinical Trials Programmer - 2020
• CITI Program: Human Subjects Research - Current

PROJECTS
COVID-19 Severity Prediction Model
• Developed machine learning model predicting COVID-19 severity using lab values and vital signs
• Achieved 0.85 AUC score and deployed in hospital setting
• Model used to guide resource allocation and patient triage decisions

Healthcare Fraud Detection System
• Built ensemble model detecting fraudulent insurance claims with 92% precision
• Processed 1M+ claims annually saving estimated $5M in fraudulent payments
• Implemented real-time scoring system with sub-second response times

ACHIEVEMENTS
• Winner of MIT Healthcare Hackathon 2022
• Invited speaker at 5+ healthcare analytics conferences
• Reviewer for Journal of Biomedical Informatics and JAMIA
• Successfully secured $500K NIH grant for population health research
""",

    "Marketing Manager Resume": """
ALEXANDRA RODRIGUEZ
Digital Marketing Manager
Email: alex.rodriguez@email.com | Phone: (555) 456-7890
LinkedIn: linkedin.com/in/alexrodriguez | Portfolio: alexmarketing.com
Location: Austin, TX

PROFESSIONAL SUMMARY
Results-driven Digital Marketing Manager with 4+ years of experience in e-commerce marketing, customer acquisition, and conversion optimization. Proven track record of scaling marketing campaigns that generated $5M+ in revenue. Expert in multi-channel digital marketing with strong analytical skills and data-driven approach to growth.

CORE COMPETENCIES
Digital Advertising: Google Ads, Facebook Ads, Instagram, TikTok, LinkedIn Ads
Analytics & Tracking: Google Analytics, Google Tag Manager, Facebook Pixel, Hotjar
Email Marketing: Klaviyo, Mailchimp, SendGrid, HubSpot
E-commerce Platforms: Shopify, WooCommerce, Magento, BigCommerce
Marketing Automation: HubSpot, Marketo, Pardot
SEO/SEM: Keyword research, On-page optimization, Link building, Search Console
Design Tools: Canva, Adobe Creative Suite, Figma
A/B Testing: Optimizely, Google Optimize, VWO

PROFESSIONAL EXPERIENCE

Digital Marketing Manager | ShopNow E-commerce | March 2022 - Present
• Manage $200K monthly advertising budget across Google Ads, Facebook, and TikTok
• Increased online revenue by 85% year-over-year through optimized marketing campaigns
• Reduced customer acquisition cost (CAC) from $45 to $28 while maintaining quality
• Implemented email marketing automation sequences with 32% average open rate
• Led website conversion optimization project increasing conversion rate from 2.1% to 3.4%
• Created and managed affiliate marketing program generating 25% of total revenue
• Collaborated with product team on pricing strategies and promotional campaigns

Marketing Specialist | TrendyStyle Fashion | June 2021 - February 2022
• Launched successful influencer marketing program resulting in 150% increase in brand awareness
• Managed social media accounts with combined following of 500K+ across platforms
• Created content calendar and managed relationships with 50+ micro-influencers
• Developed customer segmentation strategy improving email click-through rates by 40%
• Executed seasonal marketing campaigns generating $1.2M in Q4 holiday sales
• Analyzed customer data to identify high-value segments and personalization opportunities

Digital Marketing Coordinator | LocalBiz Solutions | August 2020 - May 2021
• Managed Google Ads campaigns for 15+ local business clients
• Improved average client ROAS from 3.2x to 5.8x through campaign optimization
• Created landing pages and performed A/B tests to improve conversion rates
• Developed local SEO strategies increasing organic traffic by 60% for clients
• Produced weekly performance reports and client presentations
• Assisted with marketing automation setup and email campaign management

Marketing Assistant | GrowthCorp Agency | January 2020 - July 2020
• Supported senior marketing team with campaign creation and optimization
• Conducted competitor analysis and market research for client strategies
• Managed social media content creation and scheduling
• Assisted with client onboarding and account management
• Learned advanced techniques in paid advertising and analytics

EDUCATION
Bachelor of Business Administration - Marketing | University of Texas at Austin | 2019
Minor in Digital Media | GPA: 3.7/4.0
Relevant Coursework: Consumer Behavior, Digital Marketing, Marketing Analytics, Brand Management

CERTIFICATIONS
• Google Ads Certified (Search, Display, Video, Shopping, Apps) - Current
• Google Analytics Individual Qualification (IQ) - Current
• Facebook Blueprint Certified (Facebook Ads, Instagram Ads) - Current
• HubSpot Content Marketing Certification - 2023
• Klaviyo Email Marketing Certification - 2022
• Google Tag Manager Fundamentals - 2021

PROJECTS & ACHIEVEMENTS

E-commerce Growth Case Study
• Scaled startup from $50K to $500K monthly revenue in 18 months
• Implemented multi-channel marketing strategy across 8 different platforms
• Built customer retention program increasing lifetime value by 45%

Marketing Analytics Dashboard
• Created comprehensive dashboard tracking 50+ KPIs across all marketing channels
• Automated reporting reducing manual work by 20 hours per week
• Enabled data-driven decision making for entire marketing team

ADDITIONAL SKILLS
• A/B Testing & Conversion Optimization
• Customer Journey Mapping
• Marketing Attribution Modeling
• Influencer Relationship Management
• Content Creation & Copywriting
• Project Management (Asana, Monday.com)
• Basic HTML/CSS and WordPress
• Photography and Video Editing

LANGUAGES
• English (Native)
• Spanish (Fluent)
• Portuguese (Conversational)

AWARDS & RECOGNITION
• "Rising Star in Digital Marketing" - Austin Marketing Awards 2023
• Top performer award for Q3 2022 campaign results
• Featured speaker at Texas Digital Marketing Conference 2023
"""
}

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
    st.markdown("### 📄 Sample Documents")
    
    # Sample Job Descriptions
    st.markdown("#### 📋 Job Descriptions")
    for title, content in SAMPLE_JOB_DESCRIPTIONS.items():
        if st.download_button(
            f"📥 {title}",
            content,
            file_name=f"{title.replace(' - ', '_').replace(' ', '_').lower()}_job_description.txt",
            mime="text/plain",
            key=f"job_{title}",
            use_container_width=True
        ):
            st.success(f"✅ Downloaded {title}")
    
    st.markdown("#### 📄 Sample Resumes")
    for title, content in SAMPLE_RESUMES.items():
        if st.download_button(
            f"📥 {title}",
            content,
            file_name=f"{title.replace(' ', '_').lower()}.txt",
            mime="text/plain",
            key=f"resume_{title}",
            use_container_width=True
        ):
            st.success(f"✅ Downloaded {title}")
    
    st.markdown("---")
    st.markdown("### 💡 About")
    st.info(
        "🔎 This enhanced app uses AI to extract job requirements from multiple file formats "
        "and evaluates if your resume matches those requirements! "
        "Now supports PDF, DOC, DOCX, and TXT files! 🏆"
    )
    
    # Tips section in sidebar
    st.markdown("### 📝 Tips for Best Results")
    st.markdown("""
    - 📄 Upload clear, readable files in any supported format
    - 📋 Try our sample documents to test the system
    - 📊 Update your resume based on the results
    - 💼 Focus on improving low-match areas
    - 🔄 Re-run the check after updating your resume
    """)
    st.markdown("---")
    st.markdown("Developed By Shreyas Kasture")

# Constants
CHUNK_SIZE = 5000  # characters per chunk

# Enhanced file processing functions
def extract_text_from_docx(uploaded_file):
    """Extract text from a DOCX file"""
    try:
        doc = Document(BytesIO(uploaded_file.getvalue()))
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        return '\n'.join(full_text)
    except Exception as e:
        st.error(f"❌ Error extracting text from DOCX: {str(e)}")
        return None

def extract_text_from_txt(uploaded_file):
    """Extract text from a TXT file"""
    try:
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                content = uploaded_file.getvalue().decode(encoding)
                return content
            except UnicodeDecodeError:
                continue
        st.error("❌ Could not decode text file with common encodings")
        return None
    except Exception as e:
        st.error(f"❌ Error extracting text from TXT: {str(e)}")
        return None

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

def extract_text_from_file(uploaded_file):
    """Extract text from any supported file format"""
    file_extension = uploaded_file.name.lower().split('.')[-1]
    
    if file_extension == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_extension in ['docx', 'doc']:
        return extract_text_from_docx(uploaded_file)
    elif file_extension == 'txt':
        return extract_text_from_txt(uploaded_file)
    else:
        st.error(f"❌ Unsupported file format: {file_extension}")
        return None

def extract_text_from_multiple_files(uploaded_files):
    """Extract text from multiple uploaded files of any supported format"""
    combined_text = ""
    file_texts = {}
    
    for uploaded_file in uploaded_files:
        text = extract_text_from_file(uploaded_file)
        if text:
            file_texts[uploaded_file.name] = text
            combined_text += f"\n\n--- {uploaded_file.name} ---\n\n{text}"
    
    return combined_text, file_texts

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

# Tab 1: Upload Documents (Enhanced with multi-format support)
with tabs[0]:
    st.header("📤 Upload Job Description & Company Info")
    
    # Add sample documents section at the top
    st.markdown("""
    <div class="sample-docs">
        <h4>🎯 New to the app? Try our sample documents!</h4>
        <p>Download sample job descriptions and resumes from the sidebar to test the system quickly.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📑 Step 1: Upload job description(s)
        
        **Supported formats**: PDF, DOC, DOCX, TXT
        Upload one or more job posting files to analyze the requirements.
        """)
        
        uploaded_files = st.file_uploader(
            "Choose Job Description file(s)", 
            type=["pdf", "doc", "docx", "txt"], 
            accept_multiple_files=True,
            help="Upload job description files in PDF, DOC, DOCX, or TXT format"
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
        
        st.markdown("### 📄 Supported Formats")
        st.markdown("""
        - **PDF** 📄 - Portable Document Format
        - **DOC/DOCX** 📝 - Microsoft Word Documents  
        - **TXT** 📃 - Plain Text Files
        """)
        
        if uploaded_files:
            st.markdown("### 📄 Uploaded Files")
            for file in uploaded_files:
                file_extension = file.name.split('.')[-1].upper()
                emoji = {"PDF": "📄", "DOC": "📝", "DOCX": "📝", "TXT": "📃"}.get(file_extension, "📄")
                st.write(f"{emoji} {file.name} ({file_extension})")
    
    if uploaded_files:
        if st.button("🔍 Extract Text from Files", type="primary"):
            with st.spinner("⏳ Extracting text from uploaded files..."):
                if len(uploaded_files) == 1:
                    job_desc_text = extract_text_from_file(uploaded_files[0])
                else:
                    job_desc_text, file_texts = extract_text_from_multiple_files(uploaded_files)
                    
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
                    st.error("❌ Failed to extract text from the file(s).")

# Tab 2: Extract Requirements
with tabs[1]:
    st.header("📋 Extract Job Requirements")
    
    if st.session_state.job_desc_text is None:
        st.info("🔍 Please upload job description file(s) in the '📤 Upload Documents' tab first.")
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

# Tab 3: Upload Resume (Enhanced for multiple file formats)
with tabs[2]:
    st.header("📝 Upload Your Resume(s)")
    
    if st.session_state.requirements is None:
        st.info("📋 Please extract job requirements in the '📋 Extract Requirements' tab first.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 📄 Step 3: Upload your resume(s)
            
            **Supported formats**: PDF, DOC, DOCX, TXT
            Upload one or more versions of your resume to check how well they match the job requirements.
            """)
            
            resume_files = st.file_uploader(
                "Choose your Resume file(s)", 
                type=["pdf", "doc", "docx", "txt"],
                accept_multiple_files=True,
                help="Upload resume files in PDF, DOC, DOCX, or TXT format"
            )
            
            if resume_files:
                st.session_state.resume_files = resume_files
                
                if st.button("🔍 Process Resume(s)", type="primary"):
                    with st.spinner("⏳ Processing your resume(s)..."):
                        if len(resume_files) == 1:
                            resume_text = extract_text_from_file(resume_files[0])
                        else:
                            resume_text, file_texts = extract_text_from_multiple_files(resume_files)
                            
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
            
            st.markdown("### 📄 Supported Formats")
            st.markdown("""
            - **PDF** 📄 - Most common resume format
            - **DOC/DOCX** 📝 - Microsoft Word Documents  
            - **TXT** 📃 - Plain text resumes
            """)
            
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
                    file_extension = file.name.split('.')[-1].upper()
                    emoji = {"PDF": "📄", "DOC": "📝", "DOCX": "📝", "TXT": "📃"}.get(file_extension, "📄")
                    st.write(f"{emoji} {file.name} ({file_extension})")

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

# Tab 5: Optimize & Generate
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
            generate_cover_letter_checkbox = st.checkbox("✍️ Generate Cover Letter", value=True)
            
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
        
        # Separate sections for each generation type
        st.markdown("---")
        
        # Resume Generation Section
        if generate_resume:
            st.markdown("### 📄 Resume Optimization")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown("Generate an optimized version of your resume based on the job requirements.")
            
            with col2:
                if st.button("🚀 Generate Optimized Resume", type="primary", key="generate_resume_btn"):
                    company_info_to_use = st.session_state.company_info or ""
                    
                    optimized_resume = generate_optimized_resume(
                        st.session_state.requirements, 
                        st.session_state.resume_text, 
                        company_info_to_use
                    )
                    
                    if optimized_resume:
                        st.session_state.optimized_resume = optimized_resume
                        
                        with st.expander("📄 View Optimized Resume", expanded=True):
                            st.markdown("#### 📝 Your Optimized Resume")
                            st.text_area("Optimized Resume Content", optimized_resume, height=400, key="optimized_resume_display")
                            
                            # Download button for resume
                            st.download_button(
                                "📥 Download Optimized Resume",
                                optimized_resume,
                                file_name="optimized_resume.txt",
                                mime="text/plain",
                                key="download_resume"
                            )
                        
                        st.success("✅ Optimized resume generated successfully!")
                    else:
                        st.error("❌ Failed to generate optimized resume.")
        
        st.markdown("---")
        
        # Cover Letter Generation Section  
        if generate_cover_letter_checkbox:
            st.markdown("### ✍️ Cover Letter Generation")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown("Generate a personalized cover letter that addresses the job requirements.")
            
            with col2:
                if st.button("🚀 Generate Cover Letter", type="primary", key="generate_cover_letter_btn"):
                    company_info_to_use = st.session_state.company_info or ""
                    
                    cover_letter = generate_cover_letter(
                        st.session_state.requirements,
                        st.session_state.resume_text,
                        company_info_to_use
                    )
                    
                    if cover_letter:
                        st.session_state.cover_letter = cover_letter
                        
                        with st.expander("✍️ View Cover Letter", expanded=True):
                            st.markdown("#### 📝 Your Personalized Cover Letter")
                            st.text_area("Cover Letter Content", cover_letter, height=400, key="cover_letter_display")
                            
                            # Download button for cover letter
                            st.download_button(
                                "📥 Download Cover Letter",
                                cover_letter,
                                file_name="cover_letter.txt",
                                mime="text/plain",
                                key="download_cover_letter"
                            )
                        
                        st.success("✅ Cover letter generated successfully!")
                    else:
                        st.error("❌ Failed to generate cover letter.")
        
        st.markdown("---")
        
        # Complete Package Download Section
        if st.session_state.get('optimized_resume') or st.session_state.get('cover_letter'):
            st.markdown("### 📋 Complete Application Package")
            
            # Combine all content
            combined_content = "COMPLETE APPLICATION PACKAGE\n"
            combined_content += "=" * 50 + "\n\n"
            
            if st.session_state.get('optimized_resume'):
                combined_content += "OPTIMIZED RESUME\n"
                combined_content += "-" * 20 + "\n"
                combined_content += st.session_state.optimized_resume + "\n\n"
            
            if st.session_state.get('cover_letter'):
                combined_content += "COVER LETTER\n"
                combined_content += "-" * 15 + "\n"
                combined_content += st.session_state.cover_letter + "\n\n"
            
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
                use_container_width=True,
                key="download_complete_package"
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
            if st.button("🔄 Re-evaluate Optimized Resume", key="re_evaluate_btn"):
                if st.session_state.get('optimized_resume'):
                    st.info("Re-evaluating optimized resume against job requirements...")
                    try:
                        new_evaluation = evaluate_resume(st.session_state.requirements, st.session_state.optimized_resume)
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
            if st.button("📊 Compare Versions", key="compare_versions_btn"):
                if st.session_state.resume_files and len(st.session_state.resume_files) > 1:
                    st.info("Feature coming soon: Compare multiple resume versions!")
                else:
                    st.info("Upload multiple resume versions to compare them.")
        
        with col3:
            if st.button("🎯 Keyword Analysis", key="keyword_analysis_btn"):
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
            Features: Multi-Format Support (PDF, DOC, DOCX, TXT) | Sample Documents | Advanced Analytics | Resume Optimization | Cover Letter Generation
        </p>
        <p style="font-size:0.7rem; color:#95a5a6;">
            🆕 Now supports multiple file formats for maximum compatibility!
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    pass
