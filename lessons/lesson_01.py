"""第 1 课：让角色左右移动。先修改下面的三个参数。"""

import pyxel

# ===== 你可以动手修改的三个参数 =====
MOVE_SPEED = 4      # 每一帧移动多少像素；练习 1：改成 4
PLAYER_COLOR = 8   # 角色颜色，取值 0～15；练习 2：改成 8
PLAYER_SIZE = 12      # 角色的边长；练习 3：改成 12

# ===== 游戏画面 =====
WIDTH = 160
HEIGHT = 120
GROUND_Y = 100
player_x = (WIDTH - PLAYER_SIZE) // 2


def update():
    """处理按键，并更新角色的位置。"""
    global player_x  # 允许这个函数修改外面的 player_x 变量

    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

    # 按住左键，x 变小；按住右键，x 变大。
    if pyxel.btn(pyxel.KEY_LEFT):
        player_x -= MOVE_SPEED
    if pyxel.btn(pyxel.KEY_RIGHT):
        player_x += MOVE_SPEED

    # 把整个角色留在屏幕内。右边界需要考虑角色的宽度。
    if player_x < 0:
        player_x = 0
    if player_x > WIDTH - PLAYER_SIZE:
        player_x = WIDTH - PLAYER_SIZE


def draw():
    """根据当前的位置，把画面重新画出来。"""
    pyxel.cls(1)
    pyxel.text(8, 8, "DODGE HOMEWORK", 7)
    pyxel.text(8, 20, "LESSON 01: MOVE", 6)
    pyxel.text(8, 36, f"X: {player_x}  SPEED: {MOVE_SPEED}", 7)
    pyxel.line(0, GROUND_Y, WIDTH - 1, GROUND_Y, 5)
    pyxel.rect(
        player_x, GROUND_Y - PLAYER_SIZE,
        PLAYER_SIZE, PLAYER_SIZE, PLAYER_COLOR,
    )
    pyxel.text(8, 110, "LEFT / RIGHT: MOVE   Q: QUIT", 6)


if __name__ == "__main__":
    pyxel.init(WIDTH, HEIGHT, title="Dodge Homework - Lesson 01", fps=30)
    pyxel.run(update, draw)
