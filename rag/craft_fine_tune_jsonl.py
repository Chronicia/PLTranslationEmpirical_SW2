import json

# Input and output file paths
input_file = 'rag/Python_to_Java.json'  # Existing JSON file
output_file = 'rag/Java_to_Python.jsonl'  # New JSONL file

# Read the existing JSON file
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Open the output JSONL file
with open(output_file, 'w', encoding='utf-8') as f:
    for entry in data:
        # Extract Python and Java code
        python_code = entry["Python"]
        java_code = entry["Java"]

        # Create the JSONL structure
        jsonl_entry = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{java_code}\n\nTranslate the code from Java to Python. Print only the Python code."},
                {"role": "assistant", "content": f"Here is the translated code:\n ```\n{python_code}\n```"}
            ]
        }

        # Write the JSONL entry to the file
        f.write(json.dumps(jsonl_entry, ensure_ascii=False) + "\n")

print(f"Created {len(data)} entries in {output_file}")