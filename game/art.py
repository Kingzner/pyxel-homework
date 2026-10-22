"""原创像素图形：使用 Pyxel 绘图接口，不需要下载素材。"""

import math

import pyxel

PALETTE = [
    0x0D1125, 0x18203D, 0x252B4D, 0x405079,
    0x805450, 0x7B7591, 0xBBC5D9, 0xFFF4DF,
    0xF27378, 0xF8AA6D, 0xFFDA88, 0x82DEC0,
    0x78B7EA, 0x5C68AC, 0xF4BEA1, 0xD8EBC8,
]

# 星奈 SENA：原创 Q 版校园少女。每个字符是一格像素。
# 16 像素宽的身体，加上两侧发尾，最终组成 24 × 32 的角色。
# 十六进制数字对应调色板，点表示透明。
STUDENT = (
    ".....000000.....",
    "...00dddddd00...",
    "..0ddccccdddd0..",
    ".0ddccccdddddd0.",
    ".0ddcddddddddd0.",
    "0ddddeeeeeddddd0",
    "0dddeeeeeeeeddd0",
    "0dde00eeee00edd0",
    "0dde7ceeee7cedd0",
    "0ddec0eeeec0edd0",
    "0ddecceeeeccedd0",
    "0ddee8eeee8eedd0",
    ".0ddeee88eeedd0.",
    "..0ddeeeeeedd0..",
    "...00eeeeee00...",
    ".....077770.....",
    "....07777770....",
    "...0773773770...",
    "...0777337770...",
    "...0777887770...",
    "..0e77788777e0..",
    "..0e77788777e0..",
    "...0e777777e0...",
    "....0dddddd0....",
    "...0ddcddcdd0...",
    "..0ddcddddcdd0..",
    "..000000000000..",
    ".....ee..ee.....",
    ".....ee..ee.....",
    ".....33..33.....",
    ".....77..77.....",
    "....000..000....",
)

PIGTAIL = (
    "0880", "0880", "0dd0", "0dc0", "0dc0", "0dc0",
    "0dd0", "0dd0", "0dc0", "0dc0", "0dc0", "0dd0",
    "0dd0", "0dd0", "0dd0", "0dd0", ".0d0", ".0d0", "..00",
)

SKIN_COLORS = {
    "sena": {},
    "mint": {"d": "3", "c": "b", "8": "9", "7": "f"},
    "luna": {"d": "6", "c": "7", "7": "2", "8": "b"},
    "crimson": {"d": "8", "c": "e", "7": "0", "8": "a"},
}

# 5 × 7 字体，用于标题。普通说明继续使用 Pyxel 自带的小字体。
GLYPHS = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 14),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (31, 4, 4, 4, 4, 4, 31),
    "J": (7, 2, 2, 2, 18, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 21, 10),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 2, 4, 8, 31),
    "3": (30, 1, 1, 14, 1, 1, 30),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 16, 30, 1, 1, 30),
    "6": (14, 16, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 1, 14),
    " ": (0, 0, 0, 0, 0, 0, 0),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "-": (0, 0, 0, 31, 0, 0, 0),
    ":": (0, 4, 4, 0, 4, 4, 0),
    ".": (0, 0, 0, 0, 0, 0, 4),
    "/": (1, 1, 2, 4, 8, 16, 16),
    "+": (0, 4, 4, 31, 4, 4, 0),
}


def center_text(y, text, color=7, center=160):
    pyxel.text(center - len(text) * 2, y, text, color)


def big_text(text, y, color=7, scale=2, center=160, shadow=True):
    text = text.upper()
    x = center - (len(text) * 6 - 1) * scale // 2
    if shadow:
        _glyphs(text, x + scale, y + scale, 0, scale)
    _glyphs(text, x, y, color, scale)


def _glyphs(text, x, y, color, scale):
    for index, char in enumerate(text):
        for row, bits in enumerate(GLYPHS.get(char, GLYPHS[" "])):
            for col in range(5):
                if bits & (1 << (4 - col)):
                    pyxel.rect(x + (index * 6 + col) * scale,
                               y + row * scale, scale, scale, color)


def panel(x, y, width, height, color=0, border=3):
    pyxel.rect(x + 3, y + 4, width, height, 0)
    pyxel.rect(x, y, width, height, color)
    pyxel.rectb(x, y, width, height, border)
    pyxel.pset(x + 1, y + 1, 6)
    pyxel.pset(x + width - 2, y + 1, 6)


