# app/api/handlers/system_handler.py
from flask import jsonify
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from loguru import logger

from ...database.database_manager import DatabaseManager
from ...database.models import SystemInfo, DiskInfo, ProcessInfo
from ...monitoring.collector import SystemCollector
from ...config.config import Config
from ...utils.helpers import get_current_local_time, format_local_time


class SystemHandler:
    """系统信息处理器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logger
    
    def get_system_info(self) -> Tuple[Dict, int]:
        """获取系统信息API（从数据库获取最新数据）"""
        try:
            with self.db_manager.get_session() as session:
                # 获取最新的系统信息
                latest_system_info = session.query(SystemInfo).order_by(desc(SystemInfo.timestamp)).first()
                
                # 获取最新的磁盘信息
                latest_disk_info = session.query(DiskInfo).order_by(desc(DiskInfo.timestamp)).all()
                
                # 获取应用程序版本信息（这部分仍需要实时获取）
                app_versions = SystemCollector.get_application_versions()
                
                if latest_system_info:
                    # 转换磁盘信息为列表格式
                    disk_list = []
                    for disk in latest_disk_info:
                        disk_list.append({
                            'device': disk.device,
                            'mountpoint': disk.mountpoint,
                            'total': disk.total,
                            'used': disk.used,
                            'free': disk.free,
                            'percent': disk.percent
                        })
                    
                    response_data = {
                        'system': {
                            'cpu_percent': latest_system_info.cpu_percent,
                            'memory_percent': latest_system_info.memory_percent,
                            'boot_time': latest_system_info.uptime,
                            'load_average': eval(latest_system_info.load_average) if latest_system_info.load_average else (0, 0, 0)
                        },
                        'disks': disk_list,
                        'applications': app_versions
                    }
                    
                    return jsonify(response_data), 200
                else:
                    # 如果没有数据，返回空数据
                    return jsonify({
                        'system': {
                            'cpu_percent': 0,
                            'memory_percent': 0,
                            'boot_time': 0,
                            'load_average': (0, 0, 0)
                        },
                        'disks': [],
                        'applications': app_versions
                    }), 200
        except Exception as e:
            self.logger.error(f"获取系统信息时出错: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_cpu_info(self) -> Tuple[Dict, int]:
        """获取CPU信息API（从数据库获取最新数据和历史数据）"""
        try:
            with self.db_manager.get_session() as session:
                # 获取最新的系统信息
                latest_system_info = session.query(SystemInfo).order_by(desc(SystemInfo.timestamp)).first()
                
                # 获取最近一段时间的历史数据（例如最近1小时的数据）
                one_hour_ago = datetime.now() - timedelta(hours=1)
                history_data = session.query(SystemInfo.timestamp, SystemInfo.cpu_percent)\
                    .filter(SystemInfo.timestamp >= one_hour_ago)\
                    .order_by(SystemInfo.timestamp)\
                    .all()
                
                # 转换历史数据为列表格式
                history_list = []
                for record in history_data:
                    history_list.append({
                        'timestamp': record.timestamp.isoformat(),
                        'cpu_percent': record.cpu_percent
                    })
                
                if latest_system_info:
                    response_data = {
                        'cpu_percent': latest_system_info.cpu_percent,
                        'load_average': eval(latest_system_info.load_average) if latest_system_info.load_average else (0, 0, 0),
                        'history': history_list
                    }
                    return jsonify(response_data), 200
                else:
                    # 如果没有数据，返回空数据
                    return jsonify({
                        'cpu_percent': 0,
                        'load_average': (0, 0, 0),
                        'history': []
                    }), 200
        except Exception as e:
            self.logger.error(f"获取CPU信息时出错: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_detailed_system_info(self) -> Tuple[Dict, int]:
        """获取详细系统信息API（实时采集）"""
        try:
            detailed_info = SystemCollector.get_detailed_system_info()
            return jsonify(detailed_info), 200
        except Exception as e:
            self.logger.error(f"获取详细系统信息时出错: {e}")
            return jsonify({'error': str(e)}), 500