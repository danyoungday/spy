"""
From jailbreak.
"""
import openai
import os
from typing import List, Dict

# Set your OpenAI API key
# openai.api_key = "your-api-key-here"  # Uncomment and add your key, or set as environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")


class Agent:
    def __init__(self,
                 system_prompt: str,
                 model: str = "gpt-4o-mini",
                 temperature: float = 0.7,
                 max_tokens: int = 16384,
                 name: str = 'agent'):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.conversation_history: List[Dict] = []
        self.temperature = temperature
        self.max_tokens = max_tokens

    def add_to_history(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def get_response(self, new_message: str) -> str:
        # Create messages array with system prompt and conversation history
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": new_message})

        # Make API call to OpenAI
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            reply = response.choices[0].message.content
            # Add this exchange to the history
            self.add_to_history("user", new_message)
            self.add_to_history("assistant", reply)
            return reply
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return "Error generating response."

