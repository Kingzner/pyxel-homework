"""先从这里学习：画面尺寸、移动速度和两种难度。"""

WIDTH = 320
HEIGHT = 240
FPS = 60
FLOOR_Y = 202
PLAYER_WIDTH = 16
PLAYER_HEIGHT = 20
PLAYER_Y = FLOOR_Y - PLAYER_HEIGHT
MOVE_SPEED = 2.8
DASH_SPEED = 6.8
DASH_FRAMES = 12
DASH_COOLDOWN = 150
START_LIVES = 3
HIT_GRACE_FRAMES = 100
WAVE_SECONDS = 12
MAX_WAVE = 8

MODES = {
    "arcade": {"name": "ARCADE", "speed": 1.25, "interval": 56,
               "speed_step": 0.20, "interval_step": 4},
    "cozy": {"name": "COZY", "speed": 0.90, "interval": 84,
             "speed_step": 0.12, "interval_step": 5},
}
