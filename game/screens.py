"""菜单、能力卡、衣橱、结算和通关后日谈。"""

import math
import pyxel

from game import art, i18n
from game.config import FPS
from game.progression import SKINS
from game.upgrades import UPGRADES


def t(game, key, **values):
    return i18n.tr(game.language, key, **values)


def center(game, y, key, color=7, x=160, **values):
    i18n.center(y, t(game, key, **values), color, game.language, x)


def dim():
    pyxel.dither(0.8)
    pyxel.rect(0, 38, 320, 170, 0)
    pyxel.dither(1)


def title(game):
    art.panel(28, 39, 264, 176, 0, 13)
    center(game, 48, "club", 11)
    i18n.big(64, t(game, "dodge"), 7, game.language)
    center(game, 93, "goal", 10)
    pyxel.line(47, 108, 272, 108, 3)
    art.character(56, 131 + math.sin(game.visual_frames / 25),
                  game.visual_frames, True, scale=2, skin=game.skin)
    for index, mode in enumerate(("arcade", "cozy", "exam", "demo")):
        x = 113 + (index % 2) * 81
        y = 112 + (index // 2) * 24
        selected = game.mode == mode
        pyxel.rect(x, y, 75, 20, 3 if selected else 1)
        pyxel.rectb(x, y, 75, 20, 11 if selected else 3)
        key = str(index + 1) if index < 3 else "D"
        i18n.center(y + (5 if game.language == "zh" else 7),
                    f"{key} {i18n.mode_name(game.language, mode)}",
                    7 if selected else 6, game.language, x + 37)
    center(game, 165, "start", 10, 192)
    center(game, 180, "wardrobe", 6, 192)
    i18n.center(180, i18n.skin_name(game.language, game.skin), 11, game.language, 72)
    center(game, 191, "demo_tip" if game.mode == "demo" else "title_tip", 6)
    center(game, 204, "language", 11)


def upgrade(game):
    dim()
    center(game, 43, "loadout" if game.loadout else "upgrade", 11,
           current=len(game.skills) + 1)
    i18n.big(55, t(game, "pick_one"), 7, game.language)
    for index, key in enumerate(game.upgrade_cards):
        card = UPGRADES[key]
        x = 10 + index * 103
        selected = index == game.card_focus
        art.panel(x, 78, 94, 105, 1, card.color if selected else 3)
        pyxel.rect(x + 5, 83, 12, 12, card.color)
        pyxel.text(x + 9, 86, str(index + 1), 0)
        pyxel.circ(x + 47, 108, 10, 0)
        art.big_text(card.tag[0], 105, card.color, scale=1, center=x + 47)
        i18n.center(124, i18n.upgrade_name(game.language, key), card.color,
                    game.language, x + 47)
        for row, line in enumerate(i18n.upgrade_lines(game.language, key)):
            i18n.center(141 + row * 12, line, 7, game.language, x + 47)
    center(game, 192, "upgrade_controls", 6)
    center(game, 204, "back_menu", 5)


def wardrobe(game):
    dim()
    i18n.big(47, t(game, "wardrobe_title"), 11, game.language)
    center(game, 67, "demo_outfits" if game.mode == "demo" else "earn_outfits", 6)
    for index, (key, skin) in enumerate(SKINS.items()):
        x = 19 + index * 72
        selected = game.wardrobe_focus == index
        available = key in game.data["owned"] or game.mode == "demo"
        art.panel(x, 78, 67, 106, 1, 11 if selected else 3)
        i18n.center(85, f"{index + 1} {i18n.skin_name(game.language, key)}",
                    7 if available else 5, game.language, x + 33)
        center(game, 101, "preview" if game.mode == "demo" else
               "owned" if available else "locked", 11 if available else 8, x + 33)
        art.character(x + 18, 140, game.visual_frames, False, scale=2, skin=key)
    key = list(SKINS)[game.wardrobe_focus]
    i18n.center(190, i18n.skin_hint(game.language, key), 10, game.language)
    center(game, 204, "wardrobe_controls", 6)


def boss_intro(game):
    art.panel(32, 110, 256, 82, 0, 8)
    i18n.big(120, t(game, "dean"), 8, game.language)
    center(game, 146, "boss_intro", 7)
    center(game, 164, "boss_hard" if game.mode == "exam" else "boss_normal", 10)
    center(game, 179, "begin", 5)


def pause(game):
    dim()
    art.panel(57, 65, 206, 112, 0, 11)
    i18n.big(77, t(game, "paused"), 11, game.language)
    center(game, 105, "continue", 7)
    center(game, 122, "enter_menu", 6)
    center(game, 141, "pause_line", 5)
    center(game, 158, "language", 11)


def results(game):
    won = game.state == "victory"
    art.panel(26, 45, 268, 160, 0, 11 if won else 8)
    i18n.big(55, t(game, "cleared" if won else "game_over"),
             11 if won else 8, game.language)
    if game.mode == "demo":
        subtitle = t(game, "demo_cleared" if won else "demo_failed")
    elif won:
        rank = "S" if game.lives == game.max_lives else "A" if game.lives >= 2 else "B"
        subtitle = t(game, "rank" if game.mode == "exam" else "adventure_rank", rank=rank)
    else:
        subtitle = t(game, game.failure_reason)
    i18n.center(79, subtitle, 10, game.language)
    art.big_text(f"{game.score:05d}", 94, 7)
    center(game, 114, "run_stats", 6, seconds=game.frames // FPS,
           dodged=game.dodged, notes=game.notes)
    build = " / ".join(i18n.upgrade_tag(game.language, key) for key in game.skills)
    center(game, 128, "build", 12, build=build or t(game, "no_upgrades"))
    if game.new_unlocks:
        names = "、".join(i18n.skin_name(game.language, key) for key in game.new_unlocks)
        center(game, 143, "unlocked", 11, skins=names)
    elif game.mode == "demo":
        center(game, 143, "all_outfits", 10)
    else:
        center(game, 143, "best_mode", 10,
               best=game.data["best"].get(game.mode, 0),
               mode=i18n.mode_name(game.language, game.mode))
    pyxel.rect(68, 157, 184, 18, 3)
    pyxel.rectb(68, 157, 184, 18, 11)
    center(game, 161 if game.language == "zh" else 163, "try_again", 7)
    center(game, 186, "result_win_controls" if won else "result_lose_controls", 5)
    if not game.save_ok:
        center(game, 207, "save_failed", 8)


def ending(game):
    dim()
    art.panel(24, 45, 272, 160, 0, 11)
    i18n.big(55, t(game, "ending_title"), 11, game.language)
    pyxel.line(48, 81, 272, 81, 3)
    art.character(40, 104 + math.sin(game.visual_frames / 20),
                  game.visual_frames, True, scale=2, skin=game.skin)
    if game.mode == "demo":
        center(game, 111, "ending_demo", 7, 198)
    else:
        center(game, 95, "ending_1", 7, 198)
        center(game, 117, "ending_2", 10, 198)
        center(game, 139, "ending_3", 11, 198)
    center(game, 181, "ending_controls", 6)
