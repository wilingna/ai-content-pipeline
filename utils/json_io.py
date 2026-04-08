import json
from pathlib import Path

def save_state(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_state(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
