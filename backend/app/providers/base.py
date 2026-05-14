from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, model: str | None = None) -> str: ...

    @abstractmethod
    async def embed(self, text: str, model: str | None = None) -> list[float]: ...
