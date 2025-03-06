import os
from openai import AzureOpenAI
import logging
import tiktoken
from pathlib import Path
from dotenv import load_dotenv
import re
import argparse
from tqdm import tqdm
from translator.translator import Translator

os.makedirs(f'logs', exist_ok=True)
logging.basicConfig(filename=f"logs/translation.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class Translate:
    EXTENSTIONS = {
        "Java": "java",
        "Python": "py",
        "Go": "go",
        "C": "c",
        "C++": "cpp",
        "Rust": "rs",
        "C#": "cs"
    }

    def __init__(self, model, dataset, max_tokens=16000, temperature=0.3, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0, mode="direct") -> None:
        # Set up OpenAI API key
        self.model = model
        self.dataset = dataset
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.mode = mode
        self.translator = Translator(model, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)

    def __enter__(self):
        # api_key = os.getenv("CHATBOT_API_KEY")
        # openai.api_key = api_key
        # logging.info(f"successfully set up openai api key")

        self.main_dir = os.getcwd()
        self.output_dir = os.path.join(self.main_dir, "output")

        # Find the input directory with all the code examples
        self.input_dir = Path(self.main_dir).joinpath("dataset", self.dataset)

        self.hf_cache_dir = os.path.join(self.main_dir, "hf_cache_dir")

        if not self.input_dir.exists():
            logging.error(f"directory {str(self.input_dir)} does not exist. raising FileNotFoundError")
            raise FileNotFoundError(f"Directory {str(self.input_dir)} does not exist.")

        self.out_dir = Path(self.output_dir).joinpath(self.model, self.dataset)
        if not self.out_dir.exists():
            self.out_dir.mkdir(parents=True)

        return self

    def translate(self, source, target):
        logging.info("translate: starting translation")
        snippets = list(self.input_dir.joinpath(str(source), "Code").iterdir())
        
        for source_file in tqdm(snippets, total=len(snippets), bar_format="{desc:<5.5}{percentage:3.0f}%|{bar:10}{r_bar}"):
            code_id = source_file.stem
            code_as_str = source_file.read_text(encoding="utf-8")

            target_dir = self.out_dir.joinpath(f"{source}", f"{target}")
            if not target_dir.exists():
                target_dir.mkdir(parents=True)

            filename_of_translated_code = target_dir.joinpath(f"{code_id}.{Translate.EXTENSTIONS[target]}")
            # logging.info("translate: translating code")
            # translated_code_fp = Path(filename_of_translated_code)
            # if translated_code_fp.exists():
            #     continue

            if self.mode == "direct":
                translated_code = self.translator.translate(source, target, code_as_str)
            elif self.mode == "context":
                translated_code = self.translator.translate_with_context(source, target, code_as_str)
            elif self.mode == "thinking":
                translated_code = self.translator.translate_with_thinking(source, target, code_as_str)
            elif self.mode == "code_thinking":
                translated_code = self.translator.translate_with_code_thinking(source, target, code_as_str)
            elif self.mode == "pseudocode":
                translated_code = self.translator.translate_with_pseudocode(source, target, code_as_str)

            translated_code = re.sub('public\s*class\s*.+', 'public class ' + code_id + ' {', translated_code)

            if self.dataset == 'evalplus' and target == 'Java':
                translated_code = 'package com.example;\n' + translated_code

            with open(filename_of_translated_code, "w") as f:
                print(translated_code, file=f)
                    
    def __exit__(self, exception, _, __):
        print(exception)


if __name__ == "__main__":

    load_dotenv()

    if os.getenv("AZURE_OPENAI_ENDPOINT") is None or os.getenv("CHATBOT_API_KEY") is None:
        print("Please ensure the .env file is imported correctly.")

    client = AzureOpenAI(
        api_version = "2024-06-01",
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key = os.environ.get("CHATBOT_API_KEY"),
    )
    logging.info(f"successfully set up openai api key")

    parser = argparse.ArgumentParser(description='run translation with OpenAI\'s GPT models given dataset and languages')
    parser.add_argument('--model', help='model to use for code translation. should be one of [gpt-4o,gpt-4o-mini,...]', required=True, type=str)
    parser.add_argument('--dataset', help='dataset to use for code translation. should be one of [codenet,avatar,evalplus]', required=True, type=str)
    parser.add_argument('--source_lang', help='source language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--target_lang', help='target language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--k', help='The number of highest probability vocabulary tokens to keep for top-k-filtering. Only applies for sampling mode, with range from 1 to 100.', required=True, type=int)
    parser.add_argument('--p', help='Only the most probable tokens with probabilities that add up to top_p or higher are considered during decoding. The valid range is 0.0 to 1.0. 1.0 is equivalent to disabled and is the default. Only applies to sampling mode. Also known as nucleus sampling.', required=True, type=float)
    parser.add_argument('--temperature', help='A value used to warp next-token probabilities in sampling mode. Values less than 1.0 sharpen the probability distribution, resulting in "less random" output. Values greater than 1.0 flatten the probability distribution, resulting in "more random" output. A value of 1.0 has no effect and is the default. The allowed range is 0.0 to 2.0.', required=True, type=float)
    parser.add_argument('--mode', help='generation mode to use for code translation. should be one of [direct, context, thinking, code_thinking, pseudocode]', required=True, type=str)

    args = parser.parse_args()
    source = args.source_lang
    target = args.target_lang

    with Translate(args.model, args.dataset, top_p=args.p, temperature=args.temperature, mode=args.mode) as translator:
        logging.info(f"translating examples from {source} to {target} using {args.model} and {args.dataset} dataset")
        translator.translate(source, target)
