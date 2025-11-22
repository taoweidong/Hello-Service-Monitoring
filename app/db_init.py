# app/db_init.py
"""数据库初始化脚本"""

import os
from alembic.config import Config
from alembic import command
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect
from loguru import logger

from .config import Config as AppConfig


def init_database():
    """初始化数据库，运行所有未应用的迁移"""
    try:
        # 获取项目根目录
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 配置Alembic
        alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
        alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
        
        # 设置数据库URL
        alembic_cfg.set_main_option("sqlalchemy.url", AppConfig.SQLALCHEMY_DATABASE_URI)
        
        # 创建数据库引擎
        engine = create_engine(AppConfig.SQLALCHEMY_DATABASE_URI)
        
        # 检查是否需要初始化
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            
            # 获取所有迁移脚本
            script = ScriptDirectory.from_config(alembic_cfg)
            
            # 如果没有当前版本，说明数据库是新的，需要运行所有迁移
            if current_rev is None:
                logger.info("数据库未初始化，正在创建表结构...")
                command.upgrade(alembic_cfg, "head")
                logger.info("数据库初始化完成")
            else:
                # 检查是否有未应用的迁移
                heads = script.get_heads()
                if current_rev not in heads:
                    logger.info("发现数据库结构更新，正在应用迁移...")
                    command.upgrade(alembic_cfg, "head")
                    logger.info("数据库结构更新完成")
                else:
                    logger.info("数据库结构已是最新版本")
                    
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


def check_database_exists():
    """检查数据库是否存在"""
    try:
        engine = create_engine(AppConfig.SQLALCHEMY_DATABASE_URI)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return len(tables) > 0
    except Exception:
        return False