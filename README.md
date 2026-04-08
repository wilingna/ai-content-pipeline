# FLUX — 七Agent内容生产流水线

> 零输入，全自动。AI自己搜趋势、自己选题、自己写稿、自己过质检，输出四平台发布物料。

作者：[会灵那](https://github.com/wilingna) · 小红书/抖音/B站搜「会灵那」

---

## 这套系统做什么
```bash
python3 main.py
```

一行命令，不需要输入任何内容。

7个AI自动完成：搜趋势 → 选题 → 拆结构 → 写脚本 → 情绪优化 → 三方质检 → 四平台物料

---

## 7个Agent分工

| 编号 | 角色 | 模型 | 职责 |
|------|------|------|------|
| ① | 趋势情报官 | Perplexity Sonar | 实时搜索今日趋势，给出3个候选选题 |
| ② | 选题总监 | GPT-5.4 | 结合创作者画像，选出最优选题 |
| ③ | 结构架构师 | Claude Sonnet 4.6 | 把选题拆成视频骨架 |
| ④ | 脚本工程师 | Claude Sonnet 4.6 | 扩写成完整口播稿 |
| ⑤ | 情绪导演 | GPT-5.4 | 让内容从"能读"变成"想看" |
| ⑥ | AI编辑部 | Claude+Gemini+GPT | 三方质检，自动打回重写 |
| ⑦ | 发布总监 | Claude Sonnet 4.6 | 生成四平台差异化物料 |

③④ 是两次完全独立的API调用，上下文隔离——这是真Agent，不是伪Agent。

---

## 快速开始

### 安装
```bash
git clone https://github.com/wilingna/ai-content-pipeline
cd ai-content-pipeline
pip install openai
cp .env.template .env
# 填入你的 OPENROUTER_API_KEY
```

### 配置你的创作者画像

编辑 `user_profile.json`，填入你自己的信息：
```json
{
  "creator": "你的名字",
  "content_niche": "你的内容赛道",
  "target_audience": "你的目标受众",
  "tone": "你的内容风格",
  "signature_ending": "你的固定结尾语",
  "past_topics": [],
  "language_style": ["你的语言习惯"],
  "banned_words": ["不能出现的词"]
}
```

### 运行
```bash
python3 main.py
```

不需要输入任何参数，AI自动完成全流程。

---

## 模型配置

在 `.env` 里按需替换任意节点的模型：
