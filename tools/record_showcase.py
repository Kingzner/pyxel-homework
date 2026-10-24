"""Render a short, reproducible GIF of the real Pyxel game for the README.

Run from the repository root with ``.venv/bin/python -m tools.record_showcase``.
The clip condenses title, gameplay, upgrades, boss fight, and ending into a
short montage. It never reads or writes the player's save file.
"""

from argparse import ArgumentParser
from pathlib import Path

import pyxel

from game import storage
from game.main import Game


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("assets/showcase.gif"))
    args = parser.parse_args()

    fresh_save = {
        "version": 3,
        "best": {"arcade": 0, "cozy": 0, "exam": 0},
        "muted": True,
        "language": "en",
        "owned": ["sena"],
        "selected": "sena",
        "stats": {"notes": 0, "clears": 0, "hard_clears": 0},
    }
    storage.load = lambda: {
        **fresh_save,
        "best": fresh_save["best"].copy(),
        "stats": fresh_save["stats"].copy(),
        "owned": fresh_save["owned"].copy(),
    }
    storage.save = lambda _data: True

    original_init = pyxel.init

    def headless_init(*values, **options):
        options.update(headless=True, fps=15, capture_sec=10, capture_scale=2)
        return original_init(*values, **options)

    pyxel.init = headless_init
    game = Game("demo", seed=42)
    held: set[int] = set()
    pressed: set[int] = set()
    pyxel.btn = lambda key: key in held
    pyxel.btnp = lambda key: key in pressed

    def frame(keys=(), press=()):
        nonlocal held, pressed
        held = set(keys)
        for subframe in range(4):
            pressed = set(press) if subframe == 0 else set()
            game.update()
        pressed = set()
        game.draw()
        pyxel.flip()

    for _ in range(14):
        frame()
    game.start_game()
    for index in range(22):
        direction = pyxel.KEY_RIGHT if index < 11 else pyxel.KEY_LEFT
        frame((pyxel.KEY_Z, direction), (pyxel.KEY_SPACE,) if index == 3 else ())

    game.open_upgrade()
    for _ in range(12):
        frame()
    game.choose_upgrade(0)
    for index in range(12):
        direction = pyxel.KEY_LEFT if index < 6 else pyxel.KEY_RIGHT
        frame((pyxel.KEY_Z, direction))

    game.open_upgrade()
    for _ in range(9):
        frame()
    game.choose_upgrade(1)
    game.open_upgrade()
    for _ in range(9):
        frame()
    game.choose_upgrade(0)

    game.begin_boss()
    for _ in range(10):
        frame()
    frame(press=(pyxel.KEY_RETURN,))
    for index in range(30):
        target = game.boss.x
        player = game.player_x + 8
        direction = (pyxel.KEY_RIGHT if player < target - 6 else
                     pyxel.KEY_LEFT if player > target + 6 else None)
        keys = (pyxel.KEY_Z, direction) if direction is not None else (pyxel.KEY_Z,)
        frame(keys, (pyxel.KEY_SPACE,) if index == 8 else ())

    # Show the game's own victory and ending screens as the final montage shots.
    game.boss.damage(game.boss.hp)
    for _ in range(12):
        frame()
    frame(press=(pyxel.KEY_RETURN,))
    for _ in range(8):
        frame()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    pyxel.screencast(str(args.output), scale=2)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
