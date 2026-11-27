# TBH_AutoBot（TaskBarHero 自动挂机助手）

一个面向《TaskBarHero》的 Windows 桌面自动化小工具：自动识别并点击游戏里出现的**宝箱卡片**，定时巡检**背包 / 仓库**，仓库满时可选用**魔方**自动填充并合成。

界面是 Python + Tkinter 做的深色 Fluent 风格，单文件打包成 exe，双击即用。

## 功能

| 模块 | 说明 |
|---|---|
| 宝箱识别 | 模板匹配（`card_tpl.png`，多尺度）→ 白色阈值（严）→ 白色阈值（松）。卡片压在白色网页/聊天窗上也能认出来 |
| 点击校验 | 点完立刻回截，比较卡片区域差异；同一位置连续多次无变化自动跳过一段时间，避免一直空点 |
| 检测区域 | 默认**跟随游戏窗口右下角**（游戏窗口会随面板开合改变尺寸和位置，写死坐标必错）；也可手动框选 |
| 前台守卫 | 游戏窗口是 `WS_EX_TRANSPARENT` 的置顶窗口，不在前台时鼠标点击会**穿透**到桌面/别的软件。所以只在游戏位于前台时才点击，并给出提示 |
| 背包 / 仓库 | 点右下角「金盾」按钮开英雄面板 → 底部六边形「仓库」→ 点「仓库<背包」存仓（幂等操作，背包空着点也不会出错） |
| 魔方合成 | 仓库也满时：开「魔方」→「自动填充」→「✚ 合成」，可重复多次。**会消耗 9 件同等级装备，默认关闭** |

## 依赖

```
opencv-python
mss
numpy
pywin32
pyautogui
pillow
keyboard
```

Windows 10/11，Python 3.11。程序启动时会 `SetProcessDpiAwareness(2)`，所以 125% / 150% 缩放下 win32 坐标、截图、点击都用物理像素，三者一致。

## 运行

```bash
pip install -r requirements.txt
python tools/restore_templates.py   # 还原 card_tpl.png / arrow_icon.png
python bot_gui.py
```

`card_tpl.png`、`arrow_icon.png` 必须和脚本（或打包后的 exe）放在同一目录——它们是识别用的模板图。仓库里以 base64 存放（GitHub 只能推文本），用上面的脚本还原。

打包（可选）：

```bash
python -m PyInstaller -F -w -n TBH_AutoBot --hidden-import win32timezone --collect-submodules mss bot_gui.py
```

## 使用要点

1. 顶上选好目标窗口（`TaskBarHero`），默认已勾选「跟随窗口右下角」。
2. 点「开始」。程序会把游戏窗口切到前台；**如果切不过去（Windows 前台锁），手动点一下游戏画面**，否则点击会穿透到桌面，日志里会出现「游戏窗口不在前台」的提示。
3. 想用背包巡检：在 ④ 里勾「定时巡检背包」，再点一次「立即巡检一次」确认坐标对得上。
4. 合成开关默认关闭。打开前请确认：合成是 `9 件同等级 → 1 件更高等级`，**不可撤销**。

## 已知限制

- 游戏窗口带 `WS_EX_TRANSPARENT`，抢前台用 `SetForegroundWindow` / `AttachThreadInput` / `SwitchToThisWindow` 基本都被前台锁挡住，只有本程序自己是前台的那一刻（刚点「开始」）成功率最高。
- 面板会随开启数量左右平移（单面板 banner≈1656，两个 1354+1676，三个 1032/1354/1676），所以代码里全部用「banner 相对偏移」，改动前先重新标定。
- 魔方两个按钮的偏移是按参考图换算的，尚未逐帧实测；背包占用率目前只是「彩色像素占比」的参考值，不做判定。

## 结构

```
bot_gui.py        # 全部逻辑：窗口枚举 / 区域解析 / 卡片识别 / 引擎线程 / 面板巡检 / Tkinter 界面
card_tpl.png      # 宝箱卡片模板（62×44）
arrow_icon.png    # 右下角「金盾」按钮模板（25×29）
config.json       # 运行参数（首次运行自动生成）
FIXES.md          # 迭代记录与问题定位过程
tools/            # 模板图 base64 与还原脚本
```

## 免责

仅供个人学习与自动化练习。自动化点击作用于第三方游戏，可能违反游戏服务条款，请自行评估风险；因使用本工具造成的账号或数据损失由使用者自负。
