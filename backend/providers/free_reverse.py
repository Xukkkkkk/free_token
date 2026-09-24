import time
import httpx
from typing import Dict, Any, List
from backend.providers.base import BaseProvider

class FreeReverseProvider(BaseProvider):
    provider_type: str = "free_reverse"

    # Multi-endpoint redundant pool for zero-key high availability
    UPSTREAM_ENDPOINTS: List[str] = [
        "https://gen.pollinations.ai/v1",
        "https://text.pollinations.ai/openai"
    ]

    MODEL_MAPPING = {
        "gpt-4o": "openai",
        "gpt-4o-mini": "openai",
        "gpt-4o-free": "openai",
        "gpt-4o-mini-free": "openai",
        "qwen-coder": "qwen-coder",
        "qwen-coder-free": "qwen-coder",
        "mistral": "mistral",
        "mistral-free": "mistral",
        "claude-3-5-sonnet": "openai",
        "claude-3-5-haiku": "openai",
        "gemini-1.5-pro": "openai",
        "gemini-1.5-flash": "openai"
    }

    def format_headers(self, api_key: str) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

    async def check_health(self, base_url: str, api_key: str, model: str) -> Dict[str, Any]:
        endpoints = [base_url] if base_url else self.UPSTREAM_ENDPOINTS
        headers = self.format_headers(api_key)
        upstream_model = self.MODEL_MAPPING.get(model, "openai")
        payload = {
            "model": upstream_model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5
        }
        
        last_error = None
        for ep in endpoints:
            url = self.format_chat_url(ep)
            start = time.time()
            try:
                async with httpx.AsyncClient(timeout=12.0) as client:
                    res = await client.post(url, headers=headers, json=payload)
                    latency_ms = int((time.time() - start) * 1000)
                    if res.status_code == 200:
                        return {
                            "status": "healthy",
                            "latency_ms": latency_ms,
                            "message": f"免Key公共通道正常 ({ep.split('//')[1].split('/')[0]})"
                        }
                    else:
                        last_error = f"HTTP {res.status_code}"
            except Exception as e:
                last_error = str(e)

        return {
            "status": "error",
            "latency_ms": 0,
            "message": f"公共接口异常: {last_error}"
        }

    async def query_balance(self, base_url: str, api_key: str) -> Dict[str, Any]:
        return {
            "status": "active",
            "tier": "免Key公共通道 (双节点双冗余)",
            "notes": "聚合多个全球公共免鉴权算力池，全天候零门槛高可用"
        }
