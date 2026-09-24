import time
import secrets
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.database import (
    get_all_channels, get_channel_by_id, create_channel,
    update_channel, delete_channel, get_access_tokens,
    create_access_token, delete_access_token, get_stats
)
from backend.free_guide import get_free_guides
from backend.providers import get_provider

admin_router = APIRouter(prefix="/api", tags=["Admin and Management API"])

class ChannelCreateSchema(BaseModel):
    name: str
    provider_type: str
    base_url: str
    api_key: str
    models: List[str]
    is_active: bool = True
    weight: int = 1
    balance_info: Optional[Dict[str, Any]] = None

class ChannelUpdateSchema(BaseModel):
    name: Optional[str] = None
    provider_type: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    models: Optional[List[str]] = None
    is_active: Optional[bool] = None
    weight: Optional[int] = None
    balance_info: Optional[Dict[str, Any]] = None

class TestRawSchema(BaseModel):
    provider_type: str
    base_url: str
    api_key: str
    model: str

class TokenCreateSchema(BaseModel):
    name: str
    quota_limit: int = -1

class ImportGuideSchema(BaseModel):
    guide_id: str
    api_key: str

@admin_router.get("/stats")
async def stats():
    return get_stats()

@admin_router.get("/channels")
async def list_channels():
    return get_all_channels()

@admin_router.post("/channels")
async def add_channel(payload: ChannelCreateSchema):
    channel_id = create_channel(payload.model_dump())
    return {"id": channel_id, "message": "渠道添加成功"}

@admin_router.put("/channels/{channel_id}")
async def edit_channel(channel_id: int, payload: ChannelUpdateSchema):
    ch = get_channel_by_id(channel_id)
    if not ch:
        raise HTTPException(status_code=404, detail="渠道不存在")
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    update_channel(channel_id, update_data)
    return {"message": "渠道更新成功"}

@admin_router.delete("/channels/{channel_id}")
async def remove_channel(channel_id: int):
    delete_channel(channel_id)
    return {"message": "渠道已删除"}

@admin_router.post("/channels/{channel_id}/test")
async def test_channel(channel_id: int):
    ch = get_channel_by_id(channel_id)
    if not ch:
        raise HTTPException(status_code=404, detail="渠道不存在")

    provider = get_provider(ch["provider_type"])
    models = ch.get("models", [])
    test_model = models[0] if models else "glm-4-flash"

    # Pick first key
    keys = [k.strip() for k in ch["api_key"].replace(",", "\n").splitlines() if k.strip()]
    if not keys:
        raise HTTPException(status_code=400, detail="渠道未配置有效的 API Key")

    res = await provider.check_health(ch["base_url"], keys[0], test_model)
    balance_res = await provider.query_balance(ch["base_url"], keys[0])

    # Update channel status in DB
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    update_channel(channel_id, {
        "last_status": res["status"],
        "last_latency_ms": res.get("latency_ms", 0),
        "last_checked_at": now,
        "last_error": res.get("message", "") if res["status"] != "healthy" else "",
        "balance_info": balance_res
    })

    return {
        "test_result": res,
        "balance": balance_res,
        "tested_model": test_model
    }

@admin_router.post("/channels/test_raw")
async def test_raw_channel(payload: TestRawSchema):
    provider = get_provider(payload.provider_type)
    res = await provider.check_health(payload.base_url, payload.api_key.strip(), payload.model.strip())
    balance_res = await provider.query_balance(payload.base_url, payload.api_key.strip())
    return {
        "test_result": res,
        "balance": balance_res
    }

@admin_router.get("/guides")
async def list_guides():
    return get_free_guides()

@admin_router.post("/channels/import_guide")
async def import_guide(payload: ImportGuideSchema):
    guides = {g["id"]: g for g in get_free_guides()}
    guide = guides.get(payload.guide_id)
    if not guide:
        raise HTTPException(status_code=404, detail="找不到该免费额度指南")

    cfg = guide["default_config"]
    channel_data = {
        "name": cfg["name"],
        "provider_type": cfg["provider_type"],
        "base_url": cfg["base_url"],
        "api_key": payload.api_key.strip(),
        "models": cfg["models"],
        "is_active": True,
        "weight": 10,
        "balance_info": {"plan": guide["badge"], "notes": guide["free_policy"]}
    }
    channel_id = create_channel(channel_data)

    # Immediately perform health check in background or synchronously
    provider = get_provider(cfg["provider_type"])
    test_model = cfg["models"][0] if cfg["models"] else "glm-4-flash"
    test_res = await provider.check_health(cfg["base_url"], payload.api_key.strip(), test_model)

    update_channel(channel_id, {
        "last_status": test_res["status"],
        "last_latency_ms": test_res.get("latency_ms", 0),
        "last_checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "last_error": test_res.get("message", "") if test_res["status"] != "healthy" else ""
    })

    return {
        "channel_id": channel_id,
        "message": f"成功导入 {guide['name']} 渠道！",
        "health": test_res
    }

@admin_router.get("/tokens")
async def list_tokens():
    return get_access_tokens()

@admin_router.post("/tokens")
async def add_token(payload: TokenCreateSchema):
    generated_key = f"sk-free-{secrets.token_hex(16)}"
    token_id = create_access_token(payload.name, generated_key, payload.quota_limit)
    return {
        "id": token_id,
        "token": generated_key,
        "name": payload.name,
        "message": "聚合访问令牌创建成功"
    }

@admin_router.delete("/tokens/{token_id}")
async def remove_token(token_id: int):
    delete_access_token(token_id)
    return {"message": "令牌已删除"}
