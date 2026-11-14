#!/usr/bin/env bash
# Antigravity 还原官方原版（macOS / Linux）
# v1.5.0：会校验备份版本与当前客户端是否一致，不一致拒绝还原
set -uo pipefail
cd "$(dirname "$0")"

echo "============================================"
echo "  Antigravity 还原官方原版"
echo "============================================"

PY=""
if command -v python3 >/dev/null 2>&1; then PY="python3";
elif command -v python >/dev/null 2>&1; then PY="python";
else
  echo "[ERR] 未找到 python3，请先安装 Python 3.8+。"
  exit 1
fi

"$PY" install.py --restore "$@"
code=$?
if [ "$code" -ne 0 ]; then
  echo "[ERR] 还原失败（退出码 $code）。"
  echo "      退出码 4 表示没有与当前客户端版本匹配的官方备份（保护机制）。"
  echo "      解决办法：先运行 ./install-macos.sh 生成当前版本备份，再还原。"
  exit "$code"
fi

echo "[OK] 下次启动即为官方英文原版。"
