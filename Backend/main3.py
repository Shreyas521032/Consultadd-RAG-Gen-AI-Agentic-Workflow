import PyPDF2
import textwrap
import json
import os
import subprocess

# ✅ Exact file path you provided
PDF_PATH = r"e1.pdf"
CHUNK_SIZE = 3000  # characters per chunk

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
            ["ollama", "run", "deepseek-r1"],  # Change model name here if using another
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
            with open(f"chunk_{i+1}_raw_output.txt", "w", encoding="utf-8") as f:
                f.write(result["raw_output"])

    return all_criteria

def merge_criteria(criteria_list):
    merged = {}
    for item in criteria_list:
        if isinstance(item, dict):
            for k, v in item.items():
                merged[k] = v
    return merged

def main():
    if not os.path.exists(PDF_PATH):
        print(f"File not found: {PDF_PATH}")
        return

    print("Extracting text from PDF...")
    text = extract_text_from_pdf(PDF_PATH)

    print("Processing with local LLM...")
    results = process_all_chunks(text)
    final_output = merge_criteria(results)

    print("\nExtracted Eligibility Criteria:")
    print(json.dumps(final_output, indent=2, ensure_ascii=False))

    output_file = os.path.splitext(PDF_PATH)[0] + "_eligibility.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_file}")

if __name__== "__main__":
    main()