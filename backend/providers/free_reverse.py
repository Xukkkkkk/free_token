import time
import httpx
from typing import Dict, Any
from backend.providers.base import BaseProvider

class FreeReverseProvider(BaseProvider):
    provider_type: str = "free_reverse"

    # Map friendly/standard model names to upstream model names
    MODEL_MAPPING = {
        "auto": "openai",
        "auto-free": "openai",
        "default": "openai",
        "gpt-4o": "openai",
        "gpt-4o-mini": "openai",
        "gpt-4o-free": "openai",
        "gpt-4o-mini-free": "openai",
        "claude-3-5-sonnet": "openai",
        "claude-3-5-sonnet-20241022": "openai",
        "claude-3-5-haiku": "openai",
        "claude-3-haiku-20240307": "openai",
        "claude-3-opus-20240229": "openai",
        "claude-3-sonnet-20240229": "openai",
        "gemini-1.5-pro": "openai",
        "gemini-1.5-flash": "openai",
        "gemini-2.0-flash-exp": "openai",
        "codex": "openai",
        "qwen-coder": "openai",
        "qwen-coder-free": "openai",
        "mistral": "openai",
        "mistral-free": "openai"
    }

    def format_headers(self, api_key: str) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

    async def check_health(self, base_url: str, api_key: str, model: str) -> Dict[str, Any]:
        url = self.format_chat_url(base_url)
        headers = self.format_headers(api_key)
        upstream_model = self.MODEL_MAPPING.get(model, "openai")
        payload = {
            "model": upstream_model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5
        }
        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                latency_ms = int((time.time() - start) * 1000)
                if res.status_code == 200:
                    return {
                        "status": "healthy",
                        "latency_ms": latency_ms,
                        "message": "免Key公共通道连接正常"
                    }
                else:
                    return {
                        "status": "error",
                        "latency_ms": latency_ms,
                        "message": f"公共接口状态 HTTP {res.status_code}"
                    }
        except Exception as e:
            return {
                "status": "error",
                "latency_ms": 0,
                "message": f"连接异常: {str(e)}"
            }

    async def query_balance(self, base_url: str, api_key: str) -> Dict[str, Any]:
        return {
            "status": "active",
            "tier": "免Key公共通道",
            "notes": "无需注册账号与API Key，由公共逆向聚合池提供算力"
        }
