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
        
        # 获取每个服务器的当前监控数据
        servers_with_metrics = []
        for server in servers:
            current_data = {
                'cpu': db_manager.get_latest_cpu_info(server.ip_address),
                'memory': db_manager.get_latest_memory_info(server.ip_address),
                'disk': db_manager.get_latest_disk_info(server.ip_address)
            }
            # 将SQLAlchemy对象转换为字典，以便模板可以序列化
            server_dict = {
                'id': server.id,
                'ip_address': server.ip_address,
                'hostname': server.hostname,
                'created_at': server.created_at.strftime('%Y-%m-%d %H:%M:%S') if server.created_at else None
            }
            servers_with_metrics.append({
                'server': server_dict,  # 使用字典而不是对象
                'metrics': current_data
            })
        
        db_manager.close()
        
        return render_template('index.html', servers_with_metrics=servers_with_metrics)
    except Exception as e:
        monitor_logger.error(f"获取服务器列表失败: {e}")
        import traceback
        monitor_logger.error(traceback.format_exc())
        return render_template('index.html', servers_with_metrics=[])

@main_bp.route('/server/<ip_address>')
@login_required
def server_detail(ip_address):
    """服务器详情页 - 展示特定服务器的详细监控信息"""
    try:
        from app.services.server_info_service import ServerInfoService
        
        db_manager = DatabaseManager()
        server = db_manager.session.query(ServerInfo).filter_by(ip_address=ip_address).first()
        db_manager.close()
        
        if not server:
            return "服务器未找到", 404        
        
        # 获取服务器详细信息
        server_info_service = ServerInfoService(ip_address)
        detailed_info = server_info_service.get_detailed_server_info()
        server_info_service.close()
        
        return render_template('server_detail.html', server=server, detailed_info=detailed_info)
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
        from app.services.chart_service import ChartService
        
        db_manager = DatabaseManager()
        # 获取服务器列表用于报表
        servers_query = db_manager.session.query(ServerInfo).all()
        
        # 获取每个服务器的监控数据和统计信息
        servers_with_metrics = []
        total_cpu = 0
        total_memory = 0
        total_disk = 0
        server_count = 0
        
        chart_service = ChartService()
        
        for server in servers_query:
            # 获取当前监控数据
            current_data = {
                'cpu': db_manager.get_latest_cpu_info(server.ip_address),
                'memory': db_manager.get_latest_memory_info(server.ip_address),
                'disk': db_manager.get_latest_disk_info(server.ip_address)
            }
            
            # 获取24小时趋势统计
            trend_stats = chart_service.get_trend_statistics(server.ip_address, hours=24)
            
            # 计算平均值
            cpu_percent = current_data['cpu'].get('cpu_percent', 0) if current_data['cpu'] else 0
            memory_percent = current_data['memory'].get('percent', 0) if current_data['memory'] else 0
            disk_percent = current_data['disk'].get('percent', 0) if current_data['disk'] else 0
            
            # 确保数值是浮点数且有效
            cpu_percent = float(cpu_percent) if cpu_percent is not None else 0.0
            memory_percent = float(memory_percent) if memory_percent is not None else 0.0
            disk_percent = float(disk_percent) if disk_percent is not None else 0.0
            
            if cpu_percent or memory_percent or disk_percent:
                total_cpu += cpu_percent
                total_memory += memory_percent
                total_disk += disk_percent
                server_count += 1
            
            server_dict = {
                'id': server.id,
                'ip_address': server.ip_address,
                'hostname': server.hostname,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'trend_stats': trend_stats
            }
            servers_with_metrics.append(server_dict)
        
        # 计算平均值
        avg_cpu = (total_cpu / server_count) if server_count > 0 else 0
        avg_memory = (total_memory / server_count) if server_count > 0 else 0
        avg_disk = (total_disk / server_count) if server_count > 0 else 0
        
        chart_service.close()
        db_manager.close()
        
        return render_template('reports.html', 
                             servers=servers_with_metrics,
                             avg_cpu=avg_cpu,
                             avg_memory=avg_memory,
                             avg_disk=avg_disk)
    except Exception as e:
        monitor_logger.error(f"获取报表数据失败: {e}")
        import traceback
        monitor_logger.error(traceback.format_exc())
        return render_template('reports.html', 
                             servers=[], 
                             avg_cpu=0, 
                             avg_memory=0, 
                             avg_disk=0)

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
        from app.services.chart_service import ChartService
        
        # 获取时间范围参数
        range_param = request.args.get('range', '1h')
        
        chart_service = ChartService()
        result = chart_service.get_chart_data(ip_address, range_param)
        chart_service.close()
        
        return jsonify(result)
    except Exception as e:
        monitor_logger.error(f"获取服务器历史数据失败: {e}")
        return jsonify({'error': '获取历史数据失败'}), 500

@main_bp.route('/api/server/<ip_address>/info')
@login_required
def api_server_info(ip_address):
    """API接口 - 获取服务器详细信息"""
    try:
        from app.services.server_info_service import ServerInfoService
        
        server_info_service = ServerInfoService(ip_address)
        server_info = server_info_service.get_detailed_server_info()
        server_info_service.close()
        
        if server_info:
            return jsonify(server_info)
        else:
            return jsonify({'error': '服务器信息未找到'}), 404
    except Exception as e:
        monitor_logger.error(f"获取服务器详细信息失败: {e}")
        return jsonify({'error': '获取服务器信息失败'}), 500

@main_bp.route('/api/server/<ip_address>/trends')
@login_required
def api_server_trends(ip_address):
    """API接口 - 获取服务器趋势统计信息"""
    try:
        from app.services.chart_service import ChartService
        
        hours = request.args.get('hours', 24, type=int)
        
        chart_service = ChartService()
        statistics = chart_service.get_trend_statistics(ip_address, hours)
        chart_service.close()
        
        return jsonify(statistics)
    except Exception as e:
        monitor_logger.error(f"获取服务器趋势统计信息失败: {e}")
        return jsonify({'error': '获取趋势统计信息失败'}), 500

@main_bp.route('/api/server/<ip_address>/current')
@login_required
def api_server_current(ip_address):
    """API接口 - 获取服务器当前监控数据"""
    try:
        db_manager = DatabaseManager()
        
        current_data = {
            'cpu': db_manager.get_latest_cpu_info(ip_address),
            'memory': db_manager.get_latest_memory_info(ip_address),
            'disk': db_manager.get_latest_disk_info(ip_address)
        }
        
        db_manager.close()
        
        return jsonify(current_data)
    except Exception as e:
        monitor_logger.error(f"获取服务器当前监控数据失败: {e}")
        return jsonify({'error': '获取当前监控数据失败'}), 500