def character_pixels(frame=0, moving=False, facing=1, expression="normal", skin="sena"):
    """合成一帧像素，用同一份数据绘制游戏角色和放大预览。"""
    canvas = [["."] * 24 for _ in range(32)]
    sway = int((frame // (10 if moving else 45)) % 2 == 1)
    # 发尾是独立一层：末端轻轻内摆，移动时再上下摆动一格。
    for side in (0, 20):
        for row, strip in enumerate(PIGTAIL):
            inward = sway if row > 7 else 0
            offset = inward if side == 0 else -inward
            ty = 4 + row + int(moving and row > 8 and frame % 12 < 6)
            for col, pixel in enumerate(strip):
                if pixel != ".":
                    canvas[ty][side + col + offset] = pixel
    for row, strip in enumerate(STUDENT):
        for col, pixel in enumerate(strip):
            if pixel != ".":
                # 身体位于两条发尾之间。
                canvas[row][col + 4] = pixel

    # 只重画小腿和鞋子；裙摆与上半身使用同一张基础图。
    for row in range(27, 32):
        for col in range(8, 16):
            canvas[row][col] = "."
    phase = (frame // 6) % 4
    legs = (
        (9 - int(moving and phase == 1), int(moving and phase < 2)),
        (13 + int(moving and phase == 3), int(moving and phase >= 2)),
    )
    for x, lift in legs:
        for row in range(27, 31 - lift):
            color = ("e", "e", "3", "7")[row - 27]
            canvas[row][x] = canvas[row][x + 1] = color
        for col in range(x - 1, x + 2):
            canvas[31 - lift][col] = "0"

    blink = not moving and 166 <= frame % 180 < 175
    if blink or expression == "hurt":
        for x in (8, 14):
            for row in range(7, 11):
                canvas[row][x] = canvas[row][x + 1] = "e"
            canvas[9][x] = canvas[9][x + 1] = "0"
    elif expression == "dash":
        for x in (8, 14):
            canvas[7][x] = "d"
            canvas[8][x + 1] = "0"

    if facing < 0:
        canvas = [row[::-1] for row in canvas]
    colors = SKIN_COLORS.get(skin, {})
    for y, row in enumerate(canvas):
        for x, pixel in enumerate(row):
            face = 4 <= x < 20 and 5 <= y <= 14
            if face and pixel in ("e", "8", "7"):
                continue
            if face and pixel == "c":
                canvas[y][x] = {"mint": "b", "luna": "d", "crimson": "8"}.get(skin, "c")
            else:
                canvas[y][x] = colors.get(pixel, pixel)
    return tuple("".join(row) for row in canvas)


def character(x, y, frame=0, moving=False, facing=1, scale=1, expression="normal", skin="sena"):
    # x、y 仍使用原有 16 × 20 的角色定位。较大的头发、脸部向上扩展。
    # 角色脚底对齐地面；玩法中的身体碰撞区域由 main.py 单独决定。
    origin_x = x - 4 * scale
    bob = int(moving and frame % 12 < 6)
    origin_y = y - (12 + bob) * scale
    for row, strip in enumerate(character_pixels(frame, moving, facing, expression, skin)):
        for col, pixel in enumerate(strip):
            if pixel != ".":
                pyxel.rect(origin_x + col * scale, origin_y + row * scale,
                           scale, scale, int(pixel, 16))


def heart(x, y, filled=True):
    color = 8 if filled else 3
    pyxel.rect(x + 1, y, 3, 3, color)
    pyxel.rect(x + 6, y, 3, 3, color)
    pyxel.rect(x, y + 2, 10, 3, color)
    pyxel.rect(x + 1, y + 5, 8, 2, color)
    pyxel.rect(x + 3, y + 7, 4, 2, color)
    pyxel.rect(x + 4, y + 9, 2, 1, color)
    if filled:
        pyxel.pset(x + 2, y + 1, 14)


def paper(x, y, width=12, height=15, exam=False):
    pyxel.rect(x + 2, y + 2, width, height, 0)
    pyxel.rect(x, y, width, height, 7)
    pyxel.rect(x, y, width, 3, 8 if exam else 12)
    pyxel.tri(x + width - 4, y, x + width - 1, y,
              x + width - 1, y + 3, 6)
    for row in range(5, height - 2, 3):
        pyxel.line(x + 2, y + row, x + width - 3, y + row, 5)
    if exam:
        pyxel.text(x + 2, y + 5, "F", 8)


def pickup(x, y, kind, frame=0):
    if kind == "shield":
        pyxel.circ(x + 6, y + 7, 8, 0)
        pyxel.tri(x + 1, y + 1, x + 11, y + 1, x + 6, y + 12, 11)
        pyxel.rect(x + 2, y + 1, 9, 5, 11)
        pyxel.rect(x + 5, y + 3, 2, 5, 7)
        pyxel.rect(x + 3, y + 5, 6, 2, 7)
    else:
        color = 10 if frame % 20 < 10 else 9
        pyxel.circ(x + 5, y + 5, 6, 0)
        pyxel.circ(x + 5, y + 5, 4, color)
        pyxel.line(x + 5, y + 2, x + 5, y + 7, 7)
        pyxel.pset(x + 3, y + 6, 7)


def classroom(frame=0, mood="night"):
    sky = 4 if mood == "dawn" else 0 if mood == "boss" else 2
    accent = 9 if mood == "dawn" else 8 if mood == "boss" else 6
    pyxel.cls(1)
    pyxel.rect(0, 0, 320, 39, 0)
    pyxel.line(0, 38, 319, 38, 3)
    # 三扇夜色窗户，窗外是星星与远处楼房。
    for index, x in enumerate((16, 120, 224)):
        pyxel.rect(x - 3, 43, 86, 115, 0)
        pyxel.rect(x, 46, 80, 108, sky)
        for star in range(9):
            sx = x + 5 + (star * 17 + index * 7) % 68
            sy = 53 + (star * 13 + index * 11) % 68
            if mood != "dawn":
                color = accent if (frame // 45 + star) % 4 == 0 else 3
                pyxel.pset(sx, sy, color)
        for building in range(6):
            bx = x + building * 13
            bh = 12 + (building * 11 + index * 5) % 24
            pyxel.rect(bx, 154 - bh, 11, bh, 2 if mood == "dawn" else 1)
            pyxel.pset(bx + 3, 158 - bh, 9)
            pyxel.pset(bx + 7, 164 - bh, 3)
        pyxel.rect(x + 38, 46, 3, 108, 3)
        pyxel.rect(x, 100, 80, 3, 3)
        pyxel.rect(x - 5, 154, 90, 4, 3)
    pyxel.circ(67, 69, 10, accent)
    if mood == "night":
        pyxel.circ(71, 65, 9, sky)
    elif mood == "boss":
        pyxel.circb(67, 69, 13 + (frame // 12) % 2, 8)
    else:
        for dx, dy in ((-16, 0), (16, 0), (0, -16), (0, 16)):
            pyxel.line(67 + dx // 2, 69 + dy // 2, 67 + dx, 69 + dy, 10)
    # 书架与暖色书脊。
    pyxel.rect(0, 169, 320, 24, 0)
    for index in range(40):
        x = index * 8 + 2
        height = 12 + (index * 3) % 7
        color = (3, 4, 5, 13)[index % 4]
        pyxel.rect(x, 190 - height, 5, height, color)
        pyxel.line(x + 1, 193 - height, x + 3, 193 - height, 6)
    pyxel.rect(0, 190, 320, 4, 4)
    pyxel.rect(0, 194, 320, 8, 2)
    pyxel.rect(0, 202, 320, 21, 2)
    pyxel.line(0, 202, 319, 202, accent)
    for x in range(0, 320, 32):
        pyxel.line(x, 204, x - 8, 222, 3)
    pyxel.line(0, 213, 319, 213, 3)
    pyxel.rect(0, 223, 320, 17, 0)
    pyxel.line(0, 223, 319, 223, 3)


def shield_ring(x, y, frame):
    radius = 15 + math.sin(frame / 8) * 0.7
    pyxel.circb(x + 8, y + 10, radius, 11)
    pyxel.pset(x + 19, y, 7)
    pyxel.pset(x - 4, y + 17, 7)


def dean(center, y, frame=0, flash=False, chinese_font=None):
    """原创 Boss：戴眼镜、拿试卷的期末院长。"""
    x = center - 24
    bob = math.sin(frame / 16) * 2
    y += bob
    pyxel.rect(x + 2, y + 5, 44, 34, 0)
    pyxel.rect(x + 9, y + 1, 30, 6, 6)
    pyxel.rect(x + 7, y + 5, 34, 8, 7 if flash else 5)
    pyxel.rect(x + 12, y + 12, 24, 13, 14)
    pyxel.rect(x + 10, y + 13, 12, 7, 0)
    pyxel.rect(x + 26, y + 13, 12, 7, 0)
    pyxel.rect(x + 12, y + 15, 8, 3, 12)
    pyxel.rect(x + 28, y + 15, 8, 3, 12)
    pyxel.line(x + 22, y + 16, x + 26, y + 16, 0)
    pyxel.rect(x + 21, y + 22, 6, 2, 8)
    pyxel.rect(x + 7, y + 27, 34, 13, 7 if flash else 13)
    pyxel.tri(x + 12, y + 27, x + 24, y + 27, x + 21, y + 34, 7)
    pyxel.tri(x + 24, y + 27, x + 36, y + 27, x + 27, y + 34, 7)
    pyxel.rect(x + 23, y + 31, 3, 8, 8)
    pyxel.rect(x - 3, y + 35, 55, 12, 0)
    pyxel.rect(x - 1, y + 34, 51, 10, 7)
    pyxel.line(x + 24, y + 34, x + 24, y + 43, 5)
    if chinese_font:
        pyxel.text(x + 2, y + 34, "期末", 8, chinese_font)
        pyxel.text(x + 27, y + 34, "考试", 8, chinese_font)
    else:
        pyxel.text(x + 3, y + 36, "FINAL", 8)
        pyxel.text(x + 29, y + 36, "EXAM", 8)
