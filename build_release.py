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

PKG_NAME = "Antigravity汉化插件"          # 包内文件夹名（中文）
ZIP_NAME = "Antigravity-zh-plugin"        # 下载文件名（GitHub 资产名只支持 ASCII）
RUNTIME_DIR = os.path.join(HERE, "runtime")

# 仓库文件名 -> 包内文件名
RENAME = {
    "install-windows.bat": "安装汉化插件.bat",
    "restore-windows.bat": "还原官方原版.bat",
    "launch-windows.bat": "汉化并启动.bat",
    "autorepair-on-windows.bat": "注册开机自动修复.bat",
    "autorepair-off-windows.bat": "取消开机自动修复.bat",
    "shortcut-windows.bat": "创建桌面快捷方式.bat",
}

INCLUDE_FILES = [
    "install-windows.bat",
    "restore-windows.bat",
    "launch-windows.bat",
    "autorepair-on-windows.bat",
    "autorepair-off-windows.bat",
    "shortcut-windows.bat",
    "install-macos.sh",
    "restore-macos.sh",
    "launch-macos.sh",
    "install.py",
    "asar.py",
    "README.md",
    "LICENSE",
    "VERSION",
]
INCLUDE_DIRS = ["dicts", "docs"]

EXECUTABLES = {"install-macos.sh", "restore-macos.sh", "launch-macos.sh"}

USAGE_TXT = r"""Antigravity 汉化插件 v{version}
================================

这是给 Google Antigravity 桌面客户端用的中文界面插件包。
不需要 git、不需要安装 Python——解压后双击就能用。

零、开始之前（重要）
--------------------
v1.5.0 的安装器会「先自检、再留下」：
  - 注入后会自动启动一次客户端做冒烟测试；
  - 如果这个版本不兼容导致起不来，安装器会【自动还原官方版本】，
    客户端仍然可以正常打开（不会出现「装了汉化就打不开」的情况）；
  - 还原只接受与当前客户端版本一致的备份，避免把旧版文件还原到新客户端。

一、安装（约 20~40 秒）
------------------------
1. 解压本插件包到任意目录（路径建议不含特殊符号）
2. 双击「安装汉化插件.bat」
3. 脚本会自动：关闭 Antigravity → 注入汉化 → 自检并启动客户端
4. 看到中文界面即安装成功；若提示「不兼容」，说明已自动还原，客户端不受影响。

二、客户端更新后汉化消失？（这是正常的）
----------------------------------------
官方更新会替换 resources 目录，汉化必然消失。三种恢复方式任选：

  A. 最快：双击「汉化并启动.bat」
     检测到未汉化会自动重新注入，然后启动客户端（十几秒）。
  B. 一劳永逸：双击「注册开机自动修复.bat」
     之后每次登录系统都会自动检查并修复（客户端更新后无需手动操作）。
     取消：双击「取消开机自动修复.bat」。
  C. 双击「创建桌面快捷方式.bat」，以后从桌面「Antigravity 汉化版」图标启动，
     它指向「汉化并启动.bat」，更新后会自动重新汉化。

三、还原英文原版
----------------
双击「还原官方原版.bat」。安装器会校验备份版本与当前客户端是否一致，
版本不一致会拒绝还原（防止客户端打不开）；此时按提示先重装一次汉化即可刷新备份。

官方原版备份保存在两个地方，客户端更新清掉一个也不怕：
  - Antigravity\resources\app.asar.bak
  - %USERPROFILE%\.antigravity-zh\backup\app.asar.orig

四、自己加词条（可选）
----------------------
改 %USERPROFILE%\.antigravity-zh\zh-CN.json 后保存，界面会自动重翻（无需重装）。

五、macOS / Linux
-----------------
    ./install-macos.sh      # 安装
    ./restore-macos.sh      # 还原
    ./launch-macos.sh       # 汉化并启动（客户端更新后用）
需要系统自带 python3（macOS/Linux 平台不做冒烟测试）。

六、出问题了？
--------------
- 安装日志：%USERPROFILE%\.antigravity-zh\logs\install-*.log
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
    out_path = os.path.join(args.out, "%s-v%s.zip" % (ZIP_NAME, version))
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
