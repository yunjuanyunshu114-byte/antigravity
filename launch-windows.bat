@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title Antigravity 汉化并启动
echo [*] 检查汉化状态...
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PY_EXE="
set "PY_ARGS="
if exist "%~dp0runtime\python.exe" set "PY_EXE=%~dp0runtime\python.exe"
if not defined PY_EXE (
  where python >nul 2>&1
  if not errorlevel 1 set "PY_EXE=python"
)
if not defined PY_EXE (
  where py >nul 2>&1
  if not errorlevel 1 (
    set "PY_EXE=py"
    set "PY_ARGS=-3"
  )
)
if not defined PY_EXE (
  echo.
  echo [ERR] 未找到 Python 运行时。
  echo       插件包自带 runtime\python.exe；若解压时丢失，请安装 Python 3.8+ 后重试。
  echo       下载：https://www.python.org/downloads/
  echo.
  pause
  exit /b 1
)
"%PY_EXE%" %PY_ARGS% "%~dp0install.py" --auto
set "AGZH_CODE=%ERRORLEVEL%"
if not "%AGZH_CODE%"=="0" (
  echo.
  echo [X] 启动失败，错误码 %AGZH_CODE%。
  echo     若提示不兼容，说明汉化已自动还原，可直接双击原版 Antigravity 图标。
  pause
  exit /b %AGZH_CODE%
)
ping -n 3 127.0.0.1 >nul
endlocal
exit /b 0
