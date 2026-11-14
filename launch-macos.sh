#!/usr/bin/env bash
# Antigravity 汉化并启动（macOS / Linux）
# 客户端更新后用它：需要时自动重新注入，然后启动客户端
set -uo pipefail
cd "$(dirname "$0")"

PY=""
if command -v python3 >/dev/null 2>&1; then PY="python3";
elif command -v python >/dev/null 2>&1; then PY="python";
else
  echo "[ERR] 未找到 python3，请先安装 Python 3.8+。"
  exit 1
fi

if ! "$PY" install.py --auto "$@"; then
  echo "[ERR] 启动失败，请查看上方输出。"
  exit 1
fi
