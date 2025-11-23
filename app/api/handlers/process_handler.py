# app/api/handlers/process_handler.py
from flask import jsonify
from sqlalchemy import desc, func
from typing import Dict, List, Tuple
from loguru import logger

from app.database.database_manager import DatabaseManager
from app.database.models import ProcessInfo

class ProcessHandler:
    """进程信息处理器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logger
    
    def get_processes(self) -> Tuple[Dict, int]:
        """获取进程信息API（从数据库获取最新数据）"""
        try:
            with self.db_manager.get_session() as session:
                # 获取最新的进程信息
                # 获取最新的时间戳
                latest_timestamp = session.query(func.max(ProcessInfo.timestamp)).first()
                
                if latest_timestamp and latest_timestamp[0]:
                    # 只获取最新时间戳的数据
                    latest_processes = session.query(ProcessInfo).filter(
                        ProcessInfo.timestamp == latest_timestamp[0]
                    ).all()
                else:
                    latest_processes = []
                
                # 转换为列表格式
                processes_list = []
                for proc in latest_processes:
                    processes_list.append({
                        'pid': proc.pid,
                        'name': proc.name,
                        'status': proc.status,
                        'cpu_percent': proc.cpu_percent,
                        'memory_percent': proc.memory_percent,
                        'create_time': proc.create_time
                    })
                
                # 按内存占用率排序，取前20个进程
                processes_list.sort(key=lambda x: x['memory_percent'], reverse=True)
                processes_list = processes_list[:20]
                
                # 转换时间为ISO格式字符串
                collection_time = None
                if latest_timestamp and latest_timestamp[0]:
                    collection_time = latest_timestamp[0].isoformat()
                
                return jsonify({
                    'processes': processes_list,
                    'collection_time': collection_time
                }), 200
        except Exception as e:
            self.logger.error(f"获取进程信息时出错: {e}")
            return jsonify({'error': str(e)}), 500