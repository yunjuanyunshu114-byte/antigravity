@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================
echo   Antigravity 还原官方原版
echo ============================================
echo.

echo [1/2] 关闭 Antigravity ...
taskkill /IM Antigravity.exe /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/2] 用备份还原 ...
set "PY="
where python >nul 2>&1
if not errorlevel 1 set "PY=python"
if not defined PY (
  where py >nul 2>&1
  if not errorlevel 1 set "PY=py -3"
)
if not defined PY (
  echo [ERR] 未找到 Python，请先安装 Python 3.8+。
  pause
  exit /b 1
)

%PY% "%~dp0install.py" --restore
if errorlevel 1 (
  echo.
  echo [ERR] 还原失败，请查看上方错误信息。
  pause
  exit /b 1
)

echo.
echo 完成！下次启动即为官方英文原版。
timeout /t 3 /nobreak >nul
endlocal
exit /b 0
