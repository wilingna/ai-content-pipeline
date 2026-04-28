<div align="center">

# ⚡ FLUX

### A 7-Agent AI Content Pipeline
### 7 个 AI Agent 组成的内容生产流水线

**One command. From trending topic to multi-platform publish-ready content.**
**一条命令，从选题到多平台成稿。**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![OpenRouter](https://img.shields.io/badge/Powered%20by-OpenRouter-purple)](https://openrouter.ai/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/wilingna/ai-content-pipeline/pulls)
[![Stars](https://img.shields.io/github/stars/wilingna/ai-content-pipeline?style=social)](https://github.com/wilingna/ai-content-pipeline)

[English](#english) · [中文](#中文) · [Quick Start](#-quick-start) · [Architecture](#-architecture) · [Roadmap](#-roadmap)

</div>

---

## 🎯 TL;DR

**EN** — FLUX is not a prompt. It's a production pipeline where 7 specialized AI agents (powered by Claude, GPT, Gemini, and Perplexity via OpenRouter) hand work off to each other through structured JSON, with a multi-model editorial board that scores, critiques, and auto-rewrites content until it passes quality checks.

**中文** — FLUX 不是一个提示词，而是一条生产流水线。7 个专业化 AI Agent（通过 OpenRouter 调用 Claude、GPT、Gemini、Perplexity）以结构化 JSON 接力协作，多模型编辑委员会负责打分、批评，并自动重写直到内容达标。

```bash
python3 main.py
# ☕ Grab a coffee. Come back to publish-ready content for 4 platforms.
# ☕ 喝杯咖啡，回来就是 4 个平台的成品内容。
```

---

<a name="english"></a>
## 🌍 English

### The Problem

Most "AI content tools" are just ChatGPT with a system prompt. You ask, it answers, you edit, you repeat. That's not automation — that's typing with extra steps.

### The FLUX Approach

```
Define → Route → Generate → Review → Rewrite → Publish
```

FLUX treats content production like software: composable agents, isolated context, deterministic handoffs, automatic retries. Each agent does **one job well**, then passes a structured artifact to the next.

### Why It's Different

| | Single-Prompt Tools | **FLUX** |
|---|---|---|
| Execution | One chat window | Multi-node pipeline |
| Context | Mixed in one thread | Isolated per agent |
| Review | Self-check | 3-model editorial board |
| Retry | Manual copy-paste | Automatic (≤2 rounds) |
| Output | One blob of text | 4 platform-ready formats |
| Traceability | None | Full JSON logs per step |

---

<a name="中文"></a>
## 🇨🇳 中文

### 痛点

市面上大多数"AI 内容工具"本质都是套了壳的 ChatGPT：你问，它答，你改，你再问。这不是自动化，这只是换种方式打字。

### FLUX 的思路

```
定义 → 路由 → 生成 → 审核 → 重写 → 发布
```

FLUX 把内容生产当软件工程来做：模块化 Agent、隔离上下文、确定性交接、自动重试。每个 Agent 只做**一件事，做到位**，然后把结构化产物交给下一个。

### 和单提示词工具的对比

| | 单提示词工具 | **FLUX** |
|---|---|---|
| 执行方式 | 一个对话框 | 多节点流水线 |
| 上下文 | 全混在一起 | 每个 Agent 独立 |
| 审核 | 自己审自己 | 3 模型编委会 |
| 重试 | 手动复制粘贴 | 自动（最多 2 轮）|
| 输出 | 一坨文本 | 4 个平台成品 |
| 可追溯 | 无 | 每步 JSON 日志 |

---

## 🤖 The 7 Agents · 7 个 Agent

| # | Role · 角色 | Model · 模型 | Job · 职责 |
|---|---|---|---|
| 1 | **Trend Analyst** · 趋势分析 | Perplexity Sonar | Surface trending topics with live web data · 抓取实时热点 |
| 2 | **Creative Director** · 创意总监 | GPT-5.4 | Pick the highest-potential angle · 挑选最佳角度 |
| 3 | **Structure Architect** · 结构设计 | Claude Sonnet 4.6 | Build the content skeleton · 搭建内容骨架 |
| 4 | **Script Builder** · 文案编写 | Claude Sonnet 4.6 | Draft the full script · 生成完整脚本 |
| 5 | **Emotion Director** · 情绪导演 | GPT-5.4 | Add hooks, tension, and payoff · 加入钩子与情绪 |
| 6 | **Editorial Board** · 编辑委员会 | Claude + Gemini + GPT | Score, critique, decide · 打分、批评、决策 |
| 7 | **Distribution Manager** · 分发经理 | Claude Sonnet 4.6 | Reformat for each platform · 适配各平台格式 |

### 🧪 The Secret Sauce: Multi-Model Editorial Board

Single-AI review is just an echo chamber. FLUX uses **three different models** with three different jobs:

- **Claude** scores the draft on a rubric
- **Gemini** plays devil's advocate and finds weaknesses
- **GPT** makes the final ship/rewrite decision

If the score falls below threshold (default: 7/10), the pipeline **automatically rewrites** — up to 2 rounds.

> 单一模型审稿等于自我表扬。FLUX 用 **3 个不同模型** 干 3 件不同的事：Claude 打分、Gemini 挑刺、GPT 拍板。低于阈值（默认 7/10）就**自动重写**，最多 2 轮。

---

## 🏗 Architecture

```
                    ┌─────────────────────┐
                    │   user_profile.json │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │  1. Trend Analyst        (Perplexity Sonar)│
        └──────────────────────┬──────────────────────┘
                               ▼ 01_trend.json
        ┌─────────────────────────────────────────────┐
        │  2. Creative Director    (GPT-5.4)         │
        └──────────────────────┬──────────────────────┘
                               ▼ 02_topic.json
        ┌─────────────────────────────────────────────┐
        │  3. Structure Architect  (Claude Sonnet)   │
        └──────────────────────┬──────────────────────┘
                               ▼ 03_structure.json
        ┌─────────────────────────────────────────────┐
        │  4. Script Builder       (Claude Sonnet)   │
        └──────────────────────┬──────────────────────┘
                               ▼ 04_script.json
        ┌─────────────────────────────────────────────┐
        │  5. Emotion Director     (GPT-5.4)         │
        └──────────────────────┬──────────────────────┘
                               ▼ 05_emotion.json
        ┌─────────────────────────────────────────────┐
        │  6. Editorial Board                         │
        │     ├─ Claude  → score                      │
        │     ├─ Gemini  → critique                   │
        │     └─ GPT     → decide  ──┐                │
        └──────────────────────┬─────┼────────────────┘
                               │     │ score < 7
                               │     └──→ rewrite (≤2x)
                               ▼ 06_review.json
        ┌─────────────────────────────────────────────┐
        │  7. Distribution Manager (Claude Sonnet)   │
        └──────────────────────┬──────────────────────┘
                               ▼ 07_publish.json
                ┌──────────────┴──────────────┐
                ▼      ▼          ▼          ▼
            Twitter  LinkedIn  Xiaohongshu  YouTube
```

Every step writes a JSON artifact to `runs/`, so you can inspect, debug, or replay any stage.

每一步都会在 `runs/` 下生成 JSON 产物，可以随时查看、调试或重跑某个环节。

---

## 🚀 Quick Start

### 1. Clone & install · 克隆并安装

```bash
git clone https://github.com/wilingna/ai-content-pipeline
cd ai-content-pipeline
pip install -r requirements.txt   # or: pip install openai python-dotenv
```

### 2. Configure API · 配置 API

```bash
cp .env.template .env
```

Edit `.env`:

```env
OPENROUTER_API_KEY=sk-or-...

TREND_MODEL=perplexity/sonar
TOPIC_MODEL=openai/gpt-5.4
STRUCTURE_MODEL=anthropic/claude-sonnet-4.6
SCRIPT_MODEL=anthropic/claude-sonnet-4.6
EMOTION_MODEL=openai/gpt-5.4
REVIEW_EDITOR_MODEL=anthropic/claude-sonnet-4.6
REVIEW_CRITIC_MODEL=google/gemini-3.1-pro-preview
REVIEW_FINAL_MODEL=openai/gpt-5.4-mini
PUBLISH_MODEL=anthropic/claude-sonnet-4.6
```

> 💡 Get an OpenRouter key at [openrouter.ai](https://openrouter.ai/) — one key, all models.
> 💡 在 [openrouter.ai](https://openrouter.ai/) 申请一个 key 即可调用所有模型。

### 3. Customize your creator profile · 设置创作者档案

Edit `user_profile.json`:

```json
{
  "creator": "Your Name",
  "content_niche": "AI / Business / Tech",
  "target_audience": "Who you want to reach",
  "tone": "Your voice and style",
  "signature_ending": "Your closing line"
}
```

### 4. Run · 运行

```bash
python3 main.py
```

Total runtime: **~2-3 minutes** · 全程约 **2-3 分钟**

---

## 📂 Output Structure

```
runs/
└── 2026-04-29_14-32-08/
    ├── 01_trend.json        # Trending topics found
    ├── 02_topic.json        # Selected angle + reasoning
    ├── 03_structure.json    # Content outline
    ├── 04_script.json       # Full draft
    ├── 05_emotion.json      # Enhanced version
    ├── 06_review.json       # Scores + critiques + decision
    └── 07_publish.json      # 4 platform-ready outputs
```

---

## 🎯 Who This Is For · 适合谁

- **Solo creators** tired of staring at a blank page · 对着空白页发呆的独立创作者
- **AI builders** who want a real reference for multi-agent pipelines · 想看真实多 Agent 流水线代码的开发者
- **Content teams** that want consistency at scale · 追求规模化一致性的内容团队
- **Anyone** who believes AI should be a *system*, not a chatbot · 任何认同"AI 应该是系统而非聊天机器人"的人

---

## 🛣 Roadmap

- [ ] Web UI dashboard (run + monitor pipelines visually)
- [ ] Plug-in agents (BYO custom step)
- [ ] Direct publish APIs (Twitter, LinkedIn, Xiaohongshu)
- [ ] A/B testing across model configs
- [ ] Cost tracking per run
- [ ] Template library for different content types

Have an idea? [Open an issue](https://github.com/wilingna/ai-content-pipeline/issues) · 有想法？[提个 issue](https://github.com/wilingna/ai-content-pipeline/issues)

---

## 🤝 Contributing

PRs welcome. The agent system is designed to be extensible — adding a new agent means adding a file in `agents/`, a model entry in `.env`, and a step in `main.py`.

欢迎 PR。Agent 系统设计成可扩展的：加一个新 Agent 只需要在 `agents/` 加文件、在 `.env` 加模型、在 `main.py` 加一步。

---

## 💡 Core Idea · 核心理念

> **AI is not a tool. It's a system you design.**
> **AI 不是工具，是你设计出来的系统。**

---

## 📜 License

MIT — do whatever you want, just don't blame me.

---

## 👋 About the Author

Built by **会灵那 (wilingna)**

- 📍 Xiaohongshu · 小红书: `会灵那`
- 📍 Douyin · 抖音: `会灵那`
- 📍 Bilibili · B 站: `会灵那`

---

<div align="center">

### ⭐ If FLUX saved you time, give it a star.
### ⭐ 如果 FLUX 帮你省了时间，点个 star 吧。

**Better yet — fork it, run it, and replace your workflow.**
**更好的方式——fork、运行、然后替换掉你的旧工作流。**

</div>
