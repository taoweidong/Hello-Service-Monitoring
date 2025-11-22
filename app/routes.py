# app/routes.py
from flask import Blueprint, jsonify, render_template
from .database import DatabaseManager
from .config import Config
from sqlalchemy import desc
import json
import socket
from loguru import logger

main_bp = Blueprint('main', __name__)
db_manager = DatabaseManager(Config.SQLALCHEMY_DATABASE_URI)


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


@main_bp.route('/api/processes')
def api_processes():
    """获取进程信息API（从数据库获取最新数据）"""
    try:
        with db_manager.get_session() as session:
            # 获取最新的进程信息
            from .models import ProcessInfo
            # 获取最近15秒内的进程信息
            from datetime import datetime, timedelta
            fifteen_seconds_ago = datetime.utcnow() - timedelta(seconds=15)
            latest_processes = session.query(ProcessInfo).filter(
                ProcessInfo.timestamp >= fifteen_seconds_ago
            ).order_by(desc(ProcessInfo.timestamp)).all()
            
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
            
            return jsonify({'processes': processes_list})
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
        # 这里应该从数据库获取历史数据
        # 暂时返回空数据，后续实现
        return jsonify({'history': []})
    except Exception as e:
        logger.error(f"获取历史数据时出错: {e}")
        return jsonify({'error': str(e)}), 500