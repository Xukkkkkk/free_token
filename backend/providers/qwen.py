from backend.providers.base import BaseProvider
from typing import Dict, Any

class QwenProvider(BaseProvider):
    provider_type: str = "qwen"

    async def query_balance(self, base_url: str, api_key: str) -> Dict[str, Any]:
        return {
            "status": "active",
            "tier": "百炼试用/免费额度",
            "notes": "支持 Qwen-Turbo、Qwen-Plus、Qwen2.5-Coder 等模型"
        }
