@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title Antigravity 汉化插件 - 安装

echo ============================================
echo   Antigravity 汉化插件 - 安装
echo ============================================
echo.

echo [1/3] 关闭 Antigravity ...
taskkill /IM Antigravity.exe /F >nul 2>&1
ping -n 3 127.0.0.1 >nul

echo [2/3] 注入汉化（约 10 秒）...
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
if exist "%~dp0runtime\python.exe" (
  "%~dp0runtime\python.exe" "%~dp0install.py" %*
  goto :after
)
where python >nul 2>&1
if not errorlevel 1 (
  python "%~dp0install.py" %*
  goto :after
)
where py >nul 2>&1
if not errorlevel 1 (
  py -3 "%~dp0install.py" %*
  goto :after
)
echo.
echo [ERR] 未找到 Python 运行时。
echo       本插件包自带 runtime\python.exe；若解压时丢失，请安装 Python 3.8+
echo       后重试：https://www.python.org/downloads/
echo.
pause
exit /b 1

:after
if errorlevel 1 (
  echo.
  echo [ERR] 安装失败，请查看上方错误信息。
  echo.
  pause
  exit /b 1
)

echo.
echo [3/3] 启动 Antigravity ...
set "AGY="
if exist "%LOCALAPPDATA%\Programs\Antigravity\Antigravity.exe" set "AGY=%LOCALAPPDATA%\Programs\Antigravity\Antigravity.exe"
if not defined AGY if exist "%ProgramFiles%\Antigravity\Antigravity.exe" set "AGY=%ProgramFiles%\Antigravity\Antigravity.exe"
if not defined AGY if exist "%ProgramFiles(x86)%\Antigravity\Antigravity.exe" set "AGY=%ProgramFiles(x86)%\Antigravity\Antigravity.exe"

if defined AGY (
  start "" "%AGY%" >nul 2>&1
  echo 完成！Antigravity 已重新启动，界面应为中文。
) else (
  echo [提示] 未在默认路径找到 Antigravity.exe，请手动启动客户端。
)

echo.
ping -n 4 127.0.0.1 >nul
endlocal
exit /b 0
