#!/usr/bin/env bash
# Antigravity 还原官方原版（macOS / Linux）
set -uo pipefail
cd "$(dirname "$0")"

echo "============================================"
echo "  Antigravity 还原官方原版"
echo "============================================"

echo "[1/2] 关闭 Antigravity ..."
if [[ "$(uname)" == "Darwin" ]]; then
  osascript -e 'quit app "Antigravity"' >/dev/null 2>&1 || true
fi
pkill -f "Antigravity" >/dev/null 2>&1 || true
sleep 2

echo "[2/2] 用备份还原 ..."
PY=""
if command -v python3 >/dev/null 2>&1; then PY="python3";
elif command -v python >/dev/null 2>&1; then PY="python";
else
  echo "[ERR] 未找到 python3，请先安装 Python 3.8+。"
  exit 1
fi

if ! "$PY" install.py --restore; then
  echo "[ERR] 还原失败，请查看上方错误信息。"
  exit 1
fi

echo "完成！下次启动即为官方英文原版。"
