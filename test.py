import subprocess

# Define the command to run the Python script
python_command = ['python', 'buggy/codeforces_445_A.py']

# Open the test input file and run the command with input redirection
with open('buggy/codeforces_445_A_0.in', 'r') as input_file:
    result = subprocess.run(python_command, stdin=input_file, capture_output=True, text=True)

# Print the output from the executed Python script
print("Output:")
print(result.stdout)

# Print the error message if there is any
if result.stderr:
    print("Error:")
    print(result.stderr)