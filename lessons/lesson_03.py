"""第 3 课：碰撞、存活计分，以及重新开始。"""

import pyxel

# ===== 你已经会调整的参数 =====
MOVE_SPEED = 4
PLAYER_COLOR = 8
PLAYER_SIZE = 12
DROP_SPEED = 2
SPAWN_INTERVAL = 45
SCORE_PER_SECOND = 1    # 练习：改成 10，改变每秒获得的分数

WIDTH = 160
HEIGHT = 120
GROUND_Y = 100
FPS = 30
HOMEWORK_SIZE = 8
player_x = (WIDTH - PLAYER_SIZE) // 2
homeworks = []
play_frames = 0
state = "ready"         # ready：等待开始；playing：游戏中；game_over：结束


def start_game():
    """第一次开始和 R 键重开，都使用同一套初始化。"""
    global player_x, homeworks, play_frames, state
    player_x = (WIDTH - PLAYER_SIZE) // 2
    homeworks = []
    play_frames = 0
    state = "playing"


def is_collision(homework):
    """两个方块在左右方向、上下方向都重叠，才算撞到。"""
    player_y = GROUND_Y - PLAYER_SIZE
    return (
        player_x < homework["x"] + HOMEWORK_SIZE
        and player_x + PLAYER_SIZE > homework["x"]
        and player_y < homework["y"] + HOMEWORK_SIZE
        and player_y + PLAYER_SIZE > homework["y"]
    )


def update():
    global player_x, play_frames, state

    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()
        return

    # return 让当前帧提前结束；等待和结束时不更新作业或分数。
    if state == "ready":
        if pyxel.btnp(pyxel.KEY_SPACE):
            start_game()
        return

    if state == "game_over":
        if pyxel.btnp(pyxel.KEY_R):
            start_game()
        return

    if pyxel.btn(pyxel.KEY_LEFT):
        player_x -= MOVE_SPEED
    if pyxel.btn(pyxel.KEY_RIGHT):
        player_x += MOVE_SPEED
    player_x = max(0, min(player_x, WIDTH - PLAYER_SIZE))

    play_frames += 1
    # % 是求余数：每逢 45、90、135……帧，余数为 0。
    if play_frames % SPAWN_INTERVAL == 0:
        homeworks.append({
            "x": pyxel.rndi(0, WIDTH - HOMEWORK_SIZE),
            "y": -HOMEWORK_SIZE,
        })

    for homework in homeworks[:]:
        homework["y"] += DROP_SPEED
        if is_collision(homework):
            state = "game_over"
            return
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

    # // 是整除：30 帧计为 1 秒，59 帧仍计为 1 秒。
    seconds = play_frames // FPS
    score = seconds * SCORE_PER_SECOND
    pyxel.rect(0, 0, WIDTH, 30, 1)
    pyxel.text(8, 6, "LESSON 03: DODGE HOMEWORK", 7)
    pyxel.text(8, 18, f"TIME: {seconds}s  SCORE: {score}", 6)
    pyxel.rect(0, 106, WIDTH, 14, 1)
    pyxel.text(8, 110, "LEFT / RIGHT: MOVE   Q: QUIT", 6)

    if state == "ready":
        pyxel.rect(18, 40, 124, 34, 0)
        pyxel.text(36, 47, "DODGE THE PAPERS!", 10)
        pyxel.text(44, 61, "SPACE: START", 7)
    elif state == "game_over":
        pyxel.rect(18, 38, 124, 42, 0)
        pyxel.text(62, 44, "GAME OVER", 8)
        pyxel.text(48, 57, f"FINAL SCORE: {score}", 7)
        pyxel.text(52, 70, "R: RESTART", 10)


if __name__ == "__main__":
    pyxel.init(WIDTH, HEIGHT, title="Dodge Homework - Lesson 03", fps=FPS)
    pyxel.run(update, draw)
