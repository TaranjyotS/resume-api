from app.providers.ollama import OllamaProvider
from app.providers.cloud_stub import CloudProviderStub

class AIProviderRouter:
    def get(self, provider: str):
        provider = provider.lower()
        if provider == "ollama":
            return OllamaProvider()
        return CloudProviderStub()

ai_router = AIProviderRouter()
