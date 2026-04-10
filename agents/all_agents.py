import json
import re
import os
import time
from datetime import datetime
from openai import OpenAI

def _load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

_load_env()

def _load_profile():
    profile_path = os.path.join(os.path.dirname(__file__), '..', 'user_profile.json')
    with open(profile_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _call_llm(prompt, model=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            client = OpenAI(
                api_key=os.environ.get("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
                timeout=90.0
            )
            response = client.chat.completions.create(
                model=model or "anthropic/claude-sonnet-4.6",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("模型返回空内容")
            return content.strip()
        except Exception as e:
            msg = str(e).lower()
            if attempt < max_retries - 1 and ("timeout" in msg or "connect" in msg or "空内容" in msg):
                print(f"  ⚠️ 请求失败，5秒后重试（第{attempt+1}次）...")
                time.sleep(5)
            else:
                raise

def _parse_json(raw):
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1]).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    try:
        start = cleaned.index("{")
        end = cleaned.rindex("}") + 1
        return json.loads(cleaned[start:end])
    except Exception:
        pass
    raise ValueError(f"JSON解析失败: {raw[:300]}")

# ── Agent 1：趋势情报官（自动搜索，零输入）────────────────
def run_trend_agent():
    profile = _load_profile()
    today = datetime.now().strftime("%Y年%m月%d日")

    prompt = f"""今天是{today}。

你是一个内容趋势分析师，需要主动搜索当前最新的内容趋势。

创作者背景：
- 赛道：{profile['content_niche']}
- 受众：{profile['target_audience']}
- 已做过的选题：{', '.join(profile['past_topics']) if profile['past_topics'] else '暂无记录'}

请搜索并分析以下内容：
1. 当前"AI+职场效率or超级个体or一人公司orAI原生组织or最新AI趋势动态or最新AI工具skill"赛道在各平台的热门话题和讨论趋势
2. 最近7天涨势明显的内容类型和表达方式
3. 目标受众（职场人）最近在焦虑什么、讨论什么、最新AI趋势动态对企业组织及打工人的影响以及企业和普通人应该如何应对的建议
4. 哪些选题角度还没有被大量创作者覆盖（蓝海机会）

基于搜索结果，输出情报卡JSON：
{{
  "search_date": "{today}",
  "hot_angle": "当前最有传播潜力的核心角度（一句话）",
  "trending_topics": ["话题1", "话题2", "话题3"],
  "audience_anxiety": ["用户焦虑点1", "焦虑点2", "焦虑点3"],
  "blue_ocean": ["蓝海角度1", "蓝海角度2"],
  "content_patterns": ["爆款规律1", "规律2"],
  "avoid": ["已被说烂的角度1", "角度2"],
  "candidate_topics": [
    {{
      "title": "候选选题1（有冲突感）",
      "reason": "为什么这个选题现在值得做",
      "viral_score": 8
    }},
    {{
      "title": "候选选题2",
      "reason": "理由",
      "viral_score": 7
    }},
    {{
      "title": "候选选题3",
      "reason": "理由",
      "viral_score": 9
    }}
  ]
}}

只输出JSON。"""

    model = os.environ.get("TREND_MODEL", "perplexity/llama-3.1-sonar-large-128k-online")
    raw = _call_llm(prompt, model)
    return _parse_json(raw)

# ── Agent 2：选题总监（结合用户画像选最优选题）──────────────
def run_topic_agent(trend):
    profile = _load_profile()

    prompt = f"""你是选题总监，负责从候选选题中选出最适合这位创作者的一个，并深化优化。

创作者画像：
- 名称：{profile['creator']}
- 内容定位：{profile['content_niche']}
- 受众：{profile['target_audience']}
- 内容风格：{profile['tone']}
- 语言特点：{'; '.join(profile['language_style'])}

当前趋势情报：
- 最热角度：{trend['hot_angle']}
- 用户焦虑：{'; '.join(trend['audience_anxiety'])}
- 候选选题：
{json.dumps(trend['candidate_topics'], ensure_ascii=False, indent=2)}

任务：
1. 从3个候选中选出最适合这位创作者的一个
2. 结合她的风格和受众深化优化这个选题
3. 输出完整选题卡

输出JSON：
{{
  "selected_from": "选择了哪个候选（原标题）",
  "selection_reason": "为什么选这个（结合创作者特点）",
  "topic": "优化后的选题标题（有强烈冲突感，符合创作者风格）",
  "audience": "精准受众描述",
  "core_conflict": "核心矛盾（大多数人在做什么错误的事）",
  "angle": "差异化角度（为什么这个视角适合这位创作者）",
  "hook": "开头第一句话（让目标用户秒感共鸣）",
  "viral_potential": "传播潜力分析"
}}

只输出JSON。"""

    raw = _call_llm(prompt, os.environ.get("TOPIC_MODEL", "openai/gpt-5.4"))
    return _parse_json(raw)

# ── Agent 3：结构架构师────────────────────────────────────
def run_structure_agent(topic):
    profile = _load_profile()

    prompt = f"""你是短视频结构架构师。

创作者风格：{profile['tone']}
语言特点：{'; '.join(profile['language_style'])}

选题：{topic['topic']}
受众：{topic['audience']}
核心矛盾：{topic['core_conflict']}
角度：{topic['angle']}
开头钩子：{topic['hook']}

输出视频骨架JSON：
{{
  "hook": "开头钩子（直接用上面给的，可微调使其更口语化）",
  "conflict": "冲突展开（有具体职场场景，有时间地点细节）",
  "turning_point": "转折（引出正确认知，有方法论底层逻辑）",
  "solution": "解决方案（具体步骤，每步必须点名AI工具：Claude/ChatGPT/Kimi/豆包等）",
  "conclusion": "结论（一句话核心洞察，可复制可拿来即用）",
  "cta": "结尾行动指令（具体可执行，不能是互动引导）"
}}

只输出JSON。"""

    raw = _call_llm(prompt, os.environ.get("STRUCTURE_MODEL", "anthropic/claude-sonnet-4.6"))
    return _parse_json(raw)

# ── Agent 4：脚本工程师────────────────────────────────────
def run_script_agent(structure, rewrite_instruction=None):
    profile = _load_profile()
    rewrite_note = f"\n\n重写要求：{rewrite_instruction}" if rewrite_instruction else ""

    prompt = f"""你是脚本工程师，把结构骨架扩写成完整口播脚本。

创作者：{profile['creator']}
语言风格要求：{'; '.join(profile['language_style'])}
风格基调：{profile['tone']}

结构骨架：
开头钩子：{structure['hook']}
冲突展开：{structure['conflict']}
转折：{structure['turning_point']}
解决方案：{structure['solution']}
结论：{structure['conclusion']}
行动指令：{structure['cta']}
{rewrite_note}

写作要求：
1. 严格符合创作者的语言风格，像她本人在说话
2. 每句不超过20字，口语化
3. 有具体场景和细节，不泛泛而谈
4. 【工具具体化硬要求，违反视为不合格】凡涉及工具操作的地方，必须同时满足三点：
   a. 说出真实产品名称（如Claude、Kimi、飞书妙记、Notion、豆包等），
      严禁用"某AI工具""相关工具""AI""智能工具"等模糊表达代替；
   b. 用一句口语化的话说明为什么用这个工具——它最擅长什么、有什么独特优势，
      格式参考："用XX，因为它擅长____"或"选XX是因为它____"，
      例如："用飞书妙记，因为它能自动识别谁说了什么，不用你手动区分发言人"，
      例如："用Claude，因为它中文长文理解特别强，几千字的内容它能精准抓重点"；
   c. 操作步骤具体到用户听完能立刻照做，
      说"打开XX，新建对话，把文字稿全选复制进去，粘贴这段指令，点发送"，
      严禁说"把内容扔给AI处理""让AI来完成""交给AI就好了"之类无法操作的表达。
5. 有方法论，讲清楚底层逻辑
6. 最后一句必须是：{profile['signature_ending']}
7. 严禁出现：{', '.join(profile['banned_words'])}
script字段内换行用\\n，不用真实换行符。

只输出JSON：{{"script": "完整口播稿", "word_count": 字数}}"""

    result = _parse_json(_call_llm(prompt, os.environ.get("SCRIPT_MODEL", "anthropic/claude-sonnet-4.6")))
    if profile['signature_ending'] not in result.get("script", ""):
        result["script"] = result["script"].rstrip() + "\n\n" + profile['signature_ending']
    return result

# ── Agent 5：情绪导演────────────────────────────────────
def run_emotion_agent(script):
    profile = _load_profile()

    prompt = f"""你是情绪导演，把脚本改成更有人味的版本。

创作者风格：{profile['tone']}

原稿：{script['script'][:1000]}

改造要求：
1. 开头3句必须让人停下来，有强烈的代入感
2. 加入真实情绪起伏：焦虑→顿悟→轻松
3. 关键转折要有"原来如此"的释然感
4. 去掉所有书面腔，说人话
5. 保留所有具体AI工具名称及其"为什么用它"的说明，不能删掉或模糊化
6. 保留所有具体操作步骤，不能缩写成"扔给AI处理"之类的表达
7. 保留结尾：{profile['signature_ending']}
8. 严禁出现：{', '.join(profile['banned_words'])}
script字段内换行用\\n，不用真实换行符。

只输出JSON：{{"script": "优化后脚本", "word_count": 字数, "emotion_changes": ["改动1", "改动2"]}}"""

    result = _parse_json(_call_llm(prompt, os.environ.get("EMOTION_MODEL", "openai/gpt-5.4")))
    if profile['signature_ending'] not in result.get("script", ""):
        result["script"] = result["script"].rstrip() + "\n\n" + profile['signature_ending']
    return result

# ── Agent 6：三方质检────────────────────────────────────
def run_review_agent(script):
    profile = _load_profile()
    script_text = script['script'][:600]

    editor_prompt = f"""你是内容主编，审核职场AI赛道脚本。

创作者风格要求：{profile['tone']}

脚本：{script_text}

5维度打分（每项0-2分）：
1. 具体场景感：有没有真实职场细节
2. 共鸣度：目标受众（职场人）会不会说"这说的就是我"
3. 可应用性（最严格审查）：
   - 2分：每个工具都有真实产品名 + 一句话说明为什么用它/它擅长什么 + 具体到用户听完能立刻上手的操作步骤，三项全满足
   - 1分：有工具名，但缺少"为什么用它"的说明，或操作步骤仍停留在"扔给AI""让AI来处理"等模糊表达
   - 0分：出现"某AI工具""相关工具""智能工具""交给AI""扔给AI处理"等任何模糊表达，直接0分，不论其他内容多好
4. 方法论深度：有没有讲清楚底层逻辑
5. 风格契合度：是否符合创作者"真实在职非技术"的风格

检查违规词：{', '.join(profile['banned_words'])}，有则直接不通过。

只输出JSON：{{"score": 分数, "dimension_scores": {{"场景感": 分, "共鸣度": 分, "可应用": 分, "方法论": 分, "风格": 分}}, "weak_points": ["弱点1", "弱点2"], "vague_tool_expressions": ["脚本中发现的模糊工具表达（如有）"]}}"""

    critic_prompt = f"""你是毒舌编辑，只找硬伤。

脚本：{script_text}

三个问题：哪里无聊？哪里像AI写的？哪里用户会划走？

额外检查：脚本里有没有"某AI""扔给AI""让AI来处理""交给AI"之类让用户看完还是不知道该用什么工具、怎么操作的废话？如有，列出来。

只输出JSON：{{"boring_parts": ["1", "2"], "ai_sounding": ["1", "2"], "drop_points": ["1", "2"], "vague_tool_issues": ["发现的模糊工具问题（如有）"]}}"""

    editor_result = _parse_json(_call_llm(editor_prompt, os.environ.get("REVIEW_EDITOR_MODEL", "anthropic/claude-sonnet-4.6")))
    critic_result = _parse_json(_call_llm(critic_prompt, os.environ.get("REVIEW_CRITIC_MODEL", "google/gemini-3.1-pro-preview")))

    final_prompt = f"""你是总编，综合两份审稿给出最终裁决。

主编打分：{json.dumps(editor_result, ensure_ascii=False)}
毒舌反馈：{json.dumps(critic_result, ensure_ascii=False)}

裁决规则：
1. 正常综合两份审稿给出总分和通过/不通过判断
2. 【硬性退回规则，优先级最高】满足以下任一条件，无论总分多高，must输出 passed: false：
   - 主编"可应用"维度得分为0
   - editor_result 的 vague_tool_expressions 字段非空（发现了模糊工具表达）
   - critic_result 的 vague_tool_issues 字段非空（发现了模糊工具问题）
   退回时，rewrite_instruction必须明确指出：哪些位置存在模糊工具表达、应改成什么（真实工具名+为什么用它+具体操作步骤）
3. 通过标准：总分≥7.0 且 可应用维度≥1.5 且 无模糊工具表达

只输出JSON：{{"passed": true或false, "total_score": 分, "fail_reasons": ["原因"], "rewrite_instruction": "重写指令（不通过时必填，直接告诉脚本工程师改哪里、怎么改）", "review_summary": "一句话总结"}}"""

    final_result = _parse_json(_call_llm(final_prompt, os.environ.get("REVIEW_FINAL_MODEL", "openai/gpt-5.4-mini")))
    final_result["editor_score"] = editor_result
    final_result["critic_feedback"] = critic_result
    return final_result

# ── Agent 7：发布总监────────────────────────────────────
def run_publish_agent(script, topic):
    profile = _load_profile()

    prompt = f"""你是多平台发布总监，精通各平台语言差异。

脚本摘要：{script['script'][:300]}
选题角度：{topic['angle']}
创作者：{profile['creator']}

为4个平台生成差异化物料，JSON格式：
{{
  "platforms": {{
    "小红书": {{"title": "标题（25字内含emoji，强调个人故事）", "description": "简介80字", "tags": ["标签1","标签2","标签3","标签4","标签5"]}},
    "视频号": {{"title": "标题（20字内，职场感强）", "description": "简介50字", "tags": ["标签1","标签2","标签3"]}},
    "Bilibili": {{"title": "标题（30字内，偏干货感）", "description": "简介100字", "tags": ["标签1","标签2","标签3","标签4"]}},
    "抖音": {{"title": "标题（15字内，节奏强）", "description": "简介40字", "tags": ["标签1","标签2","标签3"]}}
  }}
}}

只输出JSON。"""

    return _parse_json(_call_llm(prompt, os.environ.get("PUBLISH_MODEL", "anthropic/claude-sonnet-4.6")))
