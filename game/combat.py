"""主动战斗的节奏系统：连击、分数倍率与可释放的专注爆发。"""

from dataclasses import dataclass

from game.config import FPS

FOCUS_MAX = 100
COMBO_TIMEOUT = FPS * 4


@dataclass
class CombatFlow:
    chain: int = 0
    best_chain: int = 0
    focus: int = 0
    bursts: int = 0
    last_action_frame: int = -COMBO_TIMEOUT

    @property
    def multiplier(self):
        return min(4, 1 + self.chain // 5)

    def tick(self, frame):
        if self.chain and frame - self.last_action_frame > COMBO_TIMEOUT:
            self.chain = 0

    def reward(self, points, focus, frame):
        self.tick(frame)
        self.chain += 1
        self.best_chain = max(self.best_chain, self.chain)
        self.focus = min(FOCUS_MAX, self.focus + focus)
        self.last_action_frame = frame
        return points * self.multiplier

    def break_chain(self):
        self.chain = 0
        self.focus = max(0, self.focus - 30)

    def spend(self):
        if self.focus < FOCUS_MAX:
            return False
        self.focus = 0
        self.bursts += 1
        return True
