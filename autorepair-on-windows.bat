@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title Antigravity 汉化 - 注册开机自动修复
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
echo [*] 正在注册「登录时自动修复汉化」任务（客户端更新后自动恢复中文）...
echo.
"%PY_EXE%" %PY_ARGS% "%~dp0install.py" --install-task
set "AGZH_CODE=%ERRORLEVEL%"
echo.
if not "%AGZH_CODE%"=="0" (
  echo [X] 注册失败，错误码 %AGZH_CODE%。
  pause
  exit /b %AGZH_CODE%
)
echo [i] 取消方法：双击「取消开机自动修复.bat」。
ping -n 5 127.0.0.1 >nul
endlocal
exit /b 0
