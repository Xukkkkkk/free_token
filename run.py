import sys
import os
import uvicorn

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import HOST, PORT

def main():
    print("=" * 65)
    print("  🚀 Free AI Quota Hub (大模型免费额度聚合平台)")
    print("=" * 65)
    print(f"  ● 本地控制台地址:   http://localhost:{PORT}")
    print(f"  ● OpenAI 兼容端点:  http://localhost:{PORT}/v1")
    print(f"  ● 默认 Master 令牌:  sk-free-ai-pool-master")
    print("=" * 65)
    print("  已支持聚合主流官方免费模型:")
    print("    1. 智谱 GLM:        glm-4-flash (永久免费)")
    print("    2. 阿里通义千问:     qwen-turbo / qwen2.5-coder (新客礼包)")
    print("    3. Google Gemini:   gemini-1.5-flash / 2.0-flash (15 RPM 免费层)")
    print("    4. GitHub Models:   gpt-4o / o1-mini (开发者免单)")
    print("    5. Groq:            llama-3.3-70b-versatile (极速免额度)")
    print("    6. OpenRouter:      :free 后缀聚合模型")
    print("=" * 65)
    print("  服务启动中，按 Ctrl + C 可退出服务...\n")

    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=False)

if __name__ == "__main__":
    main()
