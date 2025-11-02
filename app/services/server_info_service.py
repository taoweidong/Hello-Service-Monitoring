"""服务器信息服务模块 - 负责收集和展示服务器详细信息"""
import psutil
import platform
import socket
from datetime import datetime, timedelta
from app.services.database import DatabaseManager
from app.utils.logger import monitor_logger
from app.models.models import RemoteServer


class ServerInfoService:
    """服务器信息服务类"""
    
    def __init__(self, ip_address=None):
        self.db_manager = DatabaseManager()
        self.ip_address = ip_address or self._get_local_ip()
    
    def _get_local_ip(self):
        """获取本地IP地址"""
        try:
            # 连接到一个远程地址（不需要真正连接）
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def get_detailed_server_info(self):
        """获取详细的服务器信息"""
        try:
            # 首先检查是否是远程服务器
            remote_server = self.db_manager.session.query(RemoteServer).filter_by(ip_address=self.ip_address).first()
            
            if remote_server:
                # 这是一个远程服务器，使用远程采集器
                from app.services.remote_collector import RemoteSystemCollector
                collector = RemoteSystemCollector(remote_server)
                remote_info = collector.collect_all_info()
                
                # 如果连接失败，返回连接失败状态
                if remote_info.get('connection_failed', False):
                    return {
                        'ip_address': self.ip_address,
                        'hostname': 'Unknown',
                        'system_version': 'Unknown',
                        'kernel_version': 'Unknown',
                        'platform': 'Unknown',
                        'architecture': 'Unknown',
                        'processor': 'Unknown',
                        'cpu_count': 'N/A',
                        'cpu_count_logical': 'N/A',
                        'total_memory': 'N/A',
                        'total_disk': 'N/A',
                        'uptime': 'N/A',
                        'boot_time': 'N/A',
                        'network_interfaces': [],
                        'disk_partitions': [],
                        'connection_failed': True  # 标记连接失败
                    }
                else:
                    # 连接成功，返回基本的服务器信息
                    return {
                        'ip_address': self.ip_address,
                        'hostname': remote_info.get('hostname', 'Unknown'),
                        'system_version': 'Unknown',
                        'kernel_version': 'Unknown',
                        'platform': 'Linux',
                        'architecture': 'Unknown',
                        'processor': 'Unknown',
                        'cpu_count': 'N/A',
                        'cpu_count_logical': 'N/A',
                        'total_memory': 'N/A',
                        'total_disk': 'N/A',
                        'uptime': 'N/A',
                        'boot_time': 'N/A',
                        'network_interfaces': [],
                        'disk_partitions': [],
                        'connection_failed': False  # 连接成功
                    }
            else:
                # 这是本地服务器，获取本地系统信息
                info = {
                    'ip_address': self.ip_address,
                    'hostname': socket.gethostname(),
                    'system_version': self._get_system_version(),
                    'kernel_version': platform.release(),
                    'platform': platform.system(),
                    'architecture': platform.machine(),
                    'processor': platform.processor(),
                    'cpu_count': psutil.cpu_count(logical=False),  # 物理核心数
                    'cpu_count_logical': psutil.cpu_count(logical=True),  # 逻辑核心数
                    'total_memory': self._format_bytes(psutil.virtual_memory().total),
                    'total_disk': self._format_bytes(psutil.disk_usage('/').total),
                    'uptime': self._get_uptime(),
                    'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'),
                    'network_interfaces': self._get_network_interfaces(),
                    'disk_partitions': self._get_disk_partitions(),
                    'connection_failed': False  # 默认连接成功
                }
                return info
        except Exception as e:
            monitor_logger.error(f"获取服务器详细信息失败: {e}")
            # 返回基本的服务器信息，并标记连接失败
            return {
                'ip_address': self.ip_address,
                'hostname': 'Unknown',
                'system_version': 'Unknown',
                'kernel_version': 'Unknown',
                'platform': 'Unknown',
                'architecture': 'Unknown',
                'processor': 'Unknown',
                'cpu_count': 'N/A',
                'cpu_count_logical': 'N/A',
                'total_memory': 'N/A',
                'total_disk': 'N/A',
                'uptime': 'N/A',
                'boot_time': 'N/A',
                'network_interfaces': [],
                'disk_partitions': [],
                'connection_failed': True  # 标记连接失败
            }
    
    def _get_system_version(self):
        """获取系统版本"""
        try:
            if platform.system() == 'Windows':
                return f"{platform.system()} {platform.release()} {platform.version()}"
            elif platform.system() == 'Linux':
                try:
                    with open('/etc/os-release', 'r') as f:
                        for line in f:
                            if line.startswith('PRETTY_NAME'):
                                return line.split('=')[1].strip().strip('"')
                except:
                    pass
                return f"{platform.system()} {platform.release()}"
            else:
                return f"{platform.system()} {platform.release()}"
        except:
            return platform.system()
    
    def _get_uptime(self):
        """获取系统运行时间"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{days}天 {hours}小时 {minutes}分钟"
        except:
            return "未知"
    
    def _get_network_interfaces(self):
        """获取网络接口信息"""
        try:
            interfaces = []
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for interface_name, addrs in net_if_addrs.items():
                if interface_name == 'lo' or not interface_name:
                    continue
                
                # 获取接口状态
                is_up = False
                if interface_name in net_if_stats:
                    stat = net_if_stats[interface_name]
                    is_up = getattr(stat, 'isup', False)
                
                interface_info = {
                    'name': interface_name,
                    'addresses': [],
                    'is_up': is_up
                }
                
                for addr in addrs:
                    if addr.family == socket.AF_INET:  # IPv4
                        interface_info['addresses'].append({
                            'type': 'IPv4',
                            'address': addr.address,
                            'netmask': addr.netmask
                        })
                    elif addr.family == socket.AF_INET6:  # IPv6
                        interface_info['addresses'].append({
                            'type': 'IPv6',
                            'address': addr.address
                        })
                
                if interface_info['addresses']:
                    interfaces.append(interface_info)
            
            return interfaces[:5]  # 只返回前5个接口
        except Exception as e:
            monitor_logger.error(f"获取网络接口信息失败: {e}")
            return []
    
    def _get_disk_partitions(self):
        """获取磁盘分区信息"""
        try:
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': self._format_bytes(usage.total),
                        'used': self._format_bytes(usage.used),
                        'free': self._format_bytes(usage.free),
                        'percent': (usage.used / usage.total * 100) if usage.total > 0 else 0
                    })
                except PermissionError:
                    continue
            return partitions[:5]  # 只返回前5个分区
        except Exception as e:
            monitor_logger.error(f"获取磁盘分区信息失败: {e}")
            return []
    
    def _format_bytes(self, bytes_value):
        """格式化字节大小"""
        try:
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes_value < 1024.0:
                    return f"{bytes_value:.2f} {unit}"
                bytes_value /= 1024.0
            return f"{bytes_value:.2f} PB"
        except:
            return "未知"
    
    def get_current_metrics(self):
        """获取当前监控指标"""
        try:
            # 获取最新的监控数据
            cpu_data = self.db_manager.get_latest_cpu_info(self.ip_address)
            memory_data = self.db_manager.get_latest_memory_info(self.ip_address)
            disk_data = self.db_manager.get_latest_disk_info(self.ip_address)
            
            return {
                'cpu': cpu_data,
                'memory': memory_data,
                'disk': disk_data
            }
        except Exception as e:
            monitor_logger.error(f"获取当前监控指标失败: {e}")
            return None
    
    def get_trend_statistics(self, hours=24):
        """获取趋势统计信息"""
        try:
            # 计算时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # 获取历史数据
            cpu_history = self.db_manager.get_cpu_history_by_time_range(self.ip_address, start_time, end_time)
            memory_history = self.db_manager.get_memory_history_by_time_range(self.ip_address, start_time, end_time)
            disk_history = self.db_manager.get_disk_history_by_time_range(self.ip_address, start_time, end_time)
            
            return {
                'cpu': cpu_history,
                'memory': memory_history,
                'disk': disk_history
            }
        except Exception as e:
            monitor_logger.error(f"获取趋势统计信息失败: {e}")
            return None
    
    def close(self):
        """关闭数据库连接"""
        self.db_manager.close()