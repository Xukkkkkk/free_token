import time
import httpx
from typing import Dict, Any, Optional

class BaseProvider:
    provider_type: str = "generic"

    def format_headers(self, api_key: str) -> Dict[str, str]:
        key = api_key.strip()
        return {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

    def format_chat_url(self, base_url: str) -> str:
        base = base_url.rstrip("/")
        if not base.endswith("/chat/completions"):
            return f"{base}/chat/completions"
        return base

    def format_models_url(self, base_url: str) -> str:
        base = base_url.rstrip("/")
        if base.endswith("/chat/completions"):
            base = base[:-len("/chat/completions")]
        return f"{base}/models"

    async def check_health(self, base_url: str, api_key: str, model: str) -> Dict[str, Any]:
        """Perform a test ping by sending a minimal token generation request."""
        url = self.format_chat_url(base_url)
        headers = self.format_headers(api_key)
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5,
            "temperature": 0.1
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
                        "message": "连接正常，响应迅速"
                    }
                elif res.status_code == 429:
                    return {
                        "status": "rate_limited",
                        "latency_ms": latency_ms,
                        "message": f"触发频次限制或免费配额超限 (429): {res.text[:120]}"
                    }
                elif res.status_code in (401, 403):
                    return {
                        "status": "error",
                        "latency_ms": latency_ms,
                        "message": f"API Key 无效或未授权 ({res.status_code})"
                    }
                else:
                    return {
                        "status": "error",
                        "latency_ms": latency_ms,
                        "message": f"服务返回异常 HTTP {res.status_code}: {res.text[:120]}"
                    }
        except httpx.ConnectTimeout:
            return {
                "status": "error",
                "latency_ms": 15000,
                "message": "连接超时（若使用海外平台如 Gemini，请检查本地代理环境）"
            }
        except Exception as e:
            return {
                "status": "error",
                "latency_ms": 0,
                "message": f"网络异常: {str(e)}"
            }

    async def query_balance(self, base_url: str, api_key: str) -> Dict[str, Any]:
        """Default fallback balance info"""
        return {"status": "ok", "info": "使用官方免费额度/按量计费"}
