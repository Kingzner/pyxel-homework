"""成品版主循环：状态 → 输入 → 游戏数据 → 绘制。

运行方式：在项目目录执行 .venv/bin/python -m game.main。
学习时先读 config.py，再分别阅读这个文件中的小方法。
"""

from dataclasses import dataclass, field
import argparse
import math
import random

import pyxel

from game import art, i18n, storage, screens
from game.audio import Audio
from game.boss import Boss
from game.combat import CombatFlow, FOCUS_MAX
from game.progression import SKINS, unlock
from game.upgrades import draw_choices
from game.waves import plan as plan_wave
from game.config import (
    DASH_COOLDOWN, DASH_FRAMES, DASH_SPEED, FLOOR_Y, FPS, HEIGHT,
    HIT_GRACE_FRAMES, MAX_WAVE, MODES, MOVE_SPEED,
    PLAYER_WIDTH, PLAYER_Y, START_LIVES, WAVE_SECONDS, WIDTH,
    ADVENTURE_BOSS_SECONDS, UPGRADE_SECONDS, DEMO_BOSS_SECONDS, DEMO_UPGRADE_SECONDS,
)


@dataclass
class FallingItem:
    kind: str
    x: float
    y: float
    speed: float
    width: int
    height: int
    warning: int = 0
    age: int = 0
    phase: float = 0
    frozen: int = 0


@dataclass
class AnswerShot:
    x: float
    y: float
    vx: float
    damage: int


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: int
    life: int


@dataclass
class FloatingText:
    text: str
    x: float
    y: float
    color: int
    life: int = 48
    values: dict = field(default_factory=dict)


