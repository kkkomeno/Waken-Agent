# Waken-Agent — Claude 工作指南

## 项目概述

Waken-Agent 是一个多智能体协作平台：多个专业化 AI Agent 共享工具与记忆，协作完成复杂任务。

- **仓库**: https://github.com/kkkomeno/Waken-Agent
- **本地**: `D:\项目\AgentOS\`

### 技术栈

| 层       | 技术                                | 当前状态              |
| -------- | ----------------------------------- | --------------------- |
| 移动端   | React Native (Expo)                 | ⬜ 未开始             |
| Web 后台 | React + Vite + shadcn/ui            | ⬜ 未开始             |
| API 网关 | Node.js / NestJS                    | ⬜ 未开始             |
| AI 核心  | Python / FastAPI                    | ✅ 单 Agent 运行中    |
| 数据     | PostgreSQL + pgvector, Redis, MinIO | Docker Compose 已配置 |
| LLM      | **DeepSeek** (主力) + OpenAI (备用) | ✅ DeepSeek 可用      |
| Monorepo | Turborepo + pnpm workspace          | ✅                    |

> ⚠️ **重要**: Anthropic 被墙不可用，OpenAI 直连也被墙。**DeepSeek API 是当前主力模型**，完全兼容 OpenAI 格式但工具调用使用 DSML XML 格式。

---

## 当前进度

| 阶段                    | 状态 | 一句话                           |
| ----------------------- | ---- | -------------------------------- |
| 00-项目总览             | 🟢   | 参考文档                         |
| 01-项目初始化           | ✅   | Monorepo + Docker + CI/CD 已完成 |
| 02-AI核心-单Agent运行时 | ✅   | Agent 能自主搜索+推理+生成报告   |
| 03-记忆与知识系统       | ⬜   | **← 下一步要做**                 |
| 04-08                   | ⬜   | 待推进                           |

---

## 02 阶段关键成果 (已完成)

### AI Core 服务 (`apps/ai-core/`)

启动命令:

```bash
cd D:\项目\AgentOS\apps\ai-core
source .venv/Scripts/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 端点:

- `GET /health` — 健康检查
- `POST /api/v1/run` — 运行 Agent 任务

请求示例:

```json
{ "task": "搜索今天AI新闻，用中文总结3个要点" }
```

### 已验证的能力

Agent 成功完成多步骤任务:

- 自主调用 web_search 工具 3 次
- 4 步推理循环 (Think → Act → Observe → Repeat)
- 生成 800 字结构化中文报告
- 耗时 28 秒

### 代码架构

```
apps/ai-core/app/
├── main.py           # FastAPI 入口
├── config.py         # 配置 (pydantic-settings)
├── api/routes/agent.py    # API 路由
├── core/
│   ├── llm/
│   │   ├── base.py        # LLM 抽象接口
│   │   ├── openai_llm.py  # OpenAI/DeepSeek 实现 + DSML 解析
│   │   └── router.py      # 模型路由 (任务复杂度→模型选择)
│   ├── agent/
│   │   └── loop.py        # ReAct 循环引擎
│   ├── tools/
│   │   ├── registry.py    # 工具注册中心
│   │   ├── web_search.py  # Tavily 搜索
│   │   ├── code_exec.py   # Python 代码执行
│   │   └── file_io.py     # 文件读写 (沙箱)
│   └── memory/
│       └── short_term.py  # 短期对话记忆 (滑动窗口+摘要)
├── models/schemas.py      # Pydantic 数据模型
└── services/agent_service.py  # 业务编排
```

### 关键技术决策

1. **DeepSeek API** — 中国大陆可用，OpenAI 兼容格式，新用户送 500 万 tokens
2. **DSML 解析** — DeepSeek 的工具调用用 XML 格式 (`<DSML invoke>...</DSML invoke>`)，需要正则解析转换为标准 tool_call 格式
3. **message type 字段** — DeepSeek 要求每个消息带 `type` 字段 (`"type": "tool"`, `"type": "assistant"`, `"type": "function"`)
4. **模型路由** — 简单任务用 cheap model，复杂任务自动升级 (目前都用 deepseek-chat)

---

## 下一步: 03-记忆与知识系统

详见 `03-记忆与知识系统.md`。

**核心任务**:

1. Embedding 服务 — 文本向量化
2. pgvector 集成 — 向量存储 + 语义检索
3. 文档摄取管线 — 上传 → 分块 → 向量化 → 存储
4. 记忆分层 — 工作记忆/短期记忆/长期记忆

**需要准备**:

- Docker Desktop 启动 PostgreSQL+pgvector: `docker compose -f docker/docker-compose.yml up -d`
- 选择 Embedding 方案: DeepSeek 也有 embedding API，或本地 BGE 模型

---

## 文档规范

每个项目阶段用独立 `.md` 文件追踪，位于项目根目录。结构:

```markdown
# [阶段名称]

| 属性 | 值          |
| ---- | ----------- |
| 状态 | 🟢/🟡/✅/⬜ |

## 1. 本阶段目标

## 2. 技术决策记录

## 3. 项目进度

## 4. 主要内容与代码结构

## 5. 当前阻塞 & 待解决问题

## 6. 不足与修改计划

## 7. 关键命令

## 8. 已产出物

## 9. 下一阶段计划
```

### 迭代规则

1. 新对话开始时 → 读取 `CLAUDE.md`(本文档) + `00-项目总览.md` + 当前阶段 `.md`
2. 当前阶段完成后 → 状态改 ✅，更新 `最后更新` 日期
3. 进入下一阶段 → 状态改 🟢，更新 `00-项目总览.md` 文档链表格
4. 每次修改 `.md` 后需先获得用户确认

---

## 用户偏好

- 沟通语言: 中文
- 工作方式: 文档驱动迭代，边学边做
- LLM 策略: DeepSeek 为主 (中国大陆可用)
- 项目展示: 移动端 App + Web 后台
- API Keys 存放: `D:\项目\AgentOS\.env` (已配置 DeepSeek + Tavily)
