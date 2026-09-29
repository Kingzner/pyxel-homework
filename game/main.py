"""成品版主循环：状态 → 输入 → 游戏数据 → 绘制。

运行方式：在项目目录执行 .venv/bin/python -m game.main。
学习时先读 config.py，再分别阅读这个文件中的小方法。
"""

from dataclasses import dataclass
import math
import random

import pyxel

from game import art, storage
from game.audio import Audio
from game.config import (
    DASH_COOLDOWN, DASH_FRAMES, DASH_SPEED, FLOOR_Y, FPS, HEIGHT,
    HIT_GRACE_FRAMES, MAX_WAVE, MODES, MOVE_SPEED, PLAYER_HEIGHT,
    PLAYER_WIDTH, PLAYER_Y, START_LIVES, WAVE_SECONDS, WIDTH,
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


class Game:
    def __init__(self):
        self.data = storage.load()
        self.rng = random.Random()
        pyxel.init(WIDTH, HEIGHT, title="Dodge Homework | Midnight Study Club",
                   fps=FPS, display_scale=3, quit_key=pyxel.KEY_NONE)
        pyxel.colors[:] = art.PALETTE
        self.audio = Audio(self.data["muted"])
        self.mode = "arcade"
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
        self.notes = 0
        self.lives = START_LIVES
        self.shield = False
        self.invulnerable = 0
        self.dash_frames = 0
        self.dashing = False
        self.dash_cooldown = 0
        self.dash_direction = 1
        self.wave = 1
        self.next_paper = 42
        self.next_note = FPS * 4
        self.next_shield = FPS * 8
        self.items = []
        self.particles = []
        self.labels = []
        self.shake = 0
        self.banner_frames = 0
        self.notice = "SPACE: DASH THROUGH DANGER"
        self.notice_frames = FPS * 5
        self.new_record = False
        self.record_at_start = self.data["best"][self.mode]

    def start_game(self):
        self.reset_round()
        self.state = "playing"
        self.audio.stop()
        self.audio.music()
        self.audio.effect("start")

    def persist(self):
        if self.frames:
            self.data["best"][self.mode] = max(self.data["best"][self.mode], self.score)
        self.data["muted"] = self.audio.muted
        self.save_ok = storage.save(self.data)

    def menu(self):
        self.persist()
        self.reset_round()
        self.state = "title"
        self.audio.stop()
        self.audio.music()

    def finish(self):
        self.state = "game_over"
        self.new_record = self.score > self.record_at_start
        self.persist()
        self.audio.stop()
        self.audio.effect("over")

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            self.persist()
            pyxel.quit()
            return
        if pyxel.btnp(pyxel.KEY_M):
            self.audio.toggle(self.state in ("title", "playing"))
            self.persist()

        if self.state != "paused":
            self.visual_frames += 1
            self.update_effects()

        if self.state == "title":
            if pyxel.btnp(pyxel.KEY_1):
                self.mode = "arcade"
            if pyxel.btnp(pyxel.KEY_2):
                self.mode = "cozy"
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
                self.start_game()
            return

        if self.state == "game_over":
            if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.KEY_SPACE):
                self.start_game()
            elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_ESCAPE):
                self.menu()
            return

        if self.state == "paused":
            if pyxel.btnp(pyxel.KEY_P) or pyxel.btnp(pyxel.KEY_ESCAPE):
                self.state = "playing"
                self.audio.music()
            elif pyxel.btnp(pyxel.KEY_RETURN):
                self.menu()
            return

        if pyxel.btnp(pyxel.KEY_P) or pyxel.btnp(pyxel.KEY_ESCAPE):
            self.state = "paused"
            self.audio.stop()
            return

        self.update_player()
        self.frames += 1
        new_wave = min(MAX_WAVE, 1 + self.frames // (FPS * WAVE_SECONDS))
        if new_wave > self.wave:
            self.wave = new_wave
            self.banner_frames = FPS * 2
            self.audio.effect("wave")
            self.notice = "DEADLINES ARE GETTING CLOSER!"
            self.notice_frames = FPS * 2

        self.spawn_items()
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
            self.dash_cooldown = DASH_COOLDOWN
            self.dash_direction = self.facing
            self.audio.effect("dash")
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

    def spawn_items(self):
        config = MODES[self.mode]
        speed = config["speed"] + (self.wave - 1) * config["speed_step"]
        if self.frames >= self.next_paper:
            exam = self.wave >= 2 and self.rng.random() < 0.2
            width, height = (20, 18) if exam else (12, 15)
            x = self.rng.randint(12, WIDTH - width - 12)
            # 避免同一位置连续预告，减少成团出现的作业。
            for _ in range(4):
                if not any(item.warning and abs(item.x - x) < width + 8
                           for item in self.items):
                    break
                x = self.rng.randint(12, WIDTH - width - 12)
            self.items.append(FallingItem(
                "exam" if exam else "paper", x, 40,
                speed + (0.3 if exam else self.rng.uniform(-0.1, 0.15)),
                width, height, warning=48 if exam else 30,
                phase=self.rng.random() * math.tau,
            ))
            interval = config["interval"] - (self.wave - 1) * config["interval_step"]
            self.next_paper = self.frames + max(28, interval)

        if self.frames >= self.next_note:
            self.spawn_pickup("note")
            self.next_note = self.frames + FPS * 4
        if self.frames >= self.next_shield:
            self.spawn_pickup("shield")
            self.next_shield = self.frames + FPS * 10

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
            item.age += 1
            if item.warning:
                item.warning -= 1
                continue
            item.y += item.speed
            if item.kind != "exam":
                item.x += math.sin(item.age / 15 + item.phase) * 0.18
                item.x = max(8, min(item.x, WIDTH - item.width - 8))

            if self.collides(item):
                if item.kind in ("note", "shield"):
                    self.collect(item)
                    self.items.remove(item)
                    continue
                if self.dashing:
                    self.dodged += 1
                    self.bonus_score += 10
                    self.burst(item.x + 6, item.y + 6, 11, 10)
                    self.label("DASH +10", self.player_x + 8, PLAYER_Y - 12, 11)
                    self.items.remove(item)
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
                        self.bonus_score += 5
                        self.label("CLOSE! +5", self.player_x + 8, PLAYER_Y - 10, 10)
                    self.burst(item.x + item.width / 2, FLOOR_Y + 3, 6, 4)
                self.items.remove(item)

    def collect(self, item):
        self.audio.effect("pickup")
        if item.kind == "shield":
            self.bonus_score += 35 if self.shield else 15
            self.shield = True
            self.label("SHIELD ON", self.player_x + 8, PLAYER_Y - 12, 11)
            self.burst(item.x + 6, item.y + 6, 11, 16)
        else:
            self.bonus_score += 25
            self.notes += 1
            self.label("NOTE +25", self.player_x + 8, PLAYER_Y - 12, 10)
            self.burst(item.x + 5, item.y + 5, 10, 10)

    def hit(self):
        if self.shield:
            self.shield = False
            self.invulnerable = FPS
            self.burst(self.player_x + 8, PLAYER_Y + 10, 11, 24)
            self.label("SAVED BY SHIELD", self.player_x + 8, PLAYER_Y - 14, 11)
            self.audio.effect("shield")
            self.shake = 2
            return
        self.lives -= 1
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

    def label(self, text, x, y, color):
        # 长文字靠近边缘时仍完整留在画面中。
        half_width = len(text) * 2
        x = max(half_width + 4, min(x, WIDTH - half_width - 4))
        self.labels.append(FloatingText(text, x, y, color))

    def update_effects(self):
        self.shake = max(0, self.shake - 0.3)
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
        art.classroom(self.visual_frames)
        self.draw_items()
        self.draw_player()
        for particle in self.particles:
            size = 2 if particle.life > 12 else 1
            pyxel.rect(particle.x, particle.y, size, size, particle.color)
        for label in self.labels:
            art.center_text(label.y, label.text, label.color, label.x)
        pyxel.camera()
        self.draw_hud()

        if self.state == "title":
            self.draw_title()
        elif self.state == "paused":
            self.draw_pause()
        elif self.state == "game_over":
            self.draw_results()
        elif self.banner_frames > FPS:
            art.panel(119, 48, 82, 23)
            art.center_text(57, f"WAVE {self.wave:02d}", 10)

    def draw_items(self):
        for item in self.items:
            if item.warning:
                center = item.x + item.width / 2
                color = 8 if item.kind == "exam" else 10
                if item.warning % 12 < 8:
                    pyxel.tri(center - 4, 43, center + 4, 43, center, 49, color)
                    for y in range(56, 180, 18):
                        pyxel.line(center, y, center, y + 2, 3)
                continue
            if item.kind in ("paper", "exam"):
                art.paper(item.x, item.y, item.width, item.height, item.kind == "exam")
            else:
                art.pickup(item.x, item.y, item.kind, self.visual_frames)

    def draw_player(self):
        pyxel.rect(self.player_x + 3, FLOOR_Y + 1, 10, 2, 0)
        if self.invulnerable and self.visual_frames % 8 < 4 and self.state == "playing":
            return
        art.character(self.player_x, PLAYER_Y, self.frames,
                      self.moving and self.state == "playing", self.facing,
                      expression="hurt" if self.invulnerable else
                      "dash" if self.dashing else "normal")
        if self.shield:
            art.shield_ring(self.player_x, PLAYER_Y, self.visual_frames)
        if self.dashing:
            pyxel.line(self.player_x - self.dash_direction * 7, PLAYER_Y + 8,
                       self.player_x - self.dash_direction * 14, PLAYER_Y + 8, 11)

    def draw_hud(self):
        art.panel(12, 7, 296, 28, 0, 3)
        pyxel.text(20, 11, "SCORE", 5)
        pyxel.text(20, 23, f"{self.score:05d}", 7)
        pyxel.text(92, 11, "BEST", 5)
        pyxel.text(92, 23, f"{max(self.score, self.data['best'][self.mode]):05d}", 10)
        pyxel.text(169, 11, f"WAVE {self.wave:02d}", 6)
        pyxel.text(169, 23, MODES[self.mode]["name"], 11)
        for index in range(START_LIVES):
            art.heart(WIDTH - 19 - START_LIVES * 16 + index * 16,
                      16, index < self.lives)

        pyxel.rect(0, 208, WIDTH, 15, 2)
        pyxel.text(12, 213, "DASH", 6)
        pyxel.rect(34, 213, 45, 5, 0)
        ready = 1 - self.dash_cooldown / DASH_COOLDOWN
        pyxel.rect(35, 214, 43 * ready, 3, 11 if ready == 1 else 3)
        pyxel.text(251, 213, "SHIELD ON" if self.shield else "NO SHIELD",
                   11 if self.shield else 5)
        if self.notice_frames and self.state == "playing":
            art.center_text(213, self.notice, 10, 164)
        else:
            art.center_text(213, "MIDNIGHT STUDY CLUB", 5, 164)
        pyxel.text(12, 229, "A/D MOVE  SPACE DASH  P PAUSE", 6)
        pyxel.text(197, 229, "M:OFF" if self.audio.muted else "M:ON", 5)
        pyxel.text(282, 229, "Q EXIT", 5)

    def draw_title(self):
        art.panel(28, 43, 264, 158, 0, 13)
        art.center_text(53, "MIDNIGHT STUDY CLUB", 11)
        art.big_text("DODGE", 66, 7)
        art.big_text("HOMEWORK", 85, 10)
        pyxel.line(47, 107, 272, 107, 3)
        art.character(56, 140 + math.sin(self.visual_frames / 25),
                      self.visual_frames, True, scale=2)
        for index, mode in enumerate(("arcade", "cozy")):
            x = 113 + index * 81
            selected = self.mode == mode
            pyxel.rect(x, 119, 75, 23, 3 if selected else 1)
            pyxel.rectb(x, 119, 75, 23, 11 if selected else 3)
            art.center_text(127, f"{index + 1} {MODES[mode]['name']}",
                            7 if selected else 6, x + 37)
        art.center_text(150, "SPACE TO START", 10, 192)
        art.center_text(164, "SENA / NIGHT SHIFT", 6, 192)
        art.center_text(185, "COLLECT SHIELDS. DODGE DEADLINES.", 6)

    def draw_pause(self):
        pyxel.dither(0.65)
        pyxel.rect(0, 38, WIDTH, 169, 0)
        pyxel.dither(1)
        art.panel(57, 67, 206, 106, 0, 11)
        art.big_text("PAUSED", 81, 11)
        art.center_text(109, "P / ESC: CONTINUE", 7)
        art.center_text(125, "ENTER: MAIN MENU", 6)
        art.center_text(145, "TAKE A BREATH. YOU GOT THIS.", 5)

    def draw_results(self):
        art.panel(39, 48, 242, 153, 0, 8)
        art.big_text("GAME OVER", 62, 8)
        art.center_text(85, "NEW PERSONAL BEST!" if self.new_record else
                        "THE HOMEWORK CAN WAIT. TRY AGAIN.", 10 if self.new_record else 6)
        art.big_text(f"{self.score:05d}", 99, 7)
        seconds = self.frames // FPS
        art.center_text(122, f"TIME {seconds}s   DODGED {self.dodged}   NOTES {self.notes}", 6)
        art.center_text(139, f"BEST {self.data['best'][self.mode]:05d} / "
                        f"{MODES[self.mode]['name']}", 10)
        pyxel.rect(68, 155, 184, 20, 3)
        pyxel.rectb(68, 155, 184, 20, 11)
        art.center_text(162, "R / SPACE: TRY AGAIN", 7)
        art.center_text(185, "ENTER: MENU   Q: EXIT", 5)
        if not self.save_ok:
            art.center_text(204, "SAVE UNAVAILABLE - SCORE IS IN MEMORY", 8)


if __name__ == "__main__":
    game = Game()
    try:
        pyxel.run(game.update, game.draw)
    finally:
        game.persist()
