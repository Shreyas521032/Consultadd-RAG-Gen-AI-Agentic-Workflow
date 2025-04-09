# /c:/Users/shrey/Downloads/New/chunks_to_json.py
import os
import json
from typing import List, Dict, Any

def load_chunks_from_files(directory_path: str, prefix: str = "chunk_", suffix: str = "_raw_output.text") -> List[str]:
    """
    Load all chunk files from the specified directory.
    
    Args:
        directory_path: Path to directory containing chunk files
        prefix: Prefix of chunk files
        suffix: Suffix of chunk files
        
    Returns:
        List of text content from all chunk files
    """
    chunks = []
    chunk_data = {}  # Dictionary to store chunk data with their IDs
    
    # Define specific chunk files to load
    chunk_files = [
        os.path.join(directory_path, f"{prefix}1{suffix}"),
        os.path.join(directory_path, f"{prefix}2{suffix}"),
        os.path.join(directory_path, f"{prefix}4{suffix}"),
        os.path.join(directory_path, f"{prefix}7{suffix}"),
        os.path.join(directory_path, f"{prefix}8{suffix}")
    ]
    
    # Load each file if it exists
    for file_path in chunk_files:
        # Extract chunk ID from filename
        chunk_id = file_path.split(prefix)[1].split(suffix)[0]
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    chunks.append(content)
                    chunk_data[f"chunk_{chunk_id}"] = content
                    print(f"Successfully loaded: {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
        else:
            print(f"File not found: {file_path}")
    
    print(f"Loaded {len(chunks)} chunk files")
    return chunks, chunk_data

def save_chunks_to_json(chunk_data: Dict[str, str], output_file: str = "chunks.json"):
    """
    Save chunks to a JSON file.
    
    Args:
        chunk_data: Dictionary mapping chunk IDs to chunk content
        output_file: Path to output JSON file
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved chunks to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving chunks to JSON: {str(e)}")
        return False

if __name__ == "__main__":
    # Directory containing chunk files
    directory = r"D:\10_Projects\consultadd hackathon\project\Backend_testing"
    
    # List all files in the directory to see what's actually there
    print("Files in directory:")
    for file in os.listdir(directory):
        print(f"  - {file}")
    
    # Try loading with different extensions
    print("\nTrying with .txt extension:")
    chunks, chunk_data = load_chunks_from_files(directory, suffix="_raw_output.txt")
    
    # Check if any chunks were loaded
    if chunks:
        print(f"\nLoaded {len(chunks)} chunks with .txt extension")
        
        # Save chunks to JSON file
        output_file = os.path.join(directory, "chunks.json")
        save_chunks_to_json(chunk_data, output_file)
        
        # Print a preview of the JSON structure
        print("\nJSON structure preview:")
        preview = {k: v[:100] + "..." if len(v) > 100 else v for k, v in list(chunk_data.items())[:2]}
        print(json.dumps(preview, indent=2))
    else:
        print("\nNo chunks were loaded. Cannot create JSON file.")