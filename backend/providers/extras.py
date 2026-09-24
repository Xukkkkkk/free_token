import httpx
from backend.providers.base import BaseProvider
from typing import Dict, Any

class GitHubModelsProvider(BaseProvider):
    provider_type: str = "github"

    async def query_balance(self, base_url: str, api_key: str) -> Dict[str, Any]:
        return {
            "status": "active",
            "tier": "GitHub 开发者限免",
            "notes": "支持 GPT-4o、o1-mini、DeepSeek-R1 免费调用"
        }

class OpenRouterProvider(BaseProvider):
    provider_type: str = "openrouter"

    def format_headers(self, api_key: str) -> Dict[str, str]:
        headers = super().format_headers(api_key)
        headers["HTTP-Referer"] = "https://github.com/free-ai-quota-pool"
        headers["X-Title"] = "Free AI Quota Hub"
        return headers

    async def query_balance(self, base_url: str, api_key: str) -> Dict[str, Any]:
        url = "https://openrouter.ai/api/v1/auth/key"
        headers = self.format_headers(api_key)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    data = res.json().get("data", {})
                    limit = data.get("limit")
                    usage = data.get("usage", 0)
                    is_free_tier = data.get("is_free_tier", True)
                    return {
                        "status": "active",
                        "tier": "免费层" if is_free_tier else "标准层",
                        "usage": f"${usage:.4f}",
                        "limit": f"${limit:.4f}" if limit is not None else "无限制",
                        "notes": "支持所有带有 :free 标识的免费模型"
                    }
        except Exception:
            pass
        return {
            "status": "active",
            "tier": "免费模型池",
            "notes": "支持所有带有 :free 标识的模型"
        }

class GroqProvider(BaseProvider):
    provider_type: str = "groq"

    async def query_balance(self, base_url: str, api_key: str) -> Dict[str, Any]:
        return {
            "status": "active",
            "tier": "极速 LPU 免费层",
            "notes": "支持 Llama 3.3 70B、Mixtral 等，超低延迟"
        }
