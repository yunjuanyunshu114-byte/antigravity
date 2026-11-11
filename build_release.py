# -*- coding: utf-8 -*-
"""
生成可分发的发布包（零依赖）
==============================
用法：
    python build_release.py            # 输出到 dist/antigravity-zh-v<版本>.zip
    python build_release.py --out DIR  # 自定义输出目录

发布包内容 = 安装所需的最小集合 + 一键脚本 + 文档，解压后双击
install-windows.bat 即可完成安装（macOS / Linux 用 install-macos.sh）。
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))

# 需要打进发布包的文件 / 目录（相对仓库根目录）
INCLUDE_FILES = [
    "install.py",
    "asar.py",
    "README.md",
    "LICENSE",
    "SKILL.md",
    "VERSION",
    "install-windows.bat",
    "restore-windows.bat",
    "install-macos.sh",
    "restore-macos.sh",
]
INCLUDE_DIRS = ["dicts", "docs"]

EXECUTABLES = {"install-macos.sh", "restore-macos.sh"}


def read_version():
    path = os.path.join(HERE, "VERSION")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def validate_dictionary():
    path = os.path.join(HERE, "dicts", "zh_cn.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not data:
        sys.exit("[ERR] dicts/zh_cn.json 不是有效的词典对象")
    bad = [k for k in data if not k.strip()]
    if bad:
        sys.exit("[ERR] 词典存在空 key")
    return len(data)


def add_file(zf, src, arcname):
    info = zipfile.ZipInfo.from_file(src, arcname)
    info.compress_type = zipfile.ZIP_DEFLATED
    # 保留可执行权限（macOS / Linux 直接运行 .sh）
    mode = 0o755 if os.path.basename(src) in EXECUTABLES else 0o644
    info.external_attr = (0o100000 | mode) << 16
    with open(src, "rb") as f:
        data = f.read()
    # Windows 批处理必须是 CRLF，Unix 脚本保持 LF
    if src.lower().endswith((".bat", ".cmd")):
        data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    elif src.lower().endswith(".sh"):
        data = data.replace(b"\r\n", b"\n")
    zf.writestr(info, data)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description="生成 antigravity-zh 发布包")
    ap.add_argument("--out", default=os.path.join(HERE, "dist"), help="输出目录")
    args = ap.parse_args()

    version = read_version()
    count = validate_dictionary()
    print("[*] 版本: v%s" % version)
    print("[*] 词典: %d 条" % count)

    for rel in INCLUDE_FILES + INCLUDE_DIRS:
        if not os.path.exists(os.path.join(HERE, rel)):
            sys.exit("[ERR] 缺少文件: %s" % rel)

    os.makedirs(args.out, exist_ok=True)
    root = "antigravity-zh-v%s" % version
    out_path = os.path.join(args.out, "%s.zip" % root)

    tmp = tempfile.mkdtemp(prefix="agy_zh_rel_")
    try:
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for rel in INCLUDE_FILES:
                add_file(zf, os.path.join(HERE, rel), "%s/%s" % (root, rel))
            for d in INCLUDE_DIRS:
                src_dir = os.path.join(HERE, d)
                for name in sorted(os.listdir(src_dir)):
                    src = os.path.join(src_dir, name)
                    if not os.path.isfile(src):
                        continue
                    add_file(zf, src, "%s/%s/%s" % (root, d, name))
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    size = os.path.getsize(out_path)
    print("[OK] 发布包: %s" % out_path)
    print("[OK] 大小: %.1f KB" % (size / 1024.0))
    print("[OK] SHA256: %s" % sha256(out_path))
    print("[TIP] 解压后双击 install-windows.bat 即可安装；客户端更新后重复此步骤即可恢复汉化。")


if __name__ == "__main__":
    main()
