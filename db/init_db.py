#!/usr/bin/env python
"""
数据库初始化脚本
用于创建MySQL数据库和表结构
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.models import init_db
from app.utils.logger import monitor_logger

def main():
    """主函数"""
    try:
        print("开始初始化数据库...")
        init_db()
        print("数据库初始化完成!")
        monitor_logger.info("数据库初始化脚本执行成功")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        monitor_logger.error(f"数据库初始化脚本执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()