#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务器监控系统主入口文件
"""

import os
import sys
from loguru import logger
from logging.handlers import RotatingFileHandler
from app import create_app
from app.monitoring.scheduler import MonitoringScheduler

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
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
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