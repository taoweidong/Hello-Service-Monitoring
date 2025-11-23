# app/api/handlers/report_handler.py
from flask import jsonify
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy import desc, func
from loguru import logger

from ...database.database_manager import DatabaseManager
from ...database.models import SystemInfo, DiskInfo, ProcessInfo, AlertRecord
from ...monitoring.collector import SystemCollector
from ...config.config import Config
from ...utils.helpers import get_current_local_time
from ..handlers.system_handler import SystemHandler
from ..handlers.process_handler import ProcessHandler
from ..handlers.disk_handler import DiskHandler
from ..handlers.memory_handler import MemoryHandler


class ReportHandler:
    """报告处理器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logger
    
    def send_weekly_report(self) -> Tuple[Dict, int]:
        """发送周报邮件API"""
        try:
            # 1. 从数据库获取一周的数据
            week_ago = datetime.now() - timedelta(days=7)
            two_weeks_ago = datetime.now() - timedelta(days=14)
            
            # 获取服务器详细信息
            server_info = SystemCollector.get_detailed_system_info()
            
            # 获取服务器IP地址
            from ..routes import get_server_ip
            server_ip = get_server_ip()
            
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
                
                # 根据本周内存和磁盘使用情况生成真实的预警信息
                alerts_data = []
                
                # 检查内存使用情况
                if memory_avg > Config.MEMORY_THRESHOLD:
                    alerts_data.append({
                        'timestamp': datetime.now(),
                        'alert_type': 'memory',
                        'message': f'本周平均内存使用率 {memory_avg:.2f}% 超过阈值 {Config.MEMORY_THRESHOLD}%',
                        'is_sent': 1
                    })
                
                # 检查磁盘使用情况
                if disk_max > Config.DISK_THRESHOLD:
                    # 获取磁盘使用率最高的记录详情
                    max_disk_record = session.query(DiskInfo).filter(
                        DiskInfo.timestamp >= week_ago
                    ).order_by(desc(DiskInfo.percent)).first()
                    
                    if max_disk_record:
                        alerts_data.append({
                            'timestamp': max_disk_record.timestamp,
                            'alert_type': 'disk',
                            'message': f'本周磁盘 {max_disk_record.device} 最高使用率 {max_disk_record.percent:.2f}% 超过阈值 {Config.DISK_THRESHOLD}%',
                            'is_sent': 1
                        })
                
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
                
                weekly_data = {
                    'report_date': datetime.now().strftime('%Y年%m月%d日'),
                    'server_info': server_info,
                    'server_ip': server_ip,
                    'cpu_avg': round(cpu_avg, 2),
                    'memory_avg': round(memory_avg, 2),
                    'disk_max': round(disk_max, 2),
                    'cpu_change': cpu_change,
                    'memory_change': memory_change,
                    'disk_change': disk_change,
                    'alerts': alerts_data,
                    'top_processes': top_processes_data
                }
            
            # 2. 生成图表
            # 获取一周的历史数据
            with self.db_manager.get_session() as session:
                history_data = session.query(
                    SystemInfo.timestamp,
                    SystemInfo.cpu_percent,
                    SystemInfo.memory_percent
                ).filter(
                    SystemInfo.timestamp >= week_ago
                ).order_by(SystemInfo.timestamp).all()
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
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
            chart_dir = os.path.join(Config.BASE_DIR, 'temp')
            if not os.path.exists(chart_dir):
                os.makedirs(chart_dir)
                
            chart_path = os.path.join(chart_dir, 'weekly_trend_chart.png')
            plt.tight_layout()
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # 3. 发送邮件
            # 检查邮件配置
            if not Config.MAIL_SERVER or not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
                self.logger.warning("邮件配置不完整，无法发送周报")
                return jsonify({'error': '邮件配置不完整'}), 500
            
            # 渲染邮件模板
            template_dir = os.path.join(Config.BASE_DIR, 'templates')
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template('weekly_report.html')
            html_content = template.render(**weekly_data)
            
            # 创建邮件
            msg = MIMEMultipart('related')
            # 在邮件主题中添加服务器IP信息
            server_ip = weekly_data.get('server_ip', 'unknown')
            msg['Subject'] = f"服务器监控周报 ({server_ip}) - {weekly_data['report_date']}"
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
            
            self.logger.info("手动触发周报邮件发送成功")
            return jsonify({'message': '周报邮件发送成功'}), 200
        except Exception as e:
            self.logger.error(f"发送周报邮件时出错: {e}")
            return jsonify({'error': str(e)}), 500