# -*- coding: utf-8 -*-
"""把 src/bot_gui.py.part1..N 拼回根目录的 bot_gui.py，并打印 sha256 便于核对

    python tools/assemble_source.py

仓库里源码分片存放只为绕开「纯文本上传接口的单次长度上限」，
本地开发不需要这个脚本（bot_gui.py 本身就是完整文件）。
"""
import glob
import hashlib
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parts = sorted(glob.glob(os.path.join(BASE, "src", "bot_gui.py.part*")))
if not parts:
    raise SystemExit("找不到 src/bot_gui.py.part*")

text = "".join(open(p, encoding="utf-8").read() for p in parts)
dst = os.path.join(BASE, "bot_gui.py")
with open(dst, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
print("拼回 %s：%d 行 / %d 字节" % (dst, text.count("\n") + (0 if text.endswith("\n") else 1),
                              len(text.encode("utf-8")))
print("sha256:", hashlib.sha256(text.encode("utf-8")).hexdigest())
