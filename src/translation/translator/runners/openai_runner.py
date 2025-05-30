from openai import OpenAI
import openai
import os
from dotenv import load_dotenv
import tiktoken
from src.translation.translator.utils import LOGGER
import time

logger = LOGGER("openai_runner")
logger.setLevel(LOGGER.INFO)
logger.disable_stdout()
# Load environment variables from .env file
load_dotenv()

class GPTRunner:
    def __init__(self, model_name, max_tokens=16000, temperature=0.3, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
        if os.getenv("OPENAI_API_KEY") is None:
            print("Please ensure the .env file is imported correctly.")
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

        self.api_key = os.getenv("AZURE_OPENAI_ENDPOINT")

        self.client = OpenAI(
            api_key = os.environ.get("OPENAI_API_KEY")
        )

        logger. info(f"Using {model_name}")
        if model_name == "o1-mini":
            logger.info(f"Max tokens, temperature, top_p, frequency_penalty, presence_penalty are set to default.")
        else:
            logger.info(f"max_tokens={max_tokens}, temperature={temperature}, top_p={top_p}, frequency_penalty={frequency_penalty}, presence_penalty={presence_penalty}")

    def run(self, prompt, max_tokens=None, temperature=None, top_p=None, frequency_penalty=None, presence_penalty=None):
        # Use instance values if user does not provide specific values
        if max_tokens is None:
            max_tokens = self.max_tokens
        if temperature is None:
            temperature = self.temperature
        if top_p is None:
            top_p = self.top_p
        if frequency_penalty is None:
            frequency_penalty = self.frequency_penalty
        if presence_penalty is None:
            presence_penalty = self.presence_penalty

        if self.model_name == "o1-mini" or self.model_name == "o3-mini":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=prompt
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=prompt,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )

        # encoding = tiktoken.get_encoding("cl100k_base")
        # num_tokens = len(encoding.encode(prompt[1]["content"]))
        logger.info(f"prompt: \n{prompt}")
        # logger.info(f"num_tokens: {num_tokens}")
        logger.info(f"response: \n{response.choices[0].message.content}")
        return response.choices[0].message.content

    def run_with_retry(self, prompt, max_retries=3, max_tokens=None, temperature=None, top_p=None, frequency_penalty=None, presence_penalty=None):
        if max_tokens is None:
            max_tokens = self.max_tokens
        if temperature is None:
            temperature = self.temperature
        if top_p is None:
            top_p = self.top_p
        if frequency_penalty is None:
            frequency_penalty = self.frequency_penalty
        if presence_penalty is None:
            presence_penalty = self.presence_penalty

        retries = 0
        while retries < max_retries:
            try:
                response = self.run(prompt, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
                return response
            except Exception as e:
                logger.error(f"Error occurred: {e}")
                retries += 1
                time.sleep(1)
        return None