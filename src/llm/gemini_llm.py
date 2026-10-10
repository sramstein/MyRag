import os
from typing import Generator, Optional
from src.llm.base import BaseLLM

class GeminiLLM(BaseLLM):
    """Google Gemini LLM implementation using the official google-genai SDK."""

    def __init__(
        self,
        model_name: str = "gemini-3.8-flash",
        api_key: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1024,
    ):
        from google import genai

        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is required to use Gemini LLM. "
                "Get a free API key at https://aistudio.google.com/ and set GEMINI_API_KEY in .env"
            )
        self.client = genai.Client(api_key=self.api_key)

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        from google.genai import types

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config,
        )
        return response.text or ""

    def stream(self, prompt: str, system_instruction: Optional[str] = None) -> Generator[str, None, None]:
        from google.genai import types

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
        )
        response_stream = self.client.models.generate_content_stream(
            model=self.model_name,
            contents=prompt,
            config=config,
        )
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
