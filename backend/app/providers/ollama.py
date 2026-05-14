import httpx
from app.core.config import settings
from app.providers.base import BaseLLMProvider

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")

    async def generate(self, prompt: str, model: str | None = None) -> str:
        payload = {"model": model or settings.default_generation_model, "prompt": prompt, "stream": False}
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json().get("response", "")

    async def embed(self, text: str, model: str | None = None) -> list[float]:
        payload = {"model": model or settings.default_embedding_model, "input": text}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{self.base_url}/api/embed", json=payload)
            response.raise_for_status()
            data = response.json()
            embeddings = data.get("embeddings") or []
            return embeddings[0] if embeddings else []
