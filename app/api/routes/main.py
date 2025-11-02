from flask import Blueprint, render_template
from flask_login import login_required
from app.services.database import DatabaseManager
from app.models.models import ServerInfo, RemoteServer, AlertInfo
from app.utils.logger import monitor_logger

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