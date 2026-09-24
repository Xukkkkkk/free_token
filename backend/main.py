import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import FRONTEND_DIR, HOST, PORT
from backend.database import init_db, get_all_channels, update_channel
from backend.api import admin_router
from backend.gateway import gateway_router
from backend.providers import get_provider

async def background_health_checker():
    """Periodic background health check for all active channels"""
    while True:
        try:
            await asyncio.sleep(600) # Every 10 minutes
            channels = get_all_channels(active_only=True)
            for ch in channels:
                raw_key = ch.get("api_key", "").strip()
                if not raw_key or "请在此填入" in raw_key:
                    continue
                keys = [k.strip() for k in raw_key.replace(",", "\n").splitlines() if k.strip()]
                if not keys:
                    continue
                provider = get_provider(ch.get("provider_type", "generic"))
                models = ch.get("models", [])
                test_model = models[0] if models else "glm-4-flash"
                res = await provider.check_health(ch["base_url"], keys[0], test_model)
                update_channel(ch["id"], {
                    "last_status": res["status"],
                    "last_latency_ms": res.get("latency_ms", 0),
                    "last_error": res.get("message", "") if res["status"] != "healthy" else ""
                })
        except asyncio.CancelledError:
            break
        except Exception:
            pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    bg_task = asyncio.create_task(background_health_checker())
    yield
    # Shutdown
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Free AI Quota Hub & Aggregator (大模型免费额度聚合平台)",
    description="聚合 GLM、通义千问、Gemini、GitHub Models 等各大平台官方免费额度，提供统一标准 OpenAI 接口",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for any frontend or client extensions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(gateway_router)
app.include_router(admin_router)

# Serve Frontend SPA
@app.get("/")
async def serve_index():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Free AI Quota Hub is running. Please access /api or /v1."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=PORT, reload=True)
