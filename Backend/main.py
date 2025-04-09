import re
import PyPDF2
import json
from ollama import Client
from typing import Dict, List
import os

# Check if Ollama is running before proceeding
def check_ollama_status():
    try:
        client = Client(host='http://localhost:11434')
        # Simple model list request to check connection
        models = client.list()
        print("✅ Ollama connection successful!")
        print(f"🤖 Available models: {', '.join([m['name'] for m in models['models']])}")
        return client
    except Exception as e:
        print(f"❌ Ollama error: {str(e)}")
        print("Make sure Ollama is running on http://localhost:11434")
        return None

client = check_ollama_status()

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from all pages of a PDF."""
    print(f"📄 Reading PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return ""
        
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print(f"📑 PDF has {total_pages} pages")
            
            text = []
            for page_num in range(total_pages):
                print(f"  Processing page {page_num+1}/{total_pages}...", end="\r")
                try:
                    page_text = pdf_reader.pages[page_num].extract_text()
                    text.append(page_text if page_text else "")
                except Exception as e:
                    print(f"\n❌ Error on page {page_num+1}: {str(e)}")
                    text.append("")
            
            print("\n✅ PDF text extraction complete")
            return "\n".join(text)
    except Exception as e:
        print(f"❌ Failed to read PDF: {str(e)}")
        return ""

                
    return "\n".join(text)


RFP_PATTERNS = {
    # Certifications & Registrations
    'mbe_certification': r'\b(MBE|Minority Business Enterprise)( certification)?\b',
    'dbe_status': r'\b(HUB|DBE|Disadvantaged Business Enterprise|Historically Underutilized Business)\b',
    'wbe_certification': r'\bWBE|Women-owned Business Enterprise\b',
    'veteran_owned': r'\bVeteran[- ]Owned Business\b',
    'sba_certification': r'\bSBA 8\(a\) Certification\b',
    'iso_certification': r'\bISO[-\s]?\d{4,5}\b',
    'itars_compliance': r'\bITAR[-\s]?compliant\b',
    
    # Business Information
    'business_structure': r'\b(LLC|Corporation|Partnership|Sole Proprietorship)\b',
    'state_registration_number': r'\bState (Registration|ID) Number\b',
    'state_of_incorporation': r'\b(Incorporated|Formed) in (state of )?[A-Z]{2}\b',
    'duns_number': r'\bDUNS( Number|#)?\b',
    'cage_code': r'\bCAGE( Code|#)?\b',
    'naics_codes': r'\bNAICS( Code|#)?\b',
    'sam_registration': r'\bSAM\.gov\b',
    'uei_number': r'\bUEI Number\b',
    
    # Financial Requirements
    'bank_letter': r'\bBank (Letter|Reference) of Creditworthiness\b',
    'financial_statements': r'\b(Audited|Financial) Statements\b',
    'insurance_coverage': r'\bInsurance Coverage (of|at least) \$?(\d+[\w]*)\b',
    'bonding_capacity': r'\bBonding Capacity\b',
    
    # Experience & History
    'staffing_experience': r'\b(Temporary Staffing|Workforce) Experience\b',
    'company_age': r'\bCompany (in operation|existing) (for|since)\b',
    'project_references': r'\b(Project|Client) References\b',
    'past_performance': r'\bPast Performance References\b',
    'case_studies': r'\bCase Studies\b',
    
    # Legal & Compliance
    'licenses': r'\b(Business|Professional) License\b',
    'coi_required': r'\bCertificate of Insurance( COI)?\b',
    'w9_form': r'\bW-9 Form\b',
    'eeo_policy': r'\bEqual Employment Opportunity\b',
    'osha_compliance': r'\bOSHA Compliance\b',
    'ada_compliance': r'\bADA Compliance\b',
    
    # Technical Requirements
    'cloud_certifications': r'\b(AWS|Azure|GCP) Certified\b',
    'security_clearance': r'\bSecurity Clearance (Level )?[A-Z0-9]+\b',
    'disaster_recovery': r'\bDisaster Recovery Plan\b',
    'encryption_standards': r'\b(AES|FIPS) \d+\b',
    
    # Sustainability & Quality
    'esg_policy': r'\bESG (Policy|Framework)\b',
    'quality_certifications': r'\b(Six Sigma|Total Quality Management)\b',
    'green_initiatives': r'\bLEED Certification\b',
    
    # Industry Specific
    'hipaa_compliance': r'\bHIPAA Compliance\b',
    'gdpr_compliance': r'\bGDPR Compliance\b',
    'pci_dss_compliance': r'\bPCI DSS\b',
    'fda_compliance': r'\bFDA (Approval|Compliance)\b',
    
    # Contractual Terms
    'warranty_period': r'\bWarranty Period of (\d+ years?)\b',
    'payment_terms': r'\bNet \d+ Payment Terms\b',
    'penalty_clauses': r'\bLiquidated Damages\b',
    
    # Personnel Requirements
    'key_personnel': r'\bKey Personnel Resumes\b',
    'employee_count': r'\bMinimum (\d+) (FTE|Full-Time Employees)\b',
    'certified_staff': r'\bCertified (Engineers|Technicians)\b',
    
    # Additional Common Requirements
    'conflict_of_interest': r'\bConflict of Interest Disclosure\b',
    'references_required': r'\bProfessional References\b',
    'nda_required': r'\bNon-Disclosure Agreement\b',
    'subcontracting_limit': r'\bSubcontracting Limit( of)? (\d+%)\b',
    'safety_manual': r'\bSafety Manual\b',
    'training_programs': r'\bEmployee Training Programs\b',
    'patents': r'\bPatent(s|ed)\b',
    'trade_secrets': r'\bTrade Secrets Protection\b',
    'response_deadline': r'\bResponse Deadline: (\d{4}-\d{2}-\d{2})\b',
    'award_notification': r'\bAward Notification Date\b',
    'prototype_required': r'\bPrototype Submission\b',
    'demo_required': r'\bProduct Demonstration\b',
    'sample_work': r'\bSample Work Product\b',
    'cost_breakdown': r'\bDetailed Cost Breakdown\b',
    'implementation_timeline': r'\bImplementation Schedule\b',
    'warranty_terms': r'\bExtended Warranty Options\b',
    'escalation_procedures': r'\bTechnical Support Escalation\b',
    'slas': r'\bService Level Agreements\b',
    'change_order_process': r'\bChange Order Procedures\b',
    'term_length': r'\bContract Term (Length|Duration)\b'
}

def regex_matcher(text: str) -> Dict:
    results = {}
    text_lower = text.lower()
    
    for key, pattern in RFP_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Handle different match groups
            if any(char.isdigit() for char in pattern):
                results[key] = matches[0][-1] if isinstance(matches[0], tuple) else matches[0]
            else:
                results[key] = 'yes'
        else:
            results[key] = 'no'
    return results

def llm_analyzer(text: str, criteria_list: List[str]) -> Dict:
    """Use Ollama to analyze text for specific criteria."""
    if not client:
        print("❌ Skipping LLM analysis - Ollama not available")
        return {}
        
    print(f"🧠 Analyzing text with LLM for {len(criteria_list)} criteria...")
    
    if not criteria_list:
        print("ℹ️ No unclear criteria to analyze")
        return {}
    
    prompt = f"""Analyze this RFP document and extract requirements as JSON. Format:
    {{
        "criteria": {{
            "Criterion Name": "Value (yes/no/specific)",
            ...
        }}
    }}
    Check for: {', '.join(criteria_list)}"""
    
    try:
        # Note: Ollama's chat method is NOT async in the Python client
        response = client.chat(
            model='deepseek-r1',
            messages=[{
                'role': 'user',
                'content': f"{prompt}\n\nDocument Excerpt:\n{text[:3000]}"
            }]
        )
        print("✅ LLM analysis complete")
        
        try:
            result = json.loads(response['message']['content']).get('criteria', {})
            return result
        except json.JSONDecodeError:
            print("❌ Failed to parse LLM response as JSON")
            print(f"LLM response: {response['message']['content'][:200]}...")
            return {}
            
    except Exception as e:
        print(f"❌ LLM Error: {str(e)}")
        return {}

# Change the analyze_rfp function to not be async
def analyze_rfp(pdf_path: str) -> Dict:
    """Main function to analyze an RFP document."""
    print("\n==== 🚀 Starting RFP Analysis ====\n")
    
    # Extract text from PDF (all pages)
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("❌ No text extracted from PDF")
        return {}
    
    print(f"\n🔍 Analyzing text with regex patterns...")
    regex_results = regex_matcher(text)
    
    # Find criteria that regex couldn't confirm
    unclear_criteria = [k for k, v in regex_results.items() if v == 'no']
    print(f"📋 Found {len(unclear_criteria)} criteria to analyze with LLM")
    
    # LLM analysis (non-async now)
    llm_results = llm_analyzer(text, unclear_criteria)
    
    # Combine results
    final_results = {**regex_results, **llm_results}
    
    # Filter and format results
    formatted_results = {
        k.replace('_', ' ').title(): v 
        for k, v in final_results.items()
        if v not in ['no', '']  # Filter out negative results
    }
    
    print(f"\n✨ Analysis complete! Found {len(formatted_results)} matching criteria")
    return formatted_results

# Usage
if __name__ == "__main__":
    # No need for asyncio anymore
    results = analyze_rfp("RFP_Eligibility_Template.pdf")
    print("\n==== 📊 Analysis Results ====\n")
    print(json.dumps(results, indent=2))