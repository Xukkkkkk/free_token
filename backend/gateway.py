import time
import json
from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional, Dict, Any

from backend.router import router
from backend.database import validate_access_token, record_token_usage, log_request
from backend.config import DEFAULT_MASTER_KEY

gateway_router = APIRouter(prefix="/v1", tags=["OpenAI Compatible Gateway"])

def authenticate_client(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Validate bearer token from external client"""
    if not authorization:
        # Default allow or require token?
        # If client passes no token, we check if default master key is acceptable or allow localhost
        return {"name": "Default Guest", "token": DEFAULT_MASTER_KEY}

    token = authorization.replace("Bearer ", "").strip()
    if token == DEFAULT_MASTER_KEY:
        return {"name": "Master Admin", "token": DEFAULT_MASTER_KEY}

    record = validate_access_token(token)
    if not record:
        raise HTTPException(status_code=401, detail="Invalid API Key. Please provide a valid platform token.")
    return record

@gateway_router.get("/models")
async def list_models(authorization: Optional[str] = Header(None)):
    """Return all available models across all active free channels"""
    authenticate_client(authorization)
    models = router.get_available_models()
    return {
        "object": "list",
        "data": models
    }

@gateway_router.get("/models/{model_name}")
async def get_model(model_name: str, authorization: Optional[str] = Header(None)):
    authenticate_client(authorization)
    return {
        "id": model_name,
        "object": "model",
        "created": int(time.time()),
        "owned_by": "free-ai-pool"
    }

@gateway_router.post("/chat/completions")
async def chat_completions(request: Request, authorization: Optional[str] = Header(None)):
    client_token_info = authenticate_client(authorization)
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    model = body.get("model", "glm-4-flash")
    stream = body.get("stream", False)
    start_time = time.time()

    try:
        response, stream_gen, used_channel = await router.forward_chat_completion(body, stream=stream)
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        log_request(
            channel_id=None,
            channel_name="No Channel",
            model=model,
            prompt_tokens=0,
            completion_tokens=0,
            latency_ms=latency_ms,
            status="error",
            error_message=str(e)
        )
        raise HTTPException(status_code=502, detail=str(e))

    latency_ms = int((time.time() - start_time) * 1000)
    channel_id = used_channel["id"] if used_channel else None
    channel_name = used_channel["name"] if used_channel else "Unknown"

    if stream and stream_gen:
        # Stream response back to client with event-stream header
        # Also wrap stream to log completion
        async def event_generator():
            try:
                async for chunk in stream_gen:
                    yield chunk
                # Log success after streaming completes
                log_request(
                    channel_id=channel_id,
                    channel_name=channel_name,
                    model=model,
                    prompt_tokens=10,
                    completion_tokens=30, # Estimated for streaming
                    latency_ms=latency_ms,
                    status="success"
                )
                record_token_usage(client_token_info.get("token", ""), 40)
            except Exception as stream_err:
                log_request(
                    channel_id=channel_id,
                    channel_name=channel_name,
                    model=model,
                    prompt_tokens=0,
                    completion_tokens=0,
                    latency_ms=latency_ms,
                    status="error",
                    error_message=f"Stream broken: {str(stream_err)}"
                )

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    else:
        # Non-streaming response
        try:
            resp_data = response.json()
        except Exception:
            resp_data = {"error": "Invalid response from upstream"}

        # Extract tokens count if present
        usage = resp_data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = prompt_tokens + completion_tokens

        log_request(
            channel_id=channel_id,
            channel_name=channel_name,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            status="success"
        )
        record_token_usage(client_token_info.get("token", ""), total_tokens)

        return JSONResponse(content=resp_data, status_code=response.status_code)
