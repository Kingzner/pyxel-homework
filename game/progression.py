"""本机成就和外观解锁；演示模式可预览所有外观。"""

SKINS = {
    "sena": {"name": "SENA", "hint": "YOUR ORIGINAL CAMPUS AVATAR"},
    "mint": {"name": "MINT", "hint": "COLLECT 25 NOTES ACROSS RUNS"},
    "luna": {"name": "LUNA", "hint": "CLEAR AN ADVENTURE OR EXAM"},
    "crimson": {"name": "CRIMSON", "hint": "CLEAR THE HARD EXAM BOSS"},
}


def unlock(data):
    stats = data["stats"]
    earned = ["sena"]
    if stats["notes"] >= 25:
        earned.append("mint")
    if stats["clears"] >= 1:
        earned.append("luna")
    if stats["hard_clears"] >= 1:
        earned.append("crimson")
    new = [skin for skin in earned if skin not in data["owned"]]
    data["owned"] = [skin for skin in SKINS if skin in data["owned"] or skin in earned]
    return new
