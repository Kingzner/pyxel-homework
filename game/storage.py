"""将最高分保存为 JSON；保存失败时仍允许继续游戏。"""

import json
from pathlib import Path
import tempfile

SAVE_PATH = Path(__file__).resolve().parents[1] / "data" / "save.json"


def load():
    result = {"version": 1, "best": {"arcade": 0, "cozy": 0}, "muted": False}
    try:
        raw = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return result
        best = raw.get("best", {})
        if isinstance(best, dict):
            for mode in result["best"]:
                value = best.get(mode, 0)
                if type(value) is int and 0 <= value <= 999_999_999:
                    result["best"][mode] = value
        if type(raw.get("muted")) is bool:
            result["muted"] = raw["muted"]
    except (OSError, ValueError, UnicodeError):
        pass
    return result


def save(data):
    """先写临时文件，再原子替换，避免写一半留下损坏存档。"""
    temporary = None
    try:
        SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        current = load()
        for mode in current["best"]:
            current["best"][mode] = max(current["best"][mode], data["best"][mode])
        current["muted"] = data["muted"]
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=SAVE_PATH.parent,
            prefix="save-", suffix=".tmp", delete=False,
        ) as file:
            temporary = Path(file.name)
            json.dump(current, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temporary.replace(SAVE_PATH)
        data["best"].update(current["best"])
        return True
    except OSError:
        return False
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
