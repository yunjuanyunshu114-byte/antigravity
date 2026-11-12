@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title Antigravity 汉化插件 - 还原官方原版

echo ============================================
echo   Antigravity 汉化插件 - 还原官方原版
echo ============================================
echo.

echo [1/2] 关闭 Antigravity ...
taskkill /IM Antigravity.exe /F >nul 2>&1
ping -n 3 127.0.0.1 >nul

echo [2/2] 用备份还原 ...
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
if exist "%~dp0runtime\python.exe" (
  "%~dp0runtime\python.exe" "%~dp0install.py" --restore
  goto :after
)
where python >nul 2>&1
if not errorlevel 1 (
  python "%~dp0install.py" --restore
  goto :after
)
where py >nul 2>&1
if not errorlevel 1 (
  py -3 "%~dp0install.py" --restore
  goto :after
)
echo.
echo [ERR] 未找到 Python 运行时。
echo.
pause
exit /b 1

:after
if errorlevel 1 (
  echo.
  echo [ERR] 还原失败，请查看上方错误信息。
  echo       备份通常在 %%USERPROFILE%%\.antigravity-zh\backup\ 下。
  echo.
  pause
  exit /b 1
)

echo.
echo 完成！下次启动即为官方英文原版。
ping -n 4 127.0.0.1 >nul
endlocal
exit /b 0
