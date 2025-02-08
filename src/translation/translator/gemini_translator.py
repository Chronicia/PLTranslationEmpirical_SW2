import vertexai
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerativeModel,
    Part,
    Tool,
    HarmCategory,
    HarmBlockThreshold,
    SafetySetting
)
import vertexai.preview.generative_models as generative_models
import os
from dotenv import load_dotenv
import tiktoken
from src.translation.translator.utils import LOGGER
logger = LOGGER("gemini_translator")
logger.setLevel(LOGGER.INFO)
logger.disable_stdout()
# Load environment variables from .env file
load_dotenv()

class Translator:
    type = "gemini"
    model_name = "gemini-1.5-pro-002"
    use_backup_db = False  # whether to use the backup database or not

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.0,
        "top_p": 0,
    }

    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    def __init__(self, use_backup_db=False, logger=None):
        load_dotenv(override=True)
        # self.use_backup_db = use_backup_db

        vertexai.init(project=load_dotenv("GEMINI_PROJECT"), location=load_dotenv("GEMINI_LOCATION"))

        self.model = GenerativeModel(self.model_name)

    def get_response(self, messages):
        response = "exceptional case"
        is_success = False
        max_attempts = 5
        while max_attempts > 0:
            try:
                response = self.model.generate_content(
                    messages,
                    generation_config=self.generation_config,
                    safety_settings=self.safety_settings,
                )
                is_success = True
                break
            except Exception as e:
                # Handle all OpenAI API errors
                print(f"Error: {e}")
                max_attempts -= 1
                continue
        if not is_success:
            logger.error("Error in getting response from Gemini")
            return response

        return response.text
    def translate(self, from_language, to_language, code, additional_instruction=None):
        "Use OpenAI's ChatCompletion API to get the chatbot's response"
        logger.info("Default translation prompt is used")
        prompt = code + f"\n\n Translate the code from {from_language} to {to_language}. Print only the {to_language} code. \n You may follow the additional instruction: {additional_instruction}."

        logger.info(f"Translate from {from_language} to {to_language}")
        logger.info(f"Additional_instruction: {additional_instruction if additional_instruction else 'None'}")
        logger.info(f"Code: {code}")

        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(prompt))
        logger.info(f"num_tokens: {num_tokens}")

        messages = []
        messages.append(
            Content(
                parts=[
                    Part.from_text("You are a helpful assistant.")
                ],
                role="user"
            )
        )
        messages.append(
            Content(
                parts=[
                    Part.from_text("Understand")
                ],
                role="model"
            )
        )
        messages.append(
            Content(
                parts=[
                    Part.from_text(prompt)
                ],
                role="user"
            )
        )

        logger.info(f"messages: {messages}")

        response = self.get_response(messages)
        logger.info("Translated successfully")
        logger.info(f"Translated code: \n {response}")
        return response

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