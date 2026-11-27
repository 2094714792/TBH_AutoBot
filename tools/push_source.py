# -*- coding: utf-8 -*-
"""把本机文件原样传到 GitHub 仓库（不经过手工复制，字节级一致）。

为什么要这个脚本：GitHub 连接器只能把文件内容当文本传，58KB 的源码手抄容易失真。
用这个脚本，文件从本地磁盘直接 base64 上传，再用 git blob sha1 校验远端与本地是否完全一致。

用法（二选一）：
    python tools/push_source.py <你的 GitHub Token>
    或先 set GITHUB_TOKEN=xxx，再 python tools/push_source.py

Token 需要 fine-grained token，权限勾 "Contents: Read and write"，只给这一个仓库。
跑完可以在 https://github.com/<owner>/<repo> 上看到提交。
"""
import base64
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

OWNER = "2094714792"
REPO = "TBH_AutoBot"
BRANCH = "main"
FILES = ("bot_gui.py", "card_tpl.png", "arrow_icon.png",
         "README.md", "requirements.txt", ".gitignore")
API = "https://api.github.com"


def blob_of(path):
    """git blob sha1 —— 和 GitHub 返回的 sha 可以直接比"""
    data = open(path, "rb").read()
    return hashlib.sha1(("blob %d\0" % len(data)).encode() + data).hexdigest(), data


def request(method, url, token, payload=None):
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", "replace")
        return e.code, {"error": text}


def push_one(path, token, root):
    local_sha, data = blob_of(os.path.join(root, path))
    remote = os.path.basename(path)
    url = "%s/repos/%s/%s/contents/%s" % (API, OWNER, REPO, path)
    code, info = request("GET", url + "?ref=" + BRANCH, token)
    existing = None
    if code == 200:
        existing = info.get("sha")
        if existing == local_sha:
            print("  已一致，跳过 %s" % path)
            return True
    elif code != 404:
        print("  读取 %s 失败 HTTP %s %s" % (path, code, str(info)[:160]))
        return False
    payload = {
        "message": "更新 %s（本机直传，blob 校验一致）" % remote,
        "content": base64.b64encode(data).decode("ascii"),
        "branch": BRANCH,
    }
    if existing:
        payload["sha"] = existing
    code, info = request("PUT", url, token, payload)
    if code not in (200, 201):
        print("  写入 %s 失败 HTTP %s %s" % (path, code, str(info)[:200]))
        return False
    got = (info.get("content") or {}).get("sha")
    if got and got != local_sha:
        print("  !! %s 上传后 sha 不一致 local=%s remote=%s" % (path, local_sha, got))
        return False
    print("  ✓ %s (%d 字节, blob %s)" % (path, len(data), local_sha[:12]))
    return True


def main():
    token = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(__doc__)
        print("缺少 token。")
        return 2
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    print("推送到 %s/%s (%s)" % (OWNER, REPO, BRANCH))
    ok = 0
    for path in FILES:
        p = os.path.join(root, path)
        if not os.path.exists(p):
            print("  跳过（本地没有）%s" % path)
            continue
        if push_one(path, token, root):
            ok += 1
    print("完成：%d 个文件" % ok)
    print("仓库地址：https://github.com/%s/%s" % (OWNER, REPO))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
