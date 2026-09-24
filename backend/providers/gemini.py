from backend.providers.base import BaseProvider
from typing import Dict, Any

class GeminiProvider(BaseProvider):
    provider_type: str = "gemini"

    async def query_balance(self, base_url: str, api_key: str) -> Dict[str, Any]:
        return {
            "status": "active",
            "tier": "AI Studio 免费层",
            "notes": "15 RPM 永久免费层，每天多达 1500 次调用，支持 1.5/2.0 Flash 系列"
        }
