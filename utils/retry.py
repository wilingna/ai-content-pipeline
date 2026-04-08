import time

def call_with_retry(func, *args, max_retries=3, wait_seconds=5, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower() or "connect" in error_msg.lower():
                if attempt < max_retries - 1:
                    print(f"  ⚠️ 网络超时，{wait_seconds}秒后重试（第{attempt+1}次）...")
                    time.sleep(wait_seconds)
                    continue
            raise
    raise Exception("超过最大重试次数")
