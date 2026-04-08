def validate_topic(data):
    required = ["topic", "audience", "angle", "evidence", "risk_notes"]
    errors = [f"缺少字段: {k}" for k in required if not data.get(k)]
    return len(errors) == 0, errors

def validate_structure(data):
    required = ["hook", "conflict", "turning_point", "conclusion", "cta"]
    errors = [f"缺少字段: {k}" for k in required if not data.get(k)]
    return len(errors) == 0, errors

def validate_script(data):
    errors = []
    script = data.get("script", "")
    if not script:
        errors.append("缺少脚本正文")
    elif len(script) < 200:
        errors.append(f"脚本过短({len(script)}字)")
    ending = "今天就分享到这里。乾坤未定，下期见。"
    if ending not in script:
        errors.append("缺少固定结尾语")
    banned = ["评论区扣", "扣1", "扣个1", "发给你", "私信我领", "评论领取"]
    for word in banned:
        if word in script:
            errors.append(f"包含违规引导语: {word}")
    return len(errors) == 0, errors

def validate_review(data):
    errors = []
    if "passed" not in data:
        errors.append("缺少passed字段")
    if "total_score" not in data:
        errors.append("缺少total_score字段")
    if not data.get("passed") and not data.get("rewrite_instruction"):
        errors.append("未通过时必须有rewrite_instruction")
    return len(errors) == 0, errors
