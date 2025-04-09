import re
import json
import PyPDF2
from ollama import Client
from typing import Dict, Optional

client = Client(host='http://localhost:11434')

ELIGIBILITY_STRUCTURE = {
    "Legal Entity": "Must be a registered legal entity (Company/Firm/LLP/Proprietorship)",
    "Registration Certificates": "Copy of Certificate of Incorporation/Registration must be submitted",
    "PAN": "Valid PAN number issued by Income Tax Department",
    "GST Registration": "Valid GST registration certificate is mandatory",
    "Experience": "Minimum 3 years of experience in providing similar services",
    "Work Orders/Completion Certificates": "At least 3 work orders or completion certificates required",
    "Financial Turnover": "Minimum average annual turnover of INR 50 Lakhs",
    "Audited Financial Statements": "Audited balance sheets and profit/loss statements",
    "No Blacklisting Declaration": "Self-declaration confirming not blacklisted",
    "Authorized Signatory": "Authorization letter or board resolution",
    "Technical Proposal": "Detailed technical proposal with methodology",
    "Financial Proposal": "Itemized financial bid per format",
    "Affidavit of Correctness": "Affidavit certifying document accuracy",
    "Undertaking of Compliance": "Undertaking accepting all RFP terms",
    "Contact Information": "Contact person details including phone/email"
}

def extract_pdf_text(pdf_path: str, start_page: int = 10, end_page: int = 200) -> str:
    """Extract text from specified PDF pages"""
    text = []
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            start_idx = max(start_page - 1, 0)
            end_idx = min(end_page, len(reader.pages))
            
            for page_num in range(start_idx, end_idx):
                page = reader.pages[page_num]
                text.append(page.extract_text())
    except Exception as e:
        print(f"PDF Error: {str(e)}")
    return "\n".join(text)

async def analyze_with_llm(text: str) -> Dict:
    """Get structured eligibility criteria using LLM"""
    prompt = f"""Extract eligibility criteria exactly in this JSON format:
{json.dumps(ELIGIBILITY_STRUCTURE, indent=2)}
    
From this document content:
{text[:3000]}"""

    try:
        response = await client.chat(
            model='deepseek-r1',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.0}
        )
        return json.loads(response['message']['content'])
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        return {}

async def process_rfp_document(pdf_path: str) -> Dict:
    """Main processing function"""
    try:
        # Step 1: Extract text from PDF
        text = extract_pdf_text(pdf_path)
        if not text:
            return {"error": "Failed to extract text from PDF"}
        
        # Step 2: Analyze with LLM
        return await analyze_with_llm(text)
        
    except Exception as e:
        return {"error": str(e)}

# Usage example
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(process_rfp_document("e2.pdf"))
    print(json.dumps(result, indent=2))