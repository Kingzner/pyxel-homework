# 第 2 课：把一份作业变成作业雨

这一课学习坐标、随机数、列表和循环。建议用 20～30 分钟完成。

代码在 `lessons/lesson_02.py`。沿用你第一课的速度 4、红色角色、尺寸 12。

## 1. 先看一份作业掉下来

双击 `start-lesson-02.command`，或在项目目录运行：

```sh
./start-lesson-02.command
```

等约 1.5 秒，黄色方块从正中间落下。它代表作业。左右方向键移动角色，Q 退出。这一课可以穿过作业；碰撞判定在第三课加入。

先看这两行：

```python
homeworks.append({"x": x, "y": -HOMEWORK_SIZE})
homework["y"] += DROP_SPEED
```

第一行生成一份作业。初始 y 是负数，让它从屏幕上方进入。

第二行增加它的 y 坐标。屏幕坐标的 y 向下增加，所以作业会下落。速度为 2、每秒 30 帧时，约每秒下降 60 像素。

## 2. 亲手完成三个修改

每次先预测结果，只改一个参数。保存后，按 Q 退出旧窗口，再双击启动文件。

| 步骤 | 修改 | 观察结果 |
| --- | --- | --- |
| 1：随机位置 | `RANDOM_SPAWN = False` → `True` | 连续看几份作业，是否从不同位置出现？ |
| 2：多份作业 | `MAX_HOMEWORK = 1` → `5` | 顶部 `PAPERS` 的数字能否超过 1？ |
| 3：加密作业雨 | `SPAWN_INTERVAL = 45` → `20` | 新作业是不是出现得更频繁了？ |

`False` 和 `True` 是布尔值，分别表示假和真；注意首字母大写。

`pyxel.rndi(0, WIDTH - HOMEWORK_SIZE)` 在左右边界之间随机选一个整数。右边界减去作业宽度，保证整份作业位于屏幕内。

`SPAWN_INTERVAL` 的单位是帧。45 帧约为 1.5 秒，20 帧约为 0.67 秒。数量达到 `MAX_HOMEWORK` 时，跳过本次生成。

## 3. 列表和字典分别负责什么？

一份作业的字典长这样：

```python
{"x": 40, "y": 12}
```

`homework["y"]` 取出它的纵坐标。`homeworks` 则是装着许多作业字典的列表：

```python
homeworks = [
    {"x": 40, "y": 12},
    {"x": 90, "y": 30},
]
```

`append()` 加入一份；`len(homeworks)` 数有几份；`remove()` 删除已经掉出屏幕的一份。

```python
for homework in homeworks[:]:
    homework["y"] += DROP_SPEED
    if homework["y"] >= HEIGHT:
        homeworks.remove(homework)
```

`for` 依次处理每份作业。`[:]` 生成列表的浅拷贝：可以从原列表删除作业，同时保持本轮遍历的顺序。里面的作业字典仍然是同一份，因此修改 y 会更新游戏中的位置。

第一课的边界限制在这里简写为 `max(0, min(player_x, WIDTH - PLAYER_SIZE))`：先取右边界和 x 中较小的值，再保证它至少为 0。

## 4. 本课完成标准

- 你亲手把固定位置改成随机位置。
- 屏幕中可以同时出现多份作业。
- 能解释“y 增加为什么会向下移动”。
- 能区分：`DROP_SPEED` 控制下落速度，`SPAWN_INTERVAL` 控制出现频率。

可以用 Git 保存这次练习：

```sh
git add lessons/lesson_02.py
git commit -m "第2课练习：随机作业雨"
git push
```

接着打开 [第 3 课](lesson-03.md)，让作业真正具有危险性。
