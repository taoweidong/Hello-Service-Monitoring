import psutil
import socket
from datetime import datetime
from app.logger import monitor_logger

class SystemCollector:
    """系统信息采集器"""
    
    def __init__(self):
        self.hostname = socket.gethostname()
        self.ip_address = self._get_ip_address()
        
    def _get_ip_address(self):
        """获取本机IP地址"""
        try:
            # 获取本机IP地址
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            monitor_logger.error(f"获取IP地址失败: {e}")
            return "127.0.0.1"
    
    def collect_cpu_info(self):
        """采集CPU信息"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            cpu_info = {
                'ip_address': self.ip_address,
                'timestamp': datetime.now(),
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'cpu_max_freq': cpu_freq.max if cpu_freq else None,
                'cpu_min_freq': cpu_freq.min if cpu_freq else None,
                'cpu_current_freq': cpu_freq.current if cpu_freq else None
            }
            
            monitor_logger.info(f"采集CPU信息成功")
            return cpu_info
        except Exception as e:
            monitor_logger.error(f"采集CPU信息失败: {e}")
            return None
    
    def collect_memory_info(self):
        """采集内存信息"""
        try:
            memory = psutil.virtual_memory()
            
            memory_info = {
                'ip_address': self.ip_address,
                'timestamp': datetime.now(),
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent
            }
            
            monitor_logger.info(f"采集内存信息: {memory_info}")
            return memory_info
        except Exception as e:
            monitor_logger.error(f"采集内存信息失败: {e}")
            return None
    
    def collect_disk_info(self):
        """采集磁盘信息"""
        try:
            disk_usage = psutil.disk_usage('/')
            
            disk_info = {
                'ip_address': self.ip_address,
                'timestamp': datetime.now(),
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percent': disk_usage.percent
            }
            
            monitor_logger.info(f"采集磁盘信息: {disk_info}")
            return disk_info
        except Exception as e:
            monitor_logger.error(f"采集磁盘信息失败: {e}")
            return None
    
    def collect_process_info(self):
        """采集进程信息"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            process_info = {
                'ip_address': self.ip_address,
                'timestamp': datetime.now(),
                'process_count': len(processes),
                'processes': processes[:50]  # 只保留前50个进程
            }
            
            monitor_logger.info(f"采集进程信息，共{len(processes)}个进程")
            return process_info
        except Exception as e:
            monitor_logger.error(f"采集进程信息失败: {e}")
            return None
    
    def collect_all_info(self):
        """采集所有系统信息"""
        return {
            'cpu': self.collect_cpu_info(),
            'memory': self.collect_memory_info(),
            'disk': self.collect_disk_info(),
            'process': self.collect_process_info()
        }