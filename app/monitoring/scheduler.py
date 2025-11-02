from apscheduler.schedulers.background import BackgroundScheduler
from app.services.data_collector import DataCollector
from app.services.remote_collector import RemoteSystemCollector
from app.services.database import DatabaseManager
from app.models.models import init_db, RemoteServer
from app.utils.logger import monitor_logger
from app.config.config import Config
import atexit

# 全局调度器实例
scheduler = None

def collect_and_save_data(app):
    """采集并保存数据"""
    with app.app_context():
        try:
            # 初始化数据库
            init_db()
            
            # 创建数据库管理器
            db_manager = DatabaseManager()
            
            # 1. 采集本地服务器数据
            from app.services.local_collector import LocalSystemCollector
            collector = LocalSystemCollector()
            db_manager.add_server_info(collector.ip_address, collector.hostname)
            
            # 采集所有系统信息
            all_info = collector.collect_all_info()
            
            # 保存数据到数据库
            if all_info and all_info['cpu_info']:
                db_manager.save_cpu_info(all_info['cpu_info'])
                
            if all_info and all_info['memory_info']:
                db_manager.save_memory_info(all_info['memory_info'])
                
            if all_info and all_info['disk_info']:
                db_manager.save_disk_info(all_info['disk_info'])
                
            if all_info and all_info['process_info']:
                db_manager.save_process_info(all_info['process_info'])
            
            # 检查是否需要预警
            if all_info:
                check_thresholds(app, all_info, collector.ip_address)
            
            # 2. 采集远程服务器数据
            session = db_manager.session
            remote_servers = session.query(RemoteServer).all()
            
            for remote_server in remote_servers:
                try:
                    remote_collector = RemoteSystemCollector(remote_server)
                    remote_info = remote_collector.collect_all_info()
                    
                    # 添加服务器信息
                    hostname = 'unknown'
                    if remote_info and remote_info.get('cpu_info'):
                        hostname = f"server-{remote_server.ip_address}"
                    db_manager.add_server_info(remote_server.ip_address, hostname)
                    
                    # 保存数据到数据库
                    if remote_info and remote_info.get('cpu_info'):
                        db_manager.save_cpu_info(remote_info['cpu_info'])
                        
                    if remote_info and remote_info.get('memory_info'):
                        db_manager.save_memory_info(remote_info['memory_info'])
                        
                    if remote_info and remote_info.get('disk_info'):
                        db_manager.save_disk_info(remote_info['disk_info'])
                    
                    # 检查是否需要预警
                    if remote_info:
                        check_thresholds(app, remote_info, remote_server.ip_address)
                except Exception as e:
                    monitor_logger.error(f"采集远程服务器 {remote_server.ip_address} 数据失败: {e}")
            
            db_manager.close()
            monitor_logger.info("数据采集和保存完成")
        except Exception as e:
            monitor_logger.error(f"数据采集和保存失败: {e}")

def check_thresholds(app, all_info, ip_address):
    """检查阈值并触发预警"""
    # 延迟导入以避免循环导入
    from app.monitoring.alert import check_and_alert
    
    # 检查CPU阈值
    if all_info.get('cpu_info') and all_info['cpu_info'].get('cpu_percent', 0) > Config.CPU_THRESHOLD:
        check_and_alert(app, ip_address, 'cpu', 
                       f"CPU使用率过高: {all_info['cpu_info']['cpu_percent']:.2f}% (阈值: {Config.CPU_THRESHOLD}%)",
                       all_info)
    
    # 检查内存阈值
    if all_info.get('memory_info') and all_info['memory_info'].get('percent', 0) > Config.MEMORY_THRESHOLD:
        check_and_alert(app, ip_address, 'memory', 
                       f"内存使用率过高: {all_info['memory_info']['percent']:.2f}% (阈值: {Config.MEMORY_THRESHOLD}%)",
                       all_info)
    
    # 检查磁盘阈值
    if all_info.get('disk_info') and all_info['disk_info'].get('percent', 0) > Config.DISK_THRESHOLD:
        check_and_alert(app, ip_address, 'disk', 
                       f"磁盘使用率过高: {all_info['disk_info']['percent']:.2f}% (阈值: {Config.DISK_THRESHOLD}%)",
                       all_info)

def process_alerts_job(app):
    """处理未发送的预警信息任务"""
    with app.app_context():
        from app.monitoring.alert import process_unsent_alerts
        process_unsent_alerts(app)

def start_scheduler(app):
    """启动定时任务调度器"""
    global scheduler
    
    if scheduler is not None:
        return scheduler
    
    try:
        # 创建调度器
        scheduler = BackgroundScheduler()
        
        # 添加定时任务，每2分钟执行一次
        scheduler.add_job(
            func=collect_and_save_data,
            trigger="interval",
            minutes=Config.SCHEDULE_INTERVAL_MINUTES,
            args=[app],
            id='system_monitoring',
            name='系统监控数据采集',
            replace_existing=True
        )
        
        # 添加处理未发送预警的任务，每5分钟执行一次
        scheduler.add_job(
            func=process_alerts_job,
            trigger="interval",
            minutes=5,
            args=[app],
            id='process_alerts',
            name='处理未发送的预警信息',
            replace_existing=True
        )
        
        # 启动调度器
        scheduler.start()
        monitor_logger.info(f"定时任务调度器已启动，采集间隔: {Config.SCHEDULE_INTERVAL_MINUTES}分钟")
        
        # 注册退出时停止调度器
        if scheduler:
            atexit.register(lambda: scheduler.shutdown() if scheduler else None)
        
        # 立即执行一次数据采集
        scheduler.add_job(
            func=collect_and_save_data,
            trigger="date",
            args=[app],
            id='initial_collection',
            name='初始数据采集',
            replace_existing=True
        )
        
        return scheduler
    except Exception as e:
        monitor_logger.error(f"启动定时任务调度器失败: {e}")
        return None

def stop_scheduler():
    """停止定时任务调度器"""
    global scheduler
    
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        monitor_logger.info("定时任务调度器已停止")