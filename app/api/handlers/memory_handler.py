# app/api/handlers/memory_handler.py
from flask import jsonify
from sqlalchemy import desc
from typing import Dict, List, Tuple
from datetime import timedelta
from loguru import logger

from ...database.database_manager import DatabaseManager
from ...database.models import SystemInfo

class MemoryHandler:
    """内存信息处理器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logger
    
    def get_memory_info(self) -> Tuple[Dict, int]:
        """获取内存信息API（从数据库获取最新数据和历史数据）"""
        try:
            with self.db_manager.get_session() as session:
                # 获取最新的系统信息
                latest_system_info = session.query(SystemInfo).order_by(desc(SystemInfo.timestamp)).first()
                
                # 获取最近一段时间的历史数据（例如最近1小时的数据）
                one_hour_ago = get_current_local_time() - timedelta(hours=1)
                history_data = session.query(SystemInfo.timestamp, SystemInfo.memory_percent)\
                    .filter(SystemInfo.timestamp >= one_hour_ago)\
                    .order_by(SystemInfo.timestamp)\
                    .all()
                
                # 转换历史数据为列表格式
                history_list = []
                for record in history_data:
                    history_list.append({
                        'timestamp': record.timestamp.isoformat(),
                        'memory_percent': record.memory_percent
                    })
                
                if latest_system_info:
                    response_data = {
                        'memory_percent': latest_system_info.memory_percent,
                        'history': history_list
                    }
                    return jsonify(response_data), 200
                else:
                    # 如果没有数据，返回空数据
                    return jsonify({
                        'memory_percent': 0,
                        'history': []
                    }), 200
        except Exception as e:
            self.logger.error(f"获取内存信息时出错: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_system_memory(self) -> Tuple[Dict, int]:
        """获取系统内存信息API（从数据库获取最新数据）"""
        try:
            with self.db_manager.get_session() as session:
                # 获取最新的系统信息
                latest_system_info = session.query(SystemInfo).order_by(desc(SystemInfo.timestamp)).first()
                
                if latest_system_info:
                    response_data = {
                        'memory_percent': latest_system_info.memory_percent
                    }
                    return jsonify(response_data), 200
                else:
                    # 如果没有数据，返回空数据
                    return jsonify({
                        'memory_percent': 0
                    }), 200
        except Exception as e:
            self.logger.error(f"获取内存信息时出错: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_trend_memory(self) -> Tuple[Dict, int]:
        """获取内存使用趋势数据API（从数据库获取历史数据）"""
        try:
            with self.db_manager.get_session() as session:
                # 获取最近一段时间的历史数据（例如最近1小时的数据）
                one_hour_ago = get_current_local_time() - timedelta(hours=1)
                history_data = session.query(SystemInfo.timestamp, SystemInfo.memory_percent)\
                    .filter(SystemInfo.timestamp >= one_hour_ago)\
                    .order_by(SystemInfo.timestamp)\
                    .all()
                
                # 转换历史数据为列表格式
                history_list = []
                for record in history_data:
                    history_list.append({
                        'timestamp': record.timestamp.isoformat(),
                        'memory_percent': record.memory_percent
                    })
                
                return jsonify({'history': history_list}), 200
        except Exception as e:
            self.logger.error(f"获取内存趋势数据时出错: {e}")
            return jsonify({'error': str(e)}), 500