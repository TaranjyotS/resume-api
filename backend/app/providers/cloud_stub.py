from app.providers.base import BaseLLMProvider

class CloudProviderStub(BaseLLMProvider):
    """Placeholder adapter for OpenAI/Claude/Gemini/Bedrock/Azure OpenAI.
    Add SDK calls here. Keep this interface stable so the app can switch providers.
    """
    async def generate(self, prompt: str, model: str | None = None) -> str:
        raise NotImplementedError("Cloud provider is not configured. Use Ollama or implement this adapter.")

    async def embed(self, text: str, model: str | None = None) -> list[float]:
        raise NotImplementedError("Cloud embeddings are not configured. Use Ollama embeddings first.")
