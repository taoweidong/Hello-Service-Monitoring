from app.models.models import ServerInfo, CPUInfo, MemoryInfo, DiskInfo, ProcessInfo
from app.services.database import DatabaseManager
from app.utils.logger import monitor_logger
import psutil
import datetime
import json

class DataCollector:
    """数据收集服务"""
    
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.db_manager = DatabaseManager()
    
    def collect_cpu_info(self):
        """收集CPU信息"""
        try:
            # 获取CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 获取CPU核心数
            cpu_count = psutil.cpu_count()
            
            # 获取CPU频率信息
            cpu_freq = psutil.cpu_freq()
            cpu_max_freq = cpu_freq.max if cpu_freq else 0
            cpu_min_freq = cpu_freq.min if cpu_freq else 0
            cpu_current_freq = cpu_freq.current if cpu_freq else 0
            
            # 保存到数据库
            cpu_info = {
                'ip_address': self.ip_address,
                'timestamp': datetime.datetime.now(),
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'cpu_max_freq': cpu_max_freq,
                'cpu_min_freq': cpu_min_freq,
                'cpu_current_freq': cpu_current_freq
            }
            
            self.db_manager.save_cpu_info(cpu_info)
            monitor_logger.info(f"收集CPU信息成功: {self.ip_address} - {cpu_percent}%")
            
            return cpu_info
        except Exception as e:
            monitor_logger.error(f"收集CPU信息失败: {e}")
            return None
    
    def collect_memory_info(self):
        """收集内存信息"""
        try:
            # 获取内存信息
            memory = psutil.virtual_memory()
            
            # 保存到数据库
            memory_info = {
                'ip_address': self.ip_address,
                'timestamp': datetime.datetime.now(),
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent
            }
            
            self.db_manager.save_memory_info(memory_info)
            monitor_logger.info(f"收集内存信息成功: {self.ip_address} - {memory.percent}%")
            
            return memory_info
        except Exception as e:
            monitor_logger.error(f"收集内存信息失败: {e}")
            return None
    
    def collect_disk_info(self):
        """收集磁盘信息"""
        try:
            # 获取磁盘信息
            disk = psutil.disk_usage('/')
            
            # 计算使用率
            disk_percent = (disk.used / disk.total) * 100 if disk.total > 0 else 0
            
            # 保存到数据库
            disk_info = {
                'ip_address': self.ip_address,
                'timestamp': datetime.datetime.now(),
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk_percent
            }
            
            self.db_manager.save_disk_info(disk_info)
            monitor_logger.info(f"收集磁盘信息成功: {self.ip_address} - {disk_percent:.2f}%")
            
            return disk_info
        except Exception as e:
            monitor_logger.error(f"收集磁盘信息失败: {e}")
            return None
    
    def collect_process_info(self):
        """收集进程信息"""
        try:
            # 获取进程列表
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'] or 0,
                        'memory_percent': proc.info['memory_percent'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # 忽略无法访问的进程
                    pass
            
            # 保存到数据库
            process_info = {
                'ip_address': self.ip_address,
                'timestamp': datetime.datetime.now(),
                'process_count': len(processes),
                'processes': processes
            }
            
            self.db_manager.save_process_info(process_info)
            monitor_logger.info(f"收集进程信息成功: {self.ip_address} - {len(processes)}个进程")
            
            return process_info
        except Exception as e:
            monitor_logger.error(f"收集进程信息失败: {e}")
            return None
    
    def collect_all_info(self):
        """收集所有系统信息"""
        try:
            # 收集各项信息
            cpu_info = self.collect_cpu_info()
            memory_info = self.collect_memory_info()
            disk_info = self.collect_disk_info()
            process_info = self.collect_process_info()
            
            monitor_logger.info(f"完成所有信息收集: {self.ip_address}")
            
            return {
                'cpu_info': cpu_info,
                'memory_info': memory_info,
                'disk_info': disk_info,
                'process_info': process_info
            }
        except Exception as e:
            monitor_logger.error(f"收集所有信息失败: {e}")
            return None
    
    def close(self):
        """关闭数据库连接"""
        self.db_manager.close()