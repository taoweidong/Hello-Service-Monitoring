from app.models.models import Session, ServerInfo, CPUInfo, MemoryInfo, DiskInfo, ProcessInfo, AlertInfo
from app.utils.logger import monitor_logger
from datetime import datetime
import json

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.session = Session()
    
    def add_server_info(self, ip_address, hostname):
        """添加服务器信息"""
        try:
            # 检查服务器是否已存在
            server = self.session.query(ServerInfo).filter_by(ip_address=ip_address).first()
            if not server:
                server = ServerInfo(
                    ip_address=ip_address,
                    hostname=hostname,
                    created_at=datetime.now()
                )
                self.session.add(server)
                self.session.commit()
                monitor_logger.info(f"添加服务器信息: {ip_address}")
            return server
        except Exception as e:
            self.session.rollback()
            monitor_logger.error(f"添加服务器信息失败: {e}")
            return None
    
    def save_cpu_info(self, cpu_info):
        """保存CPU信息"""
        try:
            cpu = CPUInfo(
                ip_address=cpu_info['ip_address'],
                timestamp=cpu_info['timestamp'],
                cpu_percent=cpu_info['cpu_percent'],
                cpu_count=cpu_info['cpu_count'],
                cpu_max_freq=cpu_info['cpu_max_freq'],
                cpu_min_freq=cpu_info['cpu_min_freq'],
                cpu_current_freq=cpu_info['cpu_current_freq']
            )
            self.session.add(cpu)
            self.session.commit()
            monitor_logger.info(f"保存CPU信息: {cpu_info['ip_address']} - {cpu_info['cpu_percent']}%")
        except Exception as e:
            self.session.rollback()
            monitor_logger.error(f"保存CPU信息失败: {e}")
    
    def save_memory_info(self, memory_info):
        """保存内存信息"""
        try:
            memory = MemoryInfo(
                ip_address=memory_info['ip_address'],
                timestamp=memory_info['timestamp'],
                total=memory_info['total'],
                available=memory_info['available'],
                used=memory_info['used'],
                free=memory_info['free'],
                percent=memory_info['percent']
            )
            self.session.add(memory)
            self.session.commit()
            monitor_logger.info(f"保存内存信息: {memory_info['ip_address']} - {memory_info['percent']}%")
        except Exception as e:
            self.session.rollback()
            monitor_logger.error(f"保存内存信息失败: {e}")
    
    def save_disk_info(self, disk_info):
        """保存磁盘信息"""
        try:
            disk = DiskInfo(
                ip_address=disk_info['ip_address'],
                timestamp=disk_info['timestamp'],
                total=disk_info['total'],
                used=disk_info['used'],
                free=disk_info['free'],
                percent=disk_info['percent']
            )
            self.session.add(disk)
            self.session.commit()
            monitor_logger.info(f"保存磁盘信息: {disk_info['ip_address']} - {disk_info['percent']}%")
        except Exception as e:
            self.session.rollback()
            monitor_logger.error(f"保存磁盘信息失败: {e}")
    
    def save_process_info(self, process_info):
        """保存进程信息"""
        try:
            process = ProcessInfo(
                ip_address=process_info['ip_address'],
                timestamp=process_info['timestamp'],
                process_count=process_info['process_count'],
                processes=json.dumps(process_info['processes'])
            )
            self.session.add(process)
            self.session.commit()
            monitor_logger.info(f"保存进程信息: {process_info['ip_address']} - {process_info['process_count']}个进程")
        except Exception as e:
            self.session.rollback()
            monitor_logger.error(f"保存进程信息失败: {e}")
    
    def save_alert_info(self, alert_info):
        """保存预警信息"""
        try:
            alert = AlertInfo(
                ip_address=alert_info['ip_address'],
                timestamp=alert_info['timestamp'],
                alert_type=alert_info['alert_type'],
                alert_message=alert_info['alert_message'],
                is_sent=alert_info.get('is_sent', 0)
            )
            self.session.add(alert)
            self.session.commit()
            monitor_logger.info(f"保存预警信息: {alert_info['ip_address']} - {alert_info['alert_type']}")
        except Exception as e:
            self.session.rollback()
            monitor_logger.error(f"保存预警信息失败: {e}")
    
    def get_cpu_history(self, ip_address, limit=100):
        """获取CPU历史数据"""
        try:
            cpu_data = self.session.query(CPUInfo).filter_by(ip_address=ip_address).order_by(CPUInfo.timestamp.desc()).limit(limit).all()
            return [{
                'timestamp': data.timestamp,
                'cpu_percent': data.cpu_percent
            } for data in cpu_data]
        except Exception as e:
            monitor_logger.error(f"获取CPU历史数据失败: {e}")
            return []
    
    def get_memory_history(self, ip_address, limit=100):
        """获取内存历史数据"""
        try:
            memory_data = self.session.query(MemoryInfo).filter_by(ip_address=ip_address).order_by(MemoryInfo.timestamp.desc()).limit(limit).all()
            return [{
                'timestamp': data.timestamp,
                'percent': data.percent
            } for data in memory_data]
        except Exception as e:
            monitor_logger.error(f"获取内存历史数据失败: {e}")
            return []
    
    def get_disk_history(self, ip_address, limit=100):
        """获取磁盘历史数据"""
        try:
            disk_data = self.session.query(DiskInfo).filter_by(ip_address=ip_address).order_by(DiskInfo.timestamp.desc()).limit(limit).all()
            return [{
                'timestamp': data.timestamp,
                'percent': data.percent
            } for data in disk_data]
        except Exception as e:
            monitor_logger.error(f"获取磁盘历史数据失败: {e}")
            return []
    
    def get_unsent_alerts(self):
        """获取未发送的预警信息"""
        try:
            alerts = self.session.query(AlertInfo).filter_by(is_sent=0).all()
            return alerts
        except Exception as e:
            monitor_logger.error(f"获取未发送预警信息失败: {e}")
            return []
    
    def mark_alert_as_sent(self, alert_id):
        """标记预警信息为已发送"""
        try:
            alert = self.session.query(AlertInfo).filter_by(id=alert_id).first()
            if alert:
                # 使用setattr来设置属性值，避免类型检查问题
                setattr(alert, 'is_sent', 1)
                self.session.commit()
                monitor_logger.info(f"标记预警信息为已发送: {alert_id}")
        except Exception as e:
            self.session.rollback()
            monitor_logger.error(f"标记预警信息为已发送失败: {e}")
    
    def close(self):
        """关闭数据库连接"""
        self.session.close()