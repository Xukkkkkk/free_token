# 🚀 Free AI Quota Hub (大模型免费额度聚合与路由平台)

> **一站式聚合各大 AI 厂商官方免费额度，提供统一标准 OpenAI 格式接口，支持多 Key 轮换与自动故障降级。**

---

## 📌 平台核心特性

1. **官方免费额度雷达 (Free Quota Radar)**:
   - 内置智谱 GLM、阿里通义千问、Google Gemini、GitHub Models、Groq、OpenRouter 等各大主流平台的**免费政策、免单模型与申请指引**。
   - 支持**一键导入**渠道，填入 Key 即可自动完成连通性测试与延迟测速。

2. **多 Key 轮换与智能负载均衡 (Key Pool & Load Balancing)**:
   - 每个渠道支持输入多个 API Key（换行或逗号分隔），请求时自动轮询轮换，突破单个免费 Key 的频率限制（RPM/TPM）。
   - 智能健康检查与自动容灾：当某个 Key 或渠道触发 `429 (Rate Limit)` 或异常时，系统**无缝平滑切换**到下一个可用渠道，保障客户端零报错。

3. **统一 OpenAI 兼容网关 (Unified OpenAI Gateway)**:
   - 对外提供标准接口：`http://localhost:28899/v1/chat/completions` 和 `http://localhost:28899/v1/models`。
   - 一处配置，任意客户端（NextChat、Cherry Studio、LobeChat、Cursor、VS Code Continue、沉浸式翻译等）均可直接接入。

4. **现代化可视化控制台**:
   - 渠道管理、延迟测试、模型映射、令牌分发、调用日志与 Token 消耗统计一览无余。
   - 内置 Web 在线测试聊天室 (Playground)，无需安装任何第三方软件直接免配置测试模型效果。

---

## 🎁 各大模型官方免费额度获取秘籍

| 平台 | 免费额度 / 政策 | 推荐免费模型 | 获取门槛 | 官方申请地址 |
| :--- | :--- | :--- | :--- | :--- |
| **智谱 AI (GLM)** | **永久完全免费**<br>新用户再赠千万体验 Token | `glm-4-flash`<br>`glm-4-flashx` | 手机号注册即可 | [bigmodel.cn](https://bigmodel.cn/usercenter/apikeys) |
| **Google Gemini** | **15 RPM 永久免费层**<br>(每天多达 1500 次调用) | `gemini-1.5-flash`<br>`gemini-2.0-flash` | Google 账号 (免信用卡) | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| **阿里通义千问** | **新客免费赠送千万级 Token**<br>百炼活动试用包 | `qwen-turbo`<br>`qwen2.5-coder-32b` | 支付宝/阿里云实名 | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com/apiKey) |
| **GitHub Models** | **GitHub 开发者免费层**<br>(每天免费数百次请求) | `gpt-4o`<br>`gpt-4o-mini`<br>`o1-mini` | GitHub 账号生成普通 PAT | [github.com/marketplace/models](https://github.com/marketplace/models) |
| **Groq** | **全球最快推理 + 免费高并发**<br>(30 RPM, 300+ token/s) | `llama-3.3-70b-versatile`<br>`mixtral-8x7b-32768` | 邮箱注册即可 | [console.groq.com](https://console.groq.com/keys) |
| **OpenRouter** | **海量 `:free` 标签模型全免** | `deepseek/deepseek-r1:free`<br>`google/gemini-2.0-flash-exp:free` | 注册即可创建 Key | [openrouter.ai](https://openrouter.ai/keys) |
| **硅基流动** | **新客赠送 14 元体验金 + 部分模型免单** | `Qwen/Qwen2.5-7B-Instruct`<br>`deepseek-ai/DeepSeek-V3` | 手机号注册 | [cloud.siliconflow.cn](https://cloud.siliconflow.cn/account/ak) |

---

## ⚡ 快速开始

### 1. 运行环境要求
- Python 3.10+
- 安装依赖：
```bash
pip install -r requirements.txt
```

### 2. 启动服务
- **Windows 用户**：双击运行 `run.bat`
- **命令行启动**：
```bash
python run.py
```

启动成功后，浏览器访问：
👉 **`http://localhost:28899`** 即可打开可视化控制台！

---

## 🔌 客户端接入方法

平台对外暴露标准的 OpenAI 接口，默认信息如下：
- **接口地址 (Base URL)**: `http://localhost:28899/v1`
- **默认令牌 (API Key)**: `sk-free-ai-pool-master`（也可在平台后台生成专属分发令牌）

### 1. Cherry Studio (推荐桌面客户端)
1. 打开 Cherry Studio 设置 -> **模型服务**。
2. 添加自定义供应商（类型选择 **OpenAI**）：
   - API 地址：`http://localhost:28899/v1`
   - API 密钥：`sk-free-ai-pool-master`
3. 点击「管理模型」，添加你已激活的模型（如 `glm-4-flash`、`gemini-1.5-flash`、`gpt-4o`）。

### 2. NextChat (ChatGPT-Next-Web)
1. 打开 NextChat 设置 -> **接口设置**。
2. 接口地址填入：`http://localhost:28899`（或 `http://localhost:28899/v1` 取决于版本）。
3. API Key 填入：`sk-free-ai-pool-master`。
4. 自定义模型列表填入：`glm-4-flash,gemini-1.5-flash,gpt-4o`。

### 3. Cursor / VS Code (Cline / Continue)
1. 打开 Cursor 设置 -> **Models**。
2. 开启 OpenAI API Key 选项。
3. 勾选 **Override OpenAI Base URL**，填写：`http://localhost:28899/v1`。
4. API Key 填写：`sk-free-ai-pool-master`。

---

## 🏗️ 项目架构

```text
my_ali/
├── backend/
│   ├── config.py             # 配置管理（端口、路径、默认Key）
│   ├── database.py           # SQLite 数据库（渠道、令牌、调用日志）
│   ├── free_guide.py         # 官方免费额度获取指南与雷达数据
│   ├── providers/            # 厂商适配器 (GLM, Qwen, Gemini, GitHub, Groq 等)
│   ├── router.py             # 智能路由调度（多Key轮换、故障自动降级）
│   ├── gateway.py            # OpenAI 兼容网关 (/v1/chat/completions)
│   ├── api.py                # 管理后台 RESTful API
│   └── main.py               # FastAPI 主应用入口
├── frontend/
│   └── index.html            # 现代化暗色/亮色响应式 Web 前端
├── data/
│   └── free_ai_pool.db       # 本地 SQLite 数据库
├── requirements.txt          # Python 依赖
├── run.bat                   # Windows 一键启动
├── run.py                    # 启动运行脚本
└── README.md                 # 详细说明文档
```
