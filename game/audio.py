"""原创低音量芯片音乐和事件音效；M 键可以静音。"""

import pyxel


class Audio:
    EFFECTS = {"start": 2, "dash": 3, "pickup": 4, "shield": 5,
               "hit": 6, "over": 7, "wave": 8, "shot": 9, "win": 10,
               "paper": 13, "focus": 14}

    def __init__(self, muted=False):
        self.muted = muted
        pyxel.sounds[0].set(
            "c3e3g3r e3g3a3r g3e3c3r d3e3g3r "
            "a3g3e3r g3e3d3r f3e3d3r d3e3c3r",
            "t", "1", "f", 16,
        )
        pyxel.sounds[1].set("c1rc1r f1rg1r a1ra1r f1rg1r", "t", "1", "f", 32)
        pyxel.sounds[2].set("c3e3g3c4", "t", "3321", "nnnf", 6)
        pyxel.sounds[3].set("c2g2c3", "p", "321", "fff", 3)
        pyxel.sounds[4].set("c3e3g3c4g3c4", "t", "332211", "nnnnff", 4)
        pyxel.sounds[5].set("g3e3c3c2", "p", "4211", "ffff", 4)
        pyxel.sounds[6].set("c1c1g0r", "n", "4210", "fffn", 6)
        pyxel.sounds[7].set("g2e2c2g1c1", "t", "33221", "f", 12)
        pyxel.sounds[8].set("c3g3c4", "t", "221", "f", 8)
        pyxel.sounds[9].set("c3g3", "p", "11", "ff", 2)
        pyxel.sounds[10].set("c3e3g3c4rg3c4", "t", "3322111", "n", 10)
        pyxel.sounds[11].set("c2rc2g2 c2rc2g2 d2rd2a2 d2rd2a2", "p", "1", "f", 12)
        pyxel.sounds[12].set("c1rc1r g0rg0r c1rc1r g0rg0r", "t", "1", "f", 24)
        pyxel.sounds[13].set("g4e4c4", "p", "221", "fff", 4)
        pyxel.sounds[14].set("c3e3g3c4e4", "t", "33221", "nnnff", 8)

    def music(self, boss=False):
        if not self.muted:
            pyxel.play(0, 11 if boss else 0, loop=True)
            pyxel.play(1, 12 if boss else 1, loop=True)

    def effect(self, name):
        if not self.muted:
            channel = 3 if name in ("hit", "over") else 2
            pyxel.play(channel, self.EFFECTS[name])

    def stop(self):
        pyxel.stop()

    def toggle(self, music_active=True, boss=False):
        self.muted = not self.muted
        self.stop()
        if music_active:
            self.music(boss)
