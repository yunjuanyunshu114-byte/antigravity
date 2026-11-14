@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title Antigravity 汉化插件 - 还原官方原版
echo ============================================
echo   Antigravity 汉化插件 - 还原官方原版
echo ============================================
echo.
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
echo [*] 正在还原官方原版（会校验备份与当前客户端版本是否一致）...
echo.
"%PY_EXE%" %PY_ARGS% "%~dp0install.py" --restore
set "AGZH_CODE=%ERRORLEVEL%"
echo.
if not "%AGZH_CODE%"=="0" (
  if "%AGZH_CODE%"=="4" (
    echo [X] 没有可用于当前版本的官方备份，已拒绝还原（这是为了保护客户端不被旧版本文件破坏）。
    echo     解决办法：先双击「安装汉化插件.bat」重新生成当前版本的官方备份，再还原；
    echo     或在 Antigravity 里执行「重新安装 / 修复」。
  ) else (
    echo [X] 还原失败，错误码 %AGZH_CODE%。
  )
  echo.
  pause
  exit /b %AGZH_CODE%
)
echo [OK] 已还原，下次启动即为官方英文版。
ping -n 5 127.0.0.1 >nul
endlocal
exit /b 0
