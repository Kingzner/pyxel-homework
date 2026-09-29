"""兼容旧存档；保存成绩、成就、外观和静音设置。"""

import json
from pathlib import Path
import tempfile

from game.progression import SKINS, unlock

SAVE_PATH = Path(__file__).resolve().parents[1] / "data" / "save.json"


def load():
    result = {
        "version": 2, "best": {"arcade": 0, "cozy": 0, "exam": 0},
        "muted": False, "owned": ["sena"], "selected": "sena",
        "stats": {"notes": 0, "clears": 0, "hard_clears": 0},
    }
    try:
        raw = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return result
        for field in ("best", "stats"):
            values = raw.get(field, {})
            if isinstance(values, dict):
                for key in result[field]:
                    value = values.get(key, 0)
                    if type(value) is int and 0 <= value <= 999_999_999:
                        result[field][key] = value
        if type(raw.get("muted")) is bool:
            result["muted"] = raw["muted"]
        owned = raw.get("owned", [])
        if isinstance(owned, list):
            result["owned"] = [key for key in SKINS if key == "sena" or key in owned]
        unlock(result)
        if raw.get("selected") in result["owned"]:
            result["selected"] = raw["selected"]
    except (OSError, ValueError, UnicodeError):
        pass
    return result


def save(data):
    """先写临时文件，再原子替换，避免写一半留下损坏存档。"""
    temporary = None
    try:
        SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        current = load()
        for field in ("best", "stats"):
            for key in current[field]:
                current[field][key] = max(current[field][key], data[field][key])
        current["owned"] = [key for key in SKINS if key in current["owned"] or key in data["owned"]]
        current["selected"] = data["selected"] if data["selected"] in current["owned"] else "sena"
        current["muted"] = data["muted"]
        unlock(current)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=SAVE_PATH.parent,
            prefix="save-", suffix=".tmp", delete=False,
        ) as file:
            temporary = Path(file.name)
            json.dump(current, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temporary.replace(SAVE_PATH)
        for field in ("best", "stats"):
            data[field].update(current[field])
        data["owned"] = current["owned"]
        return True
    except OSError:
        return False
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
