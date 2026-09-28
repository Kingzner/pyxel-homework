# 躲避作业：Pyxel 学习项目

## 选择课程

按顺序学习，每课都保留独立代码与启动文件。

| 课程 | 内容 | 代码 | 双击启动 | 学习说明 |
| --- | --- | --- | --- | --- |
| 第 1 课 | 角色移动、参数与坐标 | `lessons/lesson_01.py` | `start.command` | [第一课](docs/lesson-01.md) |
| 第 2 课 | 随机数、列表与作业雨 | `lessons/lesson_02.py` | `start-lesson-02.command` | [第二课](docs/lesson-02.md) |
| 第 3 课 | 开始、碰撞、计分与重开 | `lessons/lesson_03.py` | `start-lesson-03.command` | [第三课](docs/lesson-03.md) |

也可以在项目目录运行对应启动文件，如 `./start-lesson-02.command`。

点击游戏窗口后，按 ← / → 移动，按 Q 退出。第三课按空格开始，碰撞结束后按 R 重开。

保存代码后，关闭游戏并重新启动，修改才会生效。

第一课练习完成后的角色参数（速度 4、颜色 8、尺寸 12）已沿用到第二、第三课。每课是独立程序，修改第二课不会自动修改第三课。

用 [Git 使用说明](docs/version-control.md) 保存每次练习。

## 环境

Python 3.11 以上，Pyxel 固定为 2.9.9。此项目使用自己的 `.venv`。

在新的电脑上，可以用已安装的 Python 3.11 以上版本创建环境：

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./start.command
```

## 后续课程

4. 随着存活时间增加，提升下落速度与出现频率。
5. 像素角色、音效、护盾道具与最高分。

## 官方参考

- [Pyxel 项目](https://github.com/kitao/pyxel)
- [用户指南](https://kitao.github.io/pyxel/web/user-guide/)
- [API 文档](https://kitao.github.io/pyxel/web/api-reference/)
- [官方示例](https://kitao.github.io/pyxel/web/showcase/)

本项目的教学代码是为本次学习编写的。
