import json
import re

def parse_json_safe(raw):
    cleaned = raw.strip()
    
    # 去掉markdown代码块
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1]).strip()
    
    # 第一次尝试：直接解析
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # 第二次尝试：找到第一个{到最后一个}
    try:
        start = cleaned.index("{")
        end = cleaned.rindex("}") + 1
        return json.loads(cleaned[start:end])
    except (ValueError, json.JSONDecodeError):
        pass
    
    # 第三次尝试：把script字段内容转义处理
    try:
        # 用正则找到script字段，把里面的换行和引号转义
        pattern = r'"script"\s*:\s*"(.*?)"(?=\s*,\s*"word_count")'
        match = re.search(pattern, cleaned, re.DOTALL)
        if match:
            script_content = match.group(1)
            safe_content = script_content.replace('\n', '\\n').replace('"', '\\"')
            fixed = cleaned[:match.start(1)] + safe_content + cleaned[match.end(1):]
            return json.loads(fixed)
    except Exception:
        pass
    
    raise ValueError(f"无法解析JSON，原始内容前200字: {raw[:200]}")
