import subprocess

# Define the Java file and class name
java_file = "./buggy/test/test.java"
class_name = "test"  # Class name should match the file name

# Define the input file
input_file = "./buggy/test/test.in"

try:
    # Step 1: Compile the Java program
    compile_process = subprocess.run(
        ["javac", java_file],
        capture_output=True,
        text=True
    )

    # Check if compilation failed
    if compile_process.returncode != 0:
        print("Compilation failed:")
        print(compile_process.stderr)
        exit(1)

    # Step 2: Run the Java program with input redirection
    with open(input_file, "r") as f:
        run_process = subprocess.run(
            ["java", "-cp", "./buggy/test", class_name],
            stdin=f,
            capture_output=True,
            text=True
        )

    # Print the output from the Java program
    print("Output:")
    print(run_process.stdout)

    # Print the error message if there is any
    if run_process.stderr:
        print("Error:")
        print(run_process.stderr)

except FileNotFoundError:
    print("Error: Java compiler (javac) or Java runtime (java) not found.")
except Exception as e:
    print(f"An error occurred: {e}")