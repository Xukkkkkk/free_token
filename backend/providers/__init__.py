from backend.providers.base import BaseProvider
from backend.providers.glm import GLMProvider
from backend.providers.qwen import QwenProvider
from backend.providers.gemini import GeminiProvider
from backend.providers.extras import GitHubModelsProvider, OpenRouterProvider, GroqProvider

PROVIDERS = {
    "glm": GLMProvider(),
    "qwen": QwenProvider(),
    "gemini": GeminiProvider(),
    "github": GitHubModelsProvider(),
    "openrouter": OpenRouterProvider(),
    "groq": GroqProvider(),
    "generic": BaseProvider()
}

def get_provider(provider_type: str) -> BaseProvider:
    return PROVIDERS.get(provider_type.lower(), PROVIDERS["generic"])
