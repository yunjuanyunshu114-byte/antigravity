#!/usr/bin/env bash
# Antigravity 一键汉化（macOS / Linux）
set -uo pipefail
cd "$(dirname "$0")"

echo "============================================"
echo "  Antigravity 一键汉化"
echo "============================================"

echo "[1/3] 关闭 Antigravity ..."
if [[ "$(uname)" == "Darwin" ]]; then
  osascript -e 'quit app "Antigravity"' >/dev/null 2>&1 || true
fi
pkill -f "Antigravity" >/dev/null 2>&1 || true
sleep 2

echo "[2/3] 注入汉化补丁 ..."
PY=""
if command -v python3 >/dev/null 2>&1; then PY="python3";
elif command -v python >/dev/null 2>&1; then PY="python";
else
  echo "[ERR] 未找到 python3，请先安装 Python 3.8+。"
  exit 1
fi

if ! "$PY" install.py "$@"; then
  echo "[ERR] 安装失败，请查看上方错误信息。"
  exit 1
fi

echo "[3/3] 启动 Antigravity ..."
if [[ "$(uname)" == "Darwin" ]]; then
  open -a "Antigravity" >/dev/null 2>&1 || echo "[提示] 请手动启动 Antigravity。"
else
  (antigravity >/dev/null 2>&1 &) || echo "[提示] 请手动启动 Antigravity。"
fi

echo "完成！"
