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
            seconds=30,  # 每30秒收集一次数据
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
            
            # 1. 从数据库获取一周的数据
            weekly_data = self._get_weekly_data()
            
            # 2. 生成图表
            chart_path = self._generate_weekly_chart(weekly_data)
            
            # 3. 发送邮件
            self._send_weekly_report(weekly_data, chart_path)
            
            self.logger.info("周报生成完成")
        except Exception as e:
            self.logger.error(f"生成周报时出错: {e}")
    
    def send_weekly_report_manual(self):
        """手动发送周报（可从外部调用）"""
        try:
            self.logger.info("开始手动生成周报")
            
            # 1. 从数据库获取一周的数据
            weekly_data = self._get_weekly_data()
            
            # 2. 生成图表
            chart_path = self._generate_weekly_chart(weekly_data)
            
            # 3. 发送邮件
            self._send_weekly_report(weekly_data, chart_path)
            
            self.logger.info("手动生成周报完成")
            return True
        except Exception as e:
            self.logger.error(f"手动生成周报时出错: {e}")
            return False

    def _get_weekly_data(self):
        """获取一周的数据"""
        from datetime import datetime, timedelta
        from sqlalchemy import desc, func
        from app.models import SystemInfo, DiskInfo, ProcessInfo, AlertRecord
        from app.collector import SystemCollector
        
        # 计算一周前的时间
        week_ago = datetime.now() - timedelta(days=7)
        
        try:
            # 获取服务器详细信息
            server_info = SystemCollector.get_detailed_system_info()
            
            with self.db_manager.get_session() as session:
                # 获取系统信息统计数据
                cpu_avg = session.query(func.avg(SystemInfo.cpu_percent)).filter(
                    SystemInfo.timestamp >= week_ago
                ).scalar() or 0
                
                memory_avg = session.query(func.avg(SystemInfo.memory_percent)).filter(
                    SystemInfo.timestamp >= week_ago
                ).scalar() or 0
                
                # 获取磁盘使用率最高值
                disk_max = session.query(func.max(DiskInfo.percent)).filter(
                    DiskInfo.timestamp >= week_ago
                ).scalar() or 0
                
                # 获取本周预警记录
                alerts = session.query(AlertRecord).filter(
                    AlertRecord.timestamp >= week_ago
                ).order_by(desc(AlertRecord.timestamp)).all()
                # 将AlertRecord对象转换为字典，避免Session关闭后访问对象属性的问题
                alerts_data = [
                    {
                        'id': alert.id,
                        'timestamp': alert.timestamp,
                        'alert_type': alert.alert_type,
                        'message': alert.message,
                        'is_sent': alert.is_sent
                    }
                    for alert in alerts
                ]
                
                # 获取高负载进程（按内存使用率排序，取前10）
                # 首先获取最新的时间戳
                latest_timestamp = session.query(func.max(ProcessInfo.timestamp)).filter(
                    ProcessInfo.timestamp >= week_ago
                ).scalar()
                
                # 然后获取该时间戳下的所有进程数据，并按内存使用率排序取前10
                top_processes = session.query(ProcessInfo).filter(
                    ProcessInfo.timestamp == latest_timestamp
                ).order_by(desc(ProcessInfo.memory_percent)).limit(10).all() if latest_timestamp else []
                
                # 将ProcessInfo对象转换为字典，避免Session关闭后访问对象属性的问题
                top_processes_data = [
                    {
                        'id': process.id,
                        'pid': process.pid,
                        'name': process.name,
                        'status': process.status,
                        'cpu_percent': process.cpu_percent,
                        'memory_percent': process.memory_percent,
                        'create_time': process.create_time
                    }
                    for process in top_processes
                ]
                
                # 计算变化趋势（与上周相比）
                two_weeks_ago = datetime.now() - timedelta(days=14)
                
                # 上周平均值
                last_week_cpu_avg = session.query(func.avg(SystemInfo.cpu_percent)).filter(
                    SystemInfo.timestamp >= two_weeks_ago,
                    SystemInfo.timestamp < week_ago
                ).scalar() or 0
                
                last_week_memory_avg = session.query(func.avg(SystemInfo.memory_percent)).filter(
                    SystemInfo.timestamp >= two_weeks_ago,
                    SystemInfo.timestamp < week_ago
                ).scalar() or 0
                
                last_week_disk_max = session.query(func.max(DiskInfo.percent)).filter(
                    DiskInfo.timestamp >= two_weeks_ago,
                    DiskInfo.timestamp < week_ago
                ).scalar() or 0
                
                # 计算变化值
                cpu_change = round(cpu_avg - last_week_cpu_avg, 2)
                memory_change = round(memory_avg - last_week_memory_avg, 2)
                disk_change = round(disk_max - last_week_disk_max, 2)
                
                return {
                    'report_date': datetime.now().strftime('%Y年%m月%d日'),
                    'server_info': server_info,
                    'cpu_avg': round(cpu_avg, 2),
                    'memory_avg': round(memory_avg, 2),
                    'disk_max': round(disk_max, 2),
                    'cpu_change': cpu_change,
                    'memory_change': memory_change,
                    'disk_change': disk_change,
                    'alerts': alerts_data,
                    'top_processes': top_processes_data
                }
        except Exception as e:
            self.logger.error(f"获取周报数据时出错: {e}")
            # 返回默认数据
            return {
                'report_date': datetime.now().strftime('%Y年%m月%d日'),
                'server_info': {},
                'cpu_avg': 0,
                'memory_avg': 0,
                'disk_max': 0,
                'cpu_change': 0,
                'memory_change': 0,
                'disk_change': 0,
                'alerts': [],
                'top_processes': []
            }

    def _generate_weekly_chart(self, weekly_data):
        """生成周报图表"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # 使用非交互式后端
            import matplotlib.pyplot as plt
            import numpy as np
            from datetime import datetime, timedelta
            from sqlalchemy import func
            from app.models import SystemInfo
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 计算一周前的时间
            week_ago = datetime.now() - timedelta(days=7)
            
            # 获取一周的历史数据
            with self.db_manager.get_session() as session:
                history_data = session.query(
                    SystemInfo.timestamp,
                    SystemInfo.cpu_percent,
                    SystemInfo.memory_percent
                ).filter(
                    SystemInfo.timestamp >= week_ago
                ).order_by(SystemInfo.timestamp).all()
            
            if not history_data:
                # 如果没有数据，创建一个空图表
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('资源使用趋势')
            else:
                # 提取数据
                timestamps = [record.timestamp for record in history_data]
                cpu_percents = [record.cpu_percent for record in history_data]
                memory_percents = [record.memory_percent for record in history_data]
                
                # 创建图表
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(timestamps, cpu_percents, label='CPU使用率', linewidth=2, color='#4361ee')
                ax.plot(timestamps, memory_percents, label='内存使用率', linewidth=2, color='#f72585')
                
                # 设置图表样式
                ax.set_title('资源使用趋势 (过去7天)', fontsize=16, fontweight='bold')
                ax.set_xlabel('时间', fontsize=12)
                ax.set_ylabel('使用率 (%)', fontsize=12)
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                # 格式化x轴日期
                fig.autofmt_xdate()
            
            # 保存图表
            import os
            chart_dir = os.path.join(Config.BASE_DIR, 'temp')
            if not os.path.exists(chart_dir):
                os.makedirs(chart_dir)
                
            chart_path = os.path.join(chart_dir, 'weekly_trend_chart.png')
            plt.tight_layout()
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
        except Exception as e:
            self.logger.error(f"生成周报图表时出错: {e}")
            return None

    def _send_weekly_report(self, weekly_data, chart_path):
        """发送周报邮件"""
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.image import MIMEImage
        from jinja2 import Environment, FileSystemLoader
        import os
        
        # 检查邮件配置
        if not Config.MAIL_SERVER or not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
            self.logger.warning("邮件配置不完整，无法发送周报")
            return
        
        try:
            # 渲染邮件模板
            template_dir = os.path.join(Config.BASE_DIR, 'templates')
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template('weekly_report.html')
            html_content = template.render(**weekly_data)
            
            # 创建邮件
            msg = MIMEMultipart('related')
            msg['Subject'] = f"服务器监控周报 - {weekly_data['report_date']}"
            msg['From'] = Config.MAIL_DEFAULT_SENDER or Config.MAIL_USERNAME
            msg['To'] = Config.MAIL_DEFAULT_SENDER or Config.MAIL_USERNAME
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 添加图表附件
            if chart_path and os.path.exists(chart_path):
                with open(chart_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', '<resource_trend_chart>')
                    msg.attach(img)
            
            # 发送邮件
            server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
            server.starttls()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            self.logger.info("周报邮件发送成功")
        except Exception as e:
            self.logger.error(f"发送周报邮件时出错: {e}")