#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务器监控系统主入口文件
"""

import os
import sys
import io

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置标准输出编码为UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 检查是否在虚拟环境中运行
in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

if not in_venv:
    print("警告：未在虚拟环境中运行，可能会遇到依赖问题")

import time
from loguru import logger
from logging.handlers import RotatingFileHandler
from app import create_app
from app.monitoring.scheduler import MonitoringScheduler
from app.config.config import Config
from app.database.db_init import init_database

# 设置环境变量以使用本地时区
os.environ['TZ'] = Config.LOCAL_TIMEZONE
if hasattr(time, 'tzset'):
    time.tzset()

# 配置loguru日志
def setup_logging():
    """设置日志配置"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # 移除默认的日志处理器
    logger.remove()
    
    # 添加文件日志处理器
    logger.add(
        "logs/monitoring.log",
        rotation="10 MB",
        retention="10 days",
        level="INFO",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    )
    
    # 添加控制台日志处理器
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        enqueue=True,
        backtrace=True,
        diagnose=True
    )
    
    return logger

def create_app_instance():
    """创建Flask应用实例"""
    app = create_app()
    
    # 配置日志
    setup_logging()
    
    return app

def main():
    """主函数"""
    # 初始化数据库
    try:
        init_database()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return
    
    # 创建应用实例
    app = create_app_instance()
    
    # 初始化并启动监控调度器
    scheduler = MonitoringScheduler()
    scheduler.start()
    
    try:
        # 启动Flask应用
        app.run(
            host=os.environ.get('HOST') or '0.0.0.0',
            port=int(os.environ.get('PORT') or 5000),
            debug=os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']
        )
    except KeyboardInterrupt:
        logger.info("正在关闭服务器监控系统...")
    finally:
        # 关闭调度器
        scheduler.shutdown()

if __name__ == '__main__':
    main()