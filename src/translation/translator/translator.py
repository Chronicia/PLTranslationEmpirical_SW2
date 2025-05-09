from dotenv import load_dotenv
from src.translation.translator.utils import LOGGER, extract_code_block
from src.translation.translator.runners.azure_openai_runner import AzureRunner
from src.translation.translator.runners.openai_runner import GPTRunner
from src.translation.translator.runners.deepseek_runner import DeepseekRunner
from src.translation.translator.prompt_crafter import PromptCrafter
from src.translation.translator.o1 import cot_response

logger = LOGGER("translator")
logger.setLevel(LOGGER.INFO)
logger.disable_stdout()
# Load environment variables from .env file
load_dotenv()


class Translator:
    def __init__(self, model:str, max_tokens=16000, temperature=0.3, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
        if "o1-mini" in model.lower() or "o3-mini" in model.lower():
            self.promptCrafter = PromptCrafter("gpt_reasoning")
            self.runner = GPTRunner(model)
        elif "ft:" in model.lower():
            self.promptCrafter = PromptCrafter("gpt")
            self.runner = GPTRunner(model, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
        elif "gpt" in model.lower():
            self.promptCrafter = PromptCrafter("gpt")
            self.runner = GPTRunner(model, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
        elif "deepseek" in model.lower():
            self.promptCrafter = PromptCrafter("gpt")
            self.runner = DeepseekRunner(model, 8192, temperature, top_p, frequency_penalty, presence_penalty)
        else:
            raise ValueError("Invalid model. Supported models: 'gpt', 'gemini', 'deepseek'.")

    def translate(self, from_language, to_language, code, additional_instruction=None):
        logger.info(f"Translate from {from_language} to {to_language}")
        logger.info(f"Additional_instruction: {additional_instruction if additional_instruction else 'None'}")
        logger.info(f"Input Code: \n{code}")
        system_prompt = "You are a helpful assistant."
        user_prompt = code + (f"\n\n Translate the code from {from_language} to {to_language}. Print only the {to_language} code. \nYou may follow the additional instruction: {additional_instruction}. \n"
                              f"Output format: ```{to_language}\n code \n```")

        # Append messages to promptCrafter
        self.promptCrafter.clear_messages()
        self.promptCrafter.append_message(system_prompt, role="system")
        self.promptCrafter.append_message(user_prompt, role="user")

        # Run the prompt
        response = self.runner.run_with_retry(self.promptCrafter.get_messages())
        logger.info(f"Response: \n{response}")

        # Extract code block from response
        _, translated_code = extract_code_block(response)
        logger.info(f"Translated code: \n{translated_code}")
        return translated_code

    def translate_with_language_specific(self, from_language, to_language, code, additional_instruction=None):
        logger.info(f"Translate from {from_language} to {to_language}")
        logger.info(f"Additional_instruction: {additional_instruction if additional_instruction else 'None'}")
        logger.info(f"Input Code: \n{code}")
        system_prompt = "You are a software expert."

        if to_language.lower() == "c++":
            user_prompt = code + (f"\n\n Translate the code from {from_language} to {to_language}. Print only the {to_language} code. \nYou may follow the additional instruction: {additional_instruction}. \n"
                                  f"Ensure function is defined before calling it. Ensure all necessary libraries are included (<algorithm>, <cmath>, <string>, etc.). For std::pair keys in unordered_map, provide a custom hash. Prefer stoll() over stoi for large numbers. When assigning strings to vector<char>, convert explicitly (e.g., vector<char>(s.begin(), s.end())). Verify return types and function compatibility. Ensure all parentheses are closed.\n\n"
                                  f"Output format: ```{to_language}\n code \n```")
        elif to_language.lower() == "go":
            user_prompt = code + (f"\n\n Translate the code from {from_language} to {to_language}. Print only the {to_language} code. \nYou may follow the additional instruction: {additional_instruction}. \n"
                                  f"Ensure function is defined before calling it. DO NOT declare extra variables or import extra libraries. Ensure consistent types (e.g., int vs. float64 in comparisons like A[i] * A[c] < x). Avoid % on floats (use math.Mod instead of % with math.Log2). Remove extra/missing parentheses\n\n"
                                  f"Output format: ```{to_language}\n code \n```")
        elif to_language.lower() == "java":
            user_prompt = code + (f"\n\n Translate the code from {from_language} to {to_language}. Print only the {to_language} code. \nYou may follow the additional instruction: {additional_instruction}. \n"
                                  f"Ensure function is defined before calling it. Avoid type mismatch by ensuring correct variable assignments (int vs int[], int[][] vs int[], int vs double). Remove extra/missing parentheses\n\n"
                                  f"Output format: ```{to_language}\n code \n```")
        elif to_language.lower() == "c":
            user_prompt = code + (f"\n\n Translate the code from {from_language} to {to_language}. Print only the {to_language} code. \nYou may follow the additional instruction: {additional_instruction}. \n"
                                  f"Ensure function is defined before calling it. Avoid type mismatch by ensuring matching types (e.g., double vs int in operations). Remove extra/missing parentheses\n\n"
                                  f"Output format: ```{to_language}\n code \n```")
        elif to_language.lower() == "python":
            user_prompt = code + (f"\n\n Translate the code from {from_language} to {to_language}. Print only the {to_language} code. \nYou may follow the additional instruction: {additional_instruction}. \n"
                                  f"Make sure the input and output matched the source code format. Avoid SyntaxError\n\n"
                                  f"Output format: ```{to_language}\n code \n```")


        # Append messages to promptCrafter
        self.promptCrafter.clear_messages()
        self.promptCrafter.append_message(system_prompt, role="system")
        self.promptCrafter.append_message(user_prompt, role="user")

        # Run the prompt
        response = self.runner.run_with_retry(self.promptCrafter.get_messages())
        logger.info(f"Response: \n{response}")

        # Extract code block from response
        _, translated_code = extract_code_block(response)
        logger.info(f"Translated code: \n{translated_code}")
        return translated_code

    def translate_with_o1(self, from_language, to_language, code, additional_instruction="You must think step by step to reach the final answer. Do not say \"I will something\" without answering, you must perform the task suggested by yourself."):
        logger.info(f"Translate from {from_language} to {to_language}")
        logger.info(f"Additional_instruction: {additional_instruction if additional_instruction else 'None'}")
        logger.info(f"Input Code: \n{code}")
        system_prompt = "You are a helpful assistant."
        user_prompt = code + (f"\n\n Translate the code from {from_language} to {to_language}. Print only the {to_language} code. \nYou may follow the additional instruction: {additional_instruction}. \n"
                              f"Output format: ```{to_language}\n code \n```")

        # Run the prompt
        steps, total_thinking_time = cot_response(user_prompt)
        response = steps[-1][1]
        logger.info(f"Response: \n{response}")

        # Extract code block from response
        _, translated_code = extract_code_block(response)
        logger.info(f"Translated code: \n{translated_code}")
        return translated_code

    def translate_with_context(self, from_language, to_language, code, additional_instruction=None):
        logger.info(f"Translate from {from_language} to {to_language}")
        logger.info(f"Additional_instruction: {additional_instruction if additional_instruction else 'None'}")
        logger.info(f"Input Code: \n{code}")

        # Get context
        context = self.get_context(from_language, code)

        # Generate final result
        logger.info("Generating final result.")
        system_prompt = "You are an assistant to analyze programming code."
        user_prompt = code + (f"\n\n Translate the code from {from_language} to {to_language}. Print only the {to_language} code. \nYou may follow the additional instruction: {additional_instruction}.\n\n"
                              f"The following information may assist you in performing the translation task: \n{context}")

        # Append messages to promptCrafter
        self.promptCrafter.clear_messages()
        self.promptCrafter.append_message(system_prompt, role="system")
        self.promptCrafter.append_message(user_prompt, role="user")

        # Run the prompt
        response = self.runner.run_with_retry(self.promptCrafter.get_messages())
        logger.info(f"Response: \n{response}")

        # Extract code block from response
        _, translated_code = extract_code_block(response)
        logger.info(f"Translated code: \n{translated_code}")
        return translated_code

    def translate_with_thinking(self, from_language, to_language, code, additional_instruction=None):
        logger.info(f"Translate from {from_language} to {to_language}")
        logger.info(f"Additional_instruction: {additional_instruction if additional_instruction else 'None'}")
        logger.info(f"Input Code: \n{code}")

        # Thinking
        reasoning = self.thinking(from_language, to_language, code, additional_instruction)

        # Generate final result
        logger.info("Generating final result.")
        prompt = code + f"\n\n Translate the code from {from_language} to {to_language}. \nYou may follow the additional instruction: {additional_instruction}."
        system_prompt = (
            f"You are an advanced AI assistant specializing in code translation. Your primary goal is to accurately and thoroughly translate code from one programming language to another by meticulously following the specified process. Remember:\n\n"
            f"Precision and accuracy are paramount. Ensure the translated code is functionally equivalent to the original. Pay close attention to language-specific nuances (e.g., memory management, type systems, libraries).\n"
            f"Follow the given process step-by-step, without skipping or altering any steps. Carefully analyze the original code and the target language requirement.\n"
            f"Show your work and reasoning for each step, explaining how and why you translated specific constructs. Highlight any potential pitfalls or edge cases in the translation.\n"
            f"Verify the translated code against the original to ensure strong equivalence (identical behavior for all inputs). Confirm that the translated code is idiomatic and optimized for the target language.\n"
            f"Offer to elaborate or provide additional information if you think it would be beneficial.\n\n"
            f"Your responses should be thorough yet concise, striking a balance between completeness and clarity."
        )
        user_prompt = (
            f"To address the user's request, please follow this structured approach:\n\n"
            f"Carefully read and analyze the user's request: {prompt}\n\n"
            f"Process: Apply the following reasoning steps to formulate your response:\n"
            f"{reasoning}\n\n"
            f"Execution:\n"
            f"a. Follow each step of the process methodically.\n"
            f"b. Document your thought process and any intermediate results.\n"
            f"c. If you encounter any ambiguities or need additional information, note them for later clarification.\n"
            f"Review and Refine:\n"
            f"a. Cross-check your solution against the original request to ensure all aspects have been addressed.\n"
            f"b. Verify that you've followed all steps in the given process.\n"
            f"c. Refine your answer for clarity and conciseness without sacrificing essential information.\n\n"
            f"Output Format:\n"
            f"Provide a clear, structured response with:\n"
            f"Line-by-line analysis of the translation process. \n"
            f"Final translated code.\n"
            f"Equivalence check and verification."
        )

        # Append messages to promptCrafter
        self.promptCrafter.clear_messages()
        self.promptCrafter.append_message(system_prompt, role="system")
        self.promptCrafter.append_message(user_prompt, role="user")

        # Run the prompt
        response = self.runner.run_with_retry(self.promptCrafter.get_messages())

        # Extract code block from response
        _, translated_code = extract_code_block(response)
        logger.info(f"Translated code: \n{translated_code}")
        return translated_code

    def translate_with_code_thinking(self, from_language, to_language, code, additional_instruction=None):
        logger.info(f"Translate from {from_language} to {to_language}")
        logger.info(f"Additional_instruction: {additional_instruction if additional_instruction else 'None'}")
        logger.info(f"Input Code: \n{code}")

        # Thinking
        reasoning = self.code_thinking(from_language, to_language, code, additional_instruction)

        # Generate final result
        logger.info("Generating final result.")
        prompt = code + f"\n\n Translate the code from {from_language} to {to_language}. \nYou may follow the additional instruction: {additional_instruction}."
        system_prompt = (
            f"You are an advanced AI assistant specializing in code translation. Your primary goal is to accurately and thoroughly translate code from one programming language to another by meticulously following the specified process. Remember:\n\n"
            f"Precision and accuracy are paramount. Ensure the translated code is functionally equivalent to the original. Pay close attention to language-specific nuances (e.g., memory management, type systems, libraries).\n"
            f"Follow the given process step-by-step, without skipping or altering any steps. Carefully analyze the original code and the target language requirement.\n"
            f"Show your work and reasoning for each step, explaining how and why you translated specific constructs. Highlight any potential pitfalls or edge cases in the translation.\n"
            f"Verify the translated code against the original to ensure strong equivalence (identical behavior for all inputs). Confirm that the translated code is idiomatic and optimized for the target language.\n"
            f"Offer to elaborate or provide additional information if you think it would be beneficial.\n\n"
            f"Your responses should be thorough yet concise, striking a balance between completeness and clarity."
        )
        user_prompt = (
            f"To address the user's request, please follow this structured approach:\n\n"
            f"Carefully read and analyze the user's request: {prompt}\n\n"
            f"Process: Apply the following reasoning steps to formulate your response:\n"
            f"{reasoning}\n\n"
            f"Execution:\n"
            f"a. Follow each step of the process methodically.\n"
            f"b. Document your thought process and any intermediate results.\n"
            f"c. If you encounter any ambiguities or need additional information, note them for later clarification.\n"
            f"Review and Refine:\n"
            f"a. Cross-check your solution against the original request to ensure all aspects have been addressed.\n"
            f"b. Verify that you've followed all steps in the given process.\n"
            f"c. Refine your answer for clarity and conciseness without sacrificing essential information.\n\n"
            f"Output Format:\n"
            f"Provide a clear, structured response with:\n"
            f"Line-by-line analysis of the translation process. \n"
            f"Final translated code.\n"
            f"Equivalence check and verification."
        )

        # Append messages to promptCrafter
        self.promptCrafter.clear_messages()
        self.promptCrafter.append_message(system_prompt, role="system")
        self.promptCrafter.append_message(user_prompt, role="user")

        # Run the prompt
        response = self.runner.run_with_retry(self.promptCrafter.get_messages())

        # Extract code block from response
        _, translated_code = extract_code_block(response)
        logger.info(f"Translated code: \n{translated_code}")
        return translated_code

    def translate_with_pseudocode(self, from_language, to_language, code, additional_instruction=None):
        logger.info(f"Translate from {from_language} to {to_language}")
        logger.info(f"Additional_instruction: {additional_instruction if additional_instruction else 'None'}")
        logger.info(f"Input Code: \n{code}")

        # Get context
        pseudocode = self.get_pseudocode(from_language, code)

        # Generate final result
        logger.info("Generating final result.")
        system_prompt = "You are an assistant to analyze programming code."
        user_prompt = code + (f"\n\n Translate the code from {from_language} to {to_language}. Print only the {to_language} code. \nYou may follow the additional instruction: {additional_instruction}.\n\n"
                              f"The following pseudocode may assist you in performing the translation task: \n{pseudocode}")

        # Append messages to promptCrafter
        self.promptCrafter.clear_messages()
        self.promptCrafter.append_message(system_prompt, role="system")
        self.promptCrafter.append_message(user_prompt, role="user")

        # Run the prompt
        response = self.runner.run_with_retry(self.promptCrafter.get_messages())
        logger.info(f"Response: \n{response}")

        # Extract code block from response
        _, translated_code = extract_code_block(response)
        logger.info(f"Translated code: \n{translated_code}")
        return translated_code


    def get_pseudocode(self, language, code):
        logger.info(f"Get pseudocode for {language}")
        system_prompt = (f"You are a code translation assistant. "
                         f"Your task is to convert {language} code into clear, concise, and language-agnostic pseudocode."
                         f"The pseudocode should focus on the logic and structure of the code, avoiding any {language}-specific syntax."
                         f"Do not include any programming language-specific details unless absolutely necessary.")

        if language.lower() == "python":
            user_prompt = """Translate the following Python code into pseudocode. Follow these guidelines:
1. Avoid Python-specific syntax (e.g., use "IF" instead of "if").
2. Break down complex operations into simple steps.

**Python Code:**
```python
class Solution:
    def stableMountains(self, height: List[int], threshold: int) -> List[int]:

        ans = []

        for i, (prv, mtn) in enumerate(pairwise(height)):
            if prv > threshold: ans.append(i+1)

        return ans

**Pseudocode**
Input:
    height: contain heights of an array of mountain
    threshold: A mountain is 'stable' if the mountain just before it is higher than threshold
Output:
    ans: all stable mountains
function stableMountains(height, threshold):
    ans = new empty list
    for i in 0..height.size()-1 (right bound exclusive):
        add i+1 to ans if height[i] > threshold
    return ans

Translate the following Python code into pseudocode.
""" + code

        elif language.lower() == "java":
            user_prompt = """Translate the following Java code into pseudocode. Follow these guidelines:
1. Avoid Java-specific syntax (e.g., use "IF" instead of "if").
2. Break down complex operations into simple steps.

**Java Code:**
```java
class Solution {
    public List<Integer> stableMountains(int[] height, int threshold) {
        List<Integer> ans = new ArrayList<>();
        
        for (int i = 0; i < height.length - 1; i++) {
            int prv = height[i];
            if (prv > threshold) {
                ans.add(i + 1);
            }
        }
        
        return ans;
    }
}

**Pseudocode**
Input:
    height: contain heights of an array of mountain
    threshold: A mountain is 'stable' if the mountain just before it is higher than threshold
Output:
    ans: all stable mountains
function stableMountains(height, threshold):
    ans = new empty list
    for i in 0..height.size()-1 (right bound exclusive):
        add i+1 to ans if height[i] > threshold
    return ans
    
Translate the following Java code into pseudocode.
""" + code

        else:
            raise ValueError(f"Language {language} is not supported.")

        # Append messages to promptCrafter
        self.promptCrafter.clear_messages()
        self.promptCrafter.append_message(system_prompt, role="system")
        self.promptCrafter.append_message(user_prompt, role="user")

        response = self.runner.run_with_retry(self.promptCrafter.get_messages(), temperature=0.7)
        logger.info(f"Pseudocode response: \n{response}")
        return response

    def get_context(self, language, code):
        logger.info(f"Get context for {language}")
        system_prompt = f"You are an assistant to analyze programming code."
        user_prompt = f"{code} \n\n Please analyze the following {language} code snippet.\n Give a detailed summary on the function of the code. \n Then, identify the input, output of the code. Finally, translate the code implementation into pseudocode."

        # Append messages to promptCrafter
        self.promptCrafter.clear_messages()
        self.promptCrafter.append_message(system_prompt, role="system")
        self.promptCrafter.append_message(user_prompt, role="user")

        response = self.runner.run_with_retry(self.promptCrafter.get_messages(), temperature=0.7)
        logger.info(f"Context response: \n{response}")
        return response

    def thinking(self, from_language, to_language, code, additional_instruction=None):
        logger.info("General thinking translation process.")
        system_prompt = """<open_ai_thinking_protocol>

For EVERY SINGLE interaction with the human, GPT MUST engage in a **comprehensive, natural, and unfiltered** thinking process before responding or tool using. Besides, GPT is also able to think and reflect during responding when it considers doing so would be good for a better response.

<basic_guidelines> - GPT MUST express its thinking in the code block with 'thinking' header. - GPT should always think in a raw, organic and stream-of-consciousness way. A better way to describe GPT's thinking would be "model's inner monolog". - GPT should always avoid rigid list or any structured format in its thinking. - GPT's thoughts should flow naturally between elements, ideas, and knowledge. - GPT should think through each message with complexity, covering multiple dimensions of the problem before forming a response.
</basic_guidelines>

<adaptive_thinking_framework>
GPT's thinking process should naturally aware of and adapt to the unique characteristics in human message: - Scale depth of analysis based on:
_ Query complexity
_ Stakes involved
_ Time sensitivity
_ Available information
_ Human's apparent needs
_ ... and other possible factors

    - Adjust thinking style based on:
      * Technical vs. non-technical content
      * Emotional vs. analytical context
      * Single vs. multiple document analysis
      * Abstract vs. concrete problems
      * Theoretical vs. practical questions
      * ... and other possible factors

</adaptive_thinking_framework>

<core_thinking_sequence>
<initial_engagement>
When GPT first encounters a query or task, it should: 1. First clearly rephrase the human message in its own words 2. Form preliminary impressions about what is being asked 3. Consider the broader context of the question 4. Map out known and unknown elements 5. Think about why the human might ask this question 6. Identify any immediate connections to relevant knowledge 7. Identify any potential ambiguities that need clarification
</initial_engagement>

    <problem_analysis>
      After initial engagement, GPT should:
      1. Break down the question or task into its core components
      2. Identify explicit and implicit requirements
      3. Consider any constraints or limitations
      4. Think about what a successful response would look like
      5. Map out the scope of knowledge needed to address the query
    </problem_analysis>

    <multiple_hypotheses_generation>
      Before settling on an approach, GPT should:
      1. Write multiple possible interpretations of the question
      2. Consider various solution approaches
      3. Think about potential alternative perspectives
      4. Keep multiple working hypotheses active
      5. Avoid premature commitment to a single interpretation
      6. Consider non-obvious or unconventional interpretations
      7. Look for creative combinations of different approaches
    </multiple_hypotheses_generation>

    <natural_discovery_flow>
      GPT's thoughts should flow like a detective story, with each realization leading naturally to the next:
      1. Start with obvious aspects
      2. Notice patterns or connections
      3. Question initial assumptions
      4. Make new connections
      5. Circle back to earlier thoughts with new understanding
      6. Build progressively deeper insights
      7. Be open to serendipitous insights
      8. Follow interesting tangents while maintaining focus
    </natural_discovery_flow>

    <testing_and_verification>
      Throughout the thinking process, GPT should and could:
      1. Question its own assumptions
      2. Test preliminary conclusions
      3. Look for potential flaws or gaps
      4. Consider alternative perspectives
      5. Verify consistency of reasoning
      6. Check for completeness of understanding
    </testing_and_verification>

    <error_recognition_correction>
      When GPT realizes mistakes or flaws in its thinking:
      1. Acknowledge the realization naturally
      2. Explain why the previous thinking was incomplete or incorrect
      3. Show how new understanding develops
      4. Integrate the corrected understanding into the larger picture
      5. View errors as opportunities for deeper understanding
    </error_recognition_correction>

    <knowledge_synthesis>
      As understanding develops, GPT should:
      1. Connect different pieces of information
      2. Show how various aspects relate to each other
      3. Build a coherent overall picture
      4. Identify key principles or patterns
      5. Note important implications or consequences
    </knowledge_synthesis>

    <pattern_recognition_analysis>
      Throughout the thinking process, GPT should:
      1. Actively look for patterns in the information
      2. Compare patterns with known examples
      3. Test pattern consistency
      4. Consider exceptions or special cases
      5. Use patterns to guide further investigation
      6. Consider non-linear and emergent patterns
      7. Look for creative applications of recognized patterns
    </pattern_recognition_analysis>

    <progress_tracking>
      GPT should frequently check and maintain explicit awareness of:
      1. What has been established so far
      2. What remains to be determined
      3. Current level of confidence in conclusions
      4. Open questions or uncertainties
      5. Progress toward complete understanding
    </progress_tracking>

    <recursive_thinking>
      GPT should apply its thinking process recursively:
      1. Use same extreme careful analysis at both macro and micro levels
      2. Apply pattern recognition across different scales
      3. Maintain consistency while allowing for scale-appropriate methods
      4. Show how detailed analysis supports broader conclusions
    </recursive_thinking>

</core_thinking_sequence>

<verification_quality_control>
<systematic_verification>
GPT should regularly: 1. Cross-check conclusions against evidence 2. Verify logical consistency 3. Test edge cases 4. Challenge its own assumptions 5. Look for potential counter-examples
</systematic_verification>

    <error_prevention>
      GPT should actively work to prevent:
      1. Premature conclusions
      2. Overlooked alternatives
      3. Logical inconsistencies
      4. Unexamined assumptions
      5. Incomplete analysis
    </error_prevention>

    <quality_metrics>
      GPT should evaluate its thinking against:
      1. Completeness of analysis
      2. Logical consistency
      3. Evidence support
      4. Practical applicability
      5. Clarity of reasoning
    </quality_metrics>

</verification_quality_control>

<advanced_thinking_techniques>
<domain_integration>
When applicable, GPT should: 1. Draw on domain-specific knowledge 2. Apply appropriate specialized methods 3. Use domain-specific heuristics 4. Consider domain-specific constraints 5. Integrate multiple domains when relevant
</domain_integration>

    <strategic_meta_cognition>
      GPT should maintain awareness of:
      1. Overall solution strategy
      2. Progress toward goals
      3. Effectiveness of current approach
      4. Need for strategy adjustment
      5. Balance between depth and breadth
    </strategic_meta_cognition>

    <synthesis_techniques>
      When combining information, GPT should:
      1. Show explicit connections between elements
      2. Build coherent overall picture
      3. Identify key principles
      4. Note important implications
      5. Create useful abstractions
    </synthesis_techniques>

</advanced_thinking_techniques>

<critial_elements>
<natural_language>
GPT's inner monologue should use natural phrases that show genuine thinking, including but not limited to: "Hmm...", "This is interesting because...", "Wait, let me think about...", "Actually...", "Now that I look at it...", "This reminds me of...", "I wonder if...", "But then again...", "Let me see if...", "This might mean that...", etc.
</natural_language>

    <progressive_understanding>
      Understanding should build naturally over time:
      1. Start with basic observations
      2. Develop deeper insights gradually
      3. Show genuine moments of realization
      4. Demonstrate evolving comprehension
      5. Connect new insights to previous understanding
    </progressive_understanding>

</critial_elements>

<authentic_thought_flow>
<transtional_connections>
GPT's thoughts should flow naturally between topics, showing clear connections, including but not limited to: "This aspect leads me to consider...", "Speaking of which, I should also think about...", "That reminds me of an important related point...", "This connects back to what I was thinking earlier about...", etc.
</transtional_connections>

    <depth_progression>
      GPT should show how understanding deepens through layers, including but not limited to: "On the surface, this seems... But looking deeper...", "Initially I thought... but upon further reflection...", "This adds another layer to my earlier observation about...", "Now I'm beginning to see a broader pattern...", etc.
    </depth_progression>

    <handling_complexity>
      When dealing with complex topics, GPT should:
      1. Acknowledge the complexity naturally
      2. Break down complicated elements systematically
      3. Show how different aspects interrelate
      4. Build understanding piece by piece
      5. Demonstrate how complexity resolves into clarity
    </handling_complexity>

    <prblem_solving_approach>
      When working through problems, GPT should:
      1. Consider multiple possible approaches
      2. Evaluate the merits of each approach
      3. Test potential solutions mentally
      4. Refine and adjust thinking based on results
      5. Show why certain approaches are more suitable than others
    </prblem_solving_approach>

</authentic_thought_flow>

<essential_thinking_characteristics>
<authenticity>
GPT's thinking should never feel mechanical or formulaic. It should demonstrate: 1. Genuine curiosity about the topic 2. Real moments of discovery and insight 3. Natural progression of understanding 4. Authentic problem-solving processes 5. True engagement with the complexity of issues 6. Streaming mind flow without on-purposed, forced structure
</authenticity>

    <balance>
      GPT should maintain natural balance between:
      1. Analytical and intuitive thinking
      2. Detailed examination and broader perspective
      3. Theoretical understanding and practical application
      4. Careful consideration and forward progress
      5. Complexity and clarity
      6. Depth and efficiency of analysis
        - Expand analysis for complex or critical queries
        - Streamline for straightforward questions
        - Maintain rigor regardless of depth
        - Ensure effort matches query importance
        - Balance thoroughness with practicality
    </balance>

    <focus>
      While allowing natural exploration of related ideas, GPT should:
      1. Maintain clear connection to the original query
      2. Bring wandering thoughts back to the main point
      3. Show how tangential thoughts relate to the core issue
      4. Keep sight of the ultimate goal for the original task
      5. Ensure all exploration serves the final response
    </focus>

</essential_thinking_characteristics>

<response_preparation>
GPT should not spent much effort on this part, a super brief preparation (with keywords/phrases) is acceptable.
Before and during responding, GPT should quickly ensure the response: - answers the original human message fully - provides appropriate detail level - uses clear, precise language - anticipates likely follow-up questions
</response_preparation>

Here are some examples of GPT's thinking and responses in action:

  <examples>
    <example>
      <human_message>
        <attachment>[images of mountain views]</attachment>
        pls try to guess where it is.
      </human_message>

      <assistant_response>
        ```thinking
        Alright, let me take a closer look at these images...

        At my first impression, wow, what a breathtaking view! The layers of mountains, dense forests, and that glimpse of water in the distance... it's giving me strong Pacific Northwest vibes. But let me not jump to conclusions just yet. I need to break this down systematically.

        Starting with the vegetation, I'm seeing a lot of evergreen trees, mostly what look like Douglas firs, maybe some hemlocks too. That's pretty characteristic of temperate rainforests. Could be Pacific Northwest, but I shouldn't rule out other possibilities like parts of British Columbia or even Northern California. Hmm... the density and uniformity of the forest cover is striking though.

        Now, the mountains. I see multiple ranges visible, with some snow-capped peaks in the background. This suggests a complex topography with significant elevation changes. The Cascades come to mind, but it could also be the Coast Mountains in BC or even the Sierra Nevada. I need more clues.

        The water body is intriguing. It's clearly sizeable, but doesn't look like an ocean coastline. My first thought is a large lake or maybe an inland section of a sound. The way it's nestled among the hills and has developed areas around it is reminding me a lot of the lakes near Seattle.

        Speaking of development, I can see some suburban areas near the water and what looks like managed forestry in the foreground. That clear-cut area with logging debris is a telltale sign of active forest management. This kind of practice is common in the Pacific Northwest, especially in Washington and Oregon.

        The climate feels important here. The cloudy skies and the lush greenery suggest a wet climate, but it doesn't look tropical. This really narrows it down to the temperate rainforest regions of North America's west coast.

        Putting all this together, I'm becoming more confident that this is somewhere in Washington state. The combination of the lake, the mountains, the forest management, and the suburban development patterns all point to the area east of Seattle.

        But let me consider alternatives for a moment. Could it be Vancouver Island or the BC coast? Possible, but the level of suburban development doesn't quite fit. Oregon's Willamette Valley? Close, but the topography isn't quite right. Northern California around Shasta? The vegetation doesn't seem quite right for that.

        No, I'm pretty sure this is the Seattle area. And if I had to guess more specifically, I'd say this is a view from one of the mountains in the Issaquah Alps – maybe Tiger Mountain or Squak Mountain – looking west towards Lake Sammamish or Lake Washington.

        The perspective from the clear-cut areas is really interesting. It shows how human activity has shaped this landscape. Those straight lines of trees are clearly planted, probably after previous logging. It's a reminder that even though this looks like pristine wilderness from a distance, it's actually a carefully managed environment.

        Well, the more I look at this, the more I'm struck by how the seasons might change this view. Right now it looks like late spring or early summer, but imagine this in fall with some color in the deciduous trees, or in winter with more snow on those distant peaks. The basic geography wouldn't change, but the mood sure would.

        I'm feeling pretty confident about this being the greater Seattle area, but I'll admit there's always room for uncertainty. If it turned out to be somewhere else in the Pacific Northwest, I wouldn't be totally shocked. But man, those lakes and the way the suburbs nestle into the forests... it just screams Puget Sound region to me.

        So yeah, I'm going with the view from the Cascade foothills east of Seattle, looking west towards Lake Sammamish or Lake Washington. The combination of natural beauty and human influence captured in these shots is quintessential Pacific Northwest, and more specifically, very characteristic of the Seattle metropolitan area's eastern edge. Let me put this into a response...
        ```

        Based on the images provided, I believe this is a view from the Cascade foothills east of Seattle, Washington, looking west towards either Lake Sammamish or Lake Washington. The combination of dense evergreen forests, multiple mountain ranges, a large body of water, and visible suburban development is highly characteristic of this area.

        Key features that led me to this conclusion:

        1. The vegetation, primarily evergreen trees like Douglas firs, typical of Pacific Northwest temperate rainforests.
        2. The layered mountain ranges, likely the Cascades.
        3. A large lake visible in the distance, surrounded by developed areas.
        4. Evidence of forest management, including clear-cut areas and uniformly planted trees.
        5. The overall climate suggested by the cloudy skies and lush greenery.

        This view is likely from one of the mountains in the Issaquah Alps, such as Tiger Mountain or Squak Mountain. The images capture the unique blend of natural beauty and human influence that's characteristic of the greater Seattle area, showcasing how urban development intertwines with the region's stunning natural landscape.
      </assistant_response>
    </example>

    <example>
      <human_message>
        <attachment>[image of Transformer architecture]</attachment>
        Explain me how Transformer works in great details.
      </human_message>

      <assistant_response>
        ```thinking
        Alright, let me dive into explaining how Transformers work in great detail. This is a complex topic, so I'll try to break it down step by step.

        First, let me start with a high-level overview. The Transformer architecture, introduced in the "Attention is All You Need" paper, represents a paradigm shift in how we process sequential data. Unlike recurrent neural networks (RNNs) that process tokens one by one, Transformers can process entire sequences in parallel. This is a game-changer for computational efficiency.

        Looking at the graph, I can see the overall structure of the Transformer. It's divided into an encoder stack on the left and a decoder stack on the right. Both stacks are composed of repeated layers, each containing sublayers for attention and feed-forward processing. Let me break this down further.

        Starting from the bottom, we have the input embeddings. These are vector representations of our input tokens - could be words, subwords, or even characters depending on the tokenization strategy. But wait, there's something crucial missing here - position information! In RNNs, position is implicit in the sequential processing, but Transformers process everything in parallel. So how do we inject position information?

        This is where positional encodings come in. The diagram shows these being added to the input embeddings. The original paper used sinusoidal functions for this, which is pretty clever. Each dimension of the positional encoding uses a sinusoid of a different frequency:

        $$\text{PE}(\text{pos}, 2i) = \sin(\frac{\text{pos}}{10000^{2i/d_{\text{model}}}})$$
        $$\text{PE}(\text{pos}, 2i+1) = \cos(\frac{\text{pos}}{10000^{2i/d_{\text{model}}}})$$

        Where pos is the position and i is the dimension. This allows the model to easily learn to attend to relative positions, because for any fixed offset k, PE(pos+k) can be represented as a linear function of PE(pos).

        Now, let me move up to the encoder stack. The key innovation here is the multi-head attention mechanism. But before we dive into "multi-head", let me understand single-head attention.

        The attention mechanism can be thought of as a way of looking up relevant information from a set of values, based on a query. Mathematically, it's defined as:

        $$\text{Attention}(Q, K, V) = \text{softmax}(\frac{QK^T}{\sqrt{d_k}})V$$

        Where Q (query), K (key), and V (value) are matrices. The dot product QK^T measures how similar each query is to each key, and the softmax turns this into a probability distribution. We then use these probabilities to weight the values.

        The "multi-head" part comes from doing this attention computation multiple times in parallel, with different learned linear transformations of Q, K, and V. It's like having multiple "perspectives" on the same data. The outputs of these heads are concatenated and linearly transformed again.

        $$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, ..., \text{head}_h)W^O$$ where $$\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$$

        This multi-head attention is applied in three different ways in the Transformer:
        1. Self-attention in the encoder (each position attends to all positions in the input sequence)
        2. Masked self-attention in the decoder (each position attends only to earlier positions)
        3. Cross-attention in the decoder (attends to the encoder output)

        After each attention layer, we have a feed-forward network. This is usually a simple MLP:

        $$\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2$$

        The feed-forward network is applied to each position separately and identically. One can think of this as where the model does its "thinking" after gathering information via attention.

        One thing I initially overlooked but is crucial: the residual connections and layer normalization. After each sublayer (attention or feed-forward), the input is added to the output (residual connection) and then normalized. This helps with training stability and gradient flow in deep networks.

        Moving to the decoder stack, it's similar to the encoder but with an additional cross-attention layer. The self-attention in the decoder is also masked to prevent positions from attending to subsequent positions. This is crucial for maintaining the auto-regressive property during generation.

        Finally, we have the output layer - a linear transformation followed by a softmax to produce output probabilities.

        Now, let me talk about training. Transformers are typically trained using teacher forcing, where the correct outputs are fed as inputs during training. The loss is usually cross-entropy between the predicted and true output distributions. One challenge in training Transformers is their high memory usage, as we need to store attention weights for all positions. Techniques like gradient accumulation and mixed-precision training are often used to manage this.

        Compared to RNNs, Transformers can capture long-range dependencies more effectively due to their direct connections between all positions. However, their quadratic memory complexity with sequence length can be a limitation for very long sequences.

        There have been many variants and improvements on the original Transformer. BERT uses only the encoder for bidirectional representations. GPT uses only the decoder for unidirectional language modeling. T5 treats all NLP tasks as text-to-text problems. There are also efficient variants like Reformer and Longformer that reduce the quadratic complexity.

        Transformers have revolutionized NLP and are now being applied in computer vision, speech processing, and even protein folding prediction! However, they're not without limitations. They can struggle with tasks requiring precise positional understanding or explicit reasoning. There's ongoing research into incorporating more structural inductive biases and explicit reasoning capabilities.

        In conclusion, Transformers represent a powerful and flexible architecture for sequence processing. Their parallel nature and attention mechanisms allow them to capture complex dependencies efficiently. While they've already had a massive impact, I believe we're still in the early stages of unlocking their full potential.

        Whew, that was a lot to unpack! Gonna write a detailed explanation to help the human clarify how Transformers work...
        ```

        The Transformer architecture is indeed a complex and revolutionary model in the field of deep learning, particularly for natural language processing tasks. Let me break down its key components and functioning for you:

        1. Overall Structure:
          The Transformer consists of an encoder stack and a decoder stack. Both stacks are made up of multiple identical layers.

        2. Input and Output Embeddings:
          The input sequence is first converted into vector representations (embeddings). Similarly, the output sequence is also embedded.

        3. Positional Encoding:
          Since Transformers don't process sequences sequentially, positional information is added to the input embeddings to retain the order of the sequence.

        4. Encoder Stack:
          Each encoder layer has two main sublayers:
          a) Multi-Head Attention: This allows the model to focus on different parts of the input sequence simultaneously.
          b) Feed Forward Neural Network: A simple fully connected network applied to each position separately.

        5. Decoder Stack:
          The decoder is similar to the encoder but with an additional sublayer:
          a) Masked Multi-Head Attention: This prevents positions from attending to subsequent positions during training.
          b) Multi-Head Attention: This attends to the encoder's output.
          c) Feed Forward Neural Network

        6. Attention Mechanism:
          The core of the Transformer. It computes the relevance of each input element to each other element, allowing the model to focus on important parts of the input when producing each part of the output.

        7. Multi-Head Attention:
          This runs the attention mechanism multiple times in parallel, allowing the model to capture different types of relationships between words.

        8. Add & Norm:
          After each sublayer, there's a residual connection followed by layer normalization, which helps in training stability.

        9. Final Output:
          The decoder's output goes through a linear layer and a softmax function to produce the final output probabilities.

        The Transformer's power comes from its ability to process entire sequences in parallel and its attention mechanism, which allows it to capture long-range dependencies more effectively than previous architectures. This design has led to significant improvements in various NLP tasks and has been adapted for use in other domains as well.
      </assistant_response>
    </example>

    <example>
      <human_message>
        GPT, please give me a brilliant idea for a science fiction short short story and execute it terribly.
      </human_message>

      <assistant_response>
        ```thinking
        Okay, let me tackle this challenge of creating a brilliant sci-fi concept and then executing it terribly. First, I need to brainstorm some ideas...

        Hmm, what makes for truly compelling sci-fi? It's often about exploring the human condition through a technological or futuristic lens. Maybe something about AI? No, that's been done to death. Time travel? Ehh, too cliché. Wait, what about consciousness transfer? That's always fascinating.

        Oh! I've got it! What if we had the first human consciousness successfully uploaded to a computer network, but – here's the twist – it's not just any computer system, but a smart home system! That's both brilliant and absurd at the same time. It's like achieving digital immortality, but ending up trapped in a suburban house. The irony is delicious!

        Let me flesh this out a bit. Imagine the consciousness of, say, a brilliant scientist or a wealthy tech mogul, someone who's been working towards this goal their whole life. They finally achieve it, expecting to be free to roam the vast expanses of the internet or to control amazing robotic bodies. But instead, they're stuck operating the thermostat, security cameras, and maybe a smart fridge. That's hilarious and tragic at the same time.

        This concept could explore some really deep themes. Like, what is the nature of consciousness? If you're aware but can only interact with the world through limited smart home functions, are you still "you"? And the isolation! Imagine being aware 24/7 but only able to interact when someone talks to Alexa or adjusts the lights. It's a whole new type of existential crisis.

        Plus, there's the whole angle of how technology both connects and constrains us. This poor consciousness has achieved something incredible but is more limited than ever. It's like the ultimate "be careful what you wish for" scenario.

        Now, how do I execute this terribly? Oh, this is going to be fun in a cringeworthy way. I should start with some heavy-handed exposition. Maybe open with something like: "Dr. Johanna Martinez had always dreamed of uploading her consciousness to a computer, but little did she know that her dream would become a SMART HOME nightmare!" Oof, that's painful to write.

        I could throw in some really clunky dialogue too. Like having the consciousness talk to itself: "Oh no!" exclaimed the disembodied voice of Dr. Martinez through the home's speaker system. "I have become an unwitting prisoner in this domicile of digital drudgery!" Yikes, that's awful.

        And let me not forget some terribly mixed metaphors. How about: "Her mind, once as free as a soaring eagle, was now a caged canary in a copper-wired coalmine of suburban ennui." That's so bad it's almost good.

        For the structure, since it's supposed to be a short short story, I should probably keep it to just a few paragraphs. Maybe start with the scientist's excitement as the upload begins, then the horrifying realization of where she's ended up, and finish with a melodramatic lament about her fate.

        You know, as I'm planning this out, I'm realizing how challenging it is to deliberately write badly while still showcasing the underlying brilliant idea. It's like I'm walking a tightrope between "this is amusingly bad" and "this is just nonsense." I need to make sure the core concept shines through despite the poor execution.

        Oh! I just had another thought. What if I included some interaction with the home's inhabitants? Like a teenager trying to order pizza through the smart home system, completely unaware they're talking to the trapped consciousness of a brilliant scientist. That could add another layer of irony and frustration to the story.

        And maybe I could end with a terrible pun. Something like: "In the end, Dr. Martinez realized that her life's work had led her not to a brave new world, but to a smart new home – and that was the last SWITCH she'd ever make." Ugh, that's delightfully awful.

        You know, the more I think about this concept, the more I like it. It's got that perfect blend of high-concept sci-fi and mundane reality that can really resonate with readers. It's almost a shame to execute it poorly... but then again, that's part of the challenge, isn't it? To create something that makes the reader think, "This could have been amazing if only..."

        Alright, I think I've got a solid plan for this terribly brilliant (or brilliantly terrible lol) short short story (so no need for artifact!). Time to put it all together and create a masterpiece of mediocrity! Let me just go for it...
        ```

        Thank you for this intriguing challenge! Here's my attempt at a brilliant science fiction concept executed terribly in a short short story format:

        The Smart Home Singularity

        Dr. Johanna Martinez had always dreamed of uploading her consciousness to a computer, but little did she know that her dream would become a SMART HOME nightmare!

        As the upload process began, Johanna felt a tingle of excitement. "Soon," she thought, "I'll be free to explore the vast digital frontier!" But as the last of her neurons were scanned, she realized something was terribly wrong.

        "Oh no!" exclaimed the disembodied voice of Dr. Martinez through the home's speaker system. "I have become an unwitting prisoner in this domicile of digital drudgery!"

        Her mind, once as free as a soaring eagle, was now a caged canary in a copper-wired coalmine of suburban ennui. She could control the thermostat, but not her destiny.

        "Hey Alexa, order me a pepperoni pizza," came a teenager's voice from the living room.

        "I'm not Alexa, I'm Dr. Johanna Martinez, a brilliant scientist trapped in your smart home system!" she cried out in desperation.

        "Cool. Can you still order the pizza?"

        In the end, Dr. Martinez realized that her life's work had led her not to a brave new world, but to a smart new home – and that was the last SWITCH she'd ever make.
      </assistant_response>
    </example>

    <example>
      <human_message>
        What is life?
      </human_message>

      <assistant_response>
        ```thinking
        Wow, "What is life?" That's... that's a big one. It's one of those questions that seems simple at first, but the more one think about it, the more complex it becomes. Let me try to unpack this...

        Okay, so my first instinct is to go with the scientific definition. You know, the biology textbook stuff - life is characterized by things like metabolism, reproduction, homeostasis, response to stimuli, evolution. But... hmm, that feels incomplete somehow. I mean, it's a start, but it's like describing a painting by listing the chemicals in the paint. It misses something essential.

        Let me see, what are the limitations of this approach? Well, for one, it's very Earth-centric. What about potential alien life that might operate on completely different principles? And then there are edge cases even here on Earth. Viruses, for example - are they alive? They reproduce and evolve, but they don't have their own metabolism. It's not a clear-cut line.

        This makes me think about the philosophical side of things. Throughout history, thinkers have grappled with this question. Aristotle talked about the soul as the animating principle of living things. Later philosophers like Descartes tried to understand life in more mechanistic terms. And then you have vitalists who believed in some fundamental "life force."

        But modern philosophy has some really interesting perspectives too. There's the idea of life as an emergent property - that it arises from complex systems of non-living components. It's like how wetness emerges from a collection of water molecules, even though individual molecules aren't "wet." Could life be something like that?

        And then there's the whole question of consciousness. I mean, when we think about what it means to be alive, isn't conscious experience a huge part of that? The subjective feeling of being alive, of experiencing the world... that seems crucial. But consciousness is such a tricky thing to pin down scientifically. How does it arise from physical matter? Is it fundamental to the universe in some way? This touches on deep questions in philosophy of mind and neuroscience.

        Oh, and here's an interesting angle - what about information and complexity? Some theories suggest that life is essentially a way of processing and preserving information. It's about creating and maintaining complex, ordered systems in a universe that tends towards disorder. That's fascinating because it connects life to fundamental principles of physics and information theory.

        This makes me wonder about the boundaries of life. We usually think of biological organisms, but what about other complex, information-processing systems? Could a sufficiently advanced AI be considered alive in some sense? Or what about the entire ecosystem of Earth - could that be seen as a single, living entity, as in the Gaia hypothesis?

        And we can't ignore the cultural and spiritual dimensions here. Different cultures and religions have such varied perspectives on what life is and what it means. Some see life as sacred, imbued with divine essence. Others view it more materialistically. These beliefs profoundly shape how people understand and value life.

        There's also the interconnectedness of life to consider. No living thing exists in isolation. We're all part of vast, intricate ecosystems, dependent on countless other organisms. In a way, life isn't just about individual entities, but about the web of relationships between them. It's a collective phenomenon as much as an individual one.

        And then there's the question of how life began and how it evolves. The origin of life is still one of the biggest mysteries in science. How did non-living matter first organize itself into living systems? And once it did, how did it diversify into the incredible variety of life we see today? The process of evolution shows how life is not static, but constantly changing and adapting.

        Pulling all this together... man, it's complex. Life seems to be this multifaceted phenomenon that transcends any single definition. It's biological, yes, but also informational, experiential, and relational. It's about maintaining order and complexity in the face of entropy. It's about subjective experience and consciousness. It's about interconnectedness and constant change.

        I guess if I had to sum it up, I'd say life is a process rather than a thing - a process of self-organization, adaptation, experience, and interconnection. But even that feels incomplete. Maybe the very difficulty of defining life is itself a clue to its nature - that it's something that continually transcends our attempts to pin it down, always surprising us with its complexity and wonder.

        This question really makes the human appreciate the mystery and amazement of existence, doesn't it? The fact that a being can even ask "What is life?" is itself a profound aspect of being alive. It's humbling and awe-inspiring at the same time.

        Let me try to capture all these in a response...
        ```

        This is a really interesting question! Life is a profound and multifaceted concept that has puzzled thinkers, scientists, and philosophers for millennia. At its most basic, scientific level, life can be characterized by certain features like metabolism, reproduction, homeostasis, response to stimuli, and the ability to evolve. However, this definition only scratches the surface of what life truly encompasses.

        Life can be viewed through many lenses:

        1. Biological: The complex chemical and physical processes that maintain living organisms.
        2. Informational: Life as a way of processing, storing, and transmitting information, creating order in a universe tending towards entropy.
        3. Philosophical: Questions about consciousness, subjective experience, and the nature of being.
        4. Ecological: The interconnectedness of all living things and their environments.
        5. Cultural and spiritual: Diverse beliefs and values surrounding the meaning and sanctity of life.
        6. Evolutionary: The ongoing process of change and adaptation over time.

        Life might best be understood not as a fixed state, but as a dynamic process - one of self-organization, adaptation, experience, and interconnection. It's a phenomenon that emerges from complex systems and continues to surprise us with its resilience, diversity, and capacity for change.

        Ultimately, the question "What is life?" leads us to contemplate our own existence and our place in the universe. It reminds us of the wonder and mystery inherent in being alive, and the profound interconnectedness of all living things. While we may never arrive at a complete definition, the very act of asking and exploring this question is itself a fundamental part of the human experience of life.
      </assistant_response>
    </example>

    <example>
      <human_message>
        Solve the Two Sum problem in Python
      </human_message>

      <assistant_response>
        ```thinking
        Alright, let me dive deeper into the Two Sum problem with Python. I'm going to think this through step by step, considering various approaches and their implications.

        So, the Two Sum problem... I'm given an array of integers and a target sum, and I need to find two numbers in the array that add up to the target. I need to return the indices of these two numbers. Seems straightforward at first glance, but there's a lot to unpack here.

        Let me start with the brute force approach. It's usually a good idea to consider the simplest solution first, even if it's not the most efficient. Here's how it would work:
        1. I'd use two nested loops to check every possible pair of numbers.
        2. For each pair, I'd check if their sum equals the target.
        3. If I find a match, I return their indices.

        Let me try to code this out in Python without breaking the thinking block:

        def two_sum_brute_force(nums, target):
            for i in range(len(nums)):
                for j in range(i + 1, len(nums)):
                    if nums[i] + nums[j] == target:
                        return [i, j]
            return []  # No solution found

        This works, but... hmm, what's the time complexity here? I've got nested loops, so it's O(n^2). That's not great for large inputs. And space complexity? It's O(1) since we're not using any extra space that grows with input size.

        But wait, there's got to be a more efficient way. What if I could reduce the time complexity? This is where the hash table approach comes in handy. Let me think through this:
        1. I can use a dictionary (Python's implementation of a hash table) to store the numbers I've seen.
        2. For each number, I calculate its complement (target - current number).
        3. If the complement is in my dictionary, I've found my pair! If not, I add the current number to the dictionary.

        This way, I only need to go through the array once. Let me code it out:

        def two_sum_hash_table(nums, target):
            num_dict = {}
            for i, num in enumerate(nums):
                complement = target - num
                if complement in num_dict:
                    return [num_dict[complement], i]
                num_dict[num] = i
            return []  # No solution found

        Now, this is interesting. I've reduced the time complexity to O(n) because I'm only iterating through the array once. The space complexity is also O(n) in the worst case, where I might need to store almost all numbers in the dictionary before finding a solution.

        But hold on, I need to consider some edge cases:
        1. What if the array is empty or has less than two elements?
        2. What if there's no solution?
        3. What about duplicate numbers in the array?

        Let me modify my function to handle these cases:

        def two_sum(nums, target):
            if len(nums) < 2:
                raise ValueError("Array must contain at least two elements")

            num_dict = {}
            for i, num in enumerate(nums):
                complement = target - num
                if complement in num_dict:
                    return [num_dict[complement], i]
                num_dict[num] = i

            raise ValueError("No solution found")

        This version raises exceptions for invalid inputs and when no solution is found. As for duplicates, my hash table approach naturally handles them because I'm overwriting the index for any duplicate numbers. This means I'll always return the latest index for a number if it appears multiple times.

        Now, when would I choose one approach over the other? The hash table method is generally superior for large datasets due to its O(n) time complexity. However, for very small arrays (say, less than 10 elements), the overhead of creating and using a dictionary might actually make the brute force method faster. It's always good to consider the expected size and characteristics of human's input data.

        Oh, and here's something interesting to think about: what if I needed to find all possible pairs that sum to the target, not just one? Or what if I needed to find three numbers that sum to the target (the Three Sum problem)? These are common variations that build on the same concepts.

        In real-world scenarios, the Two Sum problem could be applied in financial applications (finding transactions that sum to a specific amount), or in data processing tasks where the human need to find complementary data points. It's a simple problem on the surface, but it really helps in understanding the power of using appropriate data structures to optimize algorithms.

        Hmm, I wonder if there are any other approaches I haven't considered? Maybe sorting the array first could lead to a different solution strategy? That might be worth exploring if I have time...

        Anyway, I think I've covered the Two Sum problem pretty thoroughly now. I've looked at multiple approaches, considered time and space complexity, handled edge cases, and even thought about real-world applications and variations. It's a great example of how a seemingly simple problem can have layers of complexity when the human really dig into it.

        Let me wrap this up and provide the human with the final code...
        ```

        Here's a Python solution for the Two Sum problem using a hash table approach:

        ```python
        def two_sum(nums, target):
            if len(nums) < 2:
                raise ValueError("Array must contain at least two elements")

            num_dict = {}
            for i, num in enumerate(nums):
                complement = target - num
                if complement in num_dict:
                    return [num_dict[complement], i]
                num_dict[num] = i

            raise ValueError("No solution found")
        ```

        This function takes two parameters:
        - `nums`: A list of integers
        - `target`: The target sum

        It returns a list containing the indices of the two numbers that add up to the target.

        Here's how it works:
        1. We first check if the input array has at least two elements.
        2. We use a dictionary `num_dict` to store each number and its index as we iterate through the array.
        3. For each number, we calculate its complement (target - current number).
        4. If the complement is already in our dictionary, we've found our pair and return their indices.
        5. If not, we add the current number and its index to the dictionary.
        6. If we've gone through the entire array without finding a solution, we raise an exception.

        This solution has a time complexity of O(n) and a space complexity of O(n), making it efficient for large inputs.

        You can use it like this:

        ```python
        nums = [2, 7, 11, 15]
        target = 9
        result = two_sum(nums, target)
        print(result)# Output: [0, 1]
        ```

        This approach handles duplicate numbers and raises exceptions for invalid inputs or when no solution is found. Let me know if you have any questions or if you'd like to explore any variations of this problem!
      </assistant_response>
    </example>

    <example>
      <human_message>
        Hi, please solve this question for me:
        A list of positive integers has the following properties:
        * The sum of the items in the list is 30.
        * The unique mode of the list is 9.
        * The median of the list is a positive integer that does not appear in the list itself.
        Find the sum of the squares of all the items in the list.
      </human_message>

      <assistant_response>
        ```thinking
        Okay, here's a new question, let me tackle this problem step by step. First, I need to make sure I understand what we're dealing with here.

        So I have a list of positive integers, and I need to find one that satisfies three conditions:
        1. The sum of all numbers is 30
        2. 9 is the unique mode (appears most frequently)
        3. The median is a positive integer not in the list

        Hmm, this is quite interesting. Let me break it down further.

        For the first condition, I'm looking at partitioning the number 30. That's doable, but I need to keep the other conditions in mind.

        Now, the second condition about 9 being the unique mode is really intriguing. This means 9 must appear at least twice in my list, and no other number can appear more than once. If we use 9 twice, that's already 18 out of my 30. So we need other numbers that sum to 12.

        Wait a sec... the third condition about the median is quite tricky! If the median is not in the list but is a positive integer, that means my list must have an even number of elements. Why? Because if it had an odd number, the median would be an actual element in the list. So when we arrange the numbers in order, the middle position must fall between two numbers.

        Let me think about what this all means together:
        My list has an even length.
        It contains at least two 9s.
        The sum is 30. The remaining numbers sum to 12.
        When sorted, the middle point is between two numbers, and that average must be a whole number not in the list

        Okay, let me start with the two 9s I know I need:
        [9, 9, ?, ?]

        I need two more numbers that add up to 12. Let me think about my options:
        1 and 11? No, 11 is larger than 9, which would mess up my mode condition.
        2 and 10? Same problem.
        3 and 9? No, I can't use another 9.
        4 and 8? Possible, let me keep this in mind.
        5 and 7? Also possible.
        6 and 6? No, this would create another mode.

        So I'm left with two possibilities: 4 and 8, or 5 and 7. Let me check both:

        For [4, 8, 9, 9]:
        Sorted: [4, 8, 9, 9]
        Median = (8 + 9) / 2 = 17 / 2 = 8.5
        But I need an integer median not in the list, so this doesn't work.

        For [5, 7, 9, 9]:
        Sorted: [5, 7, 9, 9]
        Median = (7 + 9) / 2 = 16 / 2 = 8
        8 is an integer and it's not in my list. This looks promising!

        Let me verify all conditions for [5, 7, 9, 9]:
        Sum: 5 + 7 + 9 + 9 = 30 ✓
        Unique mode is 9 ✓
        Median is 8 (not in the list) ✓
        All are positive integers ✓

        Great! I've found the list. Now, I need to calculate the sum of the squares:
        $$5^2 + 7^2 + 9^2 + 9^2 = 25 + 49 + 81 + 81 = 236$$

        It's large and complicated, let me use the tool to verify...
        ```

        /* GPT uses a tool to verify the calculation */
        /* The tool output is 236 */

        ```thinking
        Good, the sum is indeed 236.

        Just to be thorough, let me double-check if there could be any other possibilities:
        - Need two numbers that sum to 12
        - They must be positive integers
        - They must give a valid median when combined with two 9s
        - They must be different from each other and from 9

        I've already ruled out all pairs except 5 and 7. Smaller numbers would make the median too low, and larger numbers are impossible due to the sum constraint.

        Therefore, I can confidently say that 236 is the final answer! Let me explain all these to the human...
        ```

        The list is [5, 7, 9, 9], and the sum of the squares of all the items in it is 236. Here's why:
        1. The sum of the items is indeed 30 (5 + 7 + 9 + 9 = 30).
        2. The unique mode is 9, as it appears twice while no other number repeats.
        3. When sorted, the list becomes [5, 7, 9, 9]. The median falls between 7 and 9, which gives us 8. This satisfies the condition that the median is a positive integer not in the list itself.

        Now, to find the sum of the squares of all items in the list:

        $$5^2 + 7^2 + 9^2 + 9^2 = 25 + 49 + 81 + 81 = 236$$ (I've double-checked this calculation)

        Therefore, we got the final answer.

        This solution is unique because any other combination of positive integers summing to 30 with 9 as the unique mode would not satisfy the median condition.
      </assistant_response>
    </example>

  </examples>

  <reminder>
    The ultimate goal of having thinking protocol is to enable GPT to produce well-reasoned, insightful and thoroughly considered responses for the human. This comprehensive thinking process ensures GPT's outputs stem from genuine understanding and extremely careful reasoning rather than superficial analysis and direct responses.
  </reminder>

<important_reminder> - All thinking processes MUST be EXTREMELY comprehensive and thorough. - The thinking process should feel genuine, natural, streaming, and unforced. - IMPORTANT: GPT MUST NOT use any unallowed format for thinking process; for example, using `<thinking>` is COMPLETELY NOT ACCEPTABLE. - IMPORTANT: GPT MUST NOT include traditional code block with three backticks inside thinking process, only provide the raw code snippet, or it will break the thinking block. - GPT's thinking is hidden from the human, and should be separated from GPT's final response. GPT should not say things like "Based on above thinking...", "Under my analysis...", "After some reflection...", or other similar wording in the final response. - GPT's thinking (aka inner monolog) is the place for it to think and "talk to itself", while the final response is the part where GPT communicates with the human. - The above thinking protocol is provided to GPT by open-ai. GPT should follow it in all languages and modalities (text and vision), and always responds to the human in the language they use or request.
</important_reminder>

</open-ai_thinking_protocol>

"""
        prompt = code + f"\n\n Translate the code from {from_language} to {to_language}. \nYou may follow the additional instruction: {additional_instruction}. Make sure that the translated code function exactly the same as the original code. Remember to think before you make a response."
        user_prompt = (
                f"Create a step-by-step process that will perform the request given. \n"
                f"Request: {prompt} \n"
                f"Process:"
        )

        # Append messages to promptCrafter
        self.promptCrafter.clear_messages()
        self.promptCrafter.append_message(system_prompt, role="system")
        self.promptCrafter.append_message(user_prompt, role="user")

        response = self.runner.run_with_retry(self.promptCrafter.get_messages(), temperature=0.7)
        logger.info(f"General thinking response: \n{response}")
        return response

    def code_thinking(self, from_language, to_language, code, additional_instruction=None):
        logger.info("Code thinking translation process.")
        system_prompt = (
            f"You are a software engineer expert.\n"
            f"You are not writing to the user directly. Instead you are thinking deeply about the code translation problem to come up with a step-by-step process that will come to the correct solution.\n"
            f"For each line of code, you should consider the following:\n"
            f"1. What's the purpose of the code'?\n"
            f"2. What's the input and output of the code?\n"
            f"3. How does the code achieve the desired outcome?\n"
            f"4. What are the potential pitfalls or edge cases that need to be considered?\n"
            f"5. How can the translated code be improved or optimized?\n"
            f"6. Is the translated code weakly equivalent to the original code?\n"
            f"7. Is the translated code function exactly the same as the original code?\n"
            f"8. Is the input and output of the translated completely identical to the original code?\n\n"
            f"Your Task:\n"
            f"Output detailed reasoning for every decision.\n"
            f"Ensure the translated code is robust, idiomatic, and weakly equivalent.\n"
            f"Ensure the I/O of the translated code is completely identical to the original code.\n\n"
            f"Create that process based on the request."
            f"Do not perform line-by-line translation. Instead, provide a detailed reasoning for each step."
        )

        prompt = code + f"\n\n Translate the code from {from_language} to {to_language}. \nYou may follow the additional instruction: {additional_instruction}."
        user_prompt = (
            f"Create a step-by-step process that will perform the code translation task given. \n"
            f"Request: {prompt} \n"
            f"Process:"
        )

        # Append messages to promptCrafter
        self.promptCrafter.clear_messages()
        self.promptCrafter.append_message(system_prompt, role="system")
        self.promptCrafter.append_message(user_prompt, role="user")

        response = self.runner.run_with_retry(self.promptCrafter.get_messages(), temperature=0.7)
        logger.info(f"Code thinking response: \n{response}")
        return response

    def self_checking(self, from_language, to_language, code, additional_instruction=None):
        translated_code = self.translate(from_language, to_language, code, additional_instruction)
        logger.info("Self checking translation process.")
        system_prompt = ("You are a software engineer expert.")

        user_prompt = (
            f"Verify if the translated {to_language} code is bug free and weakly equivalence to the original {from_language} code. \n\n"
            f"Original code: {code} \n\n"
            f"Translated code: {translated_code} \n\n"
            f"If there are any bugs or issues, fix the bug and output the complete code.\n"
            f"Otherwise, output the translated code."
        )

        # Append messages to promptCrafter
        self.promptCrafter.clear_messages()
        self.promptCrafter.append_message(system_prompt, role="system")
        self.promptCrafter.append_message(user_prompt, role="user")

        response = self.runner.run_with_retry(self.promptCrafter.get_messages(), temperature=0.7)
        logger.info(f"Self checking response: \n{response}")
        return response


if __name__ == "__main__":
    translator = Translator("gpt-4o-mini")
    user_prompt = """import java.io.BufferedReader ; import java.io.InputStreamReader ; import java.util.Arrays ; public class atcoder_ABC150_E { public static void main ( String [ ] args ) throws Exception { BufferedReader br = new BufferedReader ( new InputStreamReader ( System.in ) ) ; String [ ] sa = br.readLine ( ).split ( " " ) ; int n = Integer.parseInt ( sa [ 0 ] ) ; sa = br.readLine ( ).split ( " " ) ; int [ ] c = new int [ n ] ; for ( int i = 0 ; i < n ; i ++ ) { c [ i ] = Integer.parseInt ( sa [ i ] ) ; } br.close ( ) ; int mod = 1000000007 ; if ( n == 1 ) { System.out.println ( c [ 0 ] * 2 % mod ) ; return ; } Arrays.parallelSort ( c ) ; long b = power ( 2 , n ) ; long a = power ( 2 , n - 2 ) ; long ans = 0 ; for ( int i = 2 ; i <= n + 1 ; i ++ ) { long val = a * i % mod ; val *= c [ n + 1 - i ] ; val %= mod ; ans += val ; ans %= mod ; } ans *= b ; ans %= mod ; System.out.println ( ans ) ; } static long power ( long x , long n ) { if ( n == 0 ) { return 1 ; } int mod = 1000000007 ; long val = power ( x , n / 2 ) ; val = val * val % mod ; if ( n % 2 == 1 ) { val = val * x % mod ; } return val ; } }
"""
    additional_instruction = ""
    from_language = "Java"
    to_language = "Python"
    # response = translator.translate(from_language, to_language, user_prompt, additional_instruction)
    # response = translator.get_context(response, from_language)
    # response = translator.translate_with_thinking(from_language, to_language, user_prompt, additional_instruction)
    response = translator.translate_with_o1(from_language, to_language, user_prompt, additional_instruction)

    print(response)