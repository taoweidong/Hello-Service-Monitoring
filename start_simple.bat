@echo off
chcp 65001 >nul
title 服务器监控系统（简化版）

REM 设置Python环境变量以支持UTF-8编码
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8

echo 服务器监控系统启动脚本（简化版）
echo.

echo 检查Python是否已安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo 错误：未找到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

echo 检查依赖...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo 安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo 错误：安装依赖失败，请检查requirements.txt文件
        pause
        exit /b 1
    )
)

echo.
echo 启动服务器监控系统...
python -X utf8 app.py

pause