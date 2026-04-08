import json
import os
import sys
from datetime import datetime
from pathlib import Path
from agents.all_agents import (
    run_trend_agent, run_topic_agent, run_structure_agent,
    run_script_agent, run_emotion_agent, run_review_agent, run_publish_agent
)
from utils.validators import validate_structure, validate_script
from utils.routers import route_after_review
from utils.json_io import save_state

MAX_REWRITE = 2

def run_pipeline():
    run_dir = Path("runs") / datetime.now().strftime("%Y-%m-%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n{'='*50}\n🚀 FLUX ULTRA 启动\n📁 {run_dir}\n{'='*50}\n")

    print("【1/7】趋势情报官 自动搜索今日趋势...")
    trend = run_trend_agent()
    save_state(run_dir / "01_trend.json", trend)
    print(f"  ✅ 找到 {len(trend.get('candidate_topics', []))} 个候选选题")
    for i, t in enumerate(trend.get('candidate_topics', []), 1):
        print(f"     {i}. {t['title']} (潜力分: {t.get('viral_score', '?')})")
    print()

    print("【2/7】选题总监 结合创作者画像选出最优选题...")
    topic = run_topic_agent(trend)
    save_state(run_dir / "02_topic.json", topic)
    print(f"  ✅ 选定：{topic.get('topic', '')}")
    print(f"  原因：{topic.get('selection_reason', '')[:50]}\n")

    print("【3/7】结构架构师 (Claude Sonnet 4.6)...")
    structure = run_structure_agent(topic)
    save_state(run_dir / "03_structure.json", structure)
    ok, errors = validate_structure(structure)
    if not ok:
        print(f"  ❌ 结构校验失败: {errors}"); sys.exit(1)
    print(f"  ✅ 结构完成\n")

    rewrite_instruction = None
    script = None
    emotion_script = None

    for attempt in range(MAX_REWRITE + 1):
        print(f"【4/7】脚本工程师 (Claude Sonnet 4.6){'（重写）' if attempt > 0 else ''}...")
        script = run_script_agent(structure, rewrite_instruction)
        save_state(run_dir / f"04_script_v{attempt+1}.json", script)
        ok, errors = validate_script(script)
        if not ok:
            print(f"  ❌ 脚本校验失败: {errors}"); sys.exit(1)
        print(f"  ✅ 脚本完成 ({script.get('word_count', '?')}字)\n")

        print(f"【5/7】情绪导演 (GPT-5.4)...")
        emotion_script = run_emotion_agent(script)
        save_state(run_dir / f"05_emotion_v{attempt+1}.json", emotion_script)
        changes = emotion_script.get('emotion_changes', [])
        print(f"  ✅ 情绪优化: {'; '.join(changes[:2])}\n")

        print(f"【6/7】AI编辑部 三方质检（第{attempt+1}次）...")
        review = run_review_agent(emotion_script)
        save_state(run_dir / f"06_review_v{attempt+1}.json", review)

        score = review.get("total_score", 0)
        action = route_after_review(review)
        print(f"  评分: {score}/10 | {review.get('review_summary', '')}")
        print(f"  → 决策: {action}")

        if action == "publish":
            print("  ✅ 质检通过\n")
            break
        elif attempt < MAX_REWRITE:
            rewrite_instruction = review.get("rewrite_instruction", "")
            print(f"  🔁 退回重写: {rewrite_instruction[:60]}...\n")
        else:
            print("  ⚠️ 达到最大重写次数，强制继续\n")

    print("【7/7】发布总监 (Claude Sonnet 4.6)...")
    publish = run_publish_agent(emotion_script, topic)
    save_state(run_dir / "07_publish.json", publish)
    print("  ✅ 四平台物料完成\n")

    print(f"{'='*50}\n🎉 FLUX ULTRA 完成！\n📁 {run_dir}\n{'='*50}\n")

    for platform, content in publish.get("platforms", {}).items():
        print(f"【{platform}】")
        print(f"  标题: {content.get('title', '')}")
        print(f"  Tags: {' '.join(content.get('tags', []))}")
        print()

if __name__ == "__main__":
    run_pipeline()
