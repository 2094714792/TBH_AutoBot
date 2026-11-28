# -*- coding: utf-8 -*-
"""截取挂机助手窗口（只取可见、未最小化的那个），用于交付前目检界面"""
import ctypes
import os

import cv2
import mss
import numpy as np
import win32gui

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

HERE = os.path.dirname(os.path.abspath(__file__))
cand = []


def cb(h, _):
    t = win32gui.GetWindowText(h)
    if "挂机" in t and win32gui.IsWindowVisible(h) and not win32gui.IsIconic(h):
        r = win32gui.GetWindowRect(h)
        cand.append((r[2] - r[0], h, r, t))


win32gui.EnumWindows(cb, None)
print("candidates:", [(c[3], c[2]) for c in cand])
if not cand:
    raise SystemExit("no window")
_w, _h, r, t = sorted(cand)[-1]
print("picked", t, r)
with mss.mss() as s:
    img = np.array(s.grab({"left": r[0], "top": r[1],
                           "width": r[2] - r[0], "height": r[3] - r[1]}))[:, :, :3]
cv2.imwrite(os.path.join(HERE, "app_shot.png"), img)
print("saved", img.shape)
