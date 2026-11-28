# -*- coding: utf-8 -*-
"""运行时回归：真的驱动 PanelBot 存仓（可选魔方），并做一次仓库双向验证

    python dev/selftest.py            # 1 轮，开魔方
    python dev/selftest.py 2 0        # 2 轮，不合成
"""
import os
import queue
import sys
import time

import cv2
import win32gui

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import bot_gui as B

ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 1
CUBE = int(sys.argv[2]) if len(sys.argv) > 2 else 1


def drain(q):
    while True:
        try:
            _k, m = q.get_nowait()
        except queue.Empty:
            return
        print("   " + m)


def check_tpls():
    print("== 模板图集 ==")
    for n in ("card_tpl", "arrow_icon", "hex_rune", "hex_store", "wh_store",
              "wh_back", "cube_fill", "cube_exec_on", "cube_exec_off"):
        t = B.load_tpl(n)
        print("  %-14s %s" % (n, "缺失" if t is None else "%dx%d" % (t.shape[1], t.shape[0])))


def main():
    check_tpls()
    g = B.find_game_hwnd()
    if not g:
        print("没找到游戏窗口")
        return 1
    hwnd, cls, title = g
    print("game hwnd=%d cls=%s title=%s 可见区=%s" % (hwnd, cls, title,
                                                B.game_view_rect(hwnd, B.new_sct())))
    q = queue.Queue()
    cfg = dict(B.DEFAULT)
    cfg.update(hwnd=hwnd, hwnd_title=title, follow=1, region=None,
               bag=1, bag_interval=600, wh_click=3, cube=CUBE, cube_times=2, fg_steal=1)
    bot = B.PanelBot(cfg, q, None)

    prev = win32gui.GetForegroundWindow()
    print("抢前台:", B.force_foreground(hwnd))
    time.sleep(0.6)

    for r in range(1, ROUNDS + 1):
        print("== 第 %d 轮 ==" % r)
        t0 = time.time()
        ok = bot.store()
        drain(q)
        print("   成功=%s 用时 %.1fs 仓库占用 %.3f" % (ok, time.time() - t0, bot.bag))
        cv2.imwrite(os.path.join(HERE, "round%d.png" % r), bot._shot())
        time.sleep(1.5)

    # 双向验证：拉出 → 存回
    img = bot._shot()
    btn, ready = bot._wh_anchor(img)
    if ready:
        occ0 = bot._wh_frac(img, btn)
        bot._click(btn[0] - bot.WH_BACK_DX, btn[1])
        time.sleep(0.7)
        occ1 = bot._wh_frac(bot._shot(), btn)
        for _ in range(3):
            bot._click(*btn)
        time.sleep(0.7)
        occ2 = bot._wh_frac(bot._shot(), btn)
        print("双向：%.3f -(拉出)-> %.3f -(存回)-> %.3f  %s" % (
            occ0, occ1, occ2,
            "成立" if occ1 < occ0 - 0.02 and occ2 > occ1 + 0.02 else "没动，需要再查"))
    bot.esc(3)
    try:
        if prev and win32gui.IsWindow(prev):
            win32gui.SetForegroundWindow(prev)
    except Exception as e:
        print("还原前台失败", e)
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
