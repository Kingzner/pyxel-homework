# 躲避作业：Pyxel 学习项目

## 从第一课开始

第一课的目标：用方向键移动一个角色，亲手修改参数，观察画面如何变化。

- 游戏代码：`lessons/lesson_01.py`
- 学习说明：[第 1 课](docs/lesson-01.md)
- 保存练习版本：[Git 使用说明](docs/version-control.md)
- 启动游戏：在 Finder 中双击 `start.command`；或在项目目录运行 `./start.command`。
- 点击游戏窗口后，按 ← / → 移动，按 Q 退出。

保存代码后，关闭游戏并重新启动，修改才会生效。

## 环境

Python 3.11 以上，Pyxel 固定为 2.9.9。此项目使用自己的 `.venv`。

在新的电脑上，可以用已安装的 Python 3.11 以上版本创建环境：

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./start.command
```

## 后续课程

1. 角色移动、参数与坐标。
2. 随机生成掉落的作业。
3. 碰撞、计分与重新开始。
4. 像素角色、音效与护盾道具。

## 官方参考

- [Pyxel 项目](https://github.com/kitao/pyxel)
- [用户指南](https://kitao.github.io/pyxel/web/user-guide/)
- [API 文档](https://kitao.github.io/pyxel/web/api-reference/)
- [官方示例](https://kitao.github.io/pyxel/web/showcase/)

本项目的教学代码是为本次学习编写的。
