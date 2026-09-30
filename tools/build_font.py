"""从官方 Noto Sans CJK SC Regular OTF 生成游戏用字子集。

构建时需要 fonttools；游戏运行时不需要。用法：
python -m tools.build_font /path/to/NotoSansCJKsc-Regular.otf
"""

import argparse
from pathlib import Path
import string

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

from game import i18n


def game_characters():
    letters = string.ascii_letters + string.digits + string.punctuation + " "
    letters += "".join(chinese for chinese, _ in i18n.TEXT.values())
    letters += "".join(name + "".join(lines) for name, lines in i18n.UPGRADE_ZH.values())
    letters += "".join(name + hint for name, hint in i18n.SKIN_ZH.values())
    letters += "".join(i18n.MODE_ZH.values()) + "".join(i18n.PHASE_ZH)
    letters += "语言"
    return set(letters)


def build(source):
    font = TTFont(source)
    characters = game_characters()
    missing = characters - set(map(chr, font.getBestCmap()))
    if missing:
        raise ValueError(f"Source font lacks game characters: {''.join(sorted(missing))}")
    subset = Subsetter(options=Options())
    subset.populate(text="".join(characters))
    subset.subset(font)
    for name_id, value in ((1, "Midnight Study CJK UI"), (2, "Regular"),
                           (3, "MidnightStudyCJKUI-Regular"),
                           (4, "Midnight Study CJK UI Regular"),
                           (6, "MidnightStudyCJKUI-Regular")):
        font["name"].setName(value, name_id, 3, 1, 0x409)
        font["name"].setName(value, name_id, 1, 0, 0)
    target = i18n.FONT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    font.save(target)
    print(f"Created {target} with {len(characters)} characters")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Official NotoSansCJKsc-Regular.otf")
    build(parser.parse_args().source)
