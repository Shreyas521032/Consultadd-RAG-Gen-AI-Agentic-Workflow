# import PyPDF2
# import textwrap
# import json
# import os
# import subprocess
# import tempfile
# from flask import Flask, request, jsonify
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# CHUNK_SIZE = 3000  # characters per chunk

# def extract_text_from_pdf(pdf_path):
#     text = ""
#     with open(pdf_path, 'rb') as file:
#         reader = PyPDF2.PdfReader(file)
#         for page in reader.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return text

# def split_text_into_chunks(text, chunk_size=CHUNK_SIZE):
#     return textwrap.wrap(text, chunk_size)

# def build_prompt(chunk):
#     return f"""
# From the following RFP content, extract only the mandatory eligibility criteria 
# (such as experience, registrations, certifications, turnover, location, etc.).

# Return a valid JSON object with clear key-value pairs. Do not include explanation or surrounding text.

# Text:
# {chunk}
# """

# def extract_valid_json(text):
#     try:
#         return json.loads(text)
#     except json.JSONDecodeError:
#         try:
#             start = text.index("{")
#             end = text.rindex("}") + 1
#             return json.loads(text[start:end])
#         except Exception as e:
#             raise ValueError(f"JSON parsing failed: {e}")

# def run_ollama_model(prompt):
#     try:
#         result = subprocess.run(
#             ["ollama", "run", "deepseek-r1"],  # Change model name here if using another
#             input=prompt,
#             capture_output=True,
#             text=True,
#             encoding="utf-8",
#         )

#         output = result.stdout.strip()
#         print("Model Raw Output (first 500 chars):\n" + output[:500])

#         try:
#             return extract_valid_json(output)
#         except Exception as e:
#             return {
#                 "error": f"Failed to run model or parse JSON: {e}",
#                 "raw_output": output
#             }

#     except Exception as e:
#         return {
#             "error": f"Subprocess error: {e}",
#             "raw_output": ""
#         }

# def process_all_chunks(text):
#     chunks = split_text_into_chunks(text)
#     all_criteria = []

#     for i, chunk in enumerate(chunks):
#         print(f"\nProcessing chunk {i + 1}/{len(chunks)}...")
#         prompt = build_prompt(chunk)
#         result = run_ollama_model(prompt)

#         if "error" not in result:
#             all_criteria.append(result)
#         else:
#             print(f"Error in chunk {i + 1}: {result['error']}")
#             # Don't write to files when running as a server
#             print(f"Raw output: {result['raw_output'][:200]}...")

#     return all_criteria

# def merge_criteria(criteria_list):
#     merged = {}
#     for item in criteria_list:
#         if isinstance(item, dict):
#             for k, v in item.items():
#                 merged[k] = v
#     return merged

# def process_pdf(pdf_path):
#     """Process a PDF file and return the extracted criteria"""
#     if not os.path.exists(pdf_path):
#         return {"error": f"File not found: {pdf_path}"}

#     print(f"Extracting text from PDF: {pdf_path}")
#     text = extract_text_from_pdf(pdf_path)

#     print("Processing with local LLM...")
#     results = process_all_chunks(text)
#     final_output = merge_criteria(results)

#     print("Extraction complete!")
#     return final_output

# @app.route('/analyze', methods=['POST'])
# def analyze_pdf():
#     """API endpoint to analyze a PDF file"""
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
    
#     file = request.files['file']
    
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400
    
#     if file and file.filename.endswith('.pdf'):
#         try:
#             # Create a temporary file
#             temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
#             temp_path = temp_file.name
#             temp_file.close()
            
#             # Save the uploaded file to the temporary file
#             file.save(temp_path)
            
#             # Process the PDF
#             result = process_pdf(temp_path)
            
#             # Clean up the temporary file
#             os.unlink(temp_path)
            
#             return jsonify(result)
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500
    
#     return jsonify({"error": "Invalid file type"}), 400






# @app.route('/health', methods=['GET'])
# def health_check():
#     """Simple health check endpoint"""
#     return jsonify({"status": "ok", "message": "Server is running"})

# if __name__ == '__main__':
#     # Run the Flask app
#     app.run(host='0.0.0.0', port=5000, debug=True)














import PyPDF2
import textwrap
import json
import os
import subprocess
import tempfile
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

CHUNK_SIZE = 3000  # characters per chunk

# --- Functions for LLM-based deepseek analysis ---
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def split_text_into_chunks(text, chunk_size=CHUNK_SIZE):
    return textwrap.wrap(text, chunk_size)

def build_prompt(chunk):
    return f"""
From the following RFP content, extract only the mandatory eligibility criteria 
(such as experience, registrations, certifications, turnover, location, etc.).

Return a valid JSON object with clear key-value pairs. Do not include explanation or surrounding text.

Text:
{chunk}
"""

