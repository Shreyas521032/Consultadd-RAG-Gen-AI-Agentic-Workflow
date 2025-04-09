# /c:/Users/shrey/Downloads/New/ai_agent_eligibility_checker.py
import os
import json
import re
import requests
from typing import Dict, List, Any
from pinecone import Pinecone

class EligibilityAgent:
    """Base class for eligibility evaluation agents"""

    def __init__(self, name: str):
        self.name = name

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data and return results"""
        raise NotImplementedError("Subclasses must implement process method")

class CriteriaExtractionAgent(EligibilityAgent):
    """Agent responsible for extracting eligibility criteria from documents"""

    def __init__(self):
        super().__init__("Criteria Extraction Agent")

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract eligibility criteria from search results"""
        print(f"\n[{self.name}] Extracting eligibility criteria...")

        index = data.get("index")
        eligibility_queries = data.get("eligibility_queries")
        eligibility_results = {}
        all_criteria_text = ""

        for query in eligibility_queries:
            print(f"[{self.name}] Searching for: {query}")
            results = search_eligibility_criteria(index, query)

            if results and 'result' in results and 'hits' in results['result']:
                criterion_name = query.replace("What are the ", "").replace(" for eligibility?", "")
                eligibility_results[criterion_name] = []

                print(f"[{self.name}] Top results for {criterion_name}:")
                for hit in results['result']['hits']:
                    content_preview = hit['fields']['chunk_text'][:100] + "..." if len(hit['fields']['chunk_text']) > 100 else hit['fields']['chunk_text']
                    print(f"- Text: {content_preview}")
                    eligibility_results[criterion_name].append({
                        "text": hit['fields']['chunk_text'],
                        "score": hit['_score']
                    })

                    # Add to the combined criteria text
                    all_criteria_text += f"\n\n{criterion_name.upper()} CRITERIA:\n{hit['fields']['chunk_text']}"

        return {
            "eligibility_results": eligibility_results,
            "all_criteria_text": all_criteria_text
        }

