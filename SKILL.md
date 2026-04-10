---
name: flux-content-pipeline
description: 一人公司AI内容生产流水线。当用户想要搭建多Agent内容生产系统、自动化内容创作工作流、或者把选题到发布的全流程自动化时触发此Skill。适用场景：内容创作者想批量生产多平台内容、职场人想把内容创作自动化、想了解真实多Agent编排架构的开发者。包含7个真实Agent（趋势情报→选题→结构→脚本→情绪优化→三方质检→多平台发布），每个节点独立API调用，JSON状态流转，自动重写回退机制。
---
# FLUX — 七Agent内容生产流水线
**作者：会灵那（wilingna）**
## 这套系统做什么
输入一个选题方向 → 自动跑完7个Agent → 输出四平台发布物料
全程不需要人工介入，质检不通过自动退回重写，最多重写2次。
## 7个Agent分工
| 编号 | 角色 | 模型 | 职责 |
|------|------|------|------|
| 1号 | 趋势情报官 | Perplexity Sonar | 分析传播潜力，找热点角度和用户痛点 |
| 2号 | 选题总监 | GPT-5.4 | 基于情报输出结构化选题卡 |
| 3号 | 结构架构师 | Claude Sonnet 4.6 | 把选题拆成视频骨架 |
| 4号 | 脚本工程师 | Claude Sonnet 4.6 | 把骨架扩写成完整口播稿 |
| 5号 | 情绪导演 | GPT-5.4 | 把能读的稿改成想看的稿 |
| 6号 | AI编辑部 | Claude+Gemini+GPT三方 | 三方质检，打分，自动退回重写 |
| 7号 | 发布总监 | Claude Sonnet 4.6 | 改写成四平台差异化物料 |
## 快速开始
### 安装
```bash
git clone https://github.com/wilingna/flux-content-pipeline
cd flux-content-pipeline
pip install openai
cp .env.template .env
# 编辑 .env，填入 OPENROUTER_API_KEY
```
### 运行
```bash
python3 main.py "你的选题方向"
```
## 模型配置
在 `.env` 里按需替换任意Agent的模型，不改代码：OPENROUTER_API_KEY=sk-or-...
TREND_MODEL=perplexity/sonar
TOPIC_MODEL=openai/gpt-5.4
STRUCTURE_MODEL=anthropic/claude-sonnet-4.6
SCRIPT_MODEL=anthropic/claude-sonnet-4.6
EMOTION_MODEL=openai/gpt-5.4
REVIEW_EDITOR_MODEL=anthropic/claude-sonnet-4.6
REVIEW_CRITIC_MODEL=google/gemini-3.1-pro-preview
REVIEW_FINAL_MODEL=openai/gpt-5.4-mini
PUBLISH_MODEL=anthropic/claude-sonnet-4.6
## 真Agent vs 伪Agent
| | 伪Agent | 真Agent（FLUX） |
|---|---|---|
| 运行方式 | 同一对话窗口切换角色 | 每个节点独立API调用 |
| 上下文 | 全部混在一起 | JSON字段传递，零干扰 |
| 出错处理 | 靠人工重新提问 | 自动打回重写，最多2次 |
| 可追溯 | 对话记录难复盘 | 每步存JSON，完整追溯 |
| 批量运行 | 做不到 | 循环调用，睡觉它在跑 |
## 调节质检严格度
在 `utils/routers.py` 修改通过分数线：
```python
PASS_THRESHOLD = 7.0  # 可改成6.0（宽松）或8.0（严格）
```
## 关于作者
会灵那（wilingna）— HR出身的AI内容创作者
- 小红书 / 抖音 / B站：搜索「会灵那」
- GitHub：github.com/wilingna
