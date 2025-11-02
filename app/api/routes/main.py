from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app.services.database import DatabaseManager
from app.models.models import ServerInfo, RemoteServer, AlertInfo, CPUInfo, MemoryInfo, DiskInfo
from app.utils.logger import monitor_logger
from datetime import datetime, timedelta

# 创建蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    """主页 - 展示所有服务器信息"""
    try:
        db_manager = DatabaseManager()
        servers = db_manager.session.query(ServerInfo).all()
        db_manager.close()
        
        return render_template('index.html', servers=servers)
    except Exception as e:
        monitor_logger.error(f"获取服务器列表失败: {e}")
        return render_template('index.html', servers=[])

@main_bp.route('/server/<ip_address>')
@login_required
def server_detail(ip_address):
    """服务器详情页 - 展示特定服务器的详细监控信息"""
    try:
        db_manager = DatabaseManager()
        server = db_manager.session.query(ServerInfo).filter_by(ip_address=ip_address).first()
        db_manager.close()
        
        if not server:
            return "服务器未找到", 404
            
        return render_template('server_detail.html', server=server)
    except Exception as e:
        monitor_logger.error(f"获取服务器详情失败: {e}")
        return "服务器详情获取失败", 500

@main_bp.route('/alerts')
@login_required
def alerts():
    """预警页面 - 展示所有预警信息"""
    try:
        db_manager = DatabaseManager()
        # 获取最新的预警信息
        alerts = db_manager.session.query(AlertInfo).order_by(AlertInfo.timestamp.desc()).limit(100).all()
        db_manager.close()
        
        return render_template('alerts.html', alerts=alerts)
    except Exception as e:
        monitor_logger.error(f"获取预警信息失败: {e}")
        return render_template('alerts.html', alerts=[])

@main_bp.route('/reports')
@login_required
def reports():
    """报表页面 - 展示系统报表"""
    try:
        db_manager = DatabaseManager()
        # 获取服务器列表用于报表
        servers = db_manager.session.query(ServerInfo).all()
        db_manager.close()
        
        return render_template('reports.html', servers=servers)
    except Exception as e:
        monitor_logger.error(f"获取报表数据失败: {e}")
        return render_template('reports.html', servers=[])

@main_bp.route('/remote-servers')
@login_required
def remote_servers():
    """远程服务器管理页面"""
    try:
        db_manager = DatabaseManager()
        remote_servers = db_manager.session.query(RemoteServer).all()
        db_manager.close()
        
        return render_template('remote_servers.html', remote_servers=remote_servers)
    except Exception as e:
        monitor_logger.error(f"获取远程服务器列表失败: {e}")
        return render_template('remote_servers.html', remote_servers=[])

@main_bp.route('/server/<ip_address>/history')
@login_required
def server_history(ip_address):
    """服务器历史数据页面"""
    try:
        db_manager = DatabaseManager()
        server = db_manager.session.query(ServerInfo).filter_by(ip_address=ip_address).first()
        db_manager.close()
        
        if not server:
            return "服务器未找到", 404
            
        return render_template('history.html', server=server)
    except Exception as e:
        monitor_logger.error(f"获取服务器历史数据页面失败: {e}")
        return "服务器历史数据页面获取失败", 500

@main_bp.route('/api/history/<ip_address>')
@login_required
def api_history_data(ip_address):
    """API接口 - 获取服务器历史数据"""
    try:
        # 获取时间范围参数
        range_param = request.args.get('range', '1h')
        
        # 计算时间范围
        end_time = datetime.now()
        if range_param == '1h':
            start_time = end_time - timedelta(hours=1)
        elif range_param == '6h':
            start_time = end_time - timedelta(hours=6)
        elif range_param == '24h':
            start_time = end_time - timedelta(hours=24)
        elif range_param == '7d':
            start_time = end_time - timedelta(days=7)
        else:
            start_time = end_time - timedelta(hours=1)
        
        db_manager = DatabaseManager()
        
        # 获取CPU历史数据
        cpu_data = db_manager.get_cpu_history_by_time_range(ip_address, start_time, end_time)
        
        # 获取内存历史数据
        memory_data = db_manager.get_memory_history_by_time_range(ip_address, start_time, end_time)
        
        # 获取磁盘历史数据
        disk_data = db_manager.get_disk_history_by_time_range(ip_address, start_time, end_time)
        
        db_manager.close()
        
        # 格式化数据
        result = {
            'cpu': [{
                'timestamp': data['timestamp'].isoformat(),
                'cpu_percent': data['cpu_percent']
            } for data in cpu_data],
            'memory': [{
                'timestamp': data['timestamp'].isoformat(),
                'percent': data['percent']
            } for data in memory_data],
            'disk': [{
                'timestamp': data['timestamp'].isoformat(),
                'percent': data['percent']
            } for data in disk_data]
        }
        
        return jsonify(result)
    except Exception as e:
        monitor_logger.error(f"获取服务器历史数据失败: {e}")
        return jsonify({'error': '获取历史数据失败'}), 500