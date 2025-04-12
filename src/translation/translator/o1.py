# -*- coding: utf-8 -*-
"""
@description:
"""

import os
import json
import time
from openai import OpenAI
from src.translation.translator.utils import LOGGER
from dotenv import load_dotenv

logger = LOGGER("open-o1")
logger.setLevel(LOGGER.DEBUG)
logger.disable_stdout()

load_dotenv()
api_key: str = os.getenv("OPENAI_API_KEY")
base_url: str = os.getenv("OPENAI_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
client = OpenAI(api_key=api_key, base_url=base_url)


def make_api_call(messages, max_tokens, is_final_answer=False):
    """
    Make an API call to the OpenAI API.
    :param messages:
    :param max_tokens:
    :param is_final_answer:
    :return:
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=max_tokens,
            temperature=1.0,
            response_format={"type": "json_object"}
        )
        r = response.choices[0].message.content

        try:
            return json.loads(r)
        except json.JSONDecodeError:
            # If parsing fails, return the content as is
            return {
                "title": "Raw Response",
                "content": r,
                "next_action": "final_answer" if is_final_answer else "continue"
            }
    except Exception as e:
        error_message = f"Failed to generate {'final answer' if is_final_answer else 'step'}. Error: {str(e)}"
        return {"title": "Error", "content": error_message, "next_action": "final_answer"}


def cot_response_stream(prompt):
    """
    Generate reasoning steps for a given prompt using the CoT method. stream mode.
    messages:
    ```json
    {
        "messages": [
            {
                "role": "system",
                "content": "你是一个专家级的人工智能助手，逐步解释你的推理过程。每一步都提供一个标题，描述你在该步骤中所做的事情，并附上内容。
                决定是否需要另一步，或者是否准备好给出最终答案。以JSON格式回应，包含'title'、'content'和'next_action'（'continue'或'final_answer'）键。
                尽可能使用多个推理步骤，至少3个。注意你作为大型语言模型的局限性，以及你能做和不能做的事情。在推理中，探索替代答案。
                考虑到你可能是错误的，如果你的推理有误，指出错误的地方。全面测试所有其他可能性。你可能会错。当你说你在重新审视时，
                实际上要重新审视，并使用另一种方法进行。不要仅仅说你在重新审视。使用至少3种方法得出答案，并遵循最佳实践。
                使用与问题相同的语言回答。如果问题使用中文，答案也应为中文。",
                "next_action": "continue"
            },
            {
                "role": "user",
                "content": "prompt"
            },
            {
                "role": "assistant",
                "content": "谢谢！我将按照我的指示逐步思考，从分解问题开始。"
            }
        ]
    }
    ```
    :param prompt: str, query
    :return: steps, total_thinking_time
    """
    messages = [
{"role": "system", "content": """You are an expert AI assistant specialized in code translation between programming languages (e.g., Python to Java, Java to C). 
For each step:
1. **Analyze the Original Code**: Break down input code structure, dependencies, purpose, input and output.
2. **Identify Language-Specific Features**: Note paradigms (OOP/functional), typing systems, memory management, and unique constructs
3. **Map Equivalent Constructs**: Find target-language equivalents for data structures, libraries, and error-handling mechanisms. List all of them out.
4. **Perform translation**: Translate the source code to target language code.
5. **Self-Verification**: Check if the translated code equivalent to the source code by comparing the translated code with the source code. Ensure the translated is bug free, without any compilation, run time error and dead loop. Be aware of whether the input and output of the translated code is exactly match the source code. If the translated code consists of any bug, repeat step 4 again until bug free.

In Self-Verification stage, if you find that there's any bug in the translated code before, set 'next_action' to "translate_again".
For each step, provide:
- Title reflecting code-specific reasoning
- Detailed content including code analysis
- If you say "I will ..." in the previous step, you should perform it in the next step.
- 'next_action': 'continue' when the current step is complete.
- 'next_action': 'solve' when the current step contains some unsolved "I will" items.
- 'next_action': 'final_answer' when the verification is passed.
- 'next_action': 'translate_again' when you verified that the translated code contains bug.

Respond in JSON format with 'title', 'content', and 'next_action' (either 'continue' or 'translate_again' or 'solve' or 'final_answer') keys. 
Example of a valid JSON response:
```json
{
    "title": "Analyze the Original Code",
    "content": "To begin solving this problem, we need to carefully examine the given information and identify the crucial elements that will guide our solution process. This involves...",
    "next_action": "continue"
}```
"""},
        {"role": "user", "content": prompt},
        {"role": "assistant",
         "content": "I will now think step by step following my instructions, starting at the beginning. If I say I will perform something, I must perform it in the current step or next step. I will repeat some steps if I found any issue during my reasoning process."}
    ]

    steps = []
    step_count = 1
    total_thinking_time = 0

    while True:
        start_time = time.time()
        step_data = make_api_call(messages, 8000)
        logger.debug(f"Step {step_count}, step_data: {step_data}")
        end_time = time.time()
        thinking_time = end_time - start_time
        total_thinking_time += thinking_time
        steps.append((f"Step {step_count}: {step_data['title']}", step_data.get('content', ''), thinking_time))
        messages.append({"role": "assistant", "content": json.dumps(step_data, ensure_ascii=False)})

        if step_data['next_action'] == 'translate_again':
            messages.append({"role": "user", "content": "Sometime wrong in your previous reasoning steps, go back to step 4 to fix the problem."})
        if step_data['next_action'] == 'solve':
            messages.append({"role": "user", "content": "In your previous respond, you said that you will perform something but you did not, perrform them in the next step."})
        if step_count <= 15:
            messages.append({"role": "assistant", "content": "Wait? Did I make a mistake?"})
            messages.append({"role": "user", "content": "Translate the code again and verify the result."})
        elif step_data['next_action'] == 'final_answer' or step_count >= 50:
            break
        step_count += 1
        yield steps, total_thinking_time

    # Generate final answer
    messages.append({"role": "user", "content": "Please provide the final answer based on your reasoning above. "
                                                "output md format."})

    start_time = time.time()
    final_data = make_api_call(messages, 8000, is_final_answer=True)
    logger.debug(f"final_data: {final_data}")
    end_time = time.time()
    thinking_time = end_time - start_time
    total_thinking_time += thinking_time

    steps.append(("Final Answer", final_data.get('content', ''), thinking_time))

    yield steps, total_thinking_time


def cot_response(prompt):
    """COT response. no stream mode."""
    return list(cot_response_stream(prompt))[-1]


if __name__ == '__main__':
    prompt = """// Java Program to implement BogoSort
public class BogoSort {
	// Sorts array a[0..n-1] using Bogo sort
	void bogoSort(int[] a)
	{
		// if array is not sorted then shuffle the
		// array again
		while (isSorted(a) == false)
			shuffle(a);
	}

	// To generate permutation of the array
	void shuffle(int[] a)
	{
		// Math.random() returns a double positive
		// value, greater than or equal to 0.0 and
		// less than 1.0.
		for (int i = 0; i < a.length; i++)
			swap(a, i, (int)(Math.random() * i));
	}

	// Swapping 2 elements
	void swap(int[] a, int i, int j)
	{
		int temp = a[i];
		a[i] = a[j];
		a[j] = temp;
	}

	// To check if array is sorted or not
	boolean isSorted(int[] a)
	{
		for (int i = 1; i < a.length; i++)
			if (a[i] < a[i - 1])
				return false;
		return true;
	}

	// Prints the array
	void printArray(int[] arr)
	{
		for (int i = 0; i < arr.length; i++)
			System.out.print(arr[i] + " ");
		System.out.println();
	}

	public static void main(String[] args)
	{
		// Enter array to be sorted here
		int[] a = { 3, 2, 5, 1, 0, 4 };
		BogoSort ob = new BogoSort();

		ob.bogoSort(a);

		System.out.print("Sorted array: ");
		ob.printArray(a);
	}
}

Translate the code from Java to Python. You must think step by step to reach the final answer. Do not say "I will something" without answering, you must perform the task suggested by yourself.
"""
    # If you want to stream the response:
    response_generator = cot_response_stream(prompt)
    for steps, total_thinking_time in response_generator:
        for i, (title, content, thinking_time) in enumerate(steps):
            if title.startswith("Final Answer"):
                print(f"### {title}")
                print(content)
            else:
                print(f"{title}:")
                print(content)
        print(f"**Total thinking time so far: {total_thinking_time:.2f} seconds**")

    # Or, if you want to get the final answer only:
    # steps, total_thinking_time = cot_response(prompt)
    # for step in steps:
    #    print(step)
    # print("Total thinking time:", total_thinking_time)