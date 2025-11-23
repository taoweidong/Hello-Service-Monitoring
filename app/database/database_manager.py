# app/database/database_manager.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from typing import Generator, Optional, Dict, List
import os
from loguru import logger

from app.database.models import Base, SystemInfo, ProcessInfo, DiskInfo, AlertRecord
from app.config.config import Config
from app.utils.helpers import get_current_local_time


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, database_url: str = None):
        """初始化数据库连接"""
        if database_url is None:
            database_url = Config.SQLALCHEMY_DATABASE_URI
            
        self.engine = create_engine(database_url, echo=False)
        self.session_factory = scoped_session(sessionmaker(bind=self.engine))
        self.logger = logger
    
    @contextmanager
    def get_session(self) -> Generator:
        """获取数据库会话的上下文管理器"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def save_system_info(self, system_info: Dict) -> None:
        """保存系统信息"""
        try:
            with self.get_session() as session:
                system_record = SystemInfo(
                    cpu_percent=system_info.get('cpu_percent'),
                    memory_percent=system_info.get('memory_percent'),
                    disk_percent=system_info.get('disk_percent', 0),
                    uptime=system_info.get('boot_time'),
                    load_average=str(system_info.get('load_average'))
                )
                session.add(system_record)
            self.logger.info("系统信息保存成功")
        except Exception as e:
            self.logger.error(f"保存系统信息时出错: {e}")
    
    def save_process_info(self, processes: List[Dict]) -> None:
        """保存进程信息"""
        try:
            with self.get_session() as session:
                for proc in processes:
                    process_record = ProcessInfo(
                        pid=proc.get('pid'),
                        name=proc.get('name'),
                        status=proc.get('status'),
                        cpu_percent=proc.get('cpu_percent'),
                        memory_percent=proc.get('memory_percent'),
                        create_time=proc.get('create_time')
                    )
                    session.add(process_record)
            self.logger.info(f"进程信息保存成功，共保存 {len(processes)} 个进程")
        except Exception as e:
            self.logger.error(f"保存进程信息时出错: {e}")
    
    def save_disk_info(self, disks: List[Dict]) -> None:
        """保存磁盘信息"""
        try:
            with self.get_session() as session:
                for disk in disks:
                    disk_record = DiskInfo(
                        device=disk.get('device'),
                        mountpoint=disk.get('mountpoint'),
                        total=disk.get('total'),
                        used=disk.get('used'),
                        free=disk.get('free'),
                        percent=disk.get('percent')
                    )
                    session.add(disk_record)
            self.logger.info(f"磁盘信息保存成功，共保存 {len(disks)} 个磁盘分区")
        except Exception as e:
            self.logger.error(f"保存磁盘信息时出错: {e}")
    
    def save_alert_record(self, alert_type: str, message: str, is_sent: int = 0) -> None:
        """保存预警记录"""
        try:
            with self.get_session() as session:
                alert_record = AlertRecord(
                    alert_type=alert_type,
                    message=message,
                    is_sent=is_sent
                )
                session.add(alert_record)
            self.logger.info(f"预警记录保存成功: {alert_type} - {message}")
        except Exception as e:
            self.logger.error(f"保存预警记录时出错: {e}")