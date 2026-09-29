"""原创像素图形：使用 Pyxel 绘图接口，不需要下载素材。"""

import math

import pyxel

PALETTE = [
    0x0D1125, 0x18203D, 0x252B4D, 0x405079,
    0x805450, 0x7B7591, 0xBBC5D9, 0xFFF4DF,
    0xF27378, 0xF8AA6D, 0xFFDA88, 0x82DEC0,
    0x78B7EA, 0x5C68AC, 0xF4BEA1, 0xD8EBC8,
]

# 每个字符代表一个像素，十六进制数字对应调色板；点表示透明。
STUDENT = (
    "......0000......",
    ".....044440.....",
    "....04444440....",
    "....04444440....",
    "....0eeeeee0....",
    "....0e7ee7e0....",
    "....0eeeeee0....",
    ".....0eeee0.....",
    "....08888880....",
    "...0888988880...",
    "...0e888888e0...",
    "...0e888888e0...",
    "....08888880....",
    ".....066660.....",
    ".....066660.....",
)

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


def character(x, y, frame=0, moving=False, facing=1, scale=1):
    bob = int(moving and frame % 16 < 8)
    for row, pixels in enumerate(STUDENT):
        for col, pixel in enumerate(pixels):
            if pixel != ".":
                dx = col if facing >= 0 else 15 - col
                pyxel.rect(x + dx * scale, y + (row - bob) * scale,
                           scale, scale, int(pixel, 16))
    step = 2 if moving and frame % 16 < 8 else 0
    pyxel.rect(x + 5 * scale, y + 15 * scale, 2 * scale, 3 * scale, 3)
    pyxel.rect(x + 9 * scale, y + (15 - step) * scale,
               2 * scale, 3 * scale, 3)
    pyxel.rect(x + 3 * scale, y + 18 * scale, 4 * scale, 2 * scale, 0)
    pyxel.rect(x + 9 * scale, y + (18 - step) * scale,
               4 * scale, 2 * scale, 0)


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


def classroom(frame=0):
    pyxel.cls(1)
    pyxel.rect(0, 0, 320, 39, 0)
    pyxel.line(0, 38, 319, 38, 3)
    # 三扇夜色窗户，窗外是星星与远处楼房。
    for index, x in enumerate((16, 120, 224)):
        pyxel.rect(x - 3, 43, 86, 115, 0)
        pyxel.rect(x, 46, 80, 108, 2)
        for star in range(9):
            sx = x + 5 + (star * 17 + index * 7) % 68
            sy = 53 + (star * 13 + index * 11) % 68
            color = 6 if (frame // 45 + star) % 4 == 0 else 3
            pyxel.pset(sx, sy, color)
        for building in range(6):
            bx = x + building * 13
            bh = 12 + (building * 11 + index * 5) % 24
            pyxel.rect(bx, 154 - bh, 11, bh, 1)
            pyxel.pset(bx + 3, 158 - bh, 9)
            pyxel.pset(bx + 7, 164 - bh, 3)
        pyxel.rect(x + 38, 46, 3, 108, 3)
        pyxel.rect(x, 100, 80, 3, 3)
        pyxel.rect(x - 5, 154, 90, 4, 3)
    pyxel.circ(67, 69, 10, 6)
    pyxel.circ(71, 65, 9, 2)
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
    pyxel.line(0, 202, 319, 202, 6)
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
