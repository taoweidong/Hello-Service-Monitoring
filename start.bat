@echo off
title 服务器监控系统

echo 服务器监控系统启动脚本
echo.

REM 创建虚拟环境
echo 创建虚拟环境...
python -m venv .venv

REM 激活虚拟环境
echo 激活虚拟环境...
call .venv\Scripts\activate

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

REM 创建必要目录
echo 创建必要目录...
mkdir logs 2>nul
mkdir monitoring 2>nul

REM 启动应用
echo 启动服务器监控系统...
python app.py

pause