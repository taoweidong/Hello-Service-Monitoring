#!/bin/bash

# 服务器监控系统停止脚本

echo "正在停止服务器监控系统..."

# 查找并终止应用进程
pids=$(ps aux | grep "app.py" | grep -v grep | awk '{print $2}')

if [ -z "$pids" ]; then
    echo "未找到正在运行的服务器监控系统进程"
else
    for pid in $pids; do
        echo "终止进程 PID: $pid"
        kill $pid
    done
    echo "服务器监控系统已停止"
fi