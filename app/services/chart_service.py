"""图表服务模块 - 负责生成图表数据"""
from datetime import datetime, timedelta
from app.services.database import DatabaseManager
from app.utils.logger import monitor_logger


class ChartService:
    """图表服务类"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_chart_data(self, ip_address, time_range='1h'):
        """获取图表数据
        
        Args:
            ip_address: 服务器IP地址
            time_range: 时间范围 ('1h', '6h', '24h', '7d')
        
        Returns:
            包含CPU、内存、磁盘数据的字典
        """
        try:
            # 计算时间范围
            end_time = datetime.now()
            if time_range == '1h':
                start_time = end_time - timedelta(hours=1)
            elif time_range == '6h':
                start_time = end_time - timedelta(hours=6)
            elif time_range == '24h':
                start_time = end_time - timedelta(hours=24)
            elif time_range == '7d':
                start_time = end_time - timedelta(days=7)
            else:
                start_time = end_time - timedelta(hours=1)
            
            # 获取数据
            cpu_data = self.db_manager.get_cpu_history_by_time_range(ip_address, start_time, end_time)
            memory_data = self.db_manager.get_memory_history_by_time_range(ip_address, start_time, end_time)
            disk_data = self.db_manager.get_disk_history_by_time_range(ip_address, start_time, end_time)
            
            # 格式化数据
            result = {
                'cpu': self._format_data(cpu_data, 'cpu_percent', time_range),
                'memory': self._format_data(memory_data, 'percent', time_range),
                'disk': self._format_data(disk_data, 'percent', time_range)
            }
            
            return result
        except Exception as e:
            monitor_logger.error(f"获取图表数据失败: {e}")
            return {'cpu': [], 'memory': [], 'disk': []}
    
    def _format_data(self, data, value_key, time_range):
        """格式化数据为图表可用格式"""
        if not data:
            return {
                'labels': [],
                'values': [],
                'stats': {}
            }
        
        # 根据时间范围决定数据点间隔
        if time_range == '7d':
            # 7天数据，可能需要聚合
            step = max(1, len(data) // 100)  # 最多显示100个点
            data = data[::step]
        
        # 反转数据（因为查询结果是倒序的）
        data = list(reversed(data))
        
        labels = []
        values = []
        
        for item in data:
            timestamp = item['timestamp']
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            
            # 格式化时间标签
            if time_range == '7d':
                label = timestamp.strftime('%m/%d %H:%M')
            elif time_range == '24h':
                label = timestamp.strftime('%H:%M')
            else:
                label = timestamp.strftime('%H:%M:%S')
            
            labels.append(label)
            value = item.get(value_key, 0)
            values.append(float(value) if value is not None else 0)
        
        # 计算统计信息
        if values:
            stats = {
                'min': round(min(values), 2),
                'max': round(max(values), 2),
                'avg': round(sum(values) / len(values), 2),
                'current': values[-1] if values else 0
            }
        else:
            stats = {
                'min': 0,
                'max': 0,
                'avg': 0,
                'current': 0
            }
        
        return {
            'labels': labels,
            'values': values,
            'stats': stats
        }
    
    def get_trend_statistics(self, ip_address, hours=24):
        """获取趋势统计信息"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # 获取数据
            cpu_data = self.db_manager.get_cpu_history_by_time_range(ip_address, start_time, end_time)
            memory_data = self.db_manager.get_memory_history_by_time_range(ip_address, start_time, end_time)
            disk_data = self.db_manager.get_disk_history_by_time_range(ip_address, start_time, end_time)
            
            statistics = {}
            
            # CPU统计
            if cpu_data:
                cpu_values = [d['cpu_percent'] for d in cpu_data if d.get('cpu_percent') is not None]
                if cpu_values:
                    statistics['cpu'] = {
                        'min': round(min(cpu_values), 2),
                        'max': round(max(cpu_values), 2),
                        'avg': round(sum(cpu_values) / len(cpu_values), 2),
                        'count': len(cpu_values)
                    }
            
            # 内存统计
            if memory_data:
                memory_values = [d['percent'] for d in memory_data if d.get('percent') is not None]
                if memory_values:
                    statistics['memory'] = {
                        'min': round(min(memory_values), 2),
                        'max': round(max(memory_values), 2),
                        'avg': round(sum(memory_values) / len(memory_values), 2),
                        'count': len(memory_values)
                    }
            
            # 磁盘统计
            if disk_data:
                disk_values = [d['percent'] for d in disk_data if d.get('percent') is not None]
                if disk_values:
                    statistics['disk'] = {
                        'min': round(min(disk_values), 2),
                        'max': round(max(disk_values), 2),
                        'avg': round(sum(disk_values) / len(disk_values), 2),
                        'count': len(disk_values)
                    }
            
            return statistics
        except Exception as e:
            monitor_logger.error(f"获取趋势统计信息失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        self.db_manager.close()

