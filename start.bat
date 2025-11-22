@echo off
chcp 65001 >nul
title 服务器监控系统

REM 设置Python环境变量以支持UTF-8编码
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8

echo 服务器监控系统启动脚本
echo.

REM 检查是否已经存在虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo 发现现有虚拟环境，跳过创建步骤...
    goto activate_venv
)

REM 创建虚拟环境
echo 创建虚拟环境...
python -m venv .venv
if errorlevel 1 (
    echo.
    echo 错误：创建虚拟环境失败，请检查以下事项：
    echo 1. 确保您已安装Python
    echo 2. 确保您有足够的权限在当前目录创建文件
    echo 3. 确保当前目录没有被其他程序占用
    echo.
    echo 尝试以管理员身份运行此脚本...
    pause
    exit /b 1
)

:activate_venv
REM 激活虚拟环境
echo 激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo.
    echo 错误：激活虚拟环境失败
    pause
    exit /b 1
)

REM 升级pip
echo 升级pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo.
    echo 警告：升级pip失败，将继续执行...
)

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo 错误：安装依赖失败，请检查requirements.txt文件
    pause
    exit /b 1
)

echo.
echo 启动服务器监控系统...
python -X utf8 app.py

pause