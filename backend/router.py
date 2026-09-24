import time
import httpx
from typing import List, Dict, Any, Optional, Tuple, AsyncGenerator
from backend.database import get_all_channels, update_channel
from backend.providers import get_provider
from backend.config import REQUEST_TIMEOUT

class ModelRouter:
    def __init__(self):
        self._round_robin_counter: Dict[str, int] = {}

    def get_available_models(self) -> List[Dict[str, Any]]:
        channels = get_all_channels(active_only=True)
        model_set = set(["auto"])
        model_details = [{
            "id": "auto",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "smart-router",
            "channel_name": "自动故障转移与轮询模式 (Auto Failover Pool)"
        }]

        for ch in channels:
            for m in ch.get("models", []):
                if m not in model_set:
                    model_set.add(m)
                    model_details.append({
                        "id": m,
                        "object": "model",
                        "created": int(time.time()),
                        "owned_by": ch.get("provider_type", "free-pool"),
                        "channel_name": ch.get("name")
                    })
        return model_details

    def get_candidate_channels(self, requested_model: str) -> List[Dict[str, Any]]:
        channels = get_all_channels(active_only=True)
        matched = []

        for ch in channels:
            models = ch.get("models", [])
            # Direct match, wildcard, or prefix match
            if requested_model in models or "*" in models:
                matched.append(ch)
            else:
                # Case-insensitive or common alias match
                for m in models:
                    if m.lower() == requested_model.lower():
                        matched.append(ch)
                        break

        # If no strict match, fallback to healthy active channels
        if not matched and channels:
            matched = [ch for ch in channels if ch.get("last_status") == "healthy"] or channels

        # Sort: healthy first, then by weight descending, then by lower latency
        def sort_key(c):
            status_score = 0 if c.get("last_status") == "healthy" else 1
            weight_score = -c.get("weight", 1)
            latency_score = c.get("last_latency_ms", 9999)
            return (status_score, weight_score, latency_score)

        matched.sort(key=sort_key)
        return matched

    def pick_key_for_channel(self, channel: Dict[str, Any]) -> str:
        raw_key = channel.get("api_key", "").strip()
        keys = [k.strip() for k in raw_key.replace(",", "\n").splitlines() if k.strip()]
        if not keys:
            return ""
        ch_id = str(channel.get("id"))
        idx = self._round_robin_counter.get(ch_id, 0)
        selected_key = keys[idx % len(keys)]
        self._round_robin_counter[ch_id] = (idx + 1) % len(keys)
        return selected_key

    async def forward_chat_completion(
        self,
        request_body: Dict[str, Any],
        stream: bool = False
    ) -> Tuple[Optional[httpx.Response], Optional[AsyncGenerator[bytes, None]], Optional[Dict[str, Any]]]:
        """
        Forward request with automatic failover across candidate channels and fallback models.
        Returns (response_obj, async_stream_generator, channel_used).
        """
        requested_model = request_body.get("model", "auto")

        # Define model-level fallback sequence
        auto_pool = ["gpt-4o", "gpt-4o-mini", "qwen-coder-free", "mistral-free"]
        if requested_model in ("auto", "auto-free", "default"):
            idx = self._round_robin_counter.get("__auto__", 0)
            self._round_robin_counter["__auto__"] = idx + 1
            # Round-robin starting point across the auto pool
            models_to_try = auto_pool[idx % len(auto_pool):] + auto_pool[:idx % len(auto_pool)]
        elif requested_model in ("gpt-4o", "claude-3-5-sonnet", "claude-3-5-sonnet-20241022", "gemini-1.5-pro", "codex"):
            models_to_try = [requested_model, "gpt-4o-mini", "qwen-coder-free", "mistral-free"]
        elif requested_model in ("gpt-4o-mini", "claude-3-5-haiku", "claude-3-haiku-20240307", "gemini-1.5-flash"):
            models_to_try = [requested_model, "gpt-4o", "qwen-coder-free", "mistral-free"]
        else:
            models_to_try = [requested_model, "gpt-4o", "gpt-4o-mini", "qwen-coder-free"]

        last_error = None

        for current_model in models_to_try:
            candidates = self.get_candidate_channels(current_model)
            if not candidates:
                continue

            for ch in candidates:
                provider = get_provider(ch.get("provider_type", "generic"))
                api_key = self.pick_key_for_channel(ch)
                if not api_key and ch.get("provider_type") != "free_reverse":
                    continue

                url = provider.format_chat_url(ch.get("base_url"))
                headers = provider.format_headers(api_key or "no-key")

                payload = dict(request_body)
                if hasattr(provider, "MODEL_MAPPING") and current_model in provider.MODEL_MAPPING:
                    payload["model"] = provider.MODEL_MAPPING[current_model]
                else:
                    payload["model"] = current_model
                
                # Check for proxy configuration (Channel 8 uses high-speed node proxy)
                proxy_url = ch.get("proxy_url") or ("http://127.0.0.1:7890" if ch.get("id") == 8 else None)
                start_time = time.time()

                try:
                    client = httpx.AsyncClient(timeout=20.0, proxy=proxy_url)

                    if stream:
                        req = client.build_request("POST", url, headers=headers, json=payload)
                        response = await client.send(req, stream=True)

                        if response.status_code == 200:
                            latency_ms = int((time.time() - start_time) * 1000)
                            update_channel(ch["id"], {
                                "last_status": "healthy",
                                "last_latency_ms": latency_ms,
                                "last_checked_at": time.strftime("%Y-%m-%d %H:%M:%S")
                            })

                            async def stream_generator():
                                try:
                                    async for chunk in response.aiter_bytes():
                                        yield chunk
                                finally:
                                    await response.aclose()
                                    await client.aclose()

                            return None, stream_generator(), ch
                        else:
                            err_content = await response.aread()
                            await response.aclose()
                            await client.aclose()

                            latency_ms = int((time.time() - start_time) * 1000)
                            status_str = "rate_limited" if response.status_code == 429 else "error"
                            err_msg = f"HTTP {response.status_code}: {err_content.decode('utf-8', errors='ignore')[:200]}"

                            update_channel(ch["id"], {
                                "last_status": status_str,
                                "last_latency_ms": latency_ms,
                                "last_error": err_msg,
                                "last_checked_at": time.strftime("%Y-%m-%d %H:%M:%S")
                            })
                            last_error = err_msg
                            continue # Try next candidate channel/model

                    else:
                        async with client:
                            response = await client.post(url, headers=headers, json=payload)
                            latency_ms = int((time.time() - start_time) * 1000)

                            if response.status_code == 200:
                                update_channel(ch["id"], {
                                    "last_status": "healthy",
                                    "last_latency_ms": latency_ms,
                                    "last_checked_at": time.strftime("%Y-%m-%d %H:%M:%S")
                                })
                                return response, None, ch
                            else:
                                status_str = "rate_limited" if response.status_code == 429 else "error"
                                err_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                                update_channel(ch["id"], {
                                    "last_status": status_str,
                                    "last_latency_ms": latency_ms,
                                    "last_error": err_msg,
                                    "last_checked_at": time.strftime("%Y-%m-%d %H:%M:%S")
                                })
                                last_error = err_msg
                                continue # Try next candidate channel/model

                except Exception as e:
                    err_msg = f"请求异常: {str(e)}"
                    update_channel(ch["id"], {
                        "last_status": "error",
                        "last_error": err_msg,
                        "last_checked_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    last_error = err_msg
                    continue

        raise RuntimeError(f"所有候选渠道与轮询模型均调用失败。最后错误: {last_error}")

router = ModelRouter()
