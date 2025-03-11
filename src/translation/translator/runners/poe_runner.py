import asyncio
import fastapi_poe as fp
import os
from dotenv import load_dotenv
import tiktoken
from src.translation.translator.utils import LOGGER
import time

logger = LOGGER("poe_runner")
logger.setLevel(LOGGER.INFO)
logger.disable_stdout()
# Load environment variables from .env file
load_dotenv()

class POERunner:
    def __init__(self, model_name, max_tokens=16000, temperature=0.3, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
        if os.getenv("POE_KEY") is None:
            print("Please ensure the .env file is imported correctly.")
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

        self.api_key = os.getenv("POE_KEY")

    # An asynchronous function to encapsulate the async for loop, can be livestreamed
    async def _get_responses(self, messages):
        response = ""
        async for partial in fp.get_bot_response(messages=messages, bot_name=self.model_name, api_key=self.api_key):
            response += partial.text
        return response

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

        response = asyncio.run(self._get_responses(messages=prompt))

        # encoding = tiktoken.get_encoding("cl100k_base")
        # num_tokens = len(encoding.encode(prompt[0]["content"]))
        logger.info(f"prompt: \n{prompt}")
        # logger.info(f"num_tokens: {num_tokens}")
        logger.info(f"response: \n{response}")
        return response

    def run_with_retry(self, prompt, max_retries=30, max_tokens=None, temperature=None, top_p=None, frequency_penalty=None, presence_penalty=None):
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


