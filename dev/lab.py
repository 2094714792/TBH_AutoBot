# -*- coding: utf-8 -*-
"""诊断台：不动手，只看画面

    python dev/lab.py               # 报告窗口/可见区/各模板当前得分/六边形行坐标
    python dev/lab.py --shot out.png  # 存一张整屏截图（存到 dev/ 下）
    python dev/lab.py --open        # 打开英雄面板后再看一眼（会点一下金盾）
"""
import ctypes
import os
import queue
import sys

import cv2
import mss
import numpy as np

try:                 # 截图进程必须 DPI 感知，否则坐标会被虚拟化缩小
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import bot_gui as B  # noqa: E402

TEMPLATES = ("card_tpl", "arrow_icon", "hex_store", "hex_attr", "hex_rune",
             "hex_cube", "hex_gem", "wh_store", "wh_back", "cube_fill",
             "cube_exec_on", "cube_exec_off")


def shot():
    with mss.mss() as s:
        return np.array(s.grab(s.monitors[0]))[:, :, :3].copy()


def score_all(img):
    """逐模板全屏打分，报告最佳位置"""
    for n in TEMPLATES:
        t = B.load_tpl(n)
        if t is None or t.shape[0] >= img.shape[0] or t.shape[1] >= img.shape[1]:
            print("  %-14s 模板缺失或画面更小" % n)
            continue
        res = cv2.matchTemplate(img, t, cv2.TM_CCOEFF_NORMED)
        _mn, mx, _ml, m = cv2.minMaxLoc(res)
        print("  %-14s %.3f @(%d,%d) %dx%d" % (n, mx, m[0] + t.shape[1] // 2,
                                              m[1] + t.shape[0] // 2, t.shape[1], t.shape[0]))


def main():
    g = B.find_game_hwnd()
    print("游戏窗口:", g, "可见区:", B.game_view_rect(g[0]) if g else "-")
    if not g:
        return
    img = shot()
    print("整屏 %dx%d，模板打分：" % (img.shape[1], img.shape[0]))
    score_all(img)
    bot = B.PanelBot(dict(B.DEFAULT, hwnd=g[0]), queue.Queue())
    print("UI 缩放 ×%.2f" % bot.sc)
    row = bot._row(img)
    print("六边形行:", row or "（英雄面板没开）")
    if "--open" in sys.argv:
        print("抢前台:", B.force_foreground(g[0]))
        im = bot._open_hero()
        print("英雄面板:", im is not None, "六边形行:", bot._row(im) if im is not None else {})
    if "--shot" in sys.argv:
        p = os.path.join(HERE, sys.argv[sys.argv.index("--shot") + 1])
        cv2.imwrite(p, img)
        print("已保存", p)


if __name__ == "__main__":
    main()
