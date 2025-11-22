# app/collector.py
import psutil
import platform
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import subprocess
import os


class SystemCollector:
    """系统信息采集器"""
    
    @staticmethod
    def get_system_info() -> Dict:
        """获取系统基本信息"""
        info = {}
        
        # CPU信息
        info['cpu_percent'] = psutil.cpu_percent(interval=1)
        
        # 内存信息
        memory = psutil.virtual_memory()
        info['memory_total'] = memory.total
        info['memory_available'] = memory.available
        info['memory_percent'] = memory.percent
        
        # 系统启动时间
        info['boot_time'] = psutil.boot_time()
        
        # 系统负载（仅在Unix系统上可用）
        try:
            info['load_average'] = os.getloadavg()
        except AttributeError:
            # Windows系统不支持
            info['load_average'] = (0, 0, 0)
        
        return info
    
    @staticmethod
    def get_disk_info() -> List[Dict]:
        """获取磁盘信息"""
        disks = []
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disk_info = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'file_system': partition.fstype,
                    'total': partition_usage.total,
                    'used': partition_usage.used,
                    'free': partition_usage.free,
                    'percent': round(partition_usage.used / partition_usage.total * 100, 2)
                }
                disks.append(disk_info)
            except PermissionError:
                # 忽略无法访问的分区
                continue
        
        return disks
    
    @staticmethod
    def get_process_info() -> List[Dict]:
        """获取进程信息"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'create_time']):
            try:
                process_info = {
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'status': proc.info['status'],
                    'cpu_percent': proc.info['cpu_percent'] or 0.0,
                    'memory_percent': proc.info['memory_percent'] or 0.0,
                    'create_time': proc.info['create_time']
                }
                processes.append(process_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # 忽略无法访问的进程
                continue
        
        return processes
    
    @staticmethod
    def get_application_versions() -> Dict[str, str]:
        """获取应用程序版本信息"""
        versions = {}
        
        # 获取Python版本
        versions['python'] = platform.python_version()
        
        # 获取Java版本
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True, timeout=5)
            if result.stderr:
                versions['java'] = result.stderr.split('\n')[0]
            else:
                versions['java'] = "未安装"
        except (subprocess.CalledProcessError, FileNotFoundError):
            versions['java'] = "未安装"
        
        # 获取Docker版本
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=5)
            if result.stdout:
                versions['docker'] = result.stdout.strip()
            else:
                versions['docker'] = "未安装"
        except (subprocess.CalledProcessError, FileNotFoundError):
            versions['docker'] = "未安装"
        
        return versions