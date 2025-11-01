from flask import Blueprint, render_template, jsonify, request
from app.database import DatabaseManager
from app.models import ServerInfo
from app.logger import monitor_logger

# 创建蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
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

@main_bp.route('/api/cpu/history/<ip_address>')
def api_cpu_history(ip_address):
    """API - 获取CPU历史数据"""
    try:
        limit = request.args.get('limit', 50, type=int)
        db_manager = DatabaseManager()
        cpu_history = db_manager.get_cpu_history(ip_address, limit)
        db_manager.close()
        
        # 转换为图表可用格式
        timestamps = [data['timestamp'].strftime('%Y-%m-%d %H:%M:%S') for data in cpu_history]
        cpu_percents = [data['cpu_percent'] for data in cpu_history]
        
        return jsonify({
            'timestamps': timestamps,
            'cpu_percents': cpu_percents
        })
    except Exception as e:
        monitor_logger.error(f"获取CPU历史数据失败: {e}")
        return jsonify({'error': '获取数据失败'}), 500

@main_bp.route('/api/memory/history/<ip_address>')
def api_memory_history(ip_address):
    """API - 获取内存历史数据"""
    try:
        limit = request.args.get('limit', 50, type=int)
        db_manager = DatabaseManager()
        memory_history = db_manager.get_memory_history(ip_address, limit)
        db_manager.close()
        
        # 转换为图表可用格式
        timestamps = [data['timestamp'].strftime('%Y-%m-%d %H:%M:%S') for data in memory_history]
        memory_percents = [data['percent'] for data in memory_history]
        
        return jsonify({
            'timestamps': timestamps,
            'memory_percents': memory_percents
        })
    except Exception as e:
        monitor_logger.error(f"获取内存历史数据失败: {e}")
        return jsonify({'error': '获取数据失败'}), 500

@main_bp.route('/api/disk/history/<ip_address>')
def api_disk_history(ip_address):
    """API - 获取磁盘历史数据"""
    try:
        limit = request.args.get('limit', 50, type=int)
        db_manager = DatabaseManager()
        disk_history = db_manager.get_disk_history(ip_address, limit)
        db_manager.close()
        
        # 转换为图表可用格式
        timestamps = [data['timestamp'].strftime('%Y-%m-%d %H:%M:%S') for data in disk_history]
        disk_percents = [data['percent'] for data in disk_history]
        
        return jsonify({
            'timestamps': timestamps,
            'disk_percents': disk_percents
        })
    except Exception as e:
        monitor_logger.error(f"获取磁盘历史数据失败: {e}")
        return jsonify({'error': '获取数据失败'}), 500

@main_bp.route('/api/server/list')
def api_server_list():
    """API - 获取服务器列表"""
    try:
        db_manager = DatabaseManager()
        servers = db_manager.session.query(ServerInfo).all()
        db_manager.close()
        
        server_list = []
        for server in servers:
            server_data = {
                'id': server.id,
                'ip_address': server.ip_address,
                'hostname': server.hostname,
                'created_at': None
            }
            
            # 安全地处理created_at字段
            if hasattr(server, 'created_at') and server.created_at is not None:
                try:
                    server_data['created_at'] = server.created_at.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    server_data['created_at'] = str(server.created_at)
            
            server_list.append(server_data)
        
        return jsonify(server_list)
    except Exception as e:
        monitor_logger.error(f"获取服务器列表失败: {e}")
        return jsonify({'error': '获取数据失败'}), 500