#!/usr/bin/env python
"""
重置数据库脚本
用于删除并重新创建MySQL数据库
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.config.config import Config
from app.utils.logger import monitor_logger

def reset_database():
    """重置数据库"""
    try:
        # 获取不带数据库名的URL
        base_url = Config.DATABASE_URL.rsplit('/', 1)[0]
        database_name = Config.DATABASE_URL.rsplit('/', 1)[1]
        
        print(f"连接到MySQL服务器: {base_url}")
        print(f"数据库名: {database_name}")
        
        # 连接到MySQL服务器（不指定数据库）
        base_engine = create_engine(base_url, echo=False)
        
        # 删除并重新创建数据库
        with base_engine.connect() as conn:
            # 结束所有活动连接
            try:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            except:
                pass
                
            # 删除数据库（如果存在）
            try:
                conn.execute(text(f"DROP DATABASE IF EXISTS `{database_name}`"))
                print(f"已删除数据库: {database_name}")
            except Exception as e:
                print(f"删除数据库时出错: {e}")
            
            # 创建新数据库
            try:
                conn.execute(text(f"CREATE DATABASE `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                print(f"已创建数据库: {database_name}")
            except Exception as e:
                print(f"创建数据库时出错: {e}")
                
            try:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            except:
                pass
            
            conn.commit()
        
        print("数据库重置完成!")
        monitor_logger.info("数据库重置完成")
        
    except Exception as e:
        print(f"数据库重置失败: {e}")
        monitor_logger.error(f"数据库重置失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_database()