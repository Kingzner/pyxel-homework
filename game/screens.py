"""菜单、能力卡、衣橱与结算画面；不处理游戏中的碰撞。"""

import math
import pyxel

from game import art
from game.config import MODES
from game.progression import SKINS
from game.upgrades import UPGRADES


def dim():
    pyxel.dither(0.8)
    pyxel.rect(0, 38, 320, 170, 0)
    pyxel.dither(1)


def title(game):
    art.panel(28, 43, 264, 158, 0, 13)
    art.center_text(53, "MIDNIGHT STUDY CLUB", 11)
    art.big_text("DODGE", 66, 7)
    art.big_text("HOMEWORK", 85, 10)
    pyxel.line(47, 107, 272, 107, 3)
    art.character(56, 140 + math.sin(game.visual_frames / 25),
                  game.visual_frames, True, scale=2, skin=game.skin)
    for index, mode in enumerate(("arcade", "cozy", "exam", "demo")):
        x = 113 + (index % 2) * 81
        y = 114 + (index // 2) * 24
        selected = game.mode == mode
        pyxel.rect(x, y, 75, 20, 3 if selected else 1)
        pyxel.rectb(x, y, 75, 20, 11 if selected else 3)
        key = str(index + 1) if index < 3 else "D"
        art.center_text(y + 7, f"{key} {MODES[mode]['name']}",
                        7 if selected else 6, x + 37)
    art.center_text(169, "SPACE TO START", 10, 192)
    art.center_text(185, "C: WARDROBE", 6, 192)
    art.center_text(185, SKINS[game.skin]["name"], 11, 72)
    art.center_text(204, "DEMO: N SKIPS TO THE NEXT EVENT" if game.mode == "demo" else
                    "S: CYCLE OUTFIT / 3: HARD BOSS", 6)


def upgrade(game):
    dim()
    art.center_text(43, f"{'EXAM LOADOUT' if game.loadout else 'UPGRADE'} "
                    f"{len(game.skills) + 1}/3", 11)
    art.big_text("PICK ONE", 55, 7)
    for index, key in enumerate(game.upgrade_cards):
        card = UPGRADES[key]
        x = 10 + index * 103
        selected = index == game.card_focus
        art.panel(x, 78, 94, 105, 1, card.color if selected else 3)
        pyxel.rect(x + 5, 83, 12, 12, card.color)
        pyxel.text(x + 9, 86, str(index + 1), 0)
        pyxel.circ(x + 47, 108, 10, 0)
        art.big_text(card.tag[0], 105, card.color, scale=1, center=x + 47)
        art.center_text(125, card.name, card.color, x + 47)
        for row, line in enumerate(card.lines):
            art.center_text(143 + row * 11, line, 7, x + 47)
    art.center_text(194, "1/2/3: PICK  |  ARROWS + ENTER", 6)
    art.center_text(204, "ESC: MAIN MENU", 5)


def wardrobe(game):
    dim()
    art.big_text("WARDROBE", 47, 11)
    art.center_text(67, "DEMO: ALL OUTFITS AVAILABLE" if game.mode == "demo" else
                    "EARN OUTFITS THROUGH ACHIEVEMENTS", 6)
    for index, (key, skin) in enumerate(SKINS.items()):
        x = 19 + index * 72
        selected = game.wardrobe_focus == index
        available = key in game.data["owned"] or game.mode == "demo"
        art.panel(x, 78, 67, 106, 1, 11 if selected else 3)
        art.center_text(85, f"{index + 1} {skin['name']}", 7 if available else 5, x + 33)
        art.center_text(99, "PREVIEW" if game.mode == "demo" else
                        "OWNED" if available else "LOCKED", 11 if available else 8, x + 33)
        art.character(x + 18, 140, game.visual_frames, False, scale=2, skin=key)
    key = list(SKINS)[game.wardrobe_focus]
    art.center_text(190, SKINS[key]["hint"], 10)
    art.center_text(204, "1-4: PREVIEW  ENTER: EQUIP  C: BACK", 6)


def boss_intro(game):
    art.panel(32, 112, 256, 77, 0, 8)
    art.big_text("THE DEAN", 123, 8)
    art.center_text(148, "3 PHASES. HOLD Z TO ANSWER.", 7)
    art.center_text(163, "HARD EXAM: 2 HEARTS / 70 SECONDS" if game.mode == "exam" else
                    "DODGE, DASH, AND FIGHT BACK.", 10)
    art.center_text(178, "ENTER: BEGIN", 5)


def pause(game):
    dim()
    art.panel(57, 67, 206, 106, 0, 11)
    art.big_text("PAUSED", 81, 11)
    art.center_text(109, "P / ESC: CONTINUE", 7)
    art.center_text(125, "ENTER: MAIN MENU", 6)
    art.center_text(145, "TAKE A BREATH. YOU GOT THIS.", 5)


def results(game):
    won = game.state == "victory"
    art.panel(26, 46, 268, 158, 0, 11 if won else 8)
    art.big_text("CLEARED!" if won else "GAME OVER", 57, 11 if won else 8)
    if game.mode == "demo":
        subtitle = "SHOWCASE COMPLETE" if won else "SHOWCASE / TRY AGAIN"
    elif won:
        rank = "S" if game.lives == game.max_lives else "A" if game.lives >= 2 else "B"
        subtitle = f"EXAM PASSED / RANK {rank}"
    else:
        subtitle = game.failure_reason
    art.center_text(79, subtitle, 10)
    art.big_text(f"{game.score:05d}", 92, 7)
    art.center_text(114, f"TIME {game.frames // FPS}s  DODGED {game.dodged}  NOTES {game.notes}", 6)
    build = " / ".join(UPGRADES[key].tag for key in game.skills) or "NO UPGRADES"
    art.center_text(128, f"BUILD: {build}", 12)
    if game.new_unlocks:
        text = "UNLOCKED: " + ", ".join(SKINS[key]["name"] for key in game.new_unlocks)
        art.center_text(143, text, 11)
    else:
        best = game.data["best"].get(game.mode, 0)
        art.center_text(143, "ALL OUTFITS AVAILABLE IN DEMO" if game.mode == "demo" else
                        f"BEST {best:05d} / {MODES[game.mode]['name']}", 10)
    pyxel.rect(68, 156, 184, 18, 3)
    pyxel.rectb(68, 156, 184, 18, 11)
    art.center_text(162, "R / SPACE: TRY AGAIN", 7)
    art.center_text(186, "C: WARDROBE  ENTER: MENU  Q: EXIT", 5)
    if not game.save_ok:
        art.center_text(205, "SAVE UNAVAILABLE - SCORE IS IN MEMORY", 8)
