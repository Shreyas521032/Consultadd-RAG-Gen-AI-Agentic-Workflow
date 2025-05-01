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

# Streamlit page config
st.set_page_config(
    page_title="Eligibility Criteria Checker",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application title and description
st.title("RFP Eligibility Criteria Checker")
st.markdown("""
This app helps you extract eligibility criteria from RFP documents and evaluate whether 
your organization or model meets those criteria.
""")

# Sidebar for API configuration
with st.sidebar:
    st.header("API Configuration")
    gemini_api_key = st.text_input("Gemini API Key", type="password")
    
    if gemini_api_key:
        try:
            # Configure Gemini API
            genai.configure(api_key=gemini_api_key)
            st.success("Gemini API configured successfully!")
        except Exception as e:
            st.error(f"Error configuring Gemini API: {str(e)}")
    
    st.markdown("---")
    st.subheader("About")
    st.info(
        "This app extracts eligibility criteria from RFP documents and evaluates "
        "if your organization meets those criteria using AI."
    )

# Constants
CHUNK_SIZE = 5000  # characters per chunk

# Gemini Models
def get_gemini_model():
    """Get the appropriate Gemini model"""
    try:
        # Try to use Gemini 1.5 Pro if available
        return genai.GenerativeModel('gemini-1.5-pro')
    except:
        # Fall back to Gemini 1.0 Pro
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
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

def split_text_into_chunks(text, chunk_size=CHUNK_SIZE):
    """Split text into manageable chunks"""
    return textwrap.wrap(text, chunk_size)

def build_extraction_prompt(chunk):
    """Build prompt for eligibility criteria extraction"""
    return f"""
From the following RFP content, extract only the mandatory eligibility criteria 
(such as experience, registrations, certifications, turnover, location, etc.).

Return a valid JSON object with clear key-value pairs. Do not include explanation or surrounding text.
Structure the JSON as:
{{
  "criterion_name_1": "detailed criterion description 1",
  "criterion_name_2": "detailed criterion description 2",
  ...
}}

Use clear, descriptive keys like "experience_requirements", "technical_qualifications", "financial_requirements", etc.

Text:
{chunk}
"""

def build_evaluation_prompt(criteria_json, model_description):
    """Build prompt for eligibility evaluation"""
    return f"""
You are an expert eligibility assessor. Your task is to evaluate whether a model meets the eligibility criteria for a project.

ELIGIBILITY CRITERIA:
{json.dumps(criteria_json, indent=2)}

MODEL DESCRIPTION:
{model_description}

Please analyze if the model meets each of the eligibility criteria. Pay special attention to:
1. Experience requirements (years of experience, specific domains)
2. Technical requirements
3. Financial requirements
4. Compliance requirements

For each criterion, determine if the model meets it based on the description provided.
If there are specific numerical requirements (e.g., "5 years of experience"), check if the model meets those exact requirements.

Provide your assessment in the following JSON format:
{{
  "overall_eligible": true/false,
  "criteria_evaluation": {{
    "criterion_name_1": {{
      "meets_criterion": true/false,
      "explanation": "Detailed explanation of why the model meets or doesn't meet this criterion",
      "confidence": "high/medium/low"
    }},
    "criterion_name_2": {{
      "meets_criterion": true/false,
      "explanation": "Detailed explanation of why the model meets or doesn't meet this criterion",
      "confidence": "high/medium/low"
    }},
    ...
  }},
  "summary": "A brief summary of the overall eligibility assessment"
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
                st.error("Could not extract valid JSON from response")
                return None
        except Exception as e:
            st.error(f"JSON parsing failed: {str(e)}")
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
        st.error("Please configure your Gemini API key in the sidebar first.")
        return None
        
    try:
        model = get_gemini_model()
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error querying Gemini API: {str(e)}")
        return None

# Main App Functions
def extract_eligibility_criteria(pdf_text):
    """Extract eligibility criteria from PDF text"""
    with st.spinner("Extracting eligibility criteria from document..."):
        chunks = split_text_into_chunks(pdf_text)
        
        # Progress bar for extraction
        progress_bar = st.progress(0)
        st.write(f"Processing {len(chunks)} text chunks...")
        
        all_criteria = {}
        
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
                        all_criteria.update(json_result)
        
        # Complete progress bar
        progress_bar.progress(100)
        
        return all_criteria

def evaluate_eligibility(criteria, model_description):
    """Evaluate eligibility against criteria"""
    with st.spinner("Evaluating eligibility..."):
        prompt = build_evaluation_prompt(criteria, model_description)
        result = query_gemini(prompt)
        
        if result:
            return extract_valid_json(result)
        return None

def generate_summary(evaluation, model_description):
    """Generate a concise summary of the evaluation"""
    prompt = f"""
You are an expert at summarizing complex information. Please provide a concise, easy-to-understand summary of the following eligibility evaluation.

MODEL DESCRIPTION:
{model_description}

ELIGIBILITY EVALUATION:
{json.dumps(evaluation, indent=2)}

Your summary should:
1. Be no more than 3-4 sentences
2. Clearly state whether the model is eligible or not
3. Mention the key factors that influenced the decision
4. Use simple, direct language

Respond with only the summary text, no additional formatting or explanation.
"""
    
    return query_gemini(prompt)

# App Interface
tabs = st.tabs(["Upload RFP", "Extract Criteria", "Evaluate Eligibility", "Results"])

# Session state initialization
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = None
if 'criteria' not in st.session_state:
    st.session_state.criteria = None
if 'evaluation' not in st.session_state:
    st.session_state.evaluation = None
if 'summary' not in st.session_state:
    st.session_state.summary = None

# Tab 1: Upload RFP
with tabs[0]:
    st.header("Upload RFP Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file:
        if st.button("Extract Text from PDF"):
            with st.spinner("Extracting text from PDF..."):
                pdf_text = extract_text_from_pdf(uploaded_file)
                if pdf_text:
                    st.session_state.pdf_text = pdf_text
                    st.success(f"Successfully extracted {len(pdf_text)} characters from the PDF!")
                    st.markdown("### Preview of extracted text")
                    st.text_area("PDF Content Preview", pdf_text[:2000] + "...", height=300)
                    st.markdown("**Proceed to the 'Extract Criteria' tab to continue.**")
                else:
                    st.error("Failed to extract text from the PDF.")

# Tab 2: Extract Criteria
with tabs[1]:
    st.header("Extract Eligibility Criteria")
    
    if st.session_state.pdf_text is None:
        st.info("Please upload a PDF and extract its text in the 'Upload RFP' tab first.")
    else:
        if st.button("Extract Eligibility Criteria"):
            criteria = extract_eligibility_criteria(st.session_state.pdf_text)
            if criteria:
                st.session_state.criteria = criteria
                st.success(f"Successfully extracted {len(criteria)} eligibility criteria!")
                
                # Display criteria in a nice format
                st.markdown("### Extracted Eligibility Criteria")
                for criterion, description in criteria.items():
                    with st.expander(f"{criterion}"):
                        st.write(description)
                
                st.markdown("**Proceed to the 'Evaluate Eligibility' tab to continue.**")
            else:
                st.error("Failed to extract eligibility criteria from the document.")

# Tab 3: Evaluate Eligibility
with tabs[2]:
    st.header("Evaluate Your Eligibility")
    
    if st.session_state.criteria is None:
        st.info("Please extract eligibility criteria in the 'Extract Criteria' tab first.")
    else:
        st.markdown("Enter a detailed description of your organization, model, or product to evaluate against the eligibility criteria.")
        model_description = st.text_area("Organization/Model Description", 
                                         height=300, 
                                         placeholder="Describe your organization, including years of experience, technical capabilities, financial status, compliance certifications, etc.")
        
        if st.button("Evaluate Eligibility") and model_description:
            evaluation = evaluate_eligibility(st.session_state.criteria, model_description)
            if evaluation:
                st.session_state.evaluation = evaluation
                summary = generate_summary(evaluation, model_description)
                st.session_state.summary = summary
                
                st.success("Eligibility evaluation completed!")
                st.markdown("**Proceed to the 'Results' tab to view the evaluation results.**")
            else:
                st.error("Failed to evaluate eligibility.")

# Tab 4: Results
with tabs[3]:
    st.header("Evaluation Results")
    
    if st.session_state.evaluation is None:
        st.info("Please complete the eligibility evaluation in the 'Evaluate Eligibility' tab first.")
    else:
        evaluation = st.session_state.evaluation
        
        # Display overall result with color
        if evaluation['overall_eligible']:
            st.success("### OVERALL RESULT: ELIGIBLE ✅")
        else:
            st.error("### OVERALL RESULT: NOT ELIGIBLE ❌")
        
        # Display summary
        if st.session_state.summary:
            st.markdown("### Summary")
            st.info(st.session_state.summary)
        
        # Display criteria evaluation in a table
        st.markdown("### Criteria Evaluation")
        
        criteria_data = []
        for criterion, result in evaluation['criteria_evaluation'].items():
            criteria_data.append({
                "Criterion": criterion,
                "Status": "✅ Meets" if result["meets_criterion"] else "❌ Does not meet",
                "Confidence": result.get("confidence", "N/A").capitalize(),
                "Explanation": result["explanation"]
            })
        
        df = pd.DataFrame(criteria_data)
        st.dataframe(df, use_container_width=True)
        
        # Detailed evaluation for each criterion
        st.markdown("### Detailed Evaluation")
        for criterion, result in evaluation['criteria_evaluation'].items():
            meets = result["meets_criterion"]
            color = "green" if meets else "red"
            
            with st.expander(f"{criterion} - {'✅ Meets' if meets else '❌ Does not meet'}"):
                st.markdown(f"**Confidence**: {result.get('confidence', 'N/A').capitalize()}")
                st.markdown(f"**Explanation**: {result['explanation']}")
        
        # Download results
        if st.download_button(
            "Download Evaluation Results (JSON)",
            json.dumps(evaluation, indent=2),
            file_name="eligibility_evaluation.json",
            mime="application/json"
        ):
            st.success("Successfully downloaded evaluation results!")

if __name__ == "__main__":
    pass  # Streamlit handles the script execution
