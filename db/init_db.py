#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库初始化脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.db_init import init_database
from loguru import logger

if __name__ == "__main__":
    try:
        init_database()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        sys.exit(1)