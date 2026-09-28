"""第 2 课：从一份作业开始，亲手改成随机作业雨。"""

import pyxel

# ===== 沿用你完成的第一课 =====
MOVE_SPEED = 4
PLAYER_COLOR = 8
PLAYER_SIZE = 12

# ===== 本课的三个练习开关 =====
DROP_SPEED = 2          # 每帧向下移动多少像素
RANDOM_SPAWN = False    # 练习 1：改成 True，让作业从随机位置出现
MAX_HOMEWORK = 1        # 练习 2：改成 5，让多份作业同时存在
SPAWN_INTERVAL = 45     # 练习 3：改成 20，让作业出现得更频繁

WIDTH = 160
HEIGHT = 120
GROUND_Y = 100
FPS = 30
HOMEWORK_SIZE = 8
player_x = (WIDTH - PLAYER_SIZE) // 2
homeworks = []          # 列表：保存画面中所有作业
spawn_timer = 0


def spawn_homework():
    """字典保存一份作业的 x、y；append 把它加入列表。"""
    if RANDOM_SPAWN:
        x = pyxel.rndi(0, WIDTH - HOMEWORK_SIZE)
    else:
        x = (WIDTH - HOMEWORK_SIZE) // 2

    homeworks.append({"x": x, "y": -HOMEWORK_SIZE})


def update():
    global player_x, spawn_timer

    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()
        return

    if pyxel.btn(pyxel.KEY_LEFT):
        player_x -= MOVE_SPEED
    if pyxel.btn(pyxel.KEY_RIGHT):
        player_x += MOVE_SPEED
    player_x = max(0, min(player_x, WIDTH - PLAYER_SIZE))

    # 每过 SPAWN_INTERVAL 帧，尝试生成一份新作业。
    spawn_timer += 1
    if spawn_timer >= SPAWN_INTERVAL:
        spawn_timer = 0
        if len(homeworks) < MAX_HOMEWORK:
            spawn_homework()

    # for 循环让每一份作业都向下移动。
    # [:] 复制列表，避免删除元素时跳过下一份作业。
    for homework in homeworks[:]:
        homework["y"] += DROP_SPEED
        if homework["y"] >= HEIGHT:
            homeworks.remove(homework)


def draw():
    pyxel.cls(1)
    pyxel.line(0, GROUND_Y, WIDTH - 1, GROUND_Y, 5)
    pyxel.rect(
        player_x, GROUND_Y - PLAYER_SIZE,
        PLAYER_SIZE, PLAYER_SIZE, PLAYER_COLOR,
    )

    for homework in homeworks:
        pyxel.rect(
            homework["x"], homework["y"],
            HOMEWORK_SIZE, HOMEWORK_SIZE, 10,
        )

    # 最后画文字栏，让掉落的作业不遮住说明。
    pyxel.rect(0, 0, WIDTH, 30, 1)
    pyxel.text(8, 6, "LESSON 02: HOMEWORK RAIN", 7)
    pyxel.text(8, 18, f"PAPERS: {len(homeworks)}  SPEED: {DROP_SPEED}", 6)
    pyxel.rect(0, 106, WIDTH, 14, 1)
    pyxel.text(8, 110, "LEFT / RIGHT: MOVE   Q: QUIT", 6)


if __name__ == "__main__":
    pyxel.init(WIDTH, HEIGHT, title="Dodge Homework - Lesson 02", fps=FPS)
    pyxel.run(update, draw)
