# -*- coding: utf-8 -*-
"""
打包 Antigravity 汉化插件（零依赖的「插件包」）
================================================
用法：
    python build_release.py                 # 生成 dist/Antigravity汉化插件-v<ver>.zip（自带 Python 运行时）
    python build_release.py --slim          # 不内置 Python 运行时（体积小，需系统已装 Python）
    python build_release.py --out DIR       # 自定义输出目录

包内结构（解压后双击「安装汉化插件.bat」即可，无需 git、无需装 Python）：

    Antigravity汉化插件/
    ├── 安装汉化插件.bat
    ├── 还原官方原版.bat
    ├── 使用说明.txt
    ├── install.py / asar.py
    ├── dicts/ docs/
    └── runtime/            ← Windows 免安装 Python 运行时（--slim 时不含）
"""
import argparse
import hashlib
import json
import os
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))

PKG_NAME = "Antigravity汉化插件"
RUNTIME_DIR = os.path.join(HERE, "runtime")

# 仓库文件名 -> 包内文件名
RENAME = {
    "install-windows.bat": "安装汉化插件.bat",
    "restore-windows.bat": "还原官方原版.bat",
}

INCLUDE_FILES = [
    "install-windows.bat",
    "restore-windows.bat",
    "install-macos.sh",
    "restore-macos.sh",
    "install.py",
    "asar.py",
    "README.md",
    "LICENSE",
    "VERSION",
]
INCLUDE_DIRS = ["dicts", "docs"]

EXECUTABLES = {"install-macos.sh", "restore-macos.sh"}

USAGE_TXT = """\
Antigravity 汉化插件 v{version}
================================

这是给 Google Antigravity 桌面客户端用的中文界面插件包。
不需要 git，不需要自己装 Python——解压后双击就能用。

一、安装（约 15 秒）
--------------------
1. 双击「安装汉化插件.bat」
2. 脚本会自动：关闭 Antigravity → 注入汉化 → 重新启动客户端
3. 看到中文界面即安装成功

二、客户端更新后汉化消失？
--------------------------
正常现象。官方更新会用原版文件覆盖补丁。
再双击一次「安装汉化插件.bat」即可恢复，词典和备份都还在。

三、还原英文原版
----------------
双击「还原官方原版.bat」。

官方原版备份保存在两个地方，客户端更新清掉一个也不怕：
  - Antigravity\\resources\\app.asar.bak
  - %USERPROFILE%\\.antigravity-zh\\backup\\app.asar.orig

四、自己加词条（可选）
----------------------
改 %USERPROFILE%\\.antigravity-zh\\zh-CN.json 后保存，界面会自动重翻（无需重装）。

五、macOS / Linux
-----------------
    ./install-macos.sh      # 安装
    ./restore-macos.sh      # 还原
需要系统自带 python3。

六、更多
--------
- 翻译机制详解：docs/HOW_IT_WORKS.md
- 项目主页：https://github.com/yunjuanyunshu114-byte/antigravity-zh-plugin
- 非官方语言包，修改的是本地 app.asar，风险自负
"""


def read_version():
    with open(os.path.join(HERE, "VERSION"), "r", encoding="utf-8") as f:
        return f.read().strip()


def validate_dictionary():
    with open(os.path.join(HERE, "dicts", "zh_cn.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not data:
        sys.exit("[ERR] dicts/zh_cn.json 不是有效的词典对象")
    bad = [k for k in data if not k.strip()]
    if bad:
        sys.exit("[ERR] 词典存在空 key")
    return len(data)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def add_bytes(zf, arcname, data, mode=0o644):
    info = zipfile.ZipInfo(arcname, date_time=time.localtime()[:6])
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o100000 | mode) << 16
    zf.writestr(info, data)


def add_file(zf, src, arcname, mode=0o644):
    with open(src, "rb") as f:
        data = f.read()
    # Windows 批处理必须是 CRLF，Unix 脚本保持 LF
    if src.lower().endswith((".bat", ".cmd")):
        data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    elif src.lower().endswith(".sh"):
        data = data.replace(b"\r\n", b"\n")
    add_bytes(zf, arcname, data, mode)


def main():
    ap = argparse.ArgumentParser(description="打包 Antigravity 汉化插件")
    ap.add_argument("--out", default=os.path.join(HERE, "dist"), help="输出目录")
    ap.add_argument("--slim", action="store_true", help="不内置 Python 运行时")
    args = ap.parse_args()

    version = read_version()
    count = validate_dictionary()
    has_runtime = os.path.exists(os.path.join(RUNTIME_DIR, "python.exe"))
    with_runtime = has_runtime and not args.slim

    print("[*] 版本: v%s" % version)
    print("[*] 词典: %d 条" % count)
    print("[*] 内置运行时: %s" % ("是" if with_runtime else "否"))

    missing = [r for r in INCLUDE_FILES + INCLUDE_DIRS if not os.path.exists(os.path.join(HERE, r))]
    if missing:
        sys.exit("[ERR] 缺少文件: %s" % ", ".join(missing))

    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, "%s-v%s.zip" % (PKG_NAME, version))
    root = "%s-v%s" % (PKG_NAME, version)

    total = 0
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in INCLUDE_FILES:
            name = RENAME.get(rel, rel)
            add_file(
                zf,
                os.path.join(HERE, rel),
                "%s/%s" % (root, name),
                mode=0o755 if rel in EXECUTABLES else 0o644,
            )
            total += 1
        for d in INCLUDE_DIRS:
            src_dir = os.path.join(HERE, d)
            for name in sorted(os.listdir(src_dir)):
                src = os.path.join(src_dir, name)
                if os.path.isfile(src):
                    add_file(zf, src, "%s/%s/%s" % (root, d, name))
                    total += 1
        add_bytes(zf, "%s/使用说明.txt" % root,
                  USAGE_TXT.format(version=version).encode("utf-8"))
        total += 1

        if with_runtime:
            for name in sorted(os.listdir(RUNTIME_DIR)):
                src = os.path.join(RUNTIME_DIR, name)
                if os.path.isfile(src):
                    add_file(zf, src, "%s/runtime/%s" % (root, name), mode=0o755)
                    total += 1

    size = os.path.getsize(out_path)
    digest = sha256(out_path)
    with open(out_path + ".sha256", "w", encoding="utf-8", newline="\n") as f:
        f.write("%s  %s\n" % (digest, os.path.basename(out_path)))

    print("[OK] 插件包: %s" % out_path)
    print("[OK] 文件数: %d" % total)
    print("[OK] 大小: %.1f MB" % (size / 1024.0 / 1024.0))
    print("[OK] SHA256: %s" % digest)
    print("[TIP] 解压后双击「安装汉化插件.bat」即可；客户端每次更新后重复一次即可恢复。")


if __name__ == "__main__":
    main()
