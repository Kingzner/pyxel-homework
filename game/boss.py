"""期末院长：真实生命值、按血量切换的三阶段和有预告的攻击。"""

from dataclasses import dataclass
import math

from game.config import FPS


@dataclass(frozen=True)
class Attack:
    x: float
    speed: float
    warning: int
    width: int = 20
    height: int = 18


class Boss:
    PHASE_NAMES = ("ROLL CALL", "FIND THE GAP", "FINAL SUBMISSION")

    def __init__(self, mode):
        self.mode = mode
        self.hard = mode == "exam"
        self.demo = mode == "demo"
        self.max_hp = 210 if self.hard else 90 if self.demo else 120
        self.hp = self.max_hp
        self.frames = 0
        self.phase = 1
        self.next_attack = 60
        self.attack_index = 0
        self.max_seconds = 70 if self.hard else 45 if self.demo else 65
        self.flash = 0
        self.gap = None

    @property
    def x(self):
        return 160 + math.sin(self.frames / (70 if self.hard else 110)) * 65

    @property
    def seconds_left(self):
        return max(0, self.max_seconds - self.frames // FPS)

    @property
    def name(self):
        return self.PHASE_NAMES[self.phase - 1]

    def damage(self, amount):
        self.hp = max(0, self.hp - amount)
        self.flash = 5

    def update(self, player_x, rng):
        self.frames += 1
        self.flash = max(0, self.flash - 1)
        phase = 3 if self.hp <= self.max_hp / 3 else 2 if self.hp <= self.max_hp * 2 / 3 else 1
        changed = phase != self.phase
        if changed:
            self.phase = phase
            self.next_attack = self.frames + 65
            self.attack_index = 0
            self.gap = None
        attacks = []
        if self.frames >= self.next_attack:
            attacks = self.plan(player_x, rng)
            interval = (70, 94, 65)[self.phase - 1] if self.hard else (100, 135, 100)[self.phase - 1]
            self.next_attack = self.frames + interval
            self.attack_index += 1
        return attacks, changed

    def plan(self, player_x, rng):
        warning = 32 if self.hard else 52
        speed = (2.8 if self.hard else 1.8) + (self.phase - 1) * 0.25
        if self.demo:
            speed *= 0.8
            warning += 12
        if self.phase == 1:
            center = max(24, min(player_x + 8, 296))
            offsets = (-24, 0, 24) if self.hard else (-12, 12)
            return [Attack(max(8, min(center + offset - 10, 292)), speed, warning)
                    for offset in offsets]
        if self.phase == 2:
            gap_center = max(48, min(player_x + 8 + rng.choice((-48, 48)), 272))
            half_gap = 24 if self.hard else 38
        else:
            gap_center = 55 + (self.attack_index % 6) * 42
            if (self.attack_index // 6) % 2:
                gap_center = 320 - gap_center
            half_gap = 22 if self.hard else 35
        self.gap = (gap_center - half_gap, gap_center + half_gap)
        # 两侧分别排列，在缺口边缘缩短最后一张，保留设计好的通道。
        # 不足 8 像素的细碎边片省略，避免视觉上难辨认的危险条。
        left, right = map(int, self.gap)
        attacks = []
        for x in range(8, left, 24):
            width = min(20, left - x)
            if width >= 8:
                attacks.append(Attack(x, speed, warning, width))
        for x in range(right, 312, 24):
            width = min(20, 312 - x)
            if width >= 8:
                attacks.append(Attack(x, speed, warning, width))
        return attacks
