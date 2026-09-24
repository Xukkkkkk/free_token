from backend.providers.base import BaseProvider
from typing import Dict, Any

class GLMProvider(BaseProvider):
    provider_type: str = "glm"

    async def query_balance(self, base_url: str, api_key: str) -> Dict[str, Any]:
        return {
            "status": "active",
            "tier": "免费通道",
            "notes": "glm-4-flash 模型永久免费；新用户附赠千万 Token 体验包"
        }
