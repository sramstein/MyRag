from abc import ABC, abstractmethod
from typing import Generator, Optional

class BaseLLM(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate a complete text response."""
        pass

    @abstractmethod
    def stream(self, prompt: str, system_instruction: Optional[str] = None) -> Generator[str, None, None]:
        """Stream chunks of the generated response."""
        pass
