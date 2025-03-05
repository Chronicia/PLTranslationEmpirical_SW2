class PromptCrafter:
    messages = []
    def __init__(self, model):
        self.model = model.lower()
        if self.model not in ['gpt', 'gemini']:
            raise ValueError("Invalid model. Supported models: 'gpt', 'gemini'.")

    def append_message(self, message, role="user", context=None):
        if self.model == 'gpt':
            return self._craft_openai_prompt(message, role)
        elif self.model == 'gemini':
            return self._craft_gemini_prompt(message, role, context)

    def _craft_openai_prompt(self, message, role="user"):
        if role not in ["user", "system", "assistant"]:
            raise ValueError("Invalid role. Supported roles: 'user', 'system', 'assistant'.")
        else:
            self.messages.append({"role": role, "content": message})

    def _craft_gemini_prompt(self, message, role="user", context=None):
        pass

    def craft_poe_prompt(self, message, role="user", bot_name=None):
        pass

    def clear_messages(self):
        self.messages = []

    def get_messages(self):
        return self.messages