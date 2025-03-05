import subprocess

# Define the C file and executable name
c_file = "./buggy/test/test.c"  # Path to the C source file
executable_name = "test"  # Executable name (without .out)

# Define the input file
input_file = "./buggy/test/test.in"  # Path to the input file

try:
    # Step 1: Compile the C program
    compile_process = subprocess.run(
        ["gcc", "-o", executable_name, c_file],  # Use gcc for C programs
        capture_output=True,
        text=True
    )

    # Check if compilation failed
    if compile_process.returncode != 0:
        print("Compilation failed:")
        print(compile_process.stderr)
        exit(1)

    # Step 2: Run the compiled C program with input redirection
    with open(input_file, "r") as f:
        run_process = subprocess.run(
            [f"./{executable_name}"],  # Run the compiled executable
            stdin=f,
            capture_output=True,
            text=True
        )

    # Print the output from the C program
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