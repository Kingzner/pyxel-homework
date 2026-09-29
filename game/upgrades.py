"""能力卡：每项能力的实际效果由 main.py 中的对应逻辑执行。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Upgrade:
    key: str
    name: str
    tag: str
    color: int
    lines: tuple[str, ...]


UPGRADES = {
    "wind": Upgrade("wind", "WIND STEP", "WIND", 11,
                    ("Dash cooldown", "reduced by 25%.", "Move more often.")),
    "frost": Upgrade("frost", "FROST STEP", "ICE", 12,
                     ("Dash freezes", "nearby papers", "for 0.4 seconds.")),
    "burst": Upgrade("burst", "SHIELD NOVA", "NOVA", 13,
                     ("Broken shield", "clears papers", "within 100 px.")),
    "magnet": Upgrade("magnet", "NOTE MAGNET", "MAG", 10,
                      ("Nearby notes", "are pulled", "toward you.")),
    "recycle": Upgrade("recycle", "PAPER RECLAIM", "REC", 9,
                       ("Dash through", "papers to turn", "them into notes.")),
    "focus": Upgrade("focus", "LAST FOCUS", "FOC", 8,
                     ("At one heart:", "dash cooldown", "reduced by 40%.")),
    "answer": Upgrade("answer", "EXAM EXPERT", "ANS", 7,
                      ("Answer shots", "deal +1 damage", "and fire faster.")),
}


def draw_choices(rng, owned):
    available = [key for key in UPGRADES if key not in owned]
    return rng.sample(available, min(3, len(available)))
