"""游戏文本和随项目分发的简体中文字库。L 键随时切换语言。"""

from pathlib import Path

import pyxel

from game import art
from game.config import MODES
from game.progression import SKINS
from game.upgrades import UPGRADES

FONT_PATH = Path(__file__).resolve().parents[1] / "assets" / "fonts" / "NotoSansCJKsc-Game.otf"
FONT_SMALL = None
FONT_BIG = None

TEXT = {
    "club": ("午夜自习社", "MIDNIGHT STUDY CLUB"),
    "dodge": ("躲避作业", "DODGE HOMEWORK"),
    "goal": ("收集能力，击败期末院长！", "GET STRONG. BEAT THE DEAN!"),
    "start": ("空格 / 回车：开始", "SPACE / ENTER: START"),
    "wardrobe": ("C：换装", "C: WARDROBE"),
    "title_tip": ("S 换装  ·  3 高难 Boss", "S: OUTFIT / 3: HARD BOSS"),
    "demo_tip": ("展示模式：N 跳到下个节点", "DEMO: N SKIPS TO NEXT EVENT"),
    "language": ("L：中文 / English", "L: SWITCH LANGUAGE"),
    "loadout": ("考前备战 {current}/3", "EXAM LOADOUT {current}/3"),
    "upgrade": ("能力选择 {current}/3", "UPGRADE {current}/3"),
    "pick_one": ("选择一项", "PICK ONE"),
    "upgrade_controls": ("1/2/3 选择  ·  方向键+回车", "1/2/3 PICK  |  ARROWS + ENTER"),
    "back_menu": ("Esc：返回主菜单", "ESC: MAIN MENU"),
    "wardrobe_title": ("角色衣橱", "WARDROBE"),
    "demo_outfits": ("展示模式可预览全部外观", "DEMO: ALL OUTFITS AVAILABLE"),
    "earn_outfits": ("完成成就解锁外观", "EARN OUTFITS THROUGH ACHIEVEMENTS"),
    "preview": ("预览", "PREVIEW"),
    "owned": ("已拥有", "OWNED"),
    "locked": ("未解锁", "LOCKED"),
    "wardrobe_controls": ("1-4 预览  回车装备  C 返回", "1-4 PREVIEW  ENTER EQUIP  C BACK"),
    "dean": ("期末院长", "THE DEAN"),
    "boss_intro": ("三阶段决战 · 按住 Z 发射答案弹", "3 PHASES. HOLD Z TO ANSWER."),
    "boss_hard": ("高难考试：2 颗心 / 70 秒", "HARD EXAM: 2 HEARTS / 70 SECONDS"),
    "boss_normal": ("躲避、冲刺、反击！", "DODGE, DASH, AND FIGHT BACK."),
    "begin": ("回车：开始决战", "ENTER: BEGIN"),
    "paused": ("已暂停", "PAUSED"),
    "continue": ("P / Esc：继续", "P / ESC: CONTINUE"),
    "enter_menu": ("回车：主菜单", "ENTER: MAIN MENU"),
    "pause_line": ("喘口气，你做得到。", "TAKE A BREATH. YOU GOT THIS."),
    "cleared": ("通关成功！", "CLEARED!"),
    "game_over": ("挑战失败", "GAME OVER"),
    "demo_cleared": ("快速展示完成", "SHOWCASE COMPLETE"),
    "demo_failed": ("展示失败，再试一次", "SHOWCASE / TRY AGAIN"),
    "rank": ("考试通过 · {rank} 级", "EXAM PASSED / RANK {rank}"),
    "adventure_rank": ("冒险通关 · {rank} 级", "ADVENTURE CLEAR / RANK {rank}"),
    "hit_by_homework": ("生命值耗尽", "HIT BY HOMEWORK"),
    "time_up": ("考试时间已到", "EXAM TIME LIMIT REACHED"),
    "run_stats": ("{seconds}秒  躲避{dodged}  笔记{notes}",
                  "TIME {seconds}s  DODGED {dodged}  NOTES {notes}"),
    "build": ("能力：{build}", "BUILD: {build}"),
    "no_upgrades": ("无", "NO UPGRADES"),
    "unlocked": ("解锁：{skins}", "UNLOCKED: {skins}"),
    "all_outfits": ("展示模式已开放所有外观", "ALL OUTFITS AVAILABLE IN DEMO"),
    "best_mode": ("最高 {best:05d} · {mode}", "BEST {best:05d} / {mode}"),
    "try_again": ("R / 空格：再试一次", "R / SPACE: TRY AGAIN"),
    "result_win_controls": ("回车：结局  C：衣橱  Q：退出", "ENTER: ENDING  C: OUTFITS  Q: EXIT"),
    "result_lose_controls": ("回车：主菜单  C：衣橱  Q：退出", "ENTER: MENU  C: OUTFITS  Q: EXIT"),
    "save_failed": ("存档暂不可写，成绩仅保留在内存", "SAVE UNAVAILABLE - SCORE IS IN MEMORY"),
    "ending_title": ("黎明的毕业钟声", "THE BELL AT DAWN"),
    "ending_1": ("最后一张试卷落下，教室安静了。", "THE LAST PAPER FALLS. THE ROOM IS QUIET."),
    "ending_2": ("星奈收好笔记，推开通往清晨的门。", "SENA OPENS THE DOOR TO A NEW MORNING."),
    "ending_3": ("你通关了！下次试试更高难度吧。", "YOU MADE IT! TRY A HARDER EXAM NEXT."),
    "ending_demo": ("展示完成。正式冒险还有更多挑战。", "SHOWCASE DONE. THE FULL ADVENTURE AWAITS."),
    "ending_controls": ("回车：主菜单  R：再玩一次", "ENTER: MENU  R: PLAY AGAIN"),
    "score": ("得分", "SCORE"),
    "best": ("最高", "BEST"),
    "wave": ("第{wave}波", "WAVE {wave:02d}"),
    "phase": ("第{phase}阶段", "PHASE {phase}"),
    "boss_time": ("P{phase} 余{seconds}秒", "P{phase} {seconds}s"),
    "boss_eta": ("Boss 还有{seconds}秒", "BOSS IN {seconds}s"),
    "boss_next": ("即将决战", "BOSS NEXT"),
    "boss_name": ("院长 / {name}", "DEAN / {name}"),
    "dash": ("冲刺", "DASH"),
    "shield_on": ("护盾开启", "SHIELD ON"),
    "shield_off": ("无护盾", "NO SHIELD"),
    "hud_controls": ("A/D 移动  空格冲刺  Z 射击", "A/D MOVE  SPACE DASH  Z FIRE"),
    "pause_short": ("P 暂停", "P PAUSE"),
    "mute_on": ("M 静音", "M:OFF"),
    "mute_off": ("M 音乐", "M:ON"),
    "exit": ("Q 退出", "Q EXIT"),
    "dash_tip": ("空格冲刺可穿过作业", "SPACE: DASH THROUGH DANGER"),
    "boss_tip": ("按住 Z 向院长发射答案弹", "HOLD Z: ANSWER THE DEAN"),
    "wave_tip": ("截止时间越来越近了！", "DEADLINES ARE GETTING CLOSER!"),
    "upgrade_notice": ("获得能力：{name}", "UPGRADE: {name}"),
    "dash_score": ("冲刺 +10", "DASH +10"),
    "close_score": ("险避 +5", "CLOSE! +5"),
    "shield_label": ("获得护盾", "SHIELD ON"),
    "note_score": ("笔记 +25", "NOTE +25"),
    "shield_saved": ("护盾挡下了攻击", "SAVED BY SHIELD"),
}