class RequirementAnalysisAgent(EligibilityAgent):
    """Agent responsible for analyzing specific requirements"""

    def __init__(self):
        super().__init__("Requirement Analysis Agent")

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze specific requirements like years of experience"""
        print(f"\n[{self.name}] Analyzing specific requirements...")

        model_description = data.get("model_description")
        eligibility_results = data.get("eligibility_results")

        # Extract years of experience from model description
        model_years = extract_years_from_text(model_description)
        print(f"[{self.name}] Extracted years from model description: {model_years if model_years is not None else 'None'}")

        # Find required years in criteria
        required_years = None
        if "experience requirements" in eligibility_results:
            for result in eligibility_results["experience requirements"]:
                criterion_text = result["text"]
                # Look for required years in the criterion text
                required_years_match = extract_years_from_text(criterion_text)

                if required_years_match is not None:
                    required_years = required_years_match
                    print(f"[{self.name}] Found required years in criteria: {required_years}")
                    break

        return {
            "model_years": model_years,
            "required_years": required_years
        }

class LLMEvaluationAgent(EligibilityAgent):
    """Agent responsible for LLM-based evaluation"""

    def __init__(self, model="llama3"):
        super().__init__("LLM Evaluation Agent")
        self.model = model

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate eligibility using an LLM"""
        print(f"\n[{self.name}] Evaluating eligibility using LLM...")

        model_description = data.get("model_description")
        all_criteria_text = data.get("all_criteria_text")

        # Prepare the prompt for the LLM
        llm_prompt = f"""
You are an expert eligibility assessor. Your task is to evaluate whether a model meets the eligibility criteria for a project.

ELIGIBILITY CRITERIA:
{all_criteria_text}

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
    "technical requirements": {{
      "meets_criterion": true/false,
      "explanation": "Detailed explanation of why the model meets or doesn't meet this criterion",
      "confidence": "high/medium/low"
    }},
    "financial requirements": {{
      "meets_criterion": true/false,
      "explanation": "Detailed explanation of why the model meets or doesn't meet this criterion",
      "confidence": "high/medium/low"
    }},
    "experience requirements": {{
      "meets_criterion": true/false,
      "explanation": "Detailed explanation of why the model meets or doesn't meet this criterion",
      "confidence": "high/medium/low"
    }},
    "compliance requirements": {{
      "meets_criterion": true/false,
      "explanation": "Detailed explanation of why the model meets or doesn't meet this criterion",
      "confidence": "high/medium/low"
    }}
  }},
  "summary": "A brief summary of the overall eligibility assessment"
}}

Only respond with the JSON object, no additional text.
"""

        print(f"[{self.name}] Querying LLM for eligibility assessment...")
        llm_response = query_llm(llm_prompt, self.model)

        if llm_response:
            try:
                # Try to parse the JSON response
                import re
                # Find JSON object in the response
                json_match = re.search(r'({.*})', llm_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    evaluation = json.loads(json_str)
                else:
                    evaluation = json.loads(llm_response)

                return {"llm_evaluation": evaluation}

            except Exception as e:
                print(f"[{self.name}] Error parsing LLM response: {str(e)}")
                return {"llm_evaluation": None, "error": str(e)}
        else:
            print(f"[{self.name}] LLM query failed")
            return {"llm_evaluation": None, "error": "LLM query failed"}

class RuleBasedEvaluationAgent(EligibilityAgent):
    """Agent responsible for rule-based evaluation"""

    def __init__(self):
        super().__init__("Rule-Based Evaluation Agent")

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate eligibility using rule-based approach"""
        print(f"\n[{self.name}] Evaluating eligibility using rules...")

        model_description = data.get("model_description")
        eligibility_results = data.get("eligibility_results")
        model_years = data.get("model_years")
        required_years = data.get("required_years")

        # More sophisticated evaluation
        evaluation = {
            "overall_eligible": True,
            "criteria_evaluation": {}
        }

        # Check experience requirements specifically
        if "experience requirements" in eligibility_results:
            experience_met = False
            explanation = ""

            # Compare model years with required years
            if model_years is not None and required_years is not None:
                if model_years >= required_years:
                    experience_met = True
                    explanation = f"Model has {model_years} years of experience, which meets the requirement of {required_years} years"
                else:
                    experience_met = False
                    explanation = f"Model has only {model_years} years of experience, which does not meet the requirement of {required_years} years"
            elif model_years is None:
                experience_met = False
                explanation = "Could not determine years of experience from model description"
            elif required_years is None:
                # If we can't determine required years, fall back to keyword matching
                for result in eligibility_results["experience requirements"]:
                    criterion_text = result["text"].lower()
                    model_desc_lower = model_description.lower()

                    if "experience" in model_desc_lower and "experience" in criterion_text:
                        experience_met = True
                        explanation = "Model description mentions experience, but exact years couldn't be verified"
                        break

            evaluation["criteria_evaluation"]["experience requirements"] = {
                "meets_criterion": experience_met,
                "explanation": explanation,
                "required_years": required_years,
                "model_years": model_years
            }

            if not experience_met:
                evaluation["overall_eligible"] = False

        # Check other criteria with improved keyword matching
        for criterion, results in eligibility_results.items():
            if criterion == "experience requirements":
                continue  # Already handled above

            # Check if model description contains keywords from criteria
            criterion_met = False
            explanation = ""

            for result in results:
                criterion_text = result["text"].lower()
                model_desc_lower = model_description.lower()

                # Extract key terms from criterion text (more than just single words)
                key_terms = []
                for sentence in criterion_text.split('.'):
                    if len(sentence) > 10:  # Skip very short sentences
                        # Extract phrases that might be requirements
                        if "must" in sentence or "should" in sentence or "require" in sentence:
                            key_terms.append(sentence.strip())

                # If no key terms found, fall back to word-level matching
                if not key_terms:
                    key_terms = [word for word in criterion_text.split() if len(word) > 4]

                # Check for matches
                matches = []
                for term in key_terms:
                    if len(term) > 10 and term in model_desc_lower:  # For longer phrases
                        matches.append(term)
                    elif len(term) <= 10:  # For single words
                        if term in model_desc_lower:
                            matches.append(term)

                if matches:
                    criterion_met = True
                    explanation = f"Model description contains relevant terms: {', '.join(matches[:3])}"
                    break

            if not criterion_met:
                explanation = "No matching terms found in model description"
                # Only mark as ineligible if it's a mandatory criterion
                if "mandatory" in criterion_text.lower() or "must" in criterion_text.lower():
                    evaluation["overall_eligible"] = False

            evaluation["criteria_evaluation"][criterion] = {
                "meets_criterion": criterion_met,
                "explanation": explanation
            }

        return {"rule_evaluation": evaluation}

class EligibilityOrchestrator:
    """Orchestrates the eligibility evaluation process using agents"""

    def __init__(self):
        self.agents = {
            "criteria_extraction": CriteriaExtractionAgent(),
            "requirement_analysis": RequirementAnalysisAgent(),
            "llm_evaluation": LLMEvaluationAgent(),
            "rule_evaluation": RuleBasedEvaluationAgent()
        }

    def evaluate_eligibility(self, index, model_description):
        """
        Evaluate eligibility using a multi-agent approach

        Args:
            index: Pinecone index
            model_description: Description of the model

        Returns:
            Final eligibility evaluation
        """
        print("\n[Orchestrator] Starting eligibility evaluation process...")

        # Initial data
        data = {
            "index": index,
            "model_description": model_description,
            "eligibility_queries": [
                "What are the technical requirements for eligibility?",
                "What are the financial requirements for eligibility?",
                "What are the experience requirements for eligibility?",
                "What are the compliance requirements for eligibility?"
            ]
        }

        # Step 1: Extract eligibility criteria
        criteria_data = self.agents["criteria_extraction"].process(data)
        data.update(criteria_data)

        # Step 2: Analyze specific requirements
        requirement_data = self.agents["requirement_analysis"].process(data)
        data.update(requirement_data)

        # Step 3: Evaluate using LLM
        llm_data = self.agents["llm_evaluation"].process(data)
        data.update(llm_data)

        # Step 4: Evaluate using rules as backup
        rule_data = self.agents["rule_evaluation"].process(data)
        data.update(rule_data)

        # Step 5: Determine final evaluation
        print("\n[Orchestrator] Determining final evaluation...")

        if "llm_evaluation" in data and data["llm_evaluation"]:
            final_evaluation = data["llm_evaluation"]
            evaluation_method = "LLM-based"
        else:
            final_evaluation = data["rule_evaluation"]
            evaluation_method = "Rule-based"

        # Save evaluation to file
        with open("eligibility_evaluation.json", "w") as f:
            json.dump(final_evaluation, f, indent=2)

        # Display results
        print(f"\n=== ELIGIBILITY EVALUATION ({evaluation_method}) ===")
        print(f"Overall Eligible: {final_evaluation['overall_eligible']}")

        for criterion, result in final_evaluation['criteria_evaluation'].items():
            status = "✅ Meets criterion" if result["meets_criterion"] else "❌ Does not meet criterion"
            confidence = result.get("confidence", "N/A")
            print(f"{criterion}: {status} (Confidence: {confidence})")
            print(f"  Explanation: {result['explanation']}")

            # Print additional details for experience requirements
            if criterion == "experience requirements":
                if "required_years" in result and result["required_years"] is not None:
                    print(f"  Required years: {result['required_years']}")
                if "model_years" in result and result["model_years"] is not None:
                    print(f"  Model years: {result['model_years']}")

        if "summary" in final_evaluation:
            print(f"\nSummary: {final_evaluation['summary']}")

        print("\nDetailed evaluation saved to eligibility_evaluation.json")

        return final_evaluation

# Keep the original utility functions

def load_json_data(json_file_path):
    """
    Load data from a JSON file.

    Args:
        json_file_path: Path to the JSON file

    Returns:
        Dictionary containing the JSON data
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Successfully loaded data from {json_file_path}")
        return data
    except Exception as e:
        print(f"Error loading JSON file: {str(e)}")
        return None

def format_records_for_pinecone(json_data):
    """
    Format JSON data as records for Pinecone.

    Args:
        json_data: Dictionary containing the JSON data

    Returns:
        List of records formatted for Pinecone
    """
    records = []

    for chunk_id, chunk_text in json_data.items():
        record = {
            "_id": chunk_id,
            "chunk_text": chunk_text,
            "category": "eligibility_document"  # You can customize this metadata
        }
        records.append(record)

    print(f"Formatted {len(records)} records for Pinecone")
    return records

def upload_to_pinecone(records):
    """
    Upload records to Pinecone.

    Args:
        records: List of records to upload
    """
    try:
        # Initialize Pinecone client with your API key
        pc = Pinecone(api_key="pcsk_T297s_Sv2pwQ4X5kQx1q2vSCg88XwCHy4hXmX4uRHq46YDQGRbztCtmhg5baFzTSGnNG4")

        # Create a dense index with integrated embedding if it doesn't exist
        index_name = "eligibility-index"
        if not pc.has_index(index_name):
            print(f"Creating new index: {index_name}")
            pc.create_index_for_model(
                name=index_name,
                cloud="aws",
                region="us-east-1",
                embed={
                    "model": "llama-text-embed-v2",
                    "field_map": {"text": "chunk_text"}
                }
            )

        # Target the index
        eligibility_index = pc.Index(index_name)

        # Upsert the records into a namespace
        namespace = "eligibility-docs"
        eligibility_index.upsert_records(namespace, records)

        print(f"Successfully uploaded {len(records)} records to Pinecone")

        # Wait for the upserted vectors to be indexed
        import time
        print("Waiting for indexing to complete...")
        time.sleep(10)

        # View stats for the index
        stats = eligibility_index.describe_index_stats()
        print("Index stats:")
        print(stats)

        return eligibility_index

    except Exception as e:
        print(f"Error uploading to Pinecone: {str(e)}")
        return None

def search_eligibility_criteria(index, query):
    """
    Search for eligibility criteria.

    Args:
        index: Pinecone index
        query: Query string

    Returns:
        Search results
    """
    try:
        # Search the index with reranking for better results
        results = index.search(
            namespace="eligibility-docs",
            query={
                "top_k": 5,
                "inputs": {
                    'text': query
                }
            },
            rerank={
                "model": "bge-reranker-v2-m3",
                "top_n": 5,
                "rank_fields": ["chunk_text"]
            }
        )

        return results
    except Exception as e:
        print(f"Error searching Pinecone: {str(e)}")
        return None

def extract_years_from_text(text):
    """
    Extract years of experience from text.

    Args:
        text: Text to extract years from

    Returns:
        Number of years or None if not found
    """
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

def query_llm(prompt, model="llama3", max_tokens=1500):
    """
    Query a local LLM using Ollama.

    Args:
        prompt: The prompt to send to the LLM
        model: The model to use
        max_tokens: Maximum number of tokens to generate

    Returns:
        The LLM's response
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "max_tokens": max_tokens
            },
            timeout=60
        )

        if response.status_code == 200:
            return response.json()["response"]
        else:
            print(f"Error querying LLM: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error querying LLM: {str(e)}")
        return None

if __name__ == "__main__":
    # Path to your JSON file
    json_file_path = r"D:\10_Projects\consultadd hackathon\project\Backend_testing\chunks.json"

    # Load JSON data
    json_data = load_json_data(json_file_path)

    if json_data:
        # Format records for Pinecone
        records = format_records_for_pinecone(json_data)

        # Upload to Pinecone
        index = upload_to_pinecone(records)

        if index:
            # Get model description from user
            print("\nPlease provide a description of your model to evaluate eligibility:")
            model_description = input("> ")

            # Create orchestrator and evaluate eligibility
            orchestrator = EligibilityOrchestrator()
            orchestrator.evaluate_eligibility(index, model_description)
    else:
        print("Failed to load JSON data. Please check the file path and format.")