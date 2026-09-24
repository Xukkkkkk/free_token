import sqlite3
import json
import datetime
from typing import List, Dict, Any, Optional
from backend.config import DB_PATH, DEFAULT_MASTER_KEY

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Channels table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        provider_type TEXT NOT NULL,
        base_url TEXT NOT NULL,
        api_key TEXT NOT NULL,
        models TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        weight INTEGER DEFAULT 1,
        balance_info TEXT DEFAULT '{}',
        last_status TEXT DEFAULT 'unknown',
        last_latency_ms INTEGER DEFAULT 0,
        last_checked_at TEXT DEFAULT '',
        last_error TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # Access tokens table (Tokens generated for external apps like NextChat, Cursor, LobeChat)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS access_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        token TEXT UNIQUE NOT NULL,
        is_active INTEGER DEFAULT 1,
        quota_limit INTEGER DEFAULT -1,
        quota_used INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    # Request logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS request_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id INTEGER,
        channel_name TEXT,
        model TEXT,
        prompt_tokens INTEGER DEFAULT 0,
        completion_tokens INTEGER DEFAULT 0,
        latency_ms INTEGER DEFAULT 0,
        status TEXT DEFAULT 'success',
        error_message TEXT DEFAULT '',
        created_at TEXT NOT NULL
    )
    """)

    # Seed default master access token if none exists
    cursor.execute("SELECT COUNT(*) as count FROM access_tokens")
    if cursor.fetchone()["count"] == 0:
        now = datetime.datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO access_tokens (name, token, is_active, quota_limit, quota_used, created_at)
            VALUES (?, ?, 1, -1, 0, ?)
        """, ("默认聚合令牌 (Default Master Token)", DEFAULT_MASTER_KEY, now))

    # Pre-seed template channels if table is empty
    cursor.execute("SELECT COUNT(*) as count FROM channels")
    if cursor.fetchone()["count"] == 0:
        now = datetime.datetime.now().isoformat()
        seed_channels = [
            (
                "智谱 AI (GLM 免费通道 - 填入Key即可)",
                "glm",
                "https://open.bigmodel.cn/api/paas/v4",
                "请在此填入您的智谱API Key",
                json.dumps(["glm-4-flash", "glm-4-flashx", "glm-4-plus", "glm-4-air"]),
                0, # Disabled until user inputs key
                10,
                json.dumps({"plan": "永久免费", "notes": "glm-4-flash 完全免额度费用"}),
                "unknown",
                now,
                now
            ),
            (
                "阿里通义千问 (DashScope 百炼免费试用)",
                "qwen",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "请在此填入您的阿里DashScope API Key",
                json.dumps(["qwen-turbo", "qwen-plus", "qwen2.5-coder-32b-instruct", "qwen-long"]),
                0,
                10,
                json.dumps({"plan": "新客赠送千万Token", "notes": "支持 Qwen2.5 全系列"}),
                "unknown",
                now,
                now
            ),
            (
                "Google Gemini (AI Studio 永久免费层)",
                "gemini",
                "https://generativelanguage.googleapis.com/v1beta/openai",
                "请在此填入您的Gemini API Key",
                json.dumps(["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]),
                0,
                10,
                json.dumps({"plan": "15 RPM 永久免费", "notes": "无需绑卡，每天千次调用"}),
                "unknown",
                now,
                now
            ),
            (
                "GitHub Models (免费 GPT-4o / Claude)",
                "github",
                "https://models.inference.ai.azure.com",
                "请在此填入您的GitHub Personal Access Token",
                json.dumps(["gpt-4o", "gpt-4o-mini", "o1-mini", "DeepSeek-R1"]),
                0,
                10,
                json.dumps({"plan": "GitHub 开发者限免", "notes": "微软Azure官方提供免费测试配额"}),
                "unknown",
                now,
                now
            ),
            (
                "Groq (超高速免费 Llama 3.3)",
                "groq",
                "https://api.groq.com/openai/v1",
                "请在此填入您的Groq API Key",
                json.dumps(["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"]),
                0,
                10,
                json.dumps({"plan": "免费超高并发", "notes": "每秒500+ token 极速推理"}),
                "unknown",
                now,
                now
            ),
            (
                "OpenRouter (聚合免费模型通道)",
                "openrouter",
                "https://openrouter.ai/api/v1",
                "请在此填入您的OpenRouter API Key",
                json.dumps([
                    "google/gemini-2.0-flash-exp:free",
                    "meta-llama/llama-3.3-70b-instruct:free",
                    "deepseek/deepseek-r1:free"
                ]),
                0,
                10,
                json.dumps({"plan": ":free 后缀全免", "notes": "海量开源免费模型无缝集成"}),
                "unknown",
                now,
                now
            )
        ]
        cursor.executemany("""
            INSERT INTO channels (
                name, provider_type, base_url, api_key, models, is_active, weight,
                balance_info, last_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_channels)

    conn.commit()
    conn.close()

# Helper queries
def get_all_channels(active_only: bool = False) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if active_only:
        cursor.execute("SELECT * FROM channels WHERE is_active = 1 ORDER BY weight DESC, id ASC")
    else:
        cursor.execute("SELECT * FROM channels ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["models"] = json.loads(d["models"]) if d.get("models") else []
        try:
            d["balance_info"] = json.loads(d["balance_info"]) if d.get("balance_info") else {}
        except Exception:
            d["balance_info"] = {}
        result.append(d)
    return result

def get_channel_by_id(channel_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM channels WHERE id = ?", (channel_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["models"] = json.loads(d["models"]) if d.get("models") else []
    try:
        d["balance_info"] = json.loads(d["balance_info"]) if d.get("balance_info") else {}
    except Exception:
        d["balance_info"] = {}
    return d

def create_channel(data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    models_str = json.dumps(data.get("models", []))
    balance_str = json.dumps(data.get("balance_info", {}))
    cursor.execute("""
        INSERT INTO channels (
            name, provider_type, base_url, api_key, models, is_active, weight,
            balance_info, last_status, last_latency_ms, last_checked_at, last_error,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("provider_type"),
        data.get("base_url").rstrip("/"),
        data.get("api_key"),
        models_str,
        1 if data.get("is_active", True) else 0,
        data.get("weight", 1),
        balance_str,
        data.get("last_status", "unknown"),
        data.get("last_latency_ms", 0),
        "",
        "",
        now,
        now
    ))
    channel_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return channel_id

def update_channel(channel_id: int, data: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    fields = []
    values = []
    for k, v in data.items():
        if k in ("name", "provider_type", "base_url", "api_key", "is_active", "weight", "last_status", "last_latency_ms", "last_checked_at", "last_error"):
            if k == "base_url" and isinstance(v, str):
                v = v.rstrip("/")
            fields.append(f"{k} = ?")
            values.append(v)
        elif k == "models":
            fields.append("models = ?")
            values.append(json.dumps(v))
        elif k == "balance_info":
            fields.append("balance_info = ?")
            values.append(json.dumps(v))
    fields.append("updated_at = ?")
    values.append(now)
    values.append(channel_id)
    cursor.execute(f"UPDATE channels SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()

def delete_channel(channel_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
    conn.commit()
    conn.close()

def get_access_tokens() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM access_tokens ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_access_token(name: str, token: str, quota_limit: int = -1) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO access_tokens (name, token, is_active, quota_limit, quota_used, created_at)
        VALUES (?, ?, 1, ?, 0, ?)
    """, (name, token, quota_limit, now))
    token_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return token_id

def delete_access_token(token_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM access_tokens WHERE id = ?", (token_id,))
    conn.commit()
    conn.close()

def validate_access_token(token: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM access_tokens WHERE token = ? AND is_active = 1", (token,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def record_token_usage(token: str, tokens_count: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE access_tokens SET quota_used = quota_used + ? WHERE token = ?", (tokens_count, token))
    conn.commit()
    conn.close()

def log_request(channel_id: Optional[int], channel_name: str, model: str,
                prompt_tokens: int, completion_tokens: int, latency_ms: int,
                status: str = "success", error_message: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO request_logs (
            channel_id, channel_name, model, prompt_tokens, completion_tokens,
            latency_ms, status, error_message, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (channel_id, channel_name, model, prompt_tokens, completion_tokens, latency_ms, status, error_message, now))
    conn.commit()
    conn.close()

def get_stats() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM channels")
    total_channels = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM channels WHERE is_active = 1")
    active_channels = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM channels WHERE last_status = 'healthy' AND is_active = 1")
    healthy_channels = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count, SUM(prompt_tokens) as p_tokens, SUM(completion_tokens) as c_tokens, AVG(latency_ms) as avg_latency FROM request_logs")
    req_row = cursor.fetchone()
    total_requests = req_row["count"] or 0
    total_prompt_tokens = req_row["p_tokens"] or 0
    total_completion_tokens = req_row["c_tokens"] or 0
    avg_latency = round(req_row["avg_latency"] or 0, 1)

    # Get recent 20 logs
    cursor.execute("SELECT * FROM request_logs ORDER BY id DESC LIMIT 20")
    recent_logs = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "total_channels": total_channels,
        "active_channels": active_channels,
        "healthy_channels": healthy_channels,
        "total_requests": total_requests,
        "total_tokens": total_prompt_tokens + total_completion_tokens,
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
        "avg_latency_ms": avg_latency,
        "recent_logs": recent_logs
    }
