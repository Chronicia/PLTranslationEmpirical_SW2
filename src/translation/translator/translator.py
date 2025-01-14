from lib2to3.fixes.fix_input import context

from openai import AzureOpenAI
import openai
import os
from dotenv import load_dotenv
import tiktoken
from src.translation.translator.utils import LOGGER
logger = LOGGER("translator")
logger.setLevel(LOGGER.INFO)
logger.disable_stdout()
# Load environment variables from .env file
load_dotenv()


class Translator:
    model_name = "gpt-4o-mini"
    def __init__(self):
        if os.getenv("AZURE_OPENAI_ENDPOINT") is None or os.getenv("CHATBOT_API_KEY") is None:
            print("Please ensure the .env file is imported correctly.")
        self.client = AzureOpenAI(
            api_version = "2024-06-01",
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key = os.environ.get("CHATBOT_API_KEY"),
        )
        self.system_prompt = "You are a helpful assistant."

    def translate(self, from_language, to_language, code, additional_instruction=None, default=True):
        "Use OpenAI's ChatCompletion API to get the chatbot's response"
        if default:
            logger.info("Default translation prompt is used")
            context = self.get_context(from_language, code)
            logger.info(f"Context: \n{context}")
            prompt = code + f"\n\n Translate the code from {from_language} to {to_language}. Print only the {to_language} code. \n You may follow the additional instruction: {additional_instruction}. \n\n For your reference, the intention of this code is {context}"
        else:
            logger.info("Custom translation prompt is used")
            prompt = code

        logger.info(f"Translate from {from_language} to {to_language}")
        logger.info(f"Additional_instruction: {additional_instruction if additional_instruction else 'None'}")
        logger.info(f"Code: {code}")

        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(prompt))
        logger.info(f"num_tokens: {num_tokens}")

        messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ]

        logger.info(f"messages: {messages}")

        base_params = {
            "model": self.model_name,
            "temperature": 0.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "messages": messages,
        }

        response = "exceptional case"
        is_success = False
        max_attempts = 5
        while max_attempts > 0:
            try:
                response = self.client.chat.completions.create(**base_params)
                is_success = True
                break
            except openai.OpenAIError as e:
                # Handle all OpenAI API errors
                print(f"Error: {e}")
                max_attempts -= 1
                continue
        if not is_success:
            logger.error("Error in performing translation")
            return response

        # Find the first response from the chatbot that has text in it (some responses may not have text)
        for choice in response.choices:
            if "text" in choice:
                logger.info("Translated successfully")
                return choice.text
        logger.info("Translated successfully")
        logger.info(f"Translated code: \n {response.choices[0].message.content}")
        return response.choices[0].message.content

    def get_context(self, language, code):
        system_prompt = f"You are an assistant to analyze programming code."
        prompt = f"{code} \n\n Please analyze the following {language} code snippet.\n Identify the input, output of the code. Translate the code implementation into pseudocode. Finally, give a 100 words brief summary on the intention of the code."
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ]
        base_params = {
            "model": self.model_name,
            "temperature": 0.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "messages": messages,
        }

        response = self.client.chat.completions.create(**base_params)
        return response.choices[0].message.content


if __name__ == "__main__":
    translator = Translator()
    user_prompt = """
def merge_sort(arr):
    if len(arr) > 1:
        # Finding the mid of the array
        mid = len(arr) // 2

        # Dividing the array elements into 2 halves
        left_half = arr[:mid]
        right_half = arr[mid:]

        # Recursively sorting the halves
        merge_sort(left_half)
        merge_sort(right_half)

        # Initialize pointers for left, right and merged array
        i = j = k = 0

        # Copy data to the temporary arrays left_half and right_half
        while i < len(left_half) and j < len(right_half):
            if left_half[i] < right_half[j]:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
            k += 1

        # Checking if any element was left in the left_half
        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1

        # Checking if any element was left in the right_half
        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1

# Example usage:
arr = [38, 27, 43, 3, 9, 82, 10]
print("Original array:", arr)
merge_sort(arr)
print("Sorted array:", arr)
"""
    additional_instruction = ""
    from_language = "Python"
    to_language = "Go"
    response = translator.translate(from_language, to_language, user_prompt, additional_instruction)

    code = response.replace(f"```{'cpp' if to_language.lower() == 'c++' else to_language.lower()}", "").replace("```",
                                                                                                                "")
    os.makedirs("output", exist_ok=True)
    if to_language.lower() == "c":
        output_name = "translated_code.c"
    elif to_language.lower() == "c++":
        output_name = "translated_code.cpp"
    elif to_language.lower() == "go":
        output_name = "translated_code.go"
    elif to_language.lower() == "java":
        output_name = "translated_code.java"
    elif to_language.lower() == "python":
        output_name = "translated_code.py"
    else:
        output_name = "translated_code.txt"

    with open(f"output/{output_name}", "w") as f:
        f.write(code)