@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title Antigravity 汉化插件 - 安装
echo ============================================
echo   Antigravity 汉化插件 - 安装
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
echo [*] 正在关闭客户端、注入汉化并自检（约 15~40 秒，请勿关闭本窗口）...
echo.
"%PY_EXE%" %PY_ARGS% "%~dp0install.py" --launch
set "AGZH_CODE=%ERRORLEVEL%"
echo.
if not "%AGZH_CODE%"=="0" (
  if "%AGZH_CODE%"=="3" (
    echo [X] 汉化补丁与当前客户端版本不兼容。
    echo     安装器已【自动还原官方版本】，客户端仍然可以正常打开。
    echo     请把上面的日志文件发给作者，等待适配。
  ) else (
    echo [X] 安装失败，错误码 %AGZH_CODE%，详见上方输出与日志。
  )
  echo.
  pause
  exit /b %AGZH_CODE%
)
echo [OK] 安装完成，Antigravity 应以中文界面打开。
echo [i] 客户端自动更新后，双击「汉化并启动.bat」即可快速恢复汉化。
ping -n 5 127.0.0.1 >nul
endlocal
exit /b 0
