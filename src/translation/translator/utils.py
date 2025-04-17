import logging
import os
from datetime import datetime
import sys
import re
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


def extract_code_block(text, retry_limit=5):
    code_block_pattern = re.compile(r"```([\w+]+)?\s*(.*?)```", re.DOTALL)

    for attempt in range(retry_limit + 1):
        # Search for the first code block in the text
        match = code_block_pattern.search(text)

        if match:
            language = match.group(1)
            code = match.group(2).strip()
            return language, code
        elif attempt < retry_limit:
            # If no match, try to get code snippets by LLM and retry
            text = get_code_snippets(text)
        else:
            return None, None

def get_code_snippets(text):
    system_prompt = f"You are a helpful assistant."
    user_prompt = (f"{text} \n\nFrom the text, provide only the code snippets. Your response should contain nothing other then the code.\n"
                   f"Output format: ```language\n code \n```")

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]
    client = AzureOpenAI(
        api_version="2024-06-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.environ.get("CHATBOT_API_KEY")
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content

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
    code = """

    import numpy
```
    """

    code = get_code_snippets(code)
    print(code)