UPGRADE_ZH = {
    "wind": ("疾风步", ("冲刺冷却", "缩短 25%", "更灵活")),
    "frost": ("冰霜步", ("冲刺时冻结", "附近作业", "约 0.4 秒")),
    "burst": ("护盾新星", ("护盾破裂时", "清除附近", "100 像素作业")),
    "magnet": ("笔记磁铁", ("自动吸引", "附近的笔记", "方便收集")),
    "recycle": ("作业回收", ("冲刺穿过作业", "将它们变成", "可收集笔记")),
    "focus": ("极限专注", ("仅剩一颗心时", "冲刺冷却", "再缩短 40%")),
    "answer": ("考试高手", ("答案弹伤害+1", "同时提升", "发射速度")),
}

SKIN_ZH = {
    "sena": ("星奈", "你的原创校园角色"),
    "mint": ("薄荷", "累计收集 25 份笔记解锁"),
    "luna": ("露娜", "完成冒险或考试解锁"),
    "crimson": ("绯红", "击败高难考试 Boss 解锁"),
}

MODE_ZH = {"arcade": "普通", "cozy": "轻松", "exam": "高难", "demo": "展示"}
PHASE_ZH = ("点名", "寻找空隙", "最终交卷")


def init_fonts():
    global FONT_SMALL, FONT_BIG
    FONT_SMALL = pyxel.Font(str(FONT_PATH), 10)
    FONT_BIG = pyxel.Font(str(FONT_PATH), 18)


def tr(language, key, **values):
    return TEXT[key][0 if language == "zh" else 1].format(**values)


def mode_name(language, mode):
    return MODE_ZH[mode] if language == "zh" else MODES[mode]["name"]


def upgrade_name(language, key):
    return UPGRADE_ZH[key][0] if language == "zh" else UPGRADES[key].name


def upgrade_lines(language, key):
    return UPGRADE_ZH[key][1] if language == "zh" else UPGRADES[key].lines


def upgrade_tag(language, key):
    return UPGRADE_ZH[key][0] if language == "zh" else UPGRADES[key].tag


def skin_name(language, key):
    return SKIN_ZH[key][0] if language == "zh" else SKINS[key]["name"]


def skin_hint(language, key):
    return SKIN_ZH[key][1] if language == "zh" else SKINS[key]["hint"]


def phase_name(language, boss):
    return PHASE_ZH[boss.phase - 1] if language == "zh" else boss.name


def width(language, message, big=False):
    if language == "zh":
        return (FONT_BIG if big else FONT_SMALL).text_width(message)
    return (len(message) * 12 - 2) if big else len(message) * 4


def text(x, y, message, color, language):
    if language == "zh":
        pyxel.text(x, y, message, color, FONT_SMALL)
    else:
        pyxel.text(x, y, message, color)


def center(y, message, color, language, x=160):
    if language == "zh":
        pyxel.text(x - FONT_SMALL.text_width(message) // 2, y, message, color, FONT_SMALL)
    else:
        art.center_text(y, message, color, x)


def big(y, message, color, language, x=160):
    if language == "zh":
        pyxel.text(x - FONT_BIG.text_width(message) // 2 + 1, y + 1, message, 0, FONT_BIG)
        pyxel.text(x - FONT_BIG.text_width(message) // 2, y, message, color, FONT_BIG)
    else:
        art.big_text(message, y, color, center=x)
