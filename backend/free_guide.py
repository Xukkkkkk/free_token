"""
Free AI Quota Radar & Step-by-Step Acquisition Guide
各大主流大模型官方免费额度获取指南与快速预置配置
"""

FREE_PROVIDERS_GUIDE = [
    {
        "id": "free_reverse",
        "name": "免Key公共通道 (无需注册/开箱即用)",
        "badge": "开箱即用 · 彻底免登录",
        "badge_color": "emerald",
        "description": "系统已预置的免鉴权公共通道！无需注册账号、无需配置任何API Key，平台启动即可直接免费调用 GPT-4o、Qwen-Coder、Mistral 等顶级模型！",
        "free_policy": "完全免鉴权、零门槛调用，自带智能防限流与高可用路由。",
        "free_models": ["gpt-4o", "gpt-4o-mini", "gpt-4o-free", "gpt-4o-mini-free", "qwen-coder-free", "mistral-free"],
        "direct_url": "https://text.pollinations.ai",
        "steps": [
            "本通道已在后台默认激活并就绪，无需进行任何手动操作！",
            "在「在线测试 (Playground)」中直接选择 `gpt-4o` 或 `gpt-4o-mini` 即可直接聊天",
            "在任何第三方客户端（NextChat、Cherry Studio、Cursor）中填入平台地址和默认令牌即可随时免费调用！"
        ],
        "default_config": {
            "name": "免Key公共免费通道",
            "provider_type": "free_reverse",
            "base_url": "https://text.pollinations.ai/openai",
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4o-free", "gpt-4o-mini-free", "qwen-coder-free", "mistral-free"]
        }
    },
    {
        "id": "glm",
        "name": "智谱 AI (GLM)",
        "badge": "永久免费",
        "badge_color": "green",
        "description": "智谱官方对开发者永久免费开放 glm-4-flash 模型，无需消耗任何额度，响应极速，中文能力强劲。",
        "free_policy": "glm-4-flash / glm-4-flashx 永久免费！新注册还额外赠送 2500 万 Token 体验金。",
        "free_models": ["glm-4-flash", "glm-4-flashx", "glm-4-plus", "glm-4-air"],
        "direct_url": "https://bigmodel.cn/usercenter/apikeys",
        "steps": [
            "访问智谱大模型开放平台：https://bigmodel.cn",
            "使用手机号快速注册登录（新用户通常会获赠免费体验 Token 包）",
            "点击右上角「控制台」 -> 「API Key」",
            "点击「创建 API Key」，复制生成的 Key（形如：`xxxx.yyyy`）",
            "回到本平台，点击「一键填入」或新建渠道，粘贴该 Key 即可永久免费调用 `glm-4-flash`！"
        ],
        "default_config": {
            "name": "智谱 AI (永久免费 glm-4-flash)",
            "provider_type": "glm",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "models": ["glm-4-flash", "glm-4-flashx"]
        }
    },
    {
        "id": "gemini",
        "name": "Google Gemini",
        "badge": "每天 1500 次免费",
        "badge_color": "blue",
        "description": "Google AI Studio 官方免费层，无需绑定信用卡，直接获取 API Key，免费调用 Gemini 1.5 Flash / 2.0 Flash。",
        "free_policy": "免费层支持 15 RPM（每分钟 15 次，每日高达 1500 次），多模态能力极强，上下文支持上百万 Token。",
        "free_models": ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"],
        "direct_url": "https://aistudio.google.com/app/apikey",
        "steps": [
            "访问 Google AI Studio 官网：https://aistudio.google.com/app/apikey",
            "使用 Google 账号登录（需海外网络环境）",
            "点击「Create API key」，选择项目后立即生成 Key（形如：`AIzaSy...`）",
            "Google 官方已全面原生兼容 OpenAI 格式（端点为 `/v1beta/openai`）",
            "将 Key 填入本平台，即可免费畅享 Gemini 2.0 Flash 高速大模型！"
        ],
        "default_config": {
            "name": "Google Gemini (AI Studio 免费层)",
            "provider_type": "gemini",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
            "models": ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
        }
    },
    {
        "id": "qwen",
        "name": "阿里通义千问 (DashScope / 百炼)",
        "badge": "新客送千万Token",
        "badge_color": "purple",
        "description": "阿里云百炼大模型服务平台，新用户实名认证后赠送数千万免费 Token 体验额度，涵盖 Qwen 全系列及开源代码模型。",
        "free_policy": "新用户可领取 qwen-turbo、qwen-plus 等模型各千万级 Token 免费额度，有效期一般为 180 天。",
        "free_models": ["qwen-turbo", "qwen-plus", "qwen2.5-coder-32b-instruct", "qwen-long"],
        "direct_url": "https://dashscope.console.aliyun.com/apiKey",
        "steps": [
            "访问阿里云百炼控制台：https://dashscope.console.aliyun.com",
            "使用阿里云/支付宝账号登录，在活动中心领取「百炼新用户免费试用额度包」",
            "进入左侧菜单「API-KEY 管理」，点击「创建新的 API-KEY」",
            "复制生成的 `sk-...` Key",
            "填入本平台对应渠道，开启千问模型的高速调用！"
        ],
        "default_config": {
            "name": "阿里通义千问 (DashScope 免费体验包)",
            "provider_type": "qwen",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "models": ["qwen-turbo", "qwen-plus", "qwen2.5-coder-32b-instruct", "qwen-long"]
        }
    },
    {
        "id": "github",
        "name": "GitHub Models",
        "badge": "开发者免单",
        "badge_color": "emerald",
        "description": "微软与 GitHub 官方推出的开发者大模型 Playground 与 API，面向全体 GitHub 账号提供免费试用 GPT-4o、o1-mini、Claude 等前沿模型。",
        "free_policy": "GitHub 账号每天提供免费调用配额（高阶模型约 50 次/天，普通模型约 150 次/天），无需绑定信用卡。",
        "free_models": ["gpt-4o", "gpt-4o-mini", "o1-mini", "DeepSeek-R1"],
        "direct_url": "https://github.com/marketplace/models",
        "steps": [
            "访问 GitHub Models 页面：https://github.com/marketplace/models",
            "登录 GitHub 账号，任意选择一个模型（如 GPT-4o）",
            "点击页面上的「Get API Key」或者前往 GitHub Settings -> Developer settings -> Personal access tokens (Tokens classic)",
            "生成一个普通的 PAT（甚至无需勾选任何特殊权限，仅作为身份标识）",
            "将生成的 GitHub PAT（形如 `ghp_...`）填入本平台的 GitHub Models 渠道即可免费调用 GPT-4o！"
        ],
        "default_config": {
            "name": "GitHub Models (官方免费 GPT-4o)",
            "provider_type": "github",
            "base_url": "https://models.inference.ai.azure.com",
            "models": ["gpt-4o", "gpt-4o-mini", "o1-mini", "DeepSeek-R1"]
        }
    },
    {
        "id": "groq",
        "name": "Groq",
        "badge": "极速 LPU 免费",
        "badge_color": "amber",
        "description": "全球最快推理芯片 LPU 提供商，提供超高并发且免费的 API Key，可调用最新开源顶级模型 Llama 3.3 70B。",
        "free_policy": "永久免费级别，每分钟高达 30 次请求，输出速度达 300~500 tokens/s，近乎秒回。",
        "free_models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
        "direct_url": "https://console.groq.com/keys",
        "steps": [
            "访问 Groq 控制台：https://console.groq.com",
            "使用 Google 或 GitHub 账号免密登录",
            "进入左侧「API Keys」，点击「Create API Key」",
            "复制 Key（形如 `gsk_...`）",
            "填入本平台，体验全球最快推理大模型！"
        ],
        "default_config": {
            "name": "Groq (极速免费推理池)",
            "provider_type": "groq",
            "base_url": "https://api.groq.com/openai/v1",
            "models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"]
        }
    },
    {
        "id": "siliconflow",
        "name": "硅基流动 (SiliconFlow)",
        "badge": "新户送14元+部分永久免费",
        "badge_color": "indigo",
        "description": "国内顶级大模型推理加速平台，提供包括 Qwen2.5、DeepSeek-V3/R1 等模型的免费调用层及新用户赠费。",
        "free_policy": "部分小尺寸及开源模型（如 Qwen2.5-7B、DeepSeek 蒸馏版等）完全免费；新用户实名赠送 14~20 元体验金（相当于几千万 Token）。",
        "free_models": ["Qwen/Qwen2.5-7B-Instruct", "deepseek-ai/DeepSeek-V3", "deepseek-ai/DeepSeek-R1"],
        "direct_url": "https://cloud.siliconflow.cn/account/ak",
        "steps": [
            "访问硅基流动控制台：https://cloud.siliconflow.cn",
            "手机号或微信注册登录，在账户中心可查看赠送余额与免费模型列表",
            "左侧点击「API 密钥」，点击「新建 API 密钥」",
            "复制生成的 `sk-...` Key",
            "在当前平台选择通用 OpenAI 格式，或选择硅基流动预置模板填入！"
        ],
        "default_config": {
            "name": "硅基流动 (免费/赠送额度通道)",
            "provider_type": "generic",
            "base_url": "https://api.siliconflow.cn/v1",
            "models": ["Qwen/Qwen2.5-7B-Instruct", "deepseek-ai/DeepSeek-V3", "deepseek-ai/DeepSeek-R1"]
        }
    },
    {
        "id": "openrouter",
        "name": "OpenRouter",
        "badge": "免费模型聚合",
        "badge_color": "cyan",
        "description": "全球最大的模型聚合路由平台，专门设有多款带有 :free 标签的永久免费模型，单 Key 畅享各大主流开源与闭源前沿架构。",
        "free_policy": "所有带 `:free` 标识的模型完全免费调用，无需账户充值余额。",
        "free_models": [
            "google/gemini-2.0-flash-exp:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "deepseek/deepseek-r1:free"
        ],
        "direct_url": "https://openrouter.ai/keys",
        "steps": [
            "访问 OpenRouter 官网：https://openrouter.ai/keys",
            "使用 Google / GitHub 账号登录",
            "点击「Create Key」，生成并复制你的 Key（形如 `sk-or-v1-...`）",
            "将 Key 填入本平台，即可免费畅享带 :free 标识的顶级模型！"
        ],
        "default_config": {
            "name": "OpenRouter (免费模型池)",
            "provider_type": "openrouter",
            "base_url": "https://openrouter.ai/api/v1",
            "models": [
                "google/gemini-2.0-flash-exp:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "deepseek/deepseek-r1:free"
            ]
        }
    }
]

def get_free_guides():
    return FREE_PROVIDERS_GUIDE
