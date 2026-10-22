"""冒险阶段的可预告攻击编排；每种组合都保留横向逃生空间。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SpawnPlan:
    kind: str
    x: int
    warning: int
    speed_bonus: float = 0.0


def plan(wave, step, player_x, rng, occupied=()):
    """由波次和出招序号决定节奏，随机数只改变位置与小幅速度。"""
    if wave >= 6 and step % 6 == 0 and not occupied:
        # 三张依次落下的试卷；每张之间错开 0.2 秒。
        start = rng.randrange(24, 190, 24)
        return [SpawnPlan("exam", start + i * 32, 34 + i * 12, 0.1 * i)
                for i in range(3)]
    if wave >= 3 and step % 4 == 0 and not occupied:
        # 双侧夹击；中心留出约 76 像素的移动空间。
        center = max(64, min(int(player_x) + 8, 256))
        return [SpawnPlan("paper", center - 56, 36),
                SpawnPlan("paper", center + 44, 36)]
    kind = "exam" if wave >= 2 and rng.random() < 0.2 else "paper"
    width = 20 if kind == "exam" else 12
    x = rng.randint(12, 320 - width - 12)
    for _ in range(4):
        if all(abs(other - x) >= width + 8 for other in occupied):
            break
        x = rng.randint(12, 320 - width - 12)
    return [SpawnPlan(kind, x, 48 if kind == "exam" else 30,
                      0.3 if kind == "exam" else rng.uniform(-0.1, 0.15))]
