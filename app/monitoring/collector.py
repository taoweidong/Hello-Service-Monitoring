# app/monitoring/collector.py
import psutil
import platform
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import subprocess
import os
from loguru import logger
from ..utils.helpers import get_current_local_time


class SystemCollector:
    """系统信息采集器"""
    
    @staticmethod
    def get_system_info() -> Dict:
        """获取系统基本信息"""
        info = {}
        
        try:
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
                
            logger.info("系统基本信息采集成功")
        except Exception as e:
            logger.error(f"采集系统基本信息时出错: {e}")
            # 返回默认值
            info.update({
                'cpu_percent': 0,
                'memory_total': 0,
                'memory_available': 0,
                'memory_percent': 0,
                'boot_time': 0,
                'load_average': (0, 0, 0)
            })
        
        return info
    
    @staticmethod
    def get_disk_info() -> List[Dict]:
        """获取磁盘信息"""
        disks = []
        
        try:
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
                    
            logger.info(f"磁盘信息采集成功，共采集 {len(disks)} 个分区")
        except Exception as e:
            logger.error(f"采集磁盘信息时出错: {e}")
        
        return disks
    
    @staticmethod
    def get_process_info() -> List[Dict]:
        """获取进程信息"""
        processes = []
        
        try:
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
            
            # 按内存占用率排序，取前20个进程
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            processes = processes[:20]
                    
            logger.info(f"进程信息采集成功，共采集 {len(processes)} 个进程")
        except Exception as e:
            logger.error(f"采集进程信息时出错: {e}")
        
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
        
        logger.info("应用程序版本信息采集成功")
        return versions
    
    @staticmethod
    def get_detailed_system_info() -> Dict:
        """获取详细的系统信息"""
        info = {}
        
        try:
            # 操作系统信息
            info['system'] = platform.system()
            info['node'] = platform.node()
            info['release'] = platform.release()
            info['version'] = platform.version()
            info['machine'] = platform.machine()
            info['processor'] = platform.processor()
            
            # Python信息
            info['python_version'] = platform.python_version()
            info['python_compiler'] = platform.python_compiler()
            info['python_build'] = platform.python_build()
            
            # CPU详细信息
            info['cpu_count_logical'] = psutil.cpu_count(logical=True)
            info['cpu_count_physical'] = psutil.cpu_count(logical=False)
            info['cpu_freq'] = psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
            
            # 内存详细信息
            vm = psutil.virtual_memory()
            info['memory'] = {
                'total': vm.total,
                'available': vm.available,
                'percent': vm.percent,
                'used': vm.used,
                'free': vm.free,
                'active': getattr(vm, 'active', 0),
                'inactive': getattr(vm, 'inactive', 0),
                'buffers': getattr(vm, 'buffers', 0),
                'cached': getattr(vm, 'cached', 0),
                'shared': getattr(vm, 'shared', 0)
            }
            
            # 交换内存信息
            sm = psutil.swap_memory()
            info['swap_memory'] = {
                'total': sm.total,
                'used': sm.used,
                'free': sm.free,
                'percent': sm.percent,
                'sin': getattr(sm, 'sin', 0),
                'sout': getattr(sm, 'sout', 0)
            }
            
            # 网络接口信息
            info['network_interfaces'] = {}
            net_if_addrs = psutil.net_if_addrs()
            for interface, addresses in net_if_addrs.items():
                info['network_interfaces'][interface] = []
                for addr in addresses:
                    info['network_interfaces'][interface].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
            
            # 网络统计信息
            net_io = psutil.net_io_counters()
            info['network_io'] = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'dropin': net_io.dropin,
                'dropout': net_io.dropout
            }
            
            # 启动时间
            info['boot_time'] = psutil.boot_time()
            
            # 用户信息
            users = psutil.users()
            info['users'] = []
            for user in users:
                info['users'].append({
                    'name': user.name,
                    'terminal': user.terminal,
                    'host': user.host,
                    'started': user.started
                })
            
            logger.info("详细系统信息采集成功")
        except Exception as e:
            logger.error(f"采集详细系统信息时出错: {e}")
            # 返回基本的系统信息
            info.update({
                'system': platform.system(),
                'node': platform.node(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor()
            })
        
        return info