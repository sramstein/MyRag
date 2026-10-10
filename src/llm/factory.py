from src.config import LlmConfig
from src.llm.base import BaseLLM
from src.llm.gemini_llm import GeminiLLM
from src.llm.local_llm import LocalLLM

def get_llm(config: LlmConfig) -> BaseLLM:
    """Factory to instantiate the configured LLM provider."""
    provider = config.provider.lower()
    if provider == "gemini":
        return GeminiLLM(
            model_name=config.model_name,
            temperature=config.temperature,
            max_output_tokens=config.max_output_tokens,
        )
    elif provider == "local":
        return LocalLLM(
            ollama_url=config.ollama_url,
            ollama_model=config.ollama_model,
            temperature=config.temperature,
        )
    else:
        return LocalLLM()
