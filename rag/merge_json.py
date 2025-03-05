import os
import json

python_dir = 'dataset/avatar/Python/Code'
java_dir = 'dataset/avatar/Java/Code'
output_file = 'rag/Python_to_Java.json'


def get_base_names(directory, extension):
    bases = set()
    for filename in os.listdir(directory):
        if filename.endswith(extension):
            # Get filename without extension
            base = os.path.splitext(filename)[0]
            bases.add(base)
    return bases


# Get common base names from both directories
python_bases = get_base_names(python_dir, '.py')
java_bases = get_base_names(java_dir, '.java')
common_bases = python_bases & java_bases

data = []

for base in common_bases:
    pair = {"filename": base}
    try:
        # Read Python file
        with open(os.path.join(python_dir, f"{base}.py"), 'r', encoding='utf-8') as f:
            pair["Python"] = f.read()

        # Read Java file
        with open(os.path.join(java_dir, f"{base}.java"), 'r', encoding='utf-8') as f:
            pair["Java"] = f.read()

        data.append(pair)
    except Exception as e:
        print(f"Error processing {base}: {e}")

# Write to JSON file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print(f"Created {len(data)} paired entries in {output_file}")