# 用 Git 保存每次练习

本地 Git 的一次提交就像一个有说明的存档。GitHub 保存这些存档的远程副本。

在 `pyxel-homework` 项目目录里运行下面的命令。

## 看看改了什么

```sh
git status
git diff
```

## 保存一次练习并上传

例如修改了第一课的移动速度后：

```sh
git add lessons/lesson_01.py
git commit -m "练习：调整角色移动速度"
git push
```

每次提交只保存已经暂存的修改。以后修改说明文件时，也用 `git add` 指定对应文件。

第二、第三课同样各存一次练习。用对应的文件名，例如：

```sh
git add lessons/lesson_02.py
git commit -m "第2课练习：随机作业雨"
git push

git add lessons/lesson_03.py
git commit -m "第3课练习：计分与重新开始"
git push
```

完成修改后再执行对应命令；没有新修改时，Git 会提示没有内容需要提交。

## 查看存档

```sh
git log --oneline
```

## 从 GitHub 获取新修改

如果在 GitHub 网页或另一台电脑修改了项目，先保存本地修改，再运行：

```sh
git pull --ff-only
```

如果提示无法直接合并，把提示发给我，我们再处理两个版本的差异。

Python 虚拟环境 `.venv`、缓存和 `.env` 文件已配置为忽略。新电脑克隆代码后，按 README 创建自己的 Python 环境。
