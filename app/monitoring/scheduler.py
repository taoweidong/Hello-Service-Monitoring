# app/monitoring/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from loguru import logger

from .collector import SystemCollector
from .thresholds import ThresholdChecker
from ..database.database_manager import DatabaseManager
from ..config.config import Config

class MonitoringScheduler:
    """监控调度器"""
    
    def __init__(self):
        """初始化调度器"""
        # 配置调度器使用本地时区
        self.scheduler = BackgroundScheduler(
            executors={'default': ThreadPoolExecutor(20)},
            job_defaults={'coalesce': False, 'max_instances': 3},
            timezone=Config.LOCAL_TIMEZONE  # 使用配置中的本地时区
        )
        self.db_manager = DatabaseManager(Config.SQLALCHEMY_DATABASE_URI)
        self.threshold_checker = ThresholdChecker(self.db_manager)
        self.logger = logger
    
    def start(self) -> None:
        """启动调度器"""
        # 添加定时任务
        self.scheduler.add_job(
            self.collect_system_data,
            'interval',
            seconds=Config.COLLECT_SYSTEM_DATA_INTERVAL,  # 收集系统数据的时间间隔
            id='collect_system_data'
        )
        
        self.scheduler.add_job(
            self.check_thresholds,
            'interval',
            seconds=Config.CHECK_THRESHOLDS_INTERVAL,  # 检查阈值的时间间隔
            id='check_thresholds'
        )
        
        self.scheduler.add_job(
            self.generate_weekly_report,
            'interval',
            seconds=Config.GENERATE_WEEKLY_REPORT_INTERVAL,  # 生成周报的时间间隔
            id='generate_weekly_report',
            timezone=Config.LOCAL_TIMEZONE  # 使用配置中的本地时区
        )
        
        self.scheduler.start()
        self.logger.info("监控调度器已启动")
    
    def shutdown(self) -> None:
        """关闭调度器"""
        self.scheduler.shutdown()
        self.logger.info("监控调度器已关闭")
    
    def collect_system_data(self) -> None:
        """收集系统数据并保存到数据库"""
        try:
            self.logger.info("开始收集系统数据")
            
            # 收集系统信息
            system_info = SystemCollector.get_system_info()
            
            # 收集磁盘信息
            disk_info = SystemCollector.get_disk_info()
            
            # 收集进程信息
            process_info = SystemCollector.get_process_info()
            
            # 保存到数据库
            self.db_manager.save_system_info(system_info)
            self.db_manager.save_disk_info(disk_info)
            self.db_manager.save_process_info(process_info)
            
            self.logger.info("系统数据收集完成")
        except Exception as e:
            self.logger.error(f"收集系统数据时出错: {e}")
    
    def check_thresholds(self) -> None:
        """检查资源使用阈值"""
        try:
            self.logger.info("开始检查资源阈值")
            self.threshold_checker.check_system_thresholds()
            self.logger.info("资源阈值检查完成")
        except Exception as e:
            self.logger.error(f"检查资源阈值时出错: {e}")
    
    def generate_weekly_report(self) -> None:
        """生成周报并发送邮件"""
        try:
            self.logger.info("开始生成周报")
            # 调用ReportHandler发送周报邮件
            from ..api.handlers.report_handler import ReportHandler
            report_handler = ReportHandler(self.db_manager)
            result, status_code = report_handler.send_weekly_report()
            
            if status_code == 200:
                self.logger.info("周报邮件发送成功")
            else:
                self.logger.error(f"周报邮件发送失败: {result}")
                
        except Exception as e:
            self.logger.error(f"生成周报时出错: {e}")