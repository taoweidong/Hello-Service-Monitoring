@echo off
chcp 65001 >nul
title 停止服务器监控系统

echo 停止服务器监控系统...

REM 查找并终止Python应用进程
for /f "tokens=2" %%i in ('tasklist ^| findstr "python.*app.py"') do (
    echo 终止进程 PID: %%i
    taskkill /PID %%i /F
)

echo 服务器监控系统已停止
echo.
echo 按任意键退出...
pause >nul