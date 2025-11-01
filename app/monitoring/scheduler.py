from apscheduler.schedulers.background import BackgroundScheduler
from app.collector import SystemCollector
from app.database import DatabaseManager
from app.models import init_db
from app.logger import monitor_logger
from app.config import Config
import atexit

# 全局调度器实例
scheduler = None

def collect_and_save_data(app):
    """采集并保存数据"""
    with app.app_context():
        try:
            # 初始化数据库
            init_db()
            
            # 创建采集器和数据库管理器
            collector = SystemCollector()
            db_manager = DatabaseManager()
            
            # 添加服务器信息
            db_manager.add_server_info(collector.ip_address, collector.hostname)
            
            # 采集所有系统信息
            all_info = collector.collect_all_info()
            
            # 保存数据到数据库
            if all_info['cpu']:
                db_manager.save_cpu_info(all_info['cpu'])
                
            if all_info['memory']:
                db_manager.save_memory_info(all_info['memory'])
                
            if all_info['disk']:
                db_manager.save_disk_info(all_info['disk'])
                
            if all_info['process']:
                db_manager.save_process_info(all_info['process'])
            
            # 检查是否需要预警
            check_thresholds(app, all_info, collector.ip_address)
            
            db_manager.close()
            monitor_logger.info("数据采集和保存完成")
        except Exception as e:
            monitor_logger.error(f"数据采集和保存失败: {e}")

def check_thresholds(app, all_info, ip_address):
    """检查阈值并触发预警"""
    # 延迟导入以避免循环导入
    from app.monitoring.alert import check_and_alert
    
    # 检查CPU阈值
    if all_info['cpu'] and all_info['cpu']['cpu_percent'] > Config.CPU_THRESHOLD:
        check_and_alert(app, ip_address, 'cpu', f"CPU使用率过高: {all_info['cpu']['cpu_percent']}%")
    
    # 检查内存阈值
    if all_info['memory'] and all_info['memory']['percent'] > Config.MEMORY_THRESHOLD:
        check_and_alert(app, ip_address, 'memory', f"内存使用率过高: {all_info['memory']['percent']}%")
    
    # 检查磁盘阈值
    if all_info['disk'] and all_info['disk']['percent'] > Config.DISK_THRESHOLD:
        check_and_alert(app, ip_address, 'disk', f"磁盘使用率过高: {all_info['disk']['percent']}%")

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