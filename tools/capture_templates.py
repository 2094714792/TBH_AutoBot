# -*- coding: utf-8 -*-
"""从正在运行的游戏里重拍模板（游戏界面改版 / 换分辨率后跑一次即可）

    python tools/capture_templates.py          # 六边形 + 仓库按钮 + 魔方按钮
    python tools/capture_templates.py --wh     # 只重拍仓库两个按钮

流程：抢前台 → 开英雄面板 → 裁六边形 → 开仓库裁两个按钮 → 开魔方裁按钮
→ 写 tpl_src/*.png，再跑 tools/pack_templates.py 重新打包并更新 bot_gui.py 的 TPLS 表。
窗口被拉大/拉小时按 ui_scale() 等比缩放偏移，拍的尺寸也跟着缩放。
"""
import os
import queue
import sys
import time

import cv2
import pyautogui as pg

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
import bot_gui as B  # noqa: E402

SRC = os.path.join(BASE, "tpl_src")
# 相对「仓库」六边形中心的偏移（实测 1920×1080 / 125%）
WH_STORE = (-161, 26, 138, 48)      # 仓库<背包
WH_BACK = (-291, 26, 106, 48)       # 仓库>背包
# 相对「魔方」六边形中心的偏移（魔方开着时六边形行整体左移）
CUBE_FILL = (206, -102, 122, 40)    # 自动填充
CUBE_EXEC = (340, -104, 98, 37)     # 合成


def save(name, img, cx, cy, w, h):
    x0, y0 = int(cx - w // 2), int(cy - h // 2)
    crop = img[y0:y0 + h, x0:x0 + w]
    if crop.shape[:2] != (h, w):
        print("!! %s 越界，跳过" % name)
        return None
    os.makedirs(SRC, exist_ok=True)
    cv2.imwrite(os.path.join(SRC, name + ".png"), crop)
    print("拍下 %-14s %dx%d @(%d,%d)" % (name, w, h, int(cx), int(cy)))
    return crop


def verify(name, img, crop, cx, cy, box=80):
    """验证：拿刚拍的模板在当前画面 ±box 窗口里能稳定命中"""
    t = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    sub = img[max(0, int(cy) - box):int(cy) + box, max(0, int(cx) - box):int(cx) + box]
    r = cv2.matchTemplate(cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY), t, cv2.TM_CCOEFF_NORMED)
    mx = cv2.minMaxLoc(r)[1]
    print("  自检 %-14s 窗口内 %.3f %s" % (name, mx, "OK" if mx >= 0.95 else "!! 偏低"))


def main():
    only_wh = "--wh" in sys.argv
    g = B.find_game_hwnd()
    if not g:
        sys.exit("没找到游戏窗口")
    bot = B.PanelBot(dict(B.DEFAULT, hwnd=g[0], follow=1, region=None), queue.Queue(), None)
    bot.sc = B.ui_scale(g[0])            # 窗口被拉大/拉小时，偏移和裁剪尺寸一起缩放
    print("抢前台:", B.force_foreground(g[0]), "UI 缩放 ×%.2f" % bot.sc)
    time.sleep(0.5)
    bot.esc(3)                  # 先收掉可能开着的旧面板，保证从干净状态开始
    time.sleep(0.6)
    if bot._open_hero() is None:
        sys.exit("英雄面板打不开")
    row = bot._row(bot._shot())
    print("六边形行:", row)
    hx, hy = row["仓库"]
    sc = bot.sc

    if not only_wh:
        for n, key in (("hex_store", "仓库"), ("hex_attr", "属性"), ("hex_rune", "符文"),
                       ("hex_cube", "魔方"), ("hex_gem", "宝石")):
            img = bot._shot()
            pg.moveTo(300, 300)
            c = save(n, img, row[key][0], row[key][1], int(52 * sc), int(52 * sc))
            if c is not None:
                verify(n, img, c, row[key][0], row[key][1])
            time.sleep(0.25)

    pg.moveTo(300, 300)
    time.sleep(0.3)
    bot._click(*row["仓库"])          # 直接点开仓库（老模板失效时 _open_warehouse 认不出来）
    time.sleep(1.2)
    pg.moveTo(300, 300)
    time.sleep(0.4)
    img = bot._shot()
    for name, (dx, dy, w, h) in (("wh_store", WH_STORE), ("wh_back", WH_BACK)):
        sx, sy, sw, sh = hx + dx * sc, hy + dy * sc, int(w * sc), int(h * sc)
        c = save(name, img, sx, sy, sw, sh)
        if c is not None:
            verify(name, img, c, sx, sy)
    bot.esc(2)

    if not only_wh:
        time.sleep(0.4)
        bot._open_hero()
        row = bot._row(bot._shot())
        cx, cy = row["魔方"]
        bot._open_hex("魔方")
        pg.moveTo(300, 300)
        time.sleep(0.5)
        img = bot._shot()
        for name, (dx, dy, w, h) in (("cube_fill", CUBE_FILL), ("cube_exec_off", CUBE_EXEC)):
            sx, sy, sw, sh = cx + dx * sc, cy + dy * sc, int(w * sc), int(h * sc)
            c = save(name, img, sx, sy, sw, sh)
            if c is not None:
                verify(name, img, c, sx, sy)
        bot.esc(2)
    print("完成，接着跑 python tools/pack_templates.py")


if __name__ == "__main__":
    main()
