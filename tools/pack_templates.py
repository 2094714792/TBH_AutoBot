# -*- coding: utf-8 -*-
"""把 12 张散装模板 png 打包成一张 templates.png（也可反向拆回单图方便编辑）

用法：
    python tools/pack_templates.py            # 打包：根目录 png → templates.png，并打印 TPLS 表
    python tools/pack_templates.py --split    # 拆图：templates.png → tpl_src/*.png
"""
import os
import sys

import cv2
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATLAS = os.path.join(BASE, "templates.png")
NAMES = ["card_tpl", "arrow_icon", "hex_store", "hex_attr", "hex_rune", "hex_cube",
         "hex_gem", "wh_store", "wh_back", "cube_fill", "cube_exec_on", "cube_exec_off"]
MARGIN, GAP = 2, 4


def pack():
    imgs, x = [], MARGIN
    src = os.path.join(BASE, "tpl_src")
    for n in NAMES:
        p = os.path.join(src, n + ".png")               # 优先用重拍的单图
        if not os.path.isfile(p):
            p = os.path.join(BASE, n + ".png")
        if not os.path.isfile(p):
            sys.exit("缺少 %s（既没有 tpl_src/%s.png 也没有根目录 %s.png）" % (n, n, n))
        im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
        h, w = im.shape[:2]
        imgs.append((n, im, x))
        x += w + GAP
    W, H = x - GAP + MARGIN, max(im.shape[0] for _, im, _ in imgs) + 2 * MARGIN
    canvas = np.zeros((H, W, 3), np.uint8)
    print("TPLS = {")
    for n, im, x0 in imgs:
        canvas[MARGIN:MARGIN + im.shape[0], x0:x0 + im.shape[1]] = im[:, :, :3]
        print('    "%-12s": (%4d, %d, %3d, %2d),' % (n, x0, MARGIN, im.shape[1], im.shape[0]))
    print("}")
    cv2.imwrite(ATLAS, canvas)
    print("已生成 %s  %dx%d" % (ATLAS, W, H))


def split():
    sys.path.insert(0, BASE)
    from bot_gui import TPLS  # noqa: 复用主程序的坐标表，避免两处不一致
    atlas = cv2.imread(ATLAS)
    d = os.path.join(BASE, "tpl_src")
    os.makedirs(d, exist_ok=True)
    for n, (x, y, w, h) in TPLS.items():
        cv2.imwrite(os.path.join(d, n + ".png"), atlas[y:y + h, x:x + w])
        print("拆出", n + ".png")


if __name__ == "__main__":
    split() if "--split" in sys.argv else pack()
