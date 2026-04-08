import json
import re
import os
import time
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

def _call_llm(prompt, model=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            client = OpenAI(
                api_key=os.environ.get("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
                timeout=60.0
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
    try:
        pattern = r'"script"\s*:\s*"(.*?)",\s*"word_count"'
        match = re.search(pattern, cleaned, re.DOTALL)
        if match:
            sc = match.group(1)
            sc_safe = sc.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            fixed = cleaned[:match.start(1)] + sc_safe + cleaned[match.end(1):]
            return json.loads(fixed)
    except Exception:
        pass
    raise ValueError(f"JSON解析失败: {raw[:300]}")

def run_trend_agent(seed_topic):
    prompt = f"""你是内容趋势分析师，专注职场AI赛道。

方向：{seed_topic}

输出JSON：
{{
  "hot_angle": "当前最有传播潜力的切入角度",
  "pain_points": ["痛点1", "痛点2", "痛点3"],
  "content_patterns": ["爆款规律1", "规律2", "规律3"],
  "keywords": ["关键词1", "关键词2", "关键词3", "关键词4"],
  "avoid": ["说烂的角度1", "角度2"]
}}

只输出JSON。"""
    return _parse_json(_call_llm(prompt, os.environ.get("TREND_MODEL")))

def run_topic_agent(seed_topic, trend):
    prompt = f"""你是短视频选题总监，专注"职场人用AI重建工作流"赛道。

用户方向：{seed_topic}
最热角度：{trend['hot_angle']}
用户痛点：{'; '.join(trend['pain_points'])}
爆款规律：{'; '.join(trend['content_patterns'])}
避开：{'; '.join(trend['avoid'])}

输出JSON：
{{
  "topic": "选题标题（有强烈冲突感）",
  "audience": "精准受众（一句话）",
  "core_conflict": "核心矛盾",
  "angle": "差异化角度",
  "hook": "开头第一句话",
  "viral_potential": "传播潜力分析"
}}

只输出JSON。"""
    return _parse_json(_call_llm(prompt, os.environ.get("TOPIC_MODEL")))

def run_structure_agent(topic):
    prompt = f"""你是短视频结构架构师。

选题：{topic['topic']}
受众：{topic['audience']}
核心矛盾：{topic['core_conflict']}
角度：{topic['angle']}
开头钩子：{topic['hook']}

输出JSON：
{{
  "hook": "开头钩子",
  "conflict": "冲突展开（有具体场景）",
  "turning_point": "转折（有方法论）",
  "solution": "解决方案（具体步骤，每步必须包含具体AI工具名称）",
  "conclusion": "结论（一句话）",
  "cta": "结尾行动指令"
}}

只输出JSON。"""
    return _parse_json(_call_llm(prompt, os.environ.get("STRUCTURE_MODEL")))

def run_script_agent(structure, rewrite_instruction=None):
    rewrite_note = f"\n\n重写要求：{rewrite_instruction}" if rewrite_instruction else ""
    prompt = f"""你是脚本工程师，把结构骨架扩写成完整口播脚本。

开头钩子：{structure['hook']}
冲突展开：{structure['conflict']}
转折：{structure['turning_point']}
解决方案：{structure['solution']}
结论：{structure['conclusion']}
行动指令：{structure['cta']}
{rewrite_note}

写作要求：
1. 每句不超过20字，口语化
2. 有具体场景和细节，不泛泛而谈
3. 有方法论，讲清楚底层逻辑
4. 每个操作步骤必须点名具体AI工具（如Claude、ChatGPT、Kimi、豆包、Copilot等），不能只说"用AI"或"丢给AI"
5. 最后一句必须是：今天就分享到这里。乾坤未定，下期见。
6. 严禁出现：评论区扣、扣1、发给你、私信领取
script字段内换行用\\n，不用真实换行符。

只输出JSON：{{"script": "脚本正文", "word_count": 字数}}"""
    result = _parse_json(_call_llm(prompt, os.environ.get("SCRIPT_MODEL")))
    ending = "今天就分享到这里。乾坤未定，下期见。"
    if ending not in result.get("script", ""):
        result["script"] = result["script"].rstrip() + "\n\n" + ending
    return result

def run_emotion_agent(script):
    prompt = f"""你是情绪导演，把脚本改成更有人味的版本。

原稿：{script['script'][:800]}

改造：开头更抓人，情绪有起伏，去掉书面腔，关键转折有"原来如此"感。
保留所有具体AI工具名称，不能删掉或替换成泛称。
保留结尾：今天就分享到这里。乾坤未定，下期见。
严禁出现：评论区扣、扣1、发给你、私信领取。
script字段内换行用\\n，不用真实换行符。

只输出JSON：{{"script": "优化后脚本", "word_count": 字数, "emotion_changes": ["改动1", "改动2"]}}"""
    result = _parse_json(_call_llm(prompt, os.environ.get("EMOTION_MODEL")))
    ending = "今天就分享到这里。乾坤未定，下期见。"
    if ending not in result.get("script", ""):
        result["script"] = result["script"].rstrip() + "\n\n" + ending
    return result

def run_review_agent(script):
    script_text = script['script'][:600]

    editor_prompt = f"""你是内容主编，审核职场AI脚本。

脚本：{script_text}

5维度打分（每项0-2分）：
1. 具体场景感：有没有真实时间地点人物细节
2. 共鸣度：职场人看到开头会不会说"这说的就是我"
3. 可应用性：每个步骤有没有点名具体AI工具（Claude/ChatGPT/Kimi等），用户看完能直接打开工具照着做
4. 方法论深度：有没有讲清楚底层逻辑
5. 可复制性：用户看完知不知道怎么照着做

检查违规引导语：评论区扣、扣1、发给你、私信领取，有则直接不通过。

只输出JSON：{{"score": 分数, "dimension_scores": {{"场景感": 分, "共鸣度": 分, "可应用": 分, "方法论": 分, "可复制": 分}}, "weak_points": ["弱点1", "弱点2"]}}"""

    critic_prompt = f"""你是毒舌编辑，找内容硬伤。

脚本：{script_text}

哪里无聊？哪里像AI写的？哪里读者会划走？有没有只说"用AI"但没说用哪个工具？

只输出JSON：{{"boring_parts": ["无聊处1", "无聊处2"], "ai_sounding": ["AI腔1", "AI腔2"], "drop_points": ["划走节点1", "节点2"]}}"""

    editor_result = _parse_json(_call_llm(editor_prompt, os.environ.get("REVIEW_EDITOR_MODEL")))
    critic_result = _parse_json(_call_llm(critic_prompt, os.environ.get("REVIEW_CRITIC_MODEL")))

    final_prompt = f"""你是总编，综合两份审稿给出裁决。

主编：{json.dumps(editor_result, ensure_ascii=False)}
毒舌：{json.dumps(critic_result, ensure_ascii=False)}

只输出JSON：{{"passed": true或false, "total_score": 综合分, "fail_reasons": ["原因"], "rewrite_instruction": "重写指令（不通过时必填）", "review_summary": "一句话总结"}}"""

    final_result = _parse_json(_call_llm(final_prompt, os.environ.get("REVIEW_FINAL_MODEL")))
    final_result["editor_score"] = editor_result
    final_result["critic_feedback"] = critic_result
    return final_result

def run_publish_agent(script, topic):
    prompt = f"""你是多平台发布总监。

脚本摘要：{script['script'][:300]}
选题角度：{topic['angle']}

输出JSON：
{{
  "platforms": {{
    "小红书": {{"title": "标题（25字内含emoji）", "description": "简介80字", "tags": ["标签1","标签2","标签3","标签4","标签5"]}},
    "视频号": {{"title": "标题（20字内）", "description": "简介50字", "tags": ["标签1","标签2","标签3"]}},
    "Bilibili": {{"title": "标题（30字内）", "description": "简介100字", "tags": ["标签1","标签2","标签3","标签4"]}},
    "抖音": {{"title": "标题（15字内）", "description": "简介40字", "tags": ["标签1","标签2","标签3"]}}
  }}
}}

只输出JSON。"""
    return _parse_json(_call_llm(prompt, os.environ.get("PUBLISH_MODEL")))
