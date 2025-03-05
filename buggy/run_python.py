import subprocess

# Define the command to run the Python script
python_command = ['python', '']

# Define the input file
input_file = ""

# Open the test input file and run the command with input redirection
with open(input_file, 'r') as f:
    result = subprocess.run(python_command, stdin=f, capture_output=True, text=True)

# Print the output from the executed Python script
print("Output:")
print(result.stdout)

# Print the error message if there is any
if result.stderr:
    print("Error:")
    print(result.stderr)