# app/api/handlers/report_handler.py
from flask import jsonify
import os
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy import desc, func
from loguru import logger

from ...database.database_manager import DatabaseManager
from ...database.models import SystemInfo, DiskInfo, ProcessInfo, AlertRecord
from ...monitoring.collector import SystemCollector
from ...config.config import Config
from ...utils.helpers import get_current_local_time
from ...utils.email_utils import EmailSender
from ...utils.chart_utils import ChartGenerator


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
            
            # 获取磁盘信息
            disk_info = SystemCollector.get_disk_info()
            # 获取第一个磁盘分区的信息作为总体磁盘信息
            primary_disk_info = disk_info[0] if disk_info else {
                'total': 0,
                'free': 0
            }
            
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
                    'disk_info': primary_disk_info,
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
            # 使用新的图表工具类
            chart_generator = ChartGenerator()
            
            # 获取一周的历史数据
            with self.db_manager.get_session() as session:
                history_data = session.query(
                    SystemInfo.timestamp,
                    SystemInfo.cpu_percent,
                    SystemInfo.memory_percent
                ).filter(
                    SystemInfo.timestamp >= week_ago
                ).order_by(SystemInfo.timestamp).all()
            
            # 生成资源使用趋势图
            if not history_data:
                # 如果没有数据，创建一个空图表
                chart_path = chart_generator.create_empty_chart(
                    message="暂无数据",
                    title="资源使用趋势 (过去7天)",
                    filename="weekly_trend_chart.png"
                )
            else:
                # 提取数据
                timestamps = [record.timestamp for record in history_data]
                cpu_percents = [record.cpu_percent for record in history_data]
                memory_percents = [record.memory_percent for record in history_data]
                
                # 创建折线图
                chart_path = chart_generator.create_line_chart(
                    x_data=timestamps,
                    y_data=[cpu_percents, memory_percents],
                    labels=['CPU使用率', '内存使用率'],
                    title='资源使用趋势 (过去7天)',
                    x_label='时间',
                    y_label='使用率 (%)',
                    filename='weekly_trend_chart.png'
                )
            
            # 3. 发送邮件
            # 使用新的邮件工具类
            email_sender = EmailSender()
            
            # 检查邮件配置
            if not email_sender.is_configured():
                self.logger.warning("邮件配置不完整，无法发送周报")
                return jsonify({'error': '邮件配置不完整'}), 500
            
            # 渲染邮件模板
            template_dir = os.path.join(Config.BASE_DIR, 'templates')
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template('weekly_report.html')
            html_content = template.render(**weekly_data)
            
            # 准备邮件参数
            # 在邮件主题中添加服务器IP信息
            server_ip = weekly_data.get('server_ip', 'unknown')
            subject = f"服务器监控周报 ({server_ip}) - {weekly_data['report_date']}"
            
            # 准备图片附件
            images = []
            if chart_path and os.path.exists(chart_path):
                images.append((chart_path, 'resource_trend_chart'))
            
            # 发送邮件
            success = email_sender.send_email(
                subject=subject,
                html_content=html_content,
                images=images
            )
            
            if success:
                self.logger.info("手动触发周报邮件发送成功")
                return jsonify({'message': '周报邮件发送成功'}), 200
            else:
                return jsonify({'error': '邮件发送失败'}), 500
                
        except Exception as e:
            self.logger.error(f"发送周报邮件时出错: {e}")
            return jsonify({'error': str(e)}), 500