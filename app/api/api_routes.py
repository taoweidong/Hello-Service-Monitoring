from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.services.database import DatabaseManager
from app.models.models import ServerInfo, RemoteServer, AlertInfo
from app.utils.logger import monitor_logger
from datetime import datetime

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/cpu/history/<ip_address>')
@login_required
def cpu_history(ip_address):
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

@api_bp.route('/memory/history/<ip_address>')
@login_required
def memory_history(ip_address):
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

@api_bp.route('/disk/history/<ip_address>')
@login_required
def disk_history(ip_address):
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

@api_bp.route('/server/list')
@login_required
def server_list():
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

@api_bp.route('/remote-servers')
@login_required
def remote_servers():
    """API - 获取远程服务器列表"""
    try:
        db_manager = DatabaseManager()
        remote_servers = db_manager.session.query(RemoteServer).all()
        db_manager.close()
        
        server_list = []
        for server in remote_servers:
            server_data = {
                'id': server.id,
                'name': server.name,
                'ip_address': server.ip_address,
                'username': server.username,
                'port': server.port,
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
        monitor_logger.error(f"获取远程服务器列表失败: {e}")
        return jsonify({'error': '获取数据失败'}), 500

@api_bp.route('/remote-servers/add', methods=['POST'])
@login_required
def add_remote_server():
    """API - 添加远程服务器"""
    try:
        data = request.get_json()
        
        name = data.get('name')
        ip_address = data.get('ip_address')
        username = data.get('username')
        password = data.get('password')
        port = data.get('port', 22)
        
        if not all([name, ip_address, username, password]):
            return jsonify({'error': '缺少必要参数'}), 400
        
        db_manager = DatabaseManager()
        
        # 检查IP是否已存在
        existing_server = db_manager.session.query(RemoteServer).filter_by(ip_address=ip_address).first()
        if existing_server:
            db_manager.close()
            return jsonify({'error': '该IP地址的服务器已存在'}), 400
        
        # 创建新服务器记录
        remote_server = RemoteServer(
            name=name,
            ip_address=ip_address,
            username=username,
            port=port,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        remote_server.set_password(password)
        
        db_manager.session.add(remote_server)
        db_manager.session.commit()
        db_manager.close()
        
        return jsonify({'message': '服务器添加成功'}), 201
    except Exception as e:
        monitor_logger.error(f"添加远程服务器失败: {e}")
        return jsonify({'error': '添加服务器失败'}), 500

@api_bp.route('/remote-servers/<int:server_id>/delete', methods=['DELETE'])
@login_required
def delete_remote_server(server_id):
    """API - 删除远程服务器"""
    try:
        db_manager = DatabaseManager()
        remote_server = db_manager.session.query(RemoteServer).filter_by(id=server_id).first()
        
        if not remote_server:
            db_manager.close()
            return jsonify({'error': '服务器不存在'}), 404
        
        db_manager.session.delete(remote_server)
        db_manager.session.commit()
        db_manager.close()
        
        return jsonify({'message': '服务器删除成功'}), 200
    except Exception as e:
        monitor_logger.error(f"删除远程服务器失败: {e}")
        return jsonify({'error': '删除服务器失败'}), 500