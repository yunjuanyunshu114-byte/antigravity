#!/usr/bin/env bash
# Antigravity 一键汉化（macOS / Linux）
# v1.5.0：注入后自动启动；macOS/Linux 不执行冒烟测试（Windows 专有）
set -uo pipefail
cd "$(dirname "$0")"

echo "============================================"
echo "  Antigravity 一键汉化"
echo "============================================"

PY=""
if command -v python3 >/dev/null 2>&1; then PY="python3";
elif command -v python >/dev/null 2>&1; then PY="python";
else
  echo "[ERR] 未找到 python3，请先安装 Python 3.8+。"
  exit 1
fi

echo "[*] 注入汉化（需要时自动备份官方原版）..."
if ! "$PY" install.py --launch "$@"; then
  echo "[ERR] 安装失败，请查看上方错误信息。"
  echo "      若提示备份版本不一致，请先重新运行本脚本生成当前版本备份。"
  exit 1
fi

echo "[OK] 完成。客户端更新后，运行 ./launch-macos.sh 或重新运行本脚本即可快速恢复汉化。"
