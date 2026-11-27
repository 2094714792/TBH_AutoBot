# -*- coding: utf-8 -*-
"""把 src/chunks/bot_gui.py.part1..part5 拼回 bot_gui.py

用法：  python tools/assemble_bot_gui.py
输出：  仓库根目录的 bot_gui.py（UTF-8、LF 换行）
校验：  拼好的内容 sha256 必须等于 EXPECT_SHA256，否则报错退出
"""
import hashlib
import os

PARTS = 5
EXPECT_SHA256 = "85a52cb80e69417d88d807e6a957255a3fbb1f5b745ff279701753ce3c38da9a"


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "bot_gui.py")
    buf = b""
    for i in range(1, PARTS + 1):
        p = os.path.join(root, "src", "chunks", "bot_gui.py.part%d" % i)
        with open(p, "rb") as f:
            buf += f.read()
    sha = hashlib.sha256(buf).hexdigest()
    ok = sha == EXPECT_SHA256
    with open(out, "wb") as f:
        f.write(buf)
    print("wrote %s (%d bytes)" % (out, len(buf)))
    print("sha256 %s %s" % (sha, "OK" if ok else "（与记录值不同）"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
