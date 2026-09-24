import random
import time
import httpx
import json
from typing import List, Dict, Any, Optional, Tuple, AsyncGenerator
from backend.database import get_all_channels, update_channel, log_request
from backend.providers import get_provider
from backend.config import REQUEST_TIMEOUT

class ModelRouter:
    def __init__(self):
        self._round_robin_counter: Dict[str, int] = {}

    def get_available_models(self) -> List[Dict[str, Any]]:
        channels = get_all_channels(active_only=True)
        model_set = set()
        model_details = []

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

        # If no strict match, find channels that might have generic models
        if not matched and channels:
            # Fallback to the first healthy active channel
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
        """If a channel has multiple keys (comma or newline separated), rotate or randomly pick one."""
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
        Forward request with automatic failover across candidate channels.
        Returns (response_obj, async_stream_generator, channel_used).
        """
        requested_model = request_body.get("model", "glm-4-flash")
        candidates = self.get_candidate_channels(requested_model)

        if not candidates:
            raise ValueError(f"当前平台没有可用的渠道支持模型: '{requested_model}'。请先在后台添加或激活相应渠道。")

        last_error = None

        for ch in candidates:
            provider = get_provider(ch.get("provider_type", "generic"))
            api_key = self.pick_key_for_channel(ch)
            if not api_key and ch.get("provider_type") != "free_reverse":
                continue

            url = provider.format_chat_url(ch.get("base_url"))
            headers = provider.format_headers(api_key or "no-key")

            # Ensure model payload is set and mapped if provider specifies MODEL_MAPPING
            payload = dict(request_body)
            if hasattr(provider, "MODEL_MAPPING") and requested_model in provider.MODEL_MAPPING:
                payload["model"] = provider.MODEL_MAPPING[requested_model]
            start_time = time.time()

            try:
                client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)

                if stream:
                    # Stream mode
                    req = client.build_request("POST", url, headers=headers, json=payload)
                    response = await client.send(req, stream=True)

                    if response.status_code == 200:
                        # Success streaming
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
                        # Error response from upstream
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
                        continue # Try next candidate channel

                else:
                    # Non-stream mode
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
                            continue # Try next candidate channel

            except Exception as e:
                err_msg = f"请求异常: {str(e)}"
                update_channel(ch["id"], {
                    "last_status": "error",
                    "last_error": err_msg,
                    "last_checked_at": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                last_error = err_msg
                continue

        raise RuntimeError(f"所有候选渠道调用失败。最后错误: {last_error}")

router = ModelRouter()
