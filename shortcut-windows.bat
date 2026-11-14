@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title Antigravity 汉化 - 创建桌面快捷方式
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
"%PY_EXE%" %PY_ARGS% "%~dp0install.py" --create-shortcut
set "AGZH_CODE=%ERRORLEVEL%"
echo.
if not "%AGZH_CODE%"=="0" (
  echo [X] 创建失败，错误码 %AGZH_CODE%。
  pause
  exit /b %AGZH_CODE%
)
ping -n 5 127.0.0.1 >nul
endlocal
exit /b 0
