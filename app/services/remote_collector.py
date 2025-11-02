import paramiko
import json
from datetime import datetime
from app.utils.logger import monitor_logger

class RemoteSystemCollector:
    """远程系统信息采集器"""
    
    def __init__(self, server_info):
        self.server_info = server_info
        self.ip_address = server_info.ip_address
        self.username = server_info.username
        self.password = server_info.password
        self.port = server_info.port or 22
        
    def _connect(self):
        """建立SSH连接"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=self.ip_address,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )
            return ssh
        except Exception as e:
            monitor_logger.error(f"连接到远程服务器 {self.ip_address} 失败: {e}")
            return None
    
    def _execute_command(self, ssh, command):
        """执行命令并返回结果"""
        try:
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()
            
            if error:
                monitor_logger.error(f"执行命令 '{command}' 出错: {error}")
                return None
                
            return output
        except Exception as e:
            monitor_logger.error(f"执行命令 '{command}' 失败: {e}")
            return None
    
    def collect_cpu_info(self):
        """采集远程服务器CPU信息"""
        ssh = self._connect()
        if not ssh:
            return None
            
        try:
            # 获取CPU使用率
            cpu_percent_output = self._execute_command(ssh, "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | sed 's/%us,//'")
            cpu_percent = float(cpu_percent_output) if cpu_percent_output else 0.0
            
            # 获取CPU核心数
            cpu_count_output = self._execute_command(ssh, "nproc")
            cpu_count = int(cpu_count_output) if cpu_count_output else 0
            
            cpu_info = {
                'ip_address': self.ip_address,
                'timestamp': datetime.now(),
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'cpu_max_freq': None,
                'cpu_min_freq': None,
                'cpu_current_freq': None
            }
            
            monitor_logger.info(f"采集远程服务器CPU信息成功: {self.ip_address}")
            return cpu_info
        except Exception as e:
            monitor_logger.error(f"采集远程服务器CPU信息失败: {e}")
            return None
        finally:
            ssh.close()
    
    def collect_memory_info(self):
        """采集远程服务器内存信息"""
        ssh = self._connect()
        if not ssh:
            return None
            
        try:
            # 获取内存信息
            mem_info_output = self._execute_command(ssh, "free -b | grep Mem")
            if mem_info_output:
                parts = mem_info_output.split()
                total = int(parts[1]) if len(parts) > 1 else 0
                used = int(parts[2]) if len(parts) > 2 else 0
                free = int(parts[3]) if len(parts) > 3 else 0
                available = int(parts[6]) if len(parts) > 6 else (free or 0)
                percent = (used / total * 100) if total > 0 else 0.0
            else:
                total = used = free = available = 0
                percent = 0.0
            
            memory_info = {
                'ip_address': self.ip_address,
                'timestamp': datetime.now(),
                'total': total,
                'available': available,
                'used': used,
                'free': free,
                'percent': percent
            }
            
            monitor_logger.info(f"采集远程服务器内存信息成功: {self.ip_address}")
            return memory_info
        except Exception as e:
            monitor_logger.error(f"采集远程服务器内存信息失败: {e}")
            return None
        finally:
            ssh.close()
    
    def collect_disk_info(self):
        """采集远程服务器磁盘信息"""
        ssh = self._connect()
        if not ssh:
            return None
            
        try:
            # 获取根分区磁盘信息
            disk_info_output = self._execute_command(ssh, "df -B1 / | tail -1")
            if disk_info_output:
                parts = disk_info_output.split()
                total = int(parts[1]) if len(parts) > 1 else 0
                used = int(parts[2]) if len(parts) > 2 else 0
                free = int(parts[3]) if len(parts) > 3 else 0
                percent = float(parts[4].replace('%', '')) if len(parts) > 4 else 0.0
            else:
                total = used = free = 0
                percent = 0.0
            
            disk_info = {
                'ip_address': self.ip_address,
                'timestamp': datetime.now(),
                'total': total,
                'used': used,
                'free': free,
                'percent': percent
            }
            
            monitor_logger.info(f"采集远程服务器磁盘信息成功: {self.ip_address}")
            return disk_info
        except Exception as e:
            monitor_logger.error(f"采集远程服务器磁盘信息失败: {e}")
            return None
        finally:
            ssh.close()
    
    def collect_hostname(self):
        """获取远程服务器主机名"""
        ssh = self._connect()
        if not ssh:
            return "unknown"
            
        try:
            hostname_output = self._execute_command(ssh, "hostname")
            return hostname_output if hostname_output else "unknown"
        except Exception as e:
            monitor_logger.error(f"获取远程服务器主机名失败: {e}")
            return "unknown"
        finally:
            ssh.close()
    
    def collect_all_info(self):
        """采集所有远程服务器信息"""
        return {
            'cpu': self.collect_cpu_info(),
            'memory': self.collect_memory_info(),
            'disk': self.collect_disk_info(),
            'hostname': self.collect_hostname()
        }