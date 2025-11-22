# app/routes.py
from flask import Blueprint, jsonify, render_template, send_from_directory
import os
from .database import DatabaseManager
from .config import Config
from sqlalchemy import desc
import json
import socket
from loguru import logger
from .utils import format_local_time

main_bp = Blueprint('main', __name__)
db_manager = DatabaseManager(Config.SQLALCHEMY_DATABASE_URI)


@main_bp.route('/favicon.ico')
def favicon():
    """Favicon路由"""
    # 获取项目根目录
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    static_dir = os.path.join(base_dir, 'static')
    
    # 检查favicon文件是否存在
    favicon_path = os.path.join(static_dir, 'favicon.ico')
    if os.path.exists(favicon_path):
        return send_from_directory(static_dir, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    else:
        # 如果favicon不存在，返回空响应
        return '', 204


def get_server_ip():
    """获取服务器主网卡IP地址"""
    try:
        # 方法1: 通过连接外部地址获取本地IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # 连接到一个外部地址（不需要真实存在）
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        return ip
    except Exception:
        try:
            # 方法2: 获取主机名对应的IP
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return ip
        except Exception:
            # 方法3: 返回localhost
            return "127.0.0.1"


@main_bp.route('/')
def index():
    """首页视图"""
    return render_template('index.html')


@main_bp.route('/api/server-ip')
def api_server_ip():
    """获取服务器IP地址API"""
    try:
        ip = get_server_ip()
        return jsonify({'ip': ip})
    except Exception as e:
        logger.error(f"获取服务器IP地址时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/system-info')
def api_system_info():
    """获取系统信息API（从数据库获取最新数据）"""
    try:
        with db_manager.get_session() as session:
            # 获取最新的系统信息
            from .models import SystemInfo, DiskInfo
            latest_system_info = session.query(SystemInfo).order_by(desc(SystemInfo.timestamp)).first()
            
            # 获取最新的磁盘信息
            latest_disk_info = session.query(DiskInfo).order_by(desc(DiskInfo.timestamp)).all()
            
            # 获取应用程序版本信息（这部分仍需要实时获取）
            from .collector import SystemCollector
            app_versions = SystemCollector.get_application_versions()
            
            if latest_system_info:
                # 转换磁盘信息为列表格式
                disk_list = []
                for disk in latest_disk_info:
                    disk_list.append({
                        'device': disk.device,
                        'mountpoint': disk.mountpoint,
                        'total': disk.total,
                        'used': disk.used,
                        'free': disk.free,
                        'percent': disk.percent
                    })
                
                response_data = {
                    'system': {
                        'cpu_percent': latest_system_info.cpu_percent,
                        'memory_percent': latest_system_info.memory_percent,
                        'boot_time': latest_system_info.uptime,
                        'load_average': eval(latest_system_info.load_average) if latest_system_info.load_average else (0, 0, 0)
                    },
                    'disks': disk_list,
                    'applications': app_versions
                }
                
                return jsonify(response_data)
            else:
                # 如果没有数据，返回空数据
                return jsonify({
                    'system': {
                        'cpu_percent': 0,
                        'memory_percent': 0,
                        'boot_time': 0,
                        'load_average': (0, 0, 0)
                    },
                    'disks': [],
                    'applications': app_versions
                })
    except Exception as e:
        logger.error(f"获取系统信息时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/cpu-info')
def api_cpu_info():
    """获取CPU信息API（从数据库获取最新数据和历史数据）"""
    try:
        with db_manager.get_session() as session:
            # 获取最新的系统信息
            from .models import SystemInfo
            latest_system_info = session.query(SystemInfo).order_by(desc(SystemInfo.timestamp)).first()
            
            # 获取最近一段时间的历史数据（例如最近1小时的数据）
            from datetime import datetime, timedelta
            one_hour_ago = datetime.now() - timedelta(hours=1)
            history_data = session.query(SystemInfo.timestamp, SystemInfo.cpu_percent)\
                .filter(SystemInfo.timestamp >= one_hour_ago)\
                .order_by(SystemInfo.timestamp)\
                .all()
            
            # 转换历史数据为列表格式
            history_list = []
            for record in history_data:
                history_list.append({
                    'timestamp': record.timestamp.isoformat(),
                    'cpu_percent': record.cpu_percent
                })
            
            if latest_system_info:
                response_data = {
                    'cpu_percent': latest_system_info.cpu_percent,
                    'load_average': eval(latest_system_info.load_average) if latest_system_info.load_average else (0, 0, 0),
                    'history': history_list
                }
                return jsonify(response_data)
            else:
                # 如果没有数据，返回空数据
                return jsonify({
                    'cpu_percent': 0,
                    'load_average': (0, 0, 0),
                    'history': []
                })
    except Exception as e:
        logger.error(f"获取CPU信息时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/memory-info')
def api_memory_info():
    """获取内存信息API（从数据库获取最新数据和历史数据）"""
    try:
        with db_manager.get_session() as session:
            # 获取最新的系统信息
            from .models import SystemInfo
            latest_system_info = session.query(SystemInfo).order_by(desc(SystemInfo.timestamp)).first()
            
            # 获取最近一段时间的历史数据（例如最近1小时的数据）
            from datetime import datetime, timedelta
            from .utils import get_current_local_time
            one_hour_ago = get_current_local_time() - timedelta(hours=1)
            history_data = session.query(SystemInfo.timestamp, SystemInfo.memory_percent)\
                .filter(SystemInfo.timestamp >= one_hour_ago)\
                .order_by(SystemInfo.timestamp)\
                .all()
            
            # 转换历史数据为列表格式
            history_list = []
            for record in history_data:
                history_list.append({
                    'timestamp': record.timestamp.isoformat(),
                    'memory_percent': record.memory_percent
                })
            
            if latest_system_info:
                response_data = {
                    'memory_percent': latest_system_info.memory_percent,
                    'history': history_list
                }
                return jsonify(response_data)
            else:
                # 如果没有数据，返回空数据
                return jsonify({
                    'memory_percent': 0,
                    'history': []
                })
    except Exception as e:
        logger.error(f"获取内存信息时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/disk-info')
def api_disk_info():
    """获取磁盘信息API（从数据库获取最新数据和历史数据）"""
    try:
        with db_manager.get_session() as session:
            # 获取最新的磁盘信息
            from .models import DiskInfo
            # 获取最新的时间戳
            latest_timestamp = session.query(DiskInfo.timestamp).order_by(desc(DiskInfo.timestamp)).first()
            
            if latest_timestamp:
                # 只获取最新时间戳的数据
                latest_disk_info = session.query(DiskInfo).filter(
                    DiskInfo.timestamp == latest_timestamp[0]
                ).all()
            else:
                latest_disk_info = []
            
            # 获取最近一段时间的历史数据（例如最近1小时的数据）
            from datetime import timedelta
            from .utils import get_current_local_time
            one_hour_ago = get_current_local_time() - timedelta(hours=1)
            # 获取所有磁盘分区的历史数据
            history_data = session.query(DiskInfo.timestamp, DiskInfo.device, DiskInfo.percent)\
                .filter(DiskInfo.timestamp >= one_hour_ago)\
                .order_by(DiskInfo.timestamp)\
                .all()
            
            # 按设备分组历史数据
            history_by_device = {}
            for record in history_data:
                device = record.device
                if device not in history_by_device:
                    history_by_device[device] = []
                history_by_device[device].append({
                    'timestamp': record.timestamp.isoformat(),
                    'percent': record.percent
                })
            
            # 获取应用程序版本信息（这部分仍需要实时获取）
            from .collector import SystemCollector
            app_versions = SystemCollector.get_application_versions()
            
            # 转换磁盘信息为列表格式
            disk_list = []
            for disk in latest_disk_info:
                disk_list.append({
                    'device': disk.device,
                    'mountpoint': disk.mountpoint,
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                })
            
            # 计算最大磁盘使用率
            max_disk_percent = 0
            for disk in disk_list:
                if disk['percent'] > max_disk_percent:
                    max_disk_percent = disk['percent']
            
            # 转换时间为ISO格式字符串
            collection_time = None
            if latest_timestamp:
                collection_time = latest_timestamp[0].isoformat()
            
            response_data = {
                'disks': disk_list,
                'max_disk_percent': max_disk_percent,
                'applications': app_versions,
                'collection_time': collection_time,
                'history': history_by_device
            }
            
            return jsonify(response_data)
    except Exception as e:
        logger.error(f"获取磁盘信息时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/processes')
def api_processes():
    """获取进程信息API（从数据库获取最新数据）"""
    try:
        with db_manager.get_session() as session:
            # 获取最新的进程信息
            from .models import ProcessInfo
            
            # 获取最新的时间戳
            latest_timestamp = session.query(ProcessInfo.timestamp).order_by(desc(ProcessInfo.timestamp)).first()
            
            if latest_timestamp:
                # 只获取最新时间戳的数据
                latest_processes = session.query(ProcessInfo).filter(
                    ProcessInfo.timestamp == latest_timestamp[0]
                ).all()
            else:
                latest_processes = []
            
            # 转换为列表格式
            processes_list = []
            for proc in latest_processes:
                processes_list.append({
                    'pid': proc.pid,
                    'name': proc.name,
                    'status': proc.status,
                    'cpu_percent': proc.cpu_percent,
                    'memory_percent': proc.memory_percent,
                    'create_time': proc.create_time
                })
            
            # 按内存占用率排序，取前20个进程
            processes_list.sort(key=lambda x: x['memory_percent'], reverse=True)
            processes_list = processes_list[:20]
            
            # 转换时间为ISO格式字符串
            collection_time = None
            if latest_timestamp:
                collection_time = latest_timestamp[0].isoformat()
            
            return jsonify({
                'processes': processes_list,
                'collection_time': collection_time
            })
    except Exception as e:
        logger.error(f"获取进程信息时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/detailed-system-info')
def api_detailed_system_info():
    """获取详细系统信息API（实时采集）"""
    try:
        from .collector import SystemCollector
        detailed_info = SystemCollector.get_detailed_system_info()
        return jsonify(detailed_info)
    except Exception as e:
        logger.error(f"获取详细系统信息时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/history')
def api_history():
    """获取历史数据API"""
    try:
        with db_manager.get_session() as session:
            # 获取最近一段时间的历史数据（例如最近1小时的数据）
            from datetime import timedelta
            from .models import SystemInfo
            from .utils import get_current_local_time
            
            one_hour_ago = get_current_local_time() - timedelta(hours=1)
            history_data = session.query(SystemInfo.timestamp, SystemInfo.cpu_percent, SystemInfo.memory_percent)\
                .filter(SystemInfo.timestamp >= one_hour_ago)\
                .order_by(SystemInfo.timestamp)\
                .all()
            
            # 转换历史数据为列表格式
            history_list = []
            for record in history_data:
                history_list.append({
                    'timestamp': record.timestamp.isoformat(),
                    'cpu_percent': record.cpu_percent,
                    'memory_percent': record.memory_percent
                })
            
            return jsonify({'history': history_list})
    except Exception as e:
        logger.error(f"获取历史数据时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/system/cpu')
def api_system_cpu():
    """获取CPU信息API（从数据库获取最新数据）"""
    try:
        with db_manager.get_session() as session:
            # 获取最新的系统信息
            from .models import SystemInfo
            latest_system_info = session.query(SystemInfo).order_by(desc(SystemInfo.timestamp)).first()
            
            if latest_system_info:
                response_data = {
                    'cpu_percent': latest_system_info.cpu_percent,
                    'load_average': eval(latest_system_info.load_average) if latest_system_info.load_average else (0, 0, 0)
                }
                return jsonify(response_data)
            else:
                # 如果没有数据，返回空数据
                return jsonify({
                    'cpu_percent': 0,
                    'load_average': (0, 0, 0)
                })
    except Exception as e:
        logger.error(f"获取CPU信息时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/system/memory')
def api_system_memory():
    """获取内存信息API（从数据库获取最新数据）"""
    try:
        with db_manager.get_session() as session:
            # 获取最新的系统信息
            from .models import SystemInfo
            latest_system_info = session.query(SystemInfo).order_by(desc(SystemInfo.timestamp)).first()
            
            if latest_system_info:
                response_data = {
                    'memory_percent': latest_system_info.memory_percent
                }
                return jsonify(response_data)
            else:
                # 如果没有数据，返回空数据
                return jsonify({
                    'memory_percent': 0
                })
    except Exception as e:
        logger.error(f"获取内存信息时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/system/disk')
def api_system_disk():
    """获取磁盘信息API（从数据库获取最新数据）"""
    try:
        with db_manager.get_session() as session:
            # 获取最新的磁盘信息
            from .models import DiskInfo
            # 获取最新的时间戳
            latest_timestamp = session.query(DiskInfo.timestamp).order_by(desc(DiskInfo.timestamp)).first()
            
            if latest_timestamp:
                # 只获取最新时间戳的数据
                latest_disk_info = session.query(DiskInfo).filter(
                    DiskInfo.timestamp == latest_timestamp[0]
                ).all()
            else:
                latest_disk_info = []
            
            # 获取应用程序版本信息（这部分仍需要实时获取）
            from .collector import SystemCollector
            app_versions = SystemCollector.get_application_versions()
            
            # 转换磁盘信息为列表格式
            disk_list = []
            for disk in latest_disk_info:
                disk_list.append({
                    'device': disk.device,
                    'mountpoint': disk.mountpoint,
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                })
            
            # 计算最大磁盘使用率
            max_disk_percent = 0
            for disk in disk_list:
                if disk['percent'] > max_disk_percent:
                    max_disk_percent = disk['percent']
            
            # 转换时间为ISO格式字符串
            collection_time = None
            if latest_timestamp:
                collection_time = latest_timestamp[0].isoformat()
            
            response_data = {
                'disks': disk_list,
                'max_disk_percent': max_disk_percent,
                'applications': app_versions,
                'collection_time': collection_time
            }
            
            return jsonify(response_data)
    except Exception as e:
        logger.error(f"获取磁盘信息时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/system/details')
def api_system_details():
    """获取详细系统信息API（实时采集）"""
    try:
        from .collector import SystemCollector
        detailed_info = SystemCollector.get_detailed_system_info()
        return jsonify(detailed_info)
    except Exception as e:
        logger.error(f"获取详细系统信息时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/system/processes')
def api_system_processes():
    """获取进程信息API（从数据库获取最新数据）"""
    try:
        with db_manager.get_session() as session:
            # 获取最新的进程信息
            from .models import ProcessInfo
            
            # 获取最新的时间戳
            latest_timestamp = session.query(ProcessInfo.timestamp).order_by(desc(ProcessInfo.timestamp)).first()
            
            if latest_timestamp:
                # 只获取最新时间戳的数据
                latest_processes = session.query(ProcessInfo).filter(
                    ProcessInfo.timestamp == latest_timestamp[0]
                ).all()
            else:
                latest_processes = []
            
            # 转换为列表格式
            processes_list = []
            for proc in latest_processes:
                processes_list.append({
                    'pid': proc.pid,
                    'name': proc.name,
                    'status': proc.status,
                    'cpu_percent': proc.cpu_percent,
                    'memory_percent': proc.memory_percent,
                    'create_time': proc.create_time
                })
            
            # 按内存占用率排序，取前20个进程
            processes_list.sort(key=lambda x: x['memory_percent'], reverse=True)
            processes_list = processes_list[:20]
            
            # 转换时间为ISO格式字符串
            collection_time = None
            if latest_timestamp:
                collection_time = latest_timestamp[0].isoformat()
            
            return jsonify({
                'processes': processes_list,
                'collection_time': collection_time
            })
    except Exception as e:
        logger.error(f"获取进程信息时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/trend/memory')
def api_trend_memory():
    """获取内存使用趋势数据API（从数据库获取历史数据）"""
    try:
        with db_manager.get_session() as session:
            # 获取最近一段时间的历史数据（例如最近1小时的数据）
            from datetime import timedelta
            from .models import SystemInfo
            from .utils import get_current_local_time
            one_hour_ago = get_current_local_time() - timedelta(hours=1)
            history_data = session.query(SystemInfo.timestamp, SystemInfo.memory_percent)\
                .filter(SystemInfo.timestamp >= one_hour_ago)\
                .order_by(SystemInfo.timestamp)\
                .all()
            
            # 转换历史数据为列表格式
            history_list = []
            for record in history_data:
                history_list.append({
                    'timestamp': record.timestamp.isoformat(),
                    'memory_percent': record.memory_percent
                })
            
            return jsonify({'history': history_list})
    except Exception as e:
        logger.error(f"获取内存趋势数据时出错: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/trend/disk')
def api_trend_disk():
    """获取磁盘使用趋势数据API（从数据库获取历史数据）"""
    try:
        with db_manager.get_session() as session:
            # 获取最近一段时间的历史数据（例如最近1小时的数据）
            from datetime import timedelta
            from .models import DiskInfo
            from .utils import get_current_local_time
            one_hour_ago = get_current_local_time() - timedelta(hours=1)
            # 获取所有磁盘分区的历史数据
            history_data = session.query(DiskInfo.timestamp, DiskInfo.device, DiskInfo.percent)\
                .filter(DiskInfo.timestamp >= one_hour_ago)\
                .order_by(DiskInfo.timestamp)\
                .all()
            
            # 按设备分组历史数据
            history_by_device = {}
            for record in history_data:
                device = record.device
                if device not in history_by_device:
                    history_by_device[device] = []
                history_by_device[device].append({
                    'timestamp': record.timestamp.isoformat(),
                    'percent': record.percent
                })
            
            return jsonify({'history': history_by_device})
    except Exception as e:
        logger.error(f"获取磁盘趋势数据时出错: {e}")
        return jsonify({'error': str(e)}), 500
