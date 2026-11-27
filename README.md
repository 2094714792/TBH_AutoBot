# TBH_AutoBot

TaskBarHero 宝箱自动挂机助手（Windows 10/11，Python 3.11 + Tkinter）。
识别游戏窗口右下角的宝箱卡片并自动点击，附带「背包 → 仓库」定时巡检；仓库也满时可选走魔方自动填充 + 合成（默认关闭）。

## 功能

| 模块 | 说明 |
| --- | --- |
| 卡片识别 | 模板匹配 → 白色阈值（严）→ 白色阈值（松）。白色网页/窗口压在卡片后面时也不会漏识 |
| 点击校验 | 点完回截比对，同一位置连续多次无变化就跳过一段时间 |
| 前台守卫 | 只在游戏处于前台时才点击（游戏是透明置顶窗口，非前台时点击会穿透到桌面/其它软件） |
| 检测区域 | 默认跟随游戏窗口右下角（窗口随面板开合改变尺寸），也可手动框选 |
| 背包巡检 | 定时开英雄面板 → 仓库 → 点「仓库<背包」存仓（幂等操作，背包空着点也不会出错） |
| 魔方合成 | 可选，9 件同等级装备换 1 件，不可撤销，默认关闭 |
| 热键 | F8 暂停/继续，F12 停止；手动巡检时会自动暂停引擎，避免两边抢鼠标 |

## 环境

- Windows 10/11（目前只测过 Windows）
- Python **3.11**（3.13 的 cv2 / pyautogui 轮子还不全，不建议）
- 依赖：`pip install -r requirements.txt`

## 运行

```bat
pip install -r requirements.txt
python tools/assemble_bot_gui.py     :: 从 src/chunks 拼出 bot_gui.py（会校验 sha256）
python bot_gui.py
```

`bot_gui.py` 是拼装产物，不入库；权威内容就在 `src/chunks/bot_gui.py.part1..part5`，
拼装后的 sha256 记录在 `tools/assemble_bot_gui.py` 的 `EXPECT_SHA256` 里。

## 模板图（必须与程序同目录）

| 文件 | 尺寸 | 用途 |
| --- | --- | --- |
| `card_tpl.png` | 62×44 | 宝箱卡片模板 |
| `arrow_icon.png` | 25×29 | 右下角金盾按钮（开英雄面板的入口） |

二进制不便直接放仓库，这里以 base64 存放：

```bat
python tools/restore_templates.py     :: 由 tools/*.b64 还原出两张 png
```

## 目录结构

```
bot_gui.py            ← 由 tools/assemble_bot_gui.py 生成（不入库）
requirements.txt
FIXES.md              迭代记录：遮挡误判、点击穿透、背包/仓库/魔方
src/chunks/           bot_gui.py 的 5 段切片，字节级可拼回
tools/assemble_bot_gui.py   拼装 + sha256 校验
tools/restore_templates.py  还原模板图
tools/card_tpl.png.b64
tools/arrow_icon.png.b64
tools/push_source.py  维护者用：拿 token 直传源码（本地没装 git 时的傅逯）
```

## 使用要点

1. 先把游戏开到任务栏状态，在①里选中它（选错了可以「刷新」）
2. 检测区域建议「跟随窗口右下角」；分辨率不同就改 `rel_w / rel_h / rel_right / rel_bottom`
3. 点「开始」—— 这一瞬间本程序还在前台，程序会顺手把游戏切到前台（Windows 前台锁只在此时放行）
4. 游戏必须在前台。不在前台时程序会暂停点击，每 8 秒在日志里提示当前前台是谁
5. 背包巡检默认关闭，勾选后默认每 10 分钟一轮；想现在就试可点「立即巡检一次」

## 已知限制

- 面板按钮偏移是按顶部 banner 的相对位置算的，魔方「自动填充 / 合成」两个位置尚未逐帧实测
- 背包“占用率”只是彩色像素占比的参考值，不做满/空判定（所以存仓做成了幂等操作）
- 只支持 Windows；分辨率/缩放不同需要调参数

## 免责

仅供个人学习与自动化实验。自动化操作可能违反游戏用户协议，使用后果自负。
