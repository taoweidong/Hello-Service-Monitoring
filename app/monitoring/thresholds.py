# app/monitoring/thresholds.py
from typing import Dict, List
from loguru import logger

from app.config.config import Config
from app.database.database_manager import DatabaseManager
from app.monitoring.collector import SystemCollector


class ThresholdChecker:
    """阈值检查器"""
    
    def __init__(self, db_manager: DatabaseManager):
        """初始化阈值检查器"""
        self.db_manager = db_manager
        self.logger = logger
    
    def check_system_thresholds(self) -> None:
        """检查系统资源阈值"""
        try:
            self.logger.info("开始检查系统资源阈值")
            
            # 获取最新的系统信息
            system_info = SystemCollector.get_system_info()
            disk_info = SystemCollector.get_disk_info()
            
            # 检查内存使用率
            memory_percent = system_info.get('memory_percent', 0)
            if memory_percent > Config.MEMORY_THRESHOLD:
                message = f"内存使用率过高: {memory_percent}%"
                self.db_manager.save_alert_record("memory", message)
                self.send_alert("memory", message)
            
            # 检查磁盘使用率
            for disk in disk_info:
                disk_percent = disk.get('percent', 0)
                if disk_percent > Config.DISK_THRESHOLD:
                    message = f"磁盘 {disk['device']} 使用率过高: {disk_percent}%"
                    self.db_manager.save_alert_record("disk", message)
                    self.send_alert("disk", message)
            
            self.logger.info("系统资源阈值检查完成")
        except Exception as e:
            self.logger.error(f"检查系统资源阈值时出错: {e}")
    
    def send_alert(self, alert_type: str, message: str) -> None:
        """发送预警消息"""
        # 这里可以实现多种预警方式，目前只实现钉钉预警
        self.send_dingtalk_alert(message)
    
    def send_dingtalk_alert(self, message: str) -> None:
        """发送钉钉预警消息"""
        import requests
        import json
        
        if not Config.DINGTALK_WEBHOOK:
            self.logger.warning("未配置钉钉Webhook，无法发送预警消息")
            return
        
        try:
            # 使用本地时间
            from app.utils.helpers import get_current_local_time
            current_time = get_current_local_time().strftime('%Y-%m-%d %H:%M:%S')
            payload = {
                "msgtype": "text",
                "text": {
                    "content": f"[服务器监控预警] {message}\n时间: {current_time}"
                }
            }
            
            response = requests.post(Config.DINGTALK_WEBHOOK, json=payload)
            if response.status_code == 200:
                self.logger.info("钉钉预警消息发送成功")
            else:
                self.logger.error(f"钉钉预警消息发送失败: {response.text}")
        except Exception as e:
            self.logger.error(f"发送钉钉预警消息时出错: {e}")