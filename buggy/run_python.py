import subprocess

# Define the Go file
go_file = "./dataset/avatar/Python/Code/codeforces_456_A.py"  # Path to the Go source file

# Define the input file
input_file = "./dataset/avatar/Python/TestCases/codeforces_456_A_0.in"  # Path to the input file

try:
    # Step 1: Run the Go program with input redirection
    with open(input_file, "r") as f:
        run_process = subprocess.run(
            ["python", go_file],  # Use 'go run' to compile and run the Go program
            stdin=f,
            capture_output=True,
            text=True
        )

    # Print the output from the Go program
    print("Output:")
    print(run_process.stdout)

    # Print the error message if there is any
    if run_process.stderr:
        print("Error:")
        print(run_process.stderr)

except FileNotFoundError as e:
    print(f"Error: File not found. {e}")
except Exception as e:
    print(f"An error occurred: {e}")