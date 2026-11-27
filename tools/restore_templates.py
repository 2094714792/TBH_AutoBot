"""把仓库里的 *.b64 还原成识别用模板图。

GitHub 只能推送文本，二进制图片以 base64 存放；跑一次这个脚本就能得到
card_tpl.png / arrow_icon.png，且必须放在 bot_gui.py（或打包后的 exe）同目录。

用法：  python tools/restore_templates.py
"""
import base64
import os

PAIRS = {
    "card_tpl.png": "tools/card_tpl.png.b64",   # 宝箱卡片 62x44
    "arrow_icon.png": "tools/arrow_icon.png.b64",  # 右下角金盾 25x29
}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, ".."))
    for out_name, src_rel in PAIRS.items():
        src = os.path.join(root, src_rel)
        if not os.path.exists(src):
            print("缺少 %s，跳过 %s" % (src_rel, out_name))
            continue
        with open(src, "rb") as f:
            data = base64.b64decode(f.read().strip())
        out = os.path.join(root, out_name)
        with open(out, "wb") as f:
            f.write(data)
        print("已还原 %s (%d 字节)" % (out_name, len(data)))


if __name__ == "__main__":
    main()
