## v1.4 工程清理与瘦身

一次性把三个版本堆在一起的目录捋顺，目标只有两条：**删掉没用的**、**留下能看懂能改的**。

### 1. 目录瘦身（删前先整包备份）

删前把整个目录打了一个 zip（`tbh_bot_backup_v13_<日期>.zip`，约 57MB）再动手。

| 删掉的 | 原因 |
|---|---|
| `build/`（56 文件 / 337MB） | PyInstaller 中间产物，每次打包自己重建 |
| `dist/` 里 3 个旧 exe | 只留当次构建的 `TBH_AutoBot.exe` |
| 4 个 `*.spec` | 打包参数已固定写进 `build.bat`，spec 只会互相盖 |
| `src/chunks/`（v1.2 分块源码） | 与 `bot_gui.py` 重复 |
| `tools/assemble_bot_gui.py`、`tools/restore_templates.py`、`tools/push_source.py` | 与 `assemble_source.py` / `pack_templates.py` 功能重叠 |
| `tools/arrow_icon.png.b64`、`tools/card_tpl.png.b64` | 模板已进 `templates.png` 图集，单图 base64 是过渡产物 |
| `code.bat` | 与 `build.bat` 重复 |
| `__pycache__/`、`test_debug.png`、各类调试截图 | 垃圾 |
| `dev/` 里 272 个文件（72.9MB） | 只留 3 个真正在用的脚本 |

`dev/` 清完只剩：`lab.py`（诊断，不动手）、`selftest.py`（回归）、`shot_app.py`（截界面目检）。

### 2. 12 张零散模板 → 1 张图集

原来 12 张 png 散在目录里，加一张就要改一堆路径。现在统一打进 `templates.png`（957×56，约 41KB），代码里只登记切片坐标 `TPLS`：

```bash
python tools/pack_templates.py --split   # 图集 → tpl_src/*.png
python tools/pack_templates.py           # tpl_src/*.png → 图集（打印 TPLS 表）
```

验证方式不是“看着一样”，而是 `np.array_equal` 逐像素比对：12/12 切片与原图完全一致，反向拆开再打包仍一致（无损往返）。

### 3. 代码重写

1679 行 → 1638 行（空行 143 / 纯注释 23 / 有效 1472）。行数降得不多，但重复逻辑清掉了：

- 删死代码：`find_banners()`、`_panel_hit()`、`cycle()` 空壳、`ready_tpl` 分支、`HEX_NAME/HEX_TPL/BAG_ROI/HEX_DY` 等没人用的常量、`self.stat`。
- 合并：三处“模板 → 白色阈值严 → 白色阈值松”合成 `detect_cards()`；巡检主流程合成 `panel_pass(bot)`；6 处重复的控件写法合成 `_chk()` / `_num()`；`_build()` 拆成 6 个子函数。
- 7 处 `try: … except: pass` 换成 `contextlib.suppress`。

**5 遍检查**：结构去重 → `pyflakes` 0 警告 + `py_compile` → AST 体检（未使用变量/未调用函数）→ `suppress` 化 → 实机回归。

第 5 遍实机跑时又抓到两个真问题：

1. **模板多尺度白做**：`find_cards_tpl()` 里 `s = sc * k` 算出来了，`cv2.resize(tpl, fx=sc, fy=sc)` 却仍用 `sc` —— 7 个尺度其实全是同一个尺寸，白跑 7 次匹配。改成 `fx=s, fy=s`。
2. **仓库两个键的模板过时**：`wh_store` / `wh_back` 全屏各倍数最高只有 0.34~0.48，导致“仓库面板始终没开出来”。用新写的 `tools/capture_templates.py` 从运行中的游戏重拍（`wh_store=(-161,26,138,48)`、`wh_back=(-291,26,106,48)`、`cube_fill=(206,-102,122,40)`、`cube_exec=(340,-104,98,37)`），`TPLS` 同步为 `wh_store(377,2,138,48)`、`wh_back(519,2,106,48)`，`PanelBot` 常量改成 `WH_OFF=(-161,26)`、`WH_BACK_DX=130`。修好后实测存仓两轮成功，仓库双向验证 `0.170 → 0.034 → 0.178` 成立。

### 4. 新增：点击遮挡防护

之前“点了没反应”有一部分是点击落到了别的软件上。现在 `PanelBot._click()` 先 `point_blocked(x, y, hwnd)` 判断该点归属：被浏览器 / Steam / WeGame / 任务栏压住就不点，日志写明被谁挡住（`类名|窗口标题`）。`_open_hero` / `_open_hex` / `_open_warehouse` / `store` / `_cube` 全部接住返回值提前收手，不会“继续往下瞎点”。

用假鼠标对象验证：遮挡点返回 False、鼠标零动作、日志有窗口名；正常点照常通过。

### 5. 新增：UI 缩放自适应

游戏窗口被拖大拖小后 UI 会跟着缩放，模板和偏移全写死就会失配。现在：

- `REF_VIEW_W = 970`（拍模板时的可见宽度），`ui_scale(hwnd) = 可见宽度 / 970`，限幅 0.65~1.8；
- `load_tpl(name, sc)` 按倍数缩放并按 `(名字, 倍数)` 缓存；
- 六边形间距、`WH_OFF` / `WH_BACK_DX`、仓库格区、魔方格子区、两个魔方按钮偏移、`find_cards_tpl` 的搜索尺度、`detect_cards` 的面积阈值，全部乘 `sc`。

实测：1212 宽窗口下金盾模板 ×1.25 得 0.94（×1.0 只有 0.47）；970 宽时金盾 1.000、五枚六边形 1.000。

魔方按钮也不再写死 `box=(1400,640,1920,790)`，改由「魔方六边形 + 偏移」推出来。

### 6. `build.bat` 修好

- 原脚本直接调 PATH 里的 `python`，会被商店版/沙箱解释器抢走且缺 PyInstaller → 改成先试 `py -3`（失败再 `python`），并要求能 import `cv2,mss,numpy,win32gui,keyboard,pyautogui,PyInstaller`，缺了就明确报出来。
- 行尾必须是 CRLF（LF 的 `.bat` 会被 cmd 拆碎，报“'o' 不是内部或外部命令”）。
- 括号块里的 `%PY%` 不会延迟展开 → 改成顺序 `if errorlevel 1 set "PY=python"` 后重新校验。
- 实测 `cmd /c "build.bat < nul"` 输出 `[0/3] 解释器：py -3` 并 Build complete，产物 `dist\TBH_AutoBot.exe`。

### 7. 仓库同步（分片规则）

GitHub 上传走的是纯文本接口，单次内容长度上限约 9.3KB，所以源码分 9 片存放，并且分片/拼回规则对称：

- 每片在**非空行**处断开（片尾空行让给下一片），片内去掉尾部换行；
- 拼回时片与片之间用单个换行连接，最后补回文件末尾那一个换行；
- `tools/split_source.py`（分）与 `tools/assemble_source.py`（合）互为逆操作，已用 sha256 双向验证。

### 遗留

端到端“存仓 + 魔方”复测需要游戏窗口干净地待在**最前台**（不能被浏览器/Steam/聊天窗压住）。本轮多次复测时桌面被 WeGame、Steam、聊天窗反复抢占，游戏被改尺寸后仓库面板渲染比模板小约 18%，没能拿到完整通过记录；清理前已取得过完整成功数据，新增能力也各自单独验证过。复测命令：

```bash
python dev/selftest.py 1 1
```