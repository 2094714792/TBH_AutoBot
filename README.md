# TBH_AutoBot（TaskBarHero 自动挂机助手）

一个面向《TaskBarHero》的 Windows 桌面自动化小工具：自动识别并点击游戏里出现的**宝箱卡片**，定时巡检**背包 / 仓库**，仓库满时可选用**魔方**自动填充并合成。

界面是 Python + Tkinter 做的深色 Fluent 风格，单文件打包成 exe，双击即用。当前版本 **v1.4**。

## 功能

| 模块 | 说明 |
|---|---|
| 宝箱识别 | 模板匹配（`card_tpl`，多尺度，跟随 UI 缩放）→ 白色阈值（严）→ 白色阈值（松）。卡片压在白色网页/聊天窗上也能认出来 |
| 点击校验 | 点完立刻回截，比较卡片区域差异；同一位置连续多次无变化自动跳过一段时间，避免一直空点 |
| 点击防误触 | 点击前用 `point_blocked()` 检查该点归属，被浏览器 / Steam / WeGame / 任务栏等压住时**不点**，日志写出被谁挡住 |
| 检测区域 | 默认**跟随游戏窗口右下角**（游戏窗口会随面板开合改变尺寸和位置，写死坐标必错）；也可手动框选 |
| UI 缩放自适应 | `ui_scale()` = 可见宽度 / 970（限幅 0.65~1.8）；模板、六边形间距、按钮偏移、格子区都按倍数缩放，日志会打出实际倍数 |
| 前台守卫 | 游戏窗口是 `WS_EX_TRANSPARENT` 的置顶窗口，不在前台时鼠标点击会**穿透**到桌面/别的软件。所以只在游戏位于前台时才点击，并给出提示 |
| 背包 / 仓库 | 点右下角「金盾」开英雄面板 → 底部六边形「仓库」→ 点「仓库<背包」存仓（点多少次都不会点坏） |
| 魔方合成 | 仓库也满时：开「魔方」→「自动填充」→「✚ 合成」。**合成按钮是灰的就说明没凑够 9 件同等级，程序只报原因、不硬点**。默认关闭 |

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

Windows 10/11，Python 3.11。程序启动时会 `SetProcessDpiAwareness(2)`，125% / 150% 缩放下 win32 坐标、截图、点击都用物理像素，三者一致。

## 从仓库还原可运行目录

仓库里的 `bot_gui.py` 分成 3 片存放（`src/bot_gui.py.part1..3`）——上传走的是纯文本接口，单次有长度上限。还原：

```bash
python tools/assemble_source.py        # 拼回 bot_gui.py，并打印 sha256 供核对
pip install -r requirements.txt
python bot_gui.py
```

`templates.png`（识别必需的模板图集）不放在仓库里：

- 从发布包 `dist\TBH_AutoBot.exe` 同目录拷一份；或
- 用 `python tools/capture_templates.py` 从运行中的游戏重拍（会把 12 张图写进 `tpl_src/`，再 `python tools/pack_templates.py` 打包，并把打印的 `TPLS` 表贴回 `bot_gui.py`）。

## 模板图集怎么改

识别用的 12 张小图不散落在程序目录，统一打包成 `templates.png`：

```bash
python tools/pack_templates.py --split    # 图集 → tpl_src/*.png（想改哪张就改哪张）
python tools/pack_templates.py            # tpl_src/*.png → templates.png（会打印新的 TPLS 表）
python tools/capture_templates.py         # 游戏界面改版 / 窗口尺寸变了之后，从运行中的游戏重拍
```

改完图集后把打印的 `TPLS = {...}` 贴回 `bot_gui.py` 的 `TPLS` 常量，再把 `python dev/selftest.py 1 1` 跑一遍确认识别没坏。

## 使用要点

1. 点「自动识别」：程序自己找 `UnityWndClass` / 标题含 `TaskBarHero` 的窗口，算「窗口 ∩ 屏幕」的可见区，
   自动设成「跟随窗口右下角」，并顺手识别一次卡片写进日志。不需要手动挑窗口。
2. 点「开始」。巡检/点击时如果游戏不在前台，程序会自己把它切到前台，做完再把前台还给你原来的窗口
   （④ 里可以关掉「巡检前自动把游戏切到前台」）。
3. 想用背包巡检：在 ④ 里勾「定时巡检背包」，再点一次「立即巡检一次」确认坐标对得上。
4. 合成开关默认关闭；打开前请确认：合成是 `9 件同等级 → 1 件更高等级`，**不可撤销**。

## 已知限制

- 面板会随开启数量左右平移（例：仓库/属性/符文面板在英雄面板左侧 288px，魔方在右侧），
  所以代码先认「符文」图标，再按间距推出五枚六边形；按钮位置算出来后再用模板在小窗口里确认。
- 游戏窗口大小会变（拖拽、开关面板），UI 会跟着缩放；换分辨率或改版后按钮外观也会变，
  重新跑一次 `tools/capture_templates.py` 即可。
- 游戏窗口被别的软件压住、或被任务栏盖住底边时，程序不会动手（只报原因）。
- 打包脚本先找 `py -3`、再找 `python`，并要求能 import `cv2/mss/win32gui/PyInstaller`；
  都不满足会直接报出来（不会静默失败）。

## 结构

```
bot_gui.py            # 全部逻辑：窗口枚举 / 区域解析 / 卡片识别 / 引擎线程 / 面板巡检 / Tkinter 界面
src/bot_gui.py.part*  # 上传分片，用 tools/assemble_source.py 拼回 bot_gui.py
templates.png         # 模板图集（识别必需；不在仓库里，见上面“还原”一节）
tpl_src/              # 图集里的 12 张单图，由 pack_templates.py 拆出/打包
tools/assemble_source.py    # 拼回 bot_gui.py + 校验 sha256
tools/pack_templates.py     # 图集 ↔ 单图 互转，打印 TPLS 坐标表
tools/capture_templates.py  # 从运行中的游戏重拍模板（改版/换分辨率后）
dev/lab.py            # 诊断：报窗口/可见区/各模板当前得分/六边形坐标，不动手
dev/selftest.py       # 回归：真跑存仓（可选魔方）+ 仓库双向验证
dev/shot_app.py       # 截界面图，交付前目检
config.json           # 运行参数（首次运行自动生成）
FIXES.md              # 迭代记录与问题定位过程
```

## 免责

仅供个人学习与自动化练习。自动化点击作用于第三方游戏，可能违反游戏服务条款，请自行评估风险；因使用本工具造成的账号或数据损失由使用者自负。
