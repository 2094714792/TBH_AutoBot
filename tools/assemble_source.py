# -*- coding: utf-8 -*-
"""把 src/bot_gui.py.partNN（9 片）拼回 bot_gui.py，并打印 sha256 便于核对

    python tools/assemble_source.py          # 只校验，不改文件
    python tools/assemble_source.py --write  # 校验并写出 bot_gui.py

分片规则（tools/split_source.py 逆向生成，两边必须一致）：
- 每片在「非空行」处断开，片与片之间用单个换行拼；
- 拼回时每片先去掉尾部换行，再统一补回文件末尾那一个换行。

仓库里源码分片存放只为绕开「纯文本上传接口的单次长度上限」，
本地开发不需要这个脚本（bot_gui.py 本身就是完整文件）。
"""
import glob
import hashlib
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = sorted(glob.glob(os.path.join(BASE, "src", "bot_gui.py.part*")),
               key=lambda p: int(re.search(r"part(\d+)", p).group(1)))
if not PARTS:
    raise SystemExit("找不到 src/bot_gui.py.part*")

text = "\n".join(open(p, encoding="utf-8").read().rstrip("\n") for p in PARTS) + "\n"
dst = os.path.join(BASE, "bot_gui.py")
sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
print("拼回 %d 片：%d 行 / %d 字节" % (len(PARTS), text.count("\n"), len(text.encode("utf-8"))))
print("sha256:", sha)

if "--write" in sys.argv:
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("已写出", dst)
elif os.path.exists(dst):
    cur = hashlib.sha256(open(dst, "rb").read()).hexdigest()
    print("与现有 bot_gui.py %s" % ("一致" if cur == sha else "不一致（加 --write 覆盖）"))