# -*- coding: utf-8 -*-
"""把 bot_gui.py 切成 src/bot_gui.py.partNN（9 片）——assemble_source.py 的逆向

    python tools/split_source.py            # 只打印每片行数/字节，不写文件
    python tools/split_source.py --write    # 写出 src/bot_gui.py.partNN

规则（与 assemble_source.py 必须一致）：
- 按字节累计，超过 LIMIT 就在最近的「非空行」后断开，避免片尾的空行被拼回时吃掉；
- 每片去掉尾部换行存放（上传接口会在末尾补一个换行），拼回时用单个换行连接。
"""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMIT = 7800                       # 单次上传的长度上限约 9.3KB，留 1.5KB 余量

src = os.path.join(BASE, "bot_gui.py")
text = open(src, encoding="utf-8", newline="").read()

parts, cur, n = [], [], 0
for ln in text.splitlines(keepends=True):
    if n + len(ln.encode()) <= LIMIT:
        cur.append(ln)
        n += len(ln.encode())
        continue
    while cur and not cur[-1].strip():          # 片尾空行让给下一片
        n -= len(cur[-1].encode())
        cur.pop()
    parts.append("".join(cur).rstrip("\n"))
    cur, n = [ln], len(ln.encode())
    if n > LIMIT:
        raise SystemExit("单行过长（%d 字节），无法按期切片" % n)
if cur:
    parts.append("".join(cur).rstrip("\n"))

print("切成 %d 片，最大 %d 字节" % (len(parts), max(len(p.encode()) for p in parts)))
for i, p in enumerate(parts, 1):
    print("  part%02d  %4d 行  %5d 字节" % (i, p.count("\n") + 1, len(p.encode())))

if "--write" in sys.argv:
    d = os.path.join(BASE, "src")
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.startswith("bot_gui.py.part"):
            os.remove(os.path.join(d, f))
    for i, p in enumerate(parts, 1):
        with open(os.path.join(d, "bot_gui.py.part%02d" % i), "w", encoding="utf-8", newline="\n") as f:
            f.write(p)
    print("已写出", d)