def extract_valid_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
        except Exception as e:
            raise ValueError(f"JSON parsing failed: {e}")

def run_ollama_model(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", "deepseek-r1"],  # change model name if needed
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        output = result.stdout.strip()
        print("Model Raw Output (first 500 chars):\n" + output[:500])
        try:
            return extract_valid_json(output)
        except Exception as e:
            return {
                "error": f"Failed to run model or parse JSON: {e}",
                "raw_output": output
            }
    except Exception as e:
        return {
            "error": f"Subprocess error: {e}",
            "raw_output": ""
        }

def process_all_chunks(text):
    chunks = split_text_into_chunks(text)
    all_criteria = []
    for i, chunk in enumerate(chunks):
        print(f"\nProcessing chunk {i + 1}/{len(chunks)}...")
        prompt = build_prompt(chunk)
        result = run_ollama_model(prompt)
        if "error" not in result:
            all_criteria.append(result)
        else:
            print(f"Error in chunk {i + 1}: {result['error']}")
            print(f"Raw output: {result['raw_output'][:200]}...")
    return all_criteria

def merge_criteria(criteria_list):
    merged = {}
    for item in criteria_list:
        if isinstance(item, dict):
            for k, v in item.items():
                merged[k] = v
    return merged

def process_pdf(pdf_path):
    """Extract text from the PDF and process it with DeepSeek to get eligibility criteria."""
    if not os.path.exists(pdf_path):
        return {"error": f"File not found: {pdf_path}"}
    print(f"Extracting text from PDF: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    print("Processing with DeepSeek via local LLM...")
    results = process_all_chunks(text)
    final_output = merge_criteria(results)
    print("Extraction complete!")
    return final_output

# --- Functions for eligibility comparison ---
def compare_against_mandatory(extracted_criteria, eligibility_json):
    # eligibility_json is expected to have a key "mandatoryEligibilityCriteria" which is a list
    mandatory_list = eligibility_json.get("mandatoryEligibilityCriteria", [])
    mismatches = {}
    for item in mandatory_list:
        key = item["key"]
        expected_value = item["value"].strip().lower()
        # use the extracted criteria from DeepSeek (from the PDF) for comparison
        actual_value = str(extracted_criteria.get(key, "")).strip().lower()
        print(f"DEBUG: Comparing key: {key}, Expected: {expected_value}, Actual: {actual_value}")
        if expected_value != actual_value:
            mismatches[key] = {
                "expected": item["value"],
                "company_provided": extracted_criteria.get(key, "Not provided")
            }
    is_eligible = not bool(mismatches)
    if mismatches:
        print("Not Eligible. Mismatches:")
        for k, val in mismatches.items():
            print(f"{k} - Expected: '{val['expected']}', Got: '{val['company_provided']}'")
    else:
        print("Eligible")
    return {"eligible": is_eligible, "mismatches": mismatches}

# --- Existing Route: analyze ---
@app.route('/analyze', methods=['POST'])
def analyze_pdf():
    """API endpoint to analyze a PDF file with local LLM."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.pdf'):
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_path = temp_file.name
            temp_file.close()
            file.save(temp_path)
            result = process_pdf(temp_path)
            os.unlink(temp_path)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Invalid file type"}), 400

# --- New Route for DeepSeek & Eligibility Check ---
@app.route('/check_eligibility', methods=['POST'])
def check_eligibility():
    """
    This endpoint takes a PDF file, extracts its text, sends it to DeepSeek for eligibility extraction,
    and then compares the extracted criteria with provided eligibility JSON (from frontend, e.g. localStorage).
    
    Expects a multipart/form-data POST request with:
      - "file": the PDF document.
      - "eligibility": a JSON string representing the eligibility criteria.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    if "eligibility" not in request.form:
        return jsonify({"error": "No eligibility JSON provided"}), 400

    file = request.files["file"]
    try:
        provided_eligibility = json.loads(request.form["eligibility"])
        print(f"Provided eligibility JSON: {provided_eligibility}")
    except Exception as e:
        return jsonify({"error": f"Invalid eligibility JSON: {e}"}), 400

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "File is not a PDF"}), 400

    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        file.save(temp_file)
        temp_file.close()
        temp_path = temp_file.name

        # Process PDF using DeepSeek (local LLM pipeline) to extract criteria
        extracted_criteria = process_pdf(temp_path)
        os.unlink(temp_path)

        # Compare the DeepSeek extracted criteria with the provided eligibility criteria
        result = compare_against_mandatory(extracted_criteria, provided_eligibility)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "message": "Server is running"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)