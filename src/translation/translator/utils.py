import logging
import os
from datetime import datetime
import sys
import re


def extract_code_block(text):
    # Use a regular expression to find code blocks with any language, including those with special characters
    code_block_pattern = re.compile(r"```([\w+]+)?\s*(.*?)```", re.DOTALL)

    # Search for the first code block in the text
    match = code_block_pattern.search(text)

    if match:
        # Extract the language (if specified) and the code
        language = match.group(1)  # The language (e.g., C++, Python, Pseudocode)
        code = match.group(2).strip()  # The code inside the block
        return language, code
    else:
        return None
        #raise ValueError("No code block found in the text.")

def remove_cpp_prefix(directory):
    # Traverse the directory and find all .cpp files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.cpp'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = f.readlines()

                    # Remove "++" from the first line if it exists
                    if content and content[0].startswith('++'):
                        content[0] = content[0][2:]  # Remove the first two characters

                    # Write the modified content back to the file
                    with open(file_path, 'w') as f:
                        f.writelines(content)

                    print(f"Updated: {file_path}")

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

class LOGGER:
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    INFO = logging.INFO
    CRITICAL = logging.CRITICAL
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'

    def __init__(self, name, path="logs", logLevel=INFO):
        if not os.path.exists(path):
            os.makedirs(path)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logLevel)

        # File handler for logging to a file
        fileHandler = logging.FileHandler(f'{path}/{name}_{datetime.today().strftime("%Y-%m-%d-%H%M%S")}.txt', 'a',
                                          'utf-8')
        fileHandler.setFormatter(logging.Formatter(self.LOG_FORMAT))
        self.logger.addHandler(fileHandler)

        # Console handler for logging to stdout
        self.consoleHandler = logging.StreamHandler(sys.stdout)
        self.consoleHandler.setFormatter(logging.Formatter(self.LOG_FORMAT))
        self.logger.addHandler(self.consoleHandler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def setLevel(self, level):
        self.logger.setLevel(level)

    def enable_stdout(self):
        if self.consoleHandler not in self.logger.handlers:
            self.logger.addHandler(self.consoleHandler)

    def disable_stdout(self):
        if self.consoleHandler in self.logger.handlers:
            self.logger.removeHandler(self.consoleHandler)

if __name__ == "__main__":
    directory_path = '/Users/waipangchan/Documents/PLTranslationEmpirical_SW2/output/deepseek-chat/avatar/Python/C++'
    remove_cpp_prefix(directory_path)