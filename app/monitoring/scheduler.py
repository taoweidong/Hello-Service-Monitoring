# monitoring/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime
import logging
from typing import Optional

from app.collector import SystemCollector
from app.database import DatabaseManager
from app.config import Config


class MonitoringScheduler:
    """监控调度器"""
    
    def __init__(self):
        """初始化调度器"""
        self.scheduler = BackgroundScheduler(
            executors={'default': ThreadPoolExecutor(20)},
            job_defaults={'coalesce': False, 'max_instances': 3}
        )
        self.db_manager = DatabaseManager(Config.SQLALCHEMY_DATABASE_URI)
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """启动调度器"""
        # 添加定时任务
        self.scheduler.add_job(
            self.collect_system_data,
            'interval',
            seconds=10,  # 每10秒收集一次数据
            id='collect_system_data'
        )
        
        self.scheduler.add_job(
            self.check_thresholds,
            'interval',
            minutes=60,  # 每小时检查一次阈值
            id='check_thresholds'
        )
        
        self.scheduler.add_job(
            self.generate_weekly_report,
            'cron',
            day_of_week=0,  # 每周日
            hour=9,  # 上午9点
            minute=0,
            id='generate_weekly_report'
        )
        
        self.scheduler.start()
        self.logger.info("监控调度器已启动")
    
    def shutdown(self):
        """关闭调度器"""
        self.scheduler.shutdown()
        self.logger.info("监控调度器已关闭")
    
    def collect_system_data(self):
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
    
    def check_thresholds(self):
        """检查资源使用阈值并发送预警"""
        try:
            self.logger.info("开始检查资源阈值")
            
            # 获取最新的系统信息
            system_info = SystemCollector.get_system_info()
            disk_info = SystemCollector.get_disk_info()
            
            # 检查内存使用率
            memory_percent = system_info.get('memory_percent', 0)
            if memory_percent > Config.MEMORY_THRESHOLD:
                message = f"内存使用率过高: {memory_percent}%"
                self.db_manager.save_alert_record("memory", message)
                self.send_dingtalk_alert(message)
            
            # 检查磁盘使用率
            for disk in disk_info:
                disk_percent = disk.get('percent', 0)
                if disk_percent > Config.DISK_THRESHOLD:
                    message = f"磁盘 {disk['device']} 使用率过高: {disk_percent}%"
                    self.db_manager.save_alert_record("disk", message)
                    self.send_dingtalk_alert(message)
            
            self.logger.info("资源阈值检查完成")
        except Exception as e:
            self.logger.error(f"检查资源阈值时出错: {e}")
    
    def send_dingtalk_alert(self, message: str):
        """发送钉钉预警消息"""
        import requests
        import json
        
        if not Config.DINGTALK_WEBHOOK:
            self.logger.warning("未配置钉钉Webhook，无法发送预警消息")
            return
        
        try:
            payload = {
                "msgtype": "text",
                "text": {
                    "content": f"[服务器监控预警] {message}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }
            
            response = requests.post(Config.DINGTALK_WEBHOOK, json=payload)
            if response.status_code == 200:
                self.logger.info("钉钉预警消息发送成功")
            else:
                self.logger.error(f"钉钉预警消息发送失败: {response.text}")
        except Exception as e:
            self.logger.error(f"发送钉钉预警消息时出错: {e}")
    
    def generate_weekly_report(self):
        """生成周报"""
        try:
            self.logger.info("开始生成周报")
            # TODO: 实现周报生成功能
            # 1. 从数据库获取一周的数据
            # 2. 生成图表
            # 3. 发送邮件
            self.logger.info("周报生成完成")
        except Exception as e:
            self.logger.error(f"生成周报时出错: {e}")