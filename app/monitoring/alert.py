from app.services.database import DatabaseManager
from app.services.email_service import EmailService
from app.services.server_info_service import ServerInfoService
from app.utils.logger import monitor_logger
from datetime import datetime

def check_and_alert(app, ip_address, alert_type, message, monitor_data=None):
    """检查并触发预警"""
    try:
        # 保存预警信息到数据库
        db_manager = DatabaseManager()
        
        alert_info = {
            'ip_address': ip_address,
            'timestamp': datetime.now(),
            'alert_type': alert_type,
            'alert_message': message,
            'is_sent': 0
        }
        
        db_manager.save_alert_info(alert_info)
        
        # 获取服务器详细信息和监控数据
        server_info_service = ServerInfoService(ip_address)
        server_info = server_info_service.get_detailed_server_info()
        
        # 如果没有提供监控数据，尝试从数据库获取最新数据
        if not monitor_data:
            monitor_data = {
                'cpu_info': db_manager.get_latest_cpu_info(ip_address),
                'memory_info': db_manager.get_latest_memory_info(ip_address),
                'disk_info': db_manager.get_latest_disk_info(ip_address)
            }
        
        # 准备服务器信息字典
        server_info_dict = None
        if server_info:
            server_info_dict = {
                'ip_address': server_info.get('ip_address', ip_address),
                'hostname': server_info.get('hostname', 'Unknown'),
                'system_version': server_info.get('system_version', 'Unknown'),
                'kernel_version': server_info.get('kernel_version', 'Unknown'),
                'cpu_count': server_info.get('cpu_count', 'N/A'),
                'total_memory': server_info.get('total_memory', 'N/A'),
                'total_disk': server_info.get('total_disk', 'N/A'),
                'uptime': server_info.get('uptime', 'N/A')
            }
        
        db_manager.close()
        server_info_service.close()
        
        # 发送美化后的邮件预警
        email_service = EmailService()
        email_service.send_alert_email(alert_info, server_info_dict, monitor_data)
        email_service.close()
        
        monitor_logger.info(f"预警已触发: {ip_address} - {alert_type} - {message}")
    except Exception as e:
        monitor_logger.error(f"预警触发失败: {e}")

def process_unsent_alerts(app):
    """处理未发送的预警信息"""
    try:
        db_manager = DatabaseManager()
        email_service = EmailService()
        
        unsent_alerts = db_manager.get_unsent_alerts()
        
        for alert in unsent_alerts:
            try:
                # 为每个预警创建对应的ServerInfoService实例
                server_info_service = ServerInfoService(alert.ip_address)
                # 获取服务器信息和监控数据
                server_info = server_info_service.get_detailed_server_info()
                monitor_data = {
                    'cpu_info': db_manager.get_latest_cpu_info(alert.ip_address),
                    'memory_info': db_manager.get_latest_memory_info(alert.ip_address),
                    'disk_info': db_manager.get_latest_disk_info(alert.ip_address)
                }
                
                # 准备服务器信息字典
                server_info_dict = None
                if server_info:
                    server_info_dict = {
                        'ip_address': server_info.get('ip_address', alert.ip_address),
                        'hostname': server_info.get('hostname', 'Unknown'),
                        'system_version': server_info.get('system_version', 'Unknown'),
                        'kernel_version': server_info.get('kernel_version', 'Unknown'),
                        'cpu_count': server_info.get('cpu_count', 'N/A'),
                        'total_memory': server_info.get('total_memory', 'N/A'),
                        'total_disk': server_info.get('total_disk', 'N/A'),
                        'uptime': server_info.get('uptime', 'N/A')
                    }
                
                # 准备预警信息
                alert_info = {
                    'ip_address': alert.ip_address,
                    'timestamp': alert.timestamp,
                    'alert_type': alert.alert_type,
                    'alert_message': alert.alert_message
                }
                
                # 发送邮件
                if email_service.send_alert_email(alert_info, server_info_dict, monitor_data):
                    # 标记为已发送
                    db_manager.mark_alert_as_sent(alert.id)
                
                # 关闭server_info_service
                server_info_service.close()
            except Exception as e:
                monitor_logger.error(f"处理预警 {alert.id} 失败: {e}")
                # 确保在异常情况下也关闭server_info_service
                try:
                    server_info_service.close()
                except:
                    pass
        
        db_manager.close()
        email_service.close()
        monitor_logger.info(f"处理了 {len(unsent_alerts)} 条未发送的预警信息")
    except Exception as e:
        monitor_logger.error(f"处理未发送预警信息失败: {e}")