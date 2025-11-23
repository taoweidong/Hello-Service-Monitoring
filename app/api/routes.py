# app/api/routes.py
from flask import Blueprint, jsonify, render_template, send_from_directory
import os
from ..database.database_manager import DatabaseManager
from ..config.config import Config
import json
import socket
from loguru import logger
from ..utils.helpers import format_local_time

# 导入处理器
from .handlers.system_handler import SystemHandler
from .handlers.process_handler import ProcessHandler
from .handlers.disk_handler import DiskHandler
from .handlers.memory_handler import MemoryHandler
from .handlers.report_handler import ReportHandler

main_bp = Blueprint('main', __name__)
db_manager = DatabaseManager(Config.SQLALCHEMY_DATABASE_URI)

# 初始化处理器
system_handler = SystemHandler(db_manager)
process_handler = ProcessHandler(db_manager)
disk_handler = DiskHandler(db_manager)
memory_handler = MemoryHandler(db_manager)
report_handler = ReportHandler(db_manager)


@main_bp.route('/favicon.ico')
def favicon():
    """Favicon路由"""
    # 获取项目根目录
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
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


# 系统信息相关路由
@main_bp.route('/api/system-info')
def api_system_info():
    """获取系统信息API（从数据库获取最新数据）"""
    return system_handler.get_system_info()


@main_bp.route('/api/cpu-info')
def api_cpu_info():
    """获取CPU信息API（从数据库获取最新数据和历史数据）"""
    return system_handler.get_cpu_info()


@main_bp.route('/api/system/details')
def api_system_details():
    """获取详细系统信息API（实时采集）"""
    return system_handler.get_detailed_system_info()


# 进程信息相关路由
@main_bp.route('/api/processes')
def api_processes():
    """获取进程信息API（从数据库获取最新数据）"""
    return process_handler.get_processes()


@main_bp.route('/api/system/processes')
def api_system_processes():
    """获取进程信息API（从数据库获取最新数据）"""
    return process_handler.get_processes()


# 磁盘信息相关路由
@main_bp.route('/api/disk-info')
def api_disk_info():
    """获取磁盘信息API（从数据库获取最新数据和历史数据）"""
    return disk_handler.get_disk_info()


@main_bp.route('/api/system/disk')
def api_system_disk():
    """获取磁盘信息API（从数据库获取最新数据）"""
    return disk_handler.get_system_disk()


@main_bp.route('/api/trend/disk')
def api_trend_disk():
    """获取磁盘使用趋势数据API（从数据库获取历史数据）"""
    return disk_handler.get_trend_disk()


# 内存信息相关路由
@main_bp.route('/api/memory-info')
def api_memory_info():
    """获取内存信息API（从数据库获取最新数据和历史数据）"""
    return memory_handler.get_memory_info()


@main_bp.route('/api/system/memory')
def api_system_memory():
    """获取内存信息API（从数据库获取最新数据）"""
    return memory_handler.get_system_memory()


@main_bp.route('/api/trend/memory')
def api_trend_memory():
    """获取内存使用趋势数据API（从数据库获取历史数据）"""
    return memory_handler.get_trend_memory()


# 报告相关路由
@main_bp.route('/api/send-weekly-report', methods=['POST'])
def api_send_weekly_report():
    """发送周报邮件API"""
    return report_handler.send_weekly_report()