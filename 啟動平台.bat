@echo off
chcp 65001 >nul
title 測試案例學習平台

echo ========================================
echo    測試案例學習平台 - 啟動中
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/2] 檢查 Python...
"C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_3.11.2544.0_x64__qbz5n2kfra8p0\python3.11.exe" --version

echo.
echo [2/2] 啟動伺服器...
echo 請訪問 http://localhost:8000
echo 按 Ctrl+C 停止伺服器
echo.

"C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_3.11.2544.0_x64__qbz5n2kfra8p0\python3.11.exe" -m uvicorn main:app --port 8000

pause
