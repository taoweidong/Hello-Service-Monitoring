# app/api/handlers/disk_handler.py
from flask import jsonify
from sqlalchemy import desc, func
from typing import Dict, List, Tuple
from datetime import timedelta
from loguru import logger

from app.database.database_manager import DatabaseManager
from app.database.models import DiskInfo, SystemInfo
from app.monitoring.collector import SystemCollector
from app.config.config import Config
from app.utils.helpers import get_current_local_time  # 添加缺失的导入

class DiskHandler:
    """磁盘信息处理器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logger
    
    def get_disk_info(self) -> Tuple[Dict, int]:
        """获取磁盘信息API（从数据库获取最新数据和历史数据）"""
        try:
            with self.db_manager.get_session() as session:
                # 获取最新的磁盘信息
                # 获取最新的时间戳
                latest_timestamp = session.query(func.max(DiskInfo.timestamp)).first()
                
                if latest_timestamp and latest_timestamp[0]:
                    # 只获取最新时间戳的数据
                    latest_disk_info = session.query(DiskInfo).filter(
                        DiskInfo.timestamp == latest_timestamp[0]
                    ).all()
                else:
                    latest_disk_info = []
                
                # 获取最近一段时间的历史数据（例如最近1小时的数据）
                one_hour_ago = get_current_local_time() - timedelta(hours=1)
                # 获取所有磁盘分区的历史数据
                history_data = session.query(DiskInfo.timestamp, DiskInfo.device, DiskInfo.percent)\
                    .filter(DiskInfo.timestamp >= one_hour_ago)\
                    .order_by(DiskInfo.timestamp)\
                    .all()
                
                # 按设备分组历史数据
                history_by_device = {}
                for record in history_data:
                    device = record.device
                    if device not in history_by_device:
                        history_by_device[device] = []
                    history_by_device[device].append({
                        'timestamp': record.timestamp.isoformat(),
                        'percent': record.percent
                    })
                
                # 获取应用程序版本信息（这部分仍需要实时获取）
                app_versions = SystemCollector.get_application_versions()
                
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
                
                # 计算最大磁盘使用率
                max_disk_percent = 0
                for disk in disk_list:
                    if disk['percent'] > max_disk_percent:
                        max_disk_percent = disk['percent']
                
                # 转换时间为ISO格式字符串
                collection_time = None
                if latest_timestamp and latest_timestamp[0]:
                    collection_time = latest_timestamp[0].isoformat()
                
                response_data = {
                    'disks': disk_list,
                    'max_disk_percent': max_disk_percent,
                    'applications': app_versions,
                    'collection_time': collection_time,
                    'history': history_by_device
                }
                
                return jsonify(response_data), 200
        except Exception as e:
            self.logger.error(f"获取磁盘信息时出错: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_system_disk(self) -> Tuple[Dict, int]:
        """获取系统磁盘信息API（从数据库获取最新数据）"""
        try:
            with self.db_manager.get_session() as session:
                # 获取最新的磁盘信息
                # 获取最新的时间戳
                latest_timestamp = session.query(func.max(DiskInfo.timestamp)).first()
                
                if latest_timestamp and latest_timestamp[0]:
                    # 只获取最新时间戳的数据
                    latest_disk_info = session.query(DiskInfo).filter(
                        DiskInfo.timestamp == latest_timestamp[0]
                    ).all()
                else:
                    latest_disk_info = []
                
                # 获取应用程序版本信息（这部分仍需要实时获取）
                app_versions = SystemCollector.get_application_versions()
                
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
                
                # 计算最大磁盘使用率
                max_disk_percent = 0
                for disk in disk_list:
                    if disk['percent'] > max_disk_percent:
                        max_disk_percent = disk['percent']
                
                # 转换时间为ISO格式字符串
                collection_time = None
                if latest_timestamp and latest_timestamp[0]:
                    collection_time = latest_timestamp[0].isoformat()
                
                response_data = {
                    'disks': disk_list,
                    'max_disk_percent': max_disk_percent,
                    'applications': app_versions,
                    'collection_time': collection_time
                }
                
                return jsonify(response_data), 200
        except Exception as e:
            self.logger.error(f"获取磁盘信息时出错: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_trend_disk(self) -> Tuple[Dict, int]:
        """获取磁盘使用趋势数据API（从数据库获取历史数据）"""
        try:
            with self.db_manager.get_session() as session:
                # 获取最近一段时间的历史数据（例如最近1小时的数据）
                one_hour_ago = get_current_local_time() - timedelta(hours=1)
                # 获取所有磁盘分区的历史数据
                history_data = session.query(DiskInfo.timestamp, DiskInfo.device, DiskInfo.percent)\
                    .filter(DiskInfo.timestamp >= one_hour_ago)\
                    .order_by(DiskInfo.timestamp)\
                    .all()
                
                # 按设备分组历史数据
                history_by_device = {}
                for record in history_data:
                    device = record.device
                    if device not in history_by_device:
                        history_by_device[device] = []
                    history_by_device[device].append({
                        'timestamp': record.timestamp.isoformat(),
                        'percent': record.percent
                    })
                
                return jsonify({'history': history_by_device}), 200
        except Exception as e:
            self.logger.error(f"获取磁盘趋势数据时出错: {e}")
            return jsonify({'error': str(e)}), 500