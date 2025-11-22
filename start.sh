#!/bin/bash

# 服务器监控系统启动脚本

# 创建虚拟环境
echo "创建虚拟环境..."
python -m venv venv

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 创建必要目录
echo "创建必要目录..."
mkdir -p logs monitoring

# 启动应用
echo "启动服务器监控系统..."
python app.py