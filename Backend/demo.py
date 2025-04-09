import os
import json
import google.generativeai as genai
from PyPDF2 import PdfReader
import re
import tiktoken

# ========== CONFIGURE GEMINI ==========
genai.configure(api_key="AIzaSyDJ8PKh8Jx9V08nMsH-Kuq3yaWWhMo8BQ8")
model = genai.GenerativeModel("gemini-1.5-flash")

# ========== TOKEN COUNTER ==========
def count_tokens(text):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

# ========== PDF CLEANER ==========
def clean_pdf_text(text):
    # Remove page numbers and headers
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = re.sub(r'RFP 25-008.*?Page \d+ of 33', '', text)
    # Remove empty lines and extra spaces
    text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
    return text

# ========== SMART CHUNKING ==========
def chunk_text(text, max_tokens=2000):
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    # Split by sections using heading patterns
    sections = re.split(r'\n#+ |\n##+ |\n###+ ', text)
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        section_tokens = count_tokens(section)
        
        if section_tokens > max_tokens:
            # Split large sections into paragraphs
            paras = re.split(r'\n\n+', section)
            for para in paras:
                para_tokens = count_tokens(para)
                if current_tokens + para_tokens > max_tokens:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [para]
                    current_tokens = para_tokens
                else:
                    current_chunk.append(para)
                    current_tokens += para_tokens
        else:
            if current_tokens + section_tokens > max_tokens:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [section]
                current_tokens = section_tokens
            else:
                current_chunk.append(section)
                current_tokens += section_tokens
                
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
        
    return chunks

# ========== CRITERIA EXTRACTOR ==========
def extract_criteria(chunk):
    prompt = f"""Analyze this RFP document section and extract ALL eligibility and evaluation criteria. 
    Include requirements, certifications, insurance needs, experience thresholds, compliance standards, 
    and any other qualification criteria. Return ONLY valid JSON with key-value pairs.

    Examples:
    {{
        "Minimum Company Experience": "3 years in temporary staffing services",
        "Required Insurance Types": "Workers' Compensation, Commercial General Liability",
        "Employee Background Checks": "Mandatory for all temporary staff",
        "Financial Requirements": "Proof of financial stability for minimum 1 year",
        "Compliance Standards": "ADA, Title VII, Civil Rights Act"
    }}

    Document Section:
    {chunk}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": 2000}
        )
        if response.text:
            return json.loads(response.text.strip())
    except Exception as e:
        print(f"Error processing chunk: {str(e)}")
    return {}

# ========== MAIN PROCESSOR ==========
def process_rfp(file_path):
    print(f"Processing {file_path}...")
    
    # Read and clean PDF
    reader = PdfReader(file_path)
    text = "\n".join([page.extract_text() or "" for page in reader.pages])
    clean_text = clean_pdf_text(text)
    
    # Chunk document
    chunks = chunk_text(clean_text)
    print(f"Document divided into {len(chunks)} chunks")
    
    # Process chunks
    criteria = {}
    for i, chunk in enumerate(chunks, 1):
        print(f"Analyzing chunk {i}/{len(chunks)}")
        chunk_criteria = extract_criteria(chunk)
        criteria.update(chunk_criteria)
    
    # Post-process results
    final_criteria = {}
    for key, value in criteria.items():
        # Remove empty values and normalize keys
        if value.strip():
            norm_key = key.strip().title()
            final_criteria[norm_key] = value.strip()
    
    print("\n====== EXTRACTED CRITERIA ======")
    print(json.dumps(final_criteria, indent=2))
    return final_criteria

# ========== EXECUTION ==========
if __name__ == "__main__":
    pdf_file = "e1.pdf"  # Your PDF file
    results = process_rfp(pdf_file)
    
    # Save to JSON file
    with open("extracted_criteria.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to extracted_criteria.json")