class Game:
    def __init__(self, initial_mode="arcade", seed=None):
        self.data = storage.load()
        self.seed = seed
        self.rng = random.Random(seed)
        pyxel.init(WIDTH, HEIGHT, title="Dodge Homework v0.6 | Midnight Study Club",
                   fps=FPS, display_scale=3, quit_key=pyxel.KEY_NONE)
        pyxel.colors[:] = art.PALETTE
        i18n.init_fonts()
        self.audio = Audio(self.data["muted"])
        self.language = self.data["language"]
        self.mode = initial_mode
        self.skin = self.data["selected"]
        self.wardrobe_focus = list(SKINS).index(self.skin)
        self.state = "title"
        self.visual_frames = 0
        self.save_ok = True
        self.reset_round()
        self.audio.music()

    @property
    def score(self):
        return min(999_999_999, (self.frames // FPS) * 10 + self.bonus_score)

    def reset_round(self):
        self.player_x = (WIDTH - PLAYER_WIDTH) / 2
        self.facing = 1
        self.moving = False
        self.frames = 0
        self.bonus_score = 0
        self.dodged = 0
        self.destroyed = 0
        self.notes = 0
        self.combat = CombatFlow()
        self.focus_flash = 0
        self.max_lives = 2 if self.mode == "exam" else 5 if self.mode == "demo" else START_LIVES
        self.lives = self.max_lives
        self.shield = self.mode == "demo"
        self.invulnerable = 0
        self.dash_frames = 0
        self.dashing = False
        self.dash_cooldown = 0
        self.dash_direction = 1
        self.wave = 1
        self.next_paper = 42
        self.paper_spawns = 0
        self.next_note = FPS * 4
        self.next_shield = FPS * 8
        self.items = []
        self.particles = []
        self.labels = []
        self.shake = 0
        self.banner_frames = 0
        self.notice = "dash_tip"
        self.notice_values = {}
        self.notice_frames = FPS * 5
        self.new_record = False
        self.record_at_start = self.data["best"].get(self.mode, 0)
        self.skills = []
        self.upgrade_index = 0
        self.upgrade_cards = []
        self.card_focus = 0
        self.loadout = False
        self.boss = None
        self.intro_frames = 0
        self.shots = []
        self.shot_cooldown = 0
        self.notes_saved = 0
        self.new_unlocks = []
        self.failure_reason = "hit_by_homework"
        self.clear_registered = False
        self.pause_return = "playing"

    def start_game(self):
        if self.seed is not None:
            self.rng.seed(self.seed)
        self.reset_round()
        self.state = "playing"
        self.audio.stop()
        self.audio.music()
        self.audio.effect("start")
        if self.mode == "exam":
            self.loadout = True
            self.open_upgrade()

    def persist(self):
        if self.frames and self.mode != "demo":
            self.data["best"][self.mode] = max(self.data["best"][self.mode], self.score)
            self.data["stats"]["notes"] += max(0, self.notes - self.notes_saved)
            self.notes_saved = self.notes
            for skin in unlock(self.data):
                if skin not in self.new_unlocks:
                    self.new_unlocks.append(skin)
        self.data["muted"] = self.audio.muted
        self.data["language"] = self.language
        self.save_ok = storage.save(self.data)

    def menu(self):
        self.persist()
        self.reset_round()
        self.state = "title"
        self.audio.stop()
        self.audio.music()

    def finish(self, won=False):
        self.state = "victory" if won else "game_over"
        if won:
            self.bonus_score += 2000 if self.mode == "exam" else 500
            if self.mode != "demo" and not self.clear_registered:
                self.data["stats"]["clears"] += 1
                self.data["stats"]["hard_clears"] += int(self.mode == "exam")
                self.clear_registered = True
            self.items = []
            self.shots = []
            self.burst(160, 100, 11, 60)
        self.new_record = self.score > self.record_at_start
        self.persist()
        self.audio.stop()
        self.audio.effect("win" if won else "over")

    def select_mode(self, mode):
        self.mode = mode
        if mode != "demo" and self.skin not in self.data["owned"]:
            self.skin = self.data["selected"]
        self.reset_round()

    def cycle_skin(self):
        available = list(SKINS) if self.mode == "demo" else self.data["owned"]
        index = available.index(self.skin) if self.skin in available else -1
        self.skin = available[(index + 1) % len(available)]
        if self.skin in self.data["owned"]:
            self.data["selected"] = self.skin
            self.persist()

    def update_wardrobe(self):
        keys = (pyxel.KEY_1, pyxel.KEY_2, pyxel.KEY_3, pyxel.KEY_4)
        for index, key in enumerate(keys):
            if pyxel.btnp(key):
                self.wardrobe_focus = index
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.wardrobe_focus = (self.wardrobe_focus - 1) % len(SKINS)
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.wardrobe_focus = (self.wardrobe_focus + 1) % len(SKINS)
        if pyxel.btnp(pyxel.KEY_RETURN):
            skin = list(SKINS)[self.wardrobe_focus]
            if self.mode == "demo" or skin in self.data["owned"]:
                self.skin = skin
                if skin in self.data["owned"]:
                    self.data["selected"] = skin
                    self.persist()
                self.state = "title"
        if pyxel.btnp(pyxel.KEY_C) or pyxel.btnp(pyxel.KEY_ESCAPE):
            self.state = "title"

    def open_upgrade(self):
        self.upgrade_cards = draw_choices(self.rng, self.skills)
        self.card_focus = 0
        self.upgrade_index += 1
        self.state = "upgrade"
        self.audio.stop()
        self.audio.effect("wave")

    def choose_upgrade(self, index):
        key = self.upgrade_cards[index]
        self.skills.append(key)
        self.dash_cooldown = min(self.dash_cooldown, self.dash_cooldown_limit())
        self.notice = "upgrade_notice"
        self.notice_values = {"name": key}
        self.notice_frames = FPS * 3
        if self.loadout:
            if len(self.skills) < 3:
                self.open_upgrade()
            else:
                self.loadout = False
                self.begin_boss()
        else:
            self.state = "playing"
            self.audio.music()
            self.audio.effect("pickup")

    def update_upgrade(self):
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.card_focus = (self.card_focus - 1) % len(self.upgrade_cards)
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.card_focus = (self.card_focus + 1) % len(self.upgrade_cards)
        for index, key in enumerate((pyxel.KEY_1, pyxel.KEY_2, pyxel.KEY_3)):
            if pyxel.btnp(key) and index < len(self.upgrade_cards):
                self.choose_upgrade(index)
                return
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.choose_upgrade(self.card_focus)
        elif pyxel.btnp(pyxel.KEY_ESCAPE):
            self.menu()

    def begin_boss(self):
        self.boss = Boss(self.mode)
        self.items = []
        self.shots = []
        self.state = "boss_intro"
        self.intro_frames = 110
        self.banner_frames = 0
        self.notice = "boss_tip"
        self.notice_values = {}
        self.notice_frames = FPS * 5
        self.next_note = self.frames + FPS * 3
        self.next_shield = self.frames + FPS * (10 if self.mode == "exam" else 6)
        self.audio.stop()
        self.audio.music(True)
        self.audio.effect("wave")

    def dash_cooldown_limit(self):
        factor = 0.75 if "wind" in self.skills else 1
        if "focus" in self.skills and self.lives == 1:
            factor *= 0.6
        return max(45, int(DASH_COOLDOWN * factor))

    def update(self):
        if pyxel.btnp(pyxel.KEY_L):
            self.language = "en" if self.language == "zh" else "zh"
            self.persist()
        if pyxel.btnp(pyxel.KEY_Q):
            self.persist()
            pyxel.quit()
            return
        if pyxel.btnp(pyxel.KEY_M):
            self.audio.toggle(self.state in ("title", "help", "playing", "boss_intro", "wardrobe", "ending"),
                              self.boss is not None and self.state != "ending")
            self.persist()

        if self.state != "paused":
            self.visual_frames += 1
            self.update_effects()

        if self.state == "title":
            for key, mode in ((pyxel.KEY_1, "arcade"), (pyxel.KEY_2, "cozy"),
                              (pyxel.KEY_3, "exam"), (pyxel.KEY_D, "demo")):
                if pyxel.btnp(key):
                    self.select_mode(mode)
            if pyxel.btnp(pyxel.KEY_S):
                self.cycle_skin()
            if pyxel.btnp(pyxel.KEY_C):
                self.wardrobe_focus = list(SKINS).index(self.skin)
                self.state = "wardrobe"
                return
            if pyxel.btnp(pyxel.KEY_H):
                self.state = "help"
                return
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
                self.start_game()
            return

        if self.state == "wardrobe":
            self.update_wardrobe()
            return
        if self.state == "help":
            if (pyxel.btnp(pyxel.KEY_H) or pyxel.btnp(pyxel.KEY_RETURN)
                    or pyxel.btnp(pyxel.KEY_ESCAPE)):
                self.state = "title"
            return
        if self.state == "upgrade":
            self.update_upgrade()
            return

        if self.state in ("game_over", "victory", "ending"):
            if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.KEY_SPACE):
                self.start_game()
            elif self.state == "victory" and pyxel.btnp(pyxel.KEY_RETURN):
                self.state = "ending"
                self.audio.music()
            elif self.state != "ending" and pyxel.btnp(pyxel.KEY_C):
                self.menu()
                self.state = "wardrobe"
            elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_ESCAPE):
                self.menu()
            return

        if self.state == "paused":
            if pyxel.btnp(pyxel.KEY_P) or pyxel.btnp(pyxel.KEY_ESCAPE):
                self.state = self.pause_return
                self.audio.music(self.boss is not None)
            elif pyxel.btnp(pyxel.KEY_RETURN):
                self.menu()
            return

        if pyxel.btnp(pyxel.KEY_P) or pyxel.btnp(pyxel.KEY_ESCAPE):
            self.pause_return = self.state
            self.state = "paused"
            self.audio.stop()
            return

        if self.state == "boss_intro":
            self.intro_frames -= 1
            if self.intro_frames <= 0 or pyxel.btnp(pyxel.KEY_RETURN):
                self.state = "playing"
            return

        if self.boss is None:
            schedule = DEMO_UPGRADE_SECONDS if self.mode == "demo" else UPGRADE_SECONDS
            boss_time = DEMO_BOSS_SECONDS if self.mode == "demo" else ADVENTURE_BOSS_SECONDS
            if self.mode == "demo" and pyxel.btnp(pyxel.KEY_N):
                if len(self.skills) < 3:
                    self.open_upgrade()
                else:
                    self.begin_boss()
                return
            if self.upgrade_index < len(schedule) and self.frames >= schedule[self.upgrade_index] * FPS:
                self.open_upgrade()
                return
            if self.frames >= boss_time * FPS:
                self.begin_boss()
                return

        self.update_player()
        self.frames += 1
        self.combat.tick(self.frames)
        if pyxel.btnp(pyxel.KEY_X):
            self.focus_burst()
        new_wave = min(MAX_WAVE, 1 + self.frames // (FPS * WAVE_SECONDS))
        if new_wave > self.wave:
            self.wave = new_wave
            self.banner_frames = FPS * 2
            self.audio.effect("wave")
            self.notice = "wave_tip"
            self.notice_values = {}
            self.notice_frames = FPS * 2

        if self.boss:
            attacks, changed = self.boss.update(self.player_x, self.rng)
            if changed:
                self.items = [item for item in self.items if item.kind in ("note", "shield")]
                self.banner_frames = FPS * 2
                self.audio.effect("wave")
            for attack in attacks:
                self.items.append(FallingItem("exam", attack.x, 105,
                                  attack.speed, attack.width, attack.height, attack.warning))
            self.update_shots()
            if self.boss.hp <= 0:
                self.finish(True)
                return
            if self.boss.seconds_left <= 0:
                self.failure_reason = "time_up"
                self.finish()
                return
            self.spawn_pickups()
        else:
            self.spawn_items()
            self.update_shots()
        self.update_items()

    def update_player(self):
        left = pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A)
        right = pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D)
        direction = int(right) - int(left)
        if direction:
            self.facing = direction
        self.invulnerable = max(0, self.invulnerable - 1)
        self.dash_cooldown = max(0, self.dash_cooldown - 1)

        if pyxel.btnp(pyxel.KEY_SPACE) and self.dash_cooldown == 0:
            self.dash_frames = DASH_FRAMES
            self.dash_cooldown = self.dash_cooldown_limit()
            self.dash_direction = self.facing
            self.audio.effect("dash")
            if "frost" in self.skills:
                for item in self.items:
                    if item.kind in ("paper", "exam") and abs(item.x - self.player_x) <= 90:
                        item.frozen = 24
                self.burst(self.player_x + 8, PLAYER_Y + 5, 12, 12)
        self.dashing = self.dash_frames > 0
        self.moving = direction != 0 or self.dashing
        if self.dashing:
            self.player_x += self.dash_direction * DASH_SPEED
            self.dash_frames -= 1
            if self.frames % 2 == 0:
                self.particles.append(Particle(
                    self.player_x + 8, PLAYER_Y + 12,
                    -self.dash_direction * 0.7, -0.3, 11, 16,
                ))
        else:
            self.player_x += direction * MOVE_SPEED
        self.player_x = max(8, min(self.player_x, WIDTH - PLAYER_WIDTH - 8))

    def update_shots(self):
        self.shot_cooldown = max(0, self.shot_cooldown - 1)
        if pyxel.btn(pyxel.KEY_Z) and self.shot_cooldown == 0:
            travel_frames = max(1, (PLAYER_Y - 80) / 5)
            vx = (max(-2.5, min((self.boss.x - self.player_x - 8) / travel_frames, 2.5))
                  if self.boss else 0)
            damage = (3 if self.mode == "demo" else 2) + int("answer" in self.skills)
            self.shots.append(AnswerShot(self.player_x + 8, PLAYER_Y, vx, damage))
            self.shot_cooldown = 14 if "answer" in self.skills else 18
            self.audio.effect("shot")
        for shot in self.shots[:]:
            shot.x += shot.vx
            shot.y -= 5
            target = next((item for item in self.items
                           if item.kind in ("paper", "exam") and not item.warning
                           and item.x <= shot.x <= item.x + item.width
                           and item.y <= shot.y + 5 <= item.y + item.height), None)
            if target:
                self.items.remove(target)
                self.shots.remove(shot)
                self.dodged += 1
                self.destroyed += 1
                earned = self.combat.reward(15, 16, self.frames)
                self.bonus_score += earned
                self.burst(target.x + target.width / 2, target.y + target.height / 2,
                           10, 12)
                self.label("shot_score", target.x + target.width / 2,
                           target.y - 7, 10, points=earned)
                self.audio.effect("paper")
            elif self.boss and 57 <= shot.y <= 101 and abs(shot.x - self.boss.x) < 24:
                self.boss.damage(shot.damage)
                self.bonus_score += self.combat.reward(3, 3, self.frames)
                self.burst(shot.x, shot.y, 11, 2)
                self.shots.remove(shot)
            elif shot.y < 40 or shot.x < 0 or shot.x > WIDTH:
                self.shots.remove(shot)

    def focus_burst(self):
        if not self.combat.spend():
            return
        cleared = 0
        for item in self.items[:]:
            if item.kind in ("paper", "exam"):
                self.items.remove(item)
                cleared += 1
                self.burst(item.x + item.width / 2, item.y + item.height / 2, 11, 7)
        self.destroyed += cleared
        self.dodged += cleared
        self.bonus_score += cleared * 12
        if self.boss:
            self.boss.damage(22 if self.mode == "exam" else 18)
        self.invulnerable = max(self.invulnerable, FPS // 3)
        self.focus_flash = 18
        self.shake = 5
        self.notice = "focus_notice"
        self.notice_values = {}
        self.notice_frames = FPS * 2
        self.audio.effect("focus")

    def spawn_items(self):
        config = MODES[self.mode]
        speed = config["speed"] + (self.wave - 1) * config["speed_step"]
        if self.frames >= self.next_paper:
            self.paper_spawns += 1
            occupied = [item.x for item in self.items if item.warning]
            plans = plan_wave(self.wave, self.paper_spawns, self.player_x,
                              self.rng, occupied)
            for planned in plans:
                width, height = (20, 18) if planned.kind == "exam" else (12, 15)
                self.items.append(FallingItem(
                    planned.kind, planned.x, 40, speed + planned.speed_bonus,
                    width, height, warning=planned.warning,
                    phase=self.rng.random() * math.tau,
                ))
            interval = config["interval"] - (self.wave - 1) * config["interval_step"]
            self.next_paper = self.frames + max(28, interval) + (18 if len(plans) > 1 else 0)

        self.spawn_pickups()

    def spawn_pickups(self):
        if self.frames >= self.next_note:
            self.spawn_pickup("note")
            self.next_note = self.frames + FPS * 4
        if self.frames >= self.next_shield:
            self.spawn_pickup("shield")
            self.next_shield = self.frames + FPS * (12 if self.mode == "exam" else 10)

    def spawn_pickup(self, kind):
        self.items.append(FallingItem(
            kind, self.rng.randint(20, WIDTH - 32), 40,
            1.2 if kind == "note" else 1.05,
            12, 13, phase=self.rng.random() * math.tau,
        ))

    def collides(self, item):
        # 碰撞区域比角色图案略小，给边缘擦过留一点余量。
        return (
            self.player_x + 3 < item.x + item.width
            and self.player_x + PLAYER_WIDTH - 3 > item.x
            and PLAYER_Y + 4 < item.y + item.height
            and FLOOR_Y > item.y
        )

    def update_items(self):
        for item in self.items[:]:
            if item not in self.items:
                continue
            item.age += 1
            was_frozen = item.frozen > 0
            item.frozen = max(0, item.frozen - 1)
            if item.warning:
                if not was_frozen:
                    item.warning -= 1
                continue
            if not was_frozen:
                item.y += item.speed
            if item.kind == "note" and "magnet" in self.skills and item.y > PLAYER_Y - 70:
                distance = self.player_x + 8 - item.x - 6
                if abs(distance) < 65:
                    item.x += max(-3.5, min(distance, 3.5))
                    item.y += 1.5
            if item.kind != "exam" and not was_frozen:
                item.x += math.sin(item.age / 15 + item.phase) * 0.18
                item.x = max(8, min(item.x, WIDTH - item.width - 8))

            if self.collides(item):
                if item.kind in ("note", "shield"):
                    self.collect(item)
                    self.items.remove(item)
                    continue
                if self.dashing:
                    self.dodged += 1
                    earned = self.combat.reward(10, 16, self.frames)
                    self.bonus_score += earned
                    self.burst(item.x + 6, item.y + 6, 11, 10)
                    self.label("dash_score", self.player_x + 8,
                               PLAYER_Y - 12, 11, points=earned)
                    self.items.remove(item)
                    if "recycle" in self.skills:
                        self.items.append(FallingItem("note", item.x, item.y, 1.2, 12, 13))
                    continue
                if self.invulnerable:
                    continue
                self.items.remove(item)
                self.hit()
                if self.state == "game_over":
                    return
                continue

            if item.y > FLOOR_Y + 5:
                if item.kind in ("paper", "exam"):
                    self.dodged += 1
                    self.bonus_score += 10
                    gap = max(self.player_x + 3 - item.x - item.width,
                              item.x - self.player_x - PLAYER_WIDTH + 3, 0)
                    if gap < 14:
                        earned = self.combat.reward(5, 20, self.frames)
                        self.bonus_score += earned
                        self.label("close_score", self.player_x + 8,
                                   PLAYER_Y - 10, 10, points=earned)
                    self.burst(item.x + item.width / 2, FLOOR_Y + 3, 6, 4)
                self.items.remove(item)

    def collect(self, item):
        self.audio.effect("pickup")
        if item.kind == "shield":
            earned = self.combat.reward(35 if self.shield else 15, 8, self.frames)
            self.bonus_score += earned
            self.shield = True
            self.label("shield_label", self.player_x + 8, PLAYER_Y - 12, 11)
            self.burst(item.x + 6, item.y + 6, 11, 16)
        else:
            earned = self.combat.reward(25, 8, self.frames)
            self.bonus_score += earned
            self.notes += 1
            self.label("note_score", self.player_x + 8,
                       PLAYER_Y - 12, 10, points=earned)
            self.burst(item.x + 5, item.y + 5, 10, 10)

    def hit(self):
        if self.shield:
            self.shield = False
            self.invulnerable = FPS
            self.burst(self.player_x + 8, PLAYER_Y + 10, 11, 24)
            self.label("shield_saved", self.player_x + 8, PLAYER_Y - 14, 11)
            self.audio.effect("shield")
            self.shake = 2
            if "burst" in self.skills:
                for item in self.items[:]:
                    if item.kind in ("paper", "exam") and abs(item.x - self.player_x) <= 100:
                        self.items.remove(item)
                        self.dodged += 1
                        self.bonus_score += 10
                        self.burst(item.x + 6, item.y + 6, 13, 6)
            return
        self.lives -= 1
        self.combat.break_chain()
        self.dash_cooldown = min(self.dash_cooldown, self.dash_cooldown_limit())
        self.invulnerable = HIT_GRACE_FRAMES
        self.shake = 5
        self.burst(self.player_x + 8, PLAYER_Y + 8, 8, 22)
        self.audio.effect("hit")
        if not self.lives:
            self.finish()

    def burst(self, x, y, color, count):
        for _ in range(count):
            angle = self.rng.uniform(0, math.tau)
            speed = self.rng.uniform(0.4, 2)
            self.particles.append(Particle(
                x, y, math.cos(angle) * speed, math.sin(angle) * speed - 0.5,
                color, self.rng.randint(16, 32),
            ))
        self.particles = self.particles[-160:]

    def label(self, key, x, y, color, **values):
        # 长文字靠近边缘时仍完整留在画面中。
        message = i18n.tr(self.language, key, **values)
        half_width = i18n.width(self.language, message) / 2
        x = max(half_width + 4, min(x, WIDTH - half_width - 4))
        self.labels.append(FloatingText(key, x, y, color, values=values))

    def update_effects(self):
        self.shake = max(0, self.shake - 0.3)
        self.focus_flash = max(0, self.focus_flash - 1)
        self.banner_frames = max(0, self.banner_frames - 1)
        self.notice_frames = max(0, self.notice_frames - 1)
        for particle in self.particles:
            particle.x += particle.vx
            particle.y += particle.vy
            particle.vy += 0.035
            particle.life -= 1
        self.particles = [particle for particle in self.particles if particle.life > 0]
        for label in self.labels:
            label.y -= 0.4
            label.life -= 1
        self.labels = [label for label in self.labels if label.life > 0]

    def draw(self):
        if self.shake:
            pyxel.camera(math.sin(self.visual_frames * 2) * self.shake,
                         math.cos(self.visual_frames * 3) * self.shake / 2)
        mood = "dawn" if self.state == "ending" else "boss" if self.boss else "night"
        art.classroom(self.visual_frames, mood)
        if self.boss and self.state != "ending":
            art.dean(self.boss.x, 57, self.visual_frames, self.boss.flash > 0,
                     i18n.FONT_SMALL if self.language == "zh" else None)
        self.draw_items()
        for shot in self.shots:
            pyxel.rect(shot.x - 1, shot.y, 3, 7, 11)
            pyxel.line(shot.x, shot.y, shot.x, shot.y + 3, 7)
        self.draw_player()
        for particle in self.particles:
            size = 2 if particle.life > 12 else 1
            pyxel.rect(particle.x, particle.y, size, size, particle.color)
        if self.focus_flash:
            radius = (18 - self.focus_flash) * 15
            pyxel.circb(self.player_x + 8, PLAYER_Y + 8, radius, 11)
            if self.focus_flash >= 15:
                pyxel.dither(0.24)
                pyxel.rect(0, 38, WIDTH, 170, 11)
                pyxel.dither(1)
        for label in self.labels:
            message = i18n.tr(self.language, label.text, **label.values)
            half_width = i18n.width(self.language, message) / 2
            x = max(half_width + 4, min(label.x, WIDTH - half_width - 4))
            i18n.center(label.y, message, label.color, self.language, x)
        pyxel.camera()
        if self.state != "ending":
            self.draw_hud()

        if self.state == "title":
            screens.title(self)
        elif self.state == "wardrobe":
            screens.wardrobe(self)
        elif self.state == "help":
            screens.help_screen(self)
        elif self.state == "upgrade":
            screens.upgrade(self)
        elif self.state == "boss_intro":
            screens.boss_intro(self)
        elif self.state == "paused":
            screens.pause(self)
        elif self.state in ("game_over", "victory"):
            screens.results(self)
        elif self.state == "ending":
            screens.ending(self)
        elif self.banner_frames > FPS:
            y = 114 if self.boss else 48
            art.panel(119, y, 82, 23)
            key = "phase" if self.boss else "wave"
            message = i18n.tr(self.language, key, **({"phase": self.boss.phase}
                              if self.boss else {"wave": self.wave}))
            i18n.center(y + 7, message, 10, self.language)

    def draw_items(self):
        for item in self.items:
            if item.warning:
                center = item.x + item.width / 2
                color = 8 if item.kind == "exam" else 10
                if item.warning % 12 < 8:
                    warning_y = item.y + 3
                    pyxel.tri(center - 4, warning_y, center + 4, warning_y, center, warning_y + 6, color)
                    for y in range(int(warning_y + 13), 180, 18):
                        pyxel.line(center, y, center, y + 2, 3)
                continue
            if item.kind in ("paper", "exam"):
                art.paper(item.x, item.y, item.width, item.height, item.kind == "exam")
                if item.frozen:
                    pyxel.rectb(item.x - 1, item.y - 1, item.width + 2, item.height + 2, 12)
            else:
                art.pickup(item.x, item.y, item.kind, self.visual_frames)

    def draw_player(self):
        pyxel.rect(self.player_x + 3, FLOOR_Y + 1, 10, 2, 0)
        if self.invulnerable and self.visual_frames % 8 < 4 and self.state == "playing":
            return
        art.character(self.player_x, PLAYER_Y, self.frames,
                      self.moving and self.state == "playing", self.facing,
                      expression="hurt" if self.invulnerable else
                      "dash" if self.dashing else "normal", skin=self.skin)
        if self.shield:
            art.shield_ring(self.player_x, PLAYER_Y, self.visual_frames)
        if self.dashing:
            pyxel.line(self.player_x - self.dash_direction * 7, PLAYER_Y + 8,
                       self.player_x - self.dash_direction * 14, PLAYER_Y + 8, 11)

    def draw_hud(self):
        language = self.language
        art.panel(12, 7, 296, 28, 0, 3)
        i18n.text(20, 9, i18n.tr(language, "score"), 5, language)
        pyxel.text(20, 23, f"{self.score:05d}", 7)
        i18n.text(92, 9, i18n.tr(language, "best"), 5, language)
        pyxel.text(92, 23, f"{max(self.score, self.data['best'].get(self.mode, 0)):05d}", 10)
        if self.boss:
            progress = i18n.tr(language, "boss_time", phase=self.boss.phase,
                               seconds=self.boss.seconds_left)
        elif self.mode == "exam":
            progress = i18n.tr(language, "boss_next")
        else:
            deadline = DEMO_BOSS_SECONDS if self.mode == "demo" else ADVENTURE_BOSS_SECONDS
            remaining = max(0, deadline - self.frames // FPS)
            progress = i18n.tr(language, "boss_eta", seconds=remaining)
        i18n.text(163, 9, progress, 8 if self.boss else 6, language)
        i18n.text(163, 23, i18n.mode_name(language, self.mode), 11, language)
        for index in range(self.max_lives):
            art.heart(WIDTH - 19 - self.max_lives * 13 + index * 13,
                      16, index < self.lives)

        if self.boss:
            pyxel.rect(12, 39, 296, 17, 0)
            boss_name = i18n.phase_name(language, self.boss)
            i18n.text(18, 39, i18n.tr(language, "boss_name", name=boss_name), 6, language)
            pyxel.text(250, 41, f"{self.boss.hp}/{self.boss.max_hp}", 8)
            pyxel.rect(18, 50, 284, 4, 3)
            pyxel.rect(18, 50, 284 * self.boss.hp / self.boss.max_hp, 4, 8)

        pyxel.rect(0, 208, WIDTH, 15, 2)
        i18n.text(12, 210, i18n.tr(language, "dash"), 6, language)
        pyxel.rect(45, 213, 34, 5, 0)
        ready = max(0, min(1, 1 - self.dash_cooldown / self.dash_cooldown_limit()))
        pyxel.rect(46, 214, 32 * ready, 3, 11 if ready == 1 else 3)
        i18n.text(87, 210, i18n.tr(language, "focus_bar"), 10, language)
        pyxel.rect(121, 212, 67, 7, 0)
        pyxel.rectb(121, 212, 67, 7, 11 if self.combat.focus == FOCUS_MAX else 3)
        pyxel.rect(123, 214, 63 * self.combat.focus / FOCUS_MAX, 3,
                   11 if self.combat.focus == FOCUS_MAX else 10)
        if self.combat.chain:
            i18n.text(195, 210, f"C{self.combat.chain:02d} x{self.combat.multiplier}",
                      11, language)
        i18n.text(257, 210, i18n.tr(language, "shield_on" if self.shield else "shield_off"),
                  11 if self.shield else 5, language)
        if self.notice_frames and self.state == "playing":
            values = {}
            if self.notice == "upgrade_notice":
                values["name"] = i18n.upgrade_name(language, self.notice_values["name"])
            message = i18n.tr(language, self.notice, **values)
            i18n.center(150, message, 0, language, 161)
            i18n.center(149, message, 10, language, 160)
        i18n.text(8, 227, i18n.tr(language, "hud_controls"), 6, language)
        i18n.text(170, 227, i18n.tr(language, "pause_short"), 5, language)
        i18n.text(209, 227, i18n.tr(language, "mute_on" if self.audio.muted else "mute_off"),
                  5, language)
        i18n.text(248, 227, "L语言" if language == "zh" else "L LANG", 11, language)
        i18n.text(286, 227, i18n.tr(language, "exit"), 5, language)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dodge Homework / Midnight Study Club")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--showcase", action="store_true", help="Open the fast presentation mode")
    group.add_argument("--boss", action="store_true", help="Go directly to the hard boss loadout")
    parser.add_argument("--seed", type=int, help="Use a repeatable random seed for presentations")
    args = parser.parse_args()
    game = Game("demo" if args.showcase else "exam" if args.boss else "arcade",
                seed=args.seed)
    if args.boss:
        game.start_game()
    try:
        pyxel.run(game.update, game.draw)
    finally:
        game.persist()
