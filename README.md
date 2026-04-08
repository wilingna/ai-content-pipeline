# FLUX — 七Agent内容生产流水线

> 输入一个选题方向，7个AI自动跑完选题→结构→脚本→质检→发布全流程。

作者：[会灵那](https://github.com/wilingna)

## 快速开始
```bash
git clone https://github.com/wilingna/flux-content-pipeline
cd flux-content-pipeline
pip install openai
cp .env.template .env
python3 main.py "你的选题方向"
```

只需要一个 [OpenRouter](https://openrouter.ai) Key。

## 7个Agent

| 角色 | 模型 | 职责 |
|------|------|------|
| 趋势情报官 | GPT-5.4-mini | 分析传播潜力 |
| 选题总监 | GPT-5.4 | 输出结构化选题卡 |
| 结构架构师 | Claude Sonnet 4.6 | 拆成视频骨架 |
| 脚本工程师 | Claude Sonnet 4.6 | 扩写成口播稿 |
| 情绪导演 | GPT-5.4 | 让内容有人味 |
| AI编辑部 | Claude+Gemini+GPT | 三方质检+自动重写 |
| 发布总监 | Claude Sonnet 4.6 | 四平台物料 |

## License

MIT
