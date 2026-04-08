PASS_THRESHOLD = 7.0

def route_after_review(review_result):
    if review_result.get("passed") is True:
        return "publish"
    if review_result.get("total_score", 0) >= PASS_THRESHOLD:
        return "publish"
    return "rewrite"
