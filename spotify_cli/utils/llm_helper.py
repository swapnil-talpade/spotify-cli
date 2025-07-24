"""LLM Helper module for enhancing search queries"""

import requests
from typing import Optional


class LLMHelper:
    def __init__(self):
        self.api_url = "http://localhost:11434/api/generate"
        self.model = "mistral"  # or "mistral-openorca" for better performance

    def generate(self, prompt: str) -> Optional[str]:
        """Generate response from Ollama"""
        try:
            response = requests.post(
                self.api_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return None
