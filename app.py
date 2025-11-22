#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务器监控系统主入口文件
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from app import create_app
from app.monitoring.scheduler import MonitoringScheduler

# 配置日志
def setup_logging():
    """设置日志配置"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/monitoring.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
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
        print("正在关闭服务器监控系统...")
    finally:
        # 关闭调度器
        scheduler.shutdown()

if __name__ == '__main__':
    main()