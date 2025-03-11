from openai import OpenAI
import os
from dotenv import load_dotenv
import tiktoken
from src.translation.translator.utils import LOGGER
import time

logger = LOGGER("deepseek_runner")
logger.setLevel(LOGGER.INFO)
logger.disable_stdout()
# Load environment variables from .env file
load_dotenv()

class DeepseekRunner:
    def __init__(self, model_name, max_tokens=8192, temperature=0.3, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
        if os.getenv("DEEPSEEK_BASE_URL") is None or os.getenv("DEEPSEEK_API_KEY") is None:
            print("Please ensure the .env file is imported correctly.")
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.client = OpenAI(
            base_url = os.getenv("DEEPSEEK_BASE_URL"),
            api_key = self.api_key
        )

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

        logger.info(f"Using {self.model_name} model")
        logger.info(f"prompt: \n{prompt}")
        response = self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            messages= prompt
        )

        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(prompt[1]["content"]))
        logger.info(f"num_tokens: {num_tokens}")
        if self.model_name.startswith("deepseek-reasoner"):
            logger.info(f"reasoning response: \n{response.choices[0].message.reasoning_content}")
        logger.info(f"response: \n{response.choices[0].message.content}")
        return response.choices[0].message.content

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
                logger.info("Retrying: ".format(retries + 1))
                retries += 1
                time.sleep(1)
        raise ValueError(f"Max retries exceeded: {max_retries}")