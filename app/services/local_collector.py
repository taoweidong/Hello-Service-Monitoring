import psutil
import socket
from app.services.data_collector import DataCollector

class LocalSystemCollector(DataCollector):
    """本地系统数据收集器"""
    
    def __init__(self):
        # 获取本机IP地址
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        
        super().__init__(ip_address)
        self.hostname = hostname
    
    def get_system_info(self):
        """获取基本系统信息"""
        return {
            'hostname': self.hostname,
            'ip_address': self.ip_address
        }