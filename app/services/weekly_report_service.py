"""周报服务模块 - 负责生成和发送服务器资源使用周报"""
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
from app.config.config import Config
from app.services.database import DatabaseManager
from app.services.chart_service import ChartService
from app.utils.logger import monitor_logger
from app.models.models import ServerInfo
import numpy as np

# 设置中文字体，使用英文标签避免字体问题
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

class WeeklyReportService:
    """周报服务类"""
    
    def __init__(self):
        self.config = Config
        self.db_manager = DatabaseManager()
        self.chart_service = ChartService()
    
    def generate_weekly_report_data(self):
        """生成周报数据"""
        try:
            # 获取所有服务器
            servers = self.db_manager.session.query(ServerInfo).all()
            
            report_data = []
            
            for server in servers:
                # 获取该服务器一周的数据
                end_time = datetime.now()
                start_time = end_time - timedelta(days=7)
                
                # 获取CPU、内存、磁盘历史数据
                cpu_data = self.db_manager.get_cpu_history_by_time_range(
                    server.ip_address, start_time, end_time)
                memory_data = self.db_manager.get_memory_history_by_time_range(
                    server.ip_address, start_time, end_time)
                disk_data = self.db_manager.get_disk_history_by_time_range(
                    server.ip_address, start_time, end_time)
                
                # 分析数据
                server_report = {
                    'server_info': {
                        'ip_address': server.ip_address,
                        'hostname': server.hostname or 'Unknown'
                    },
                    'cpu_analysis': self._analyze_data(cpu_data, 'cpu_percent'),
                    'memory_analysis': self._analyze_data(memory_data, 'percent'),
                    'disk_analysis': self._analyze_data(disk_data, 'percent'),
                    'risk_points': self._identify_risk_points(cpu_data, memory_data, disk_data)
                }
                
                report_data.append(server_report)
            
            return report_data
        except Exception as e:
            monitor_logger.error(f"生成周报数据失败: {e}")
            return []
    
    def _analyze_data(self, data, value_key):
        """分析数据并生成统计信息"""
        if not data:
            return {
                'min': 0,
                'max': 0,
                'avg': 0,
                'current': 0,
                'trend': 'unknown'
            }
        
        values = [item[value_key] for item in data if item.get(value_key) is not None]
        
        if not values:
            return {
                'min': 0,
                'max': 0,
                'avg': 0,
                'current': 0,
                'trend': 'unknown'
            }
        
        # 计算趋势（通过比较前半段和后半段的平均值）
        mid_point = len(values) // 2
        if mid_point > 0:
            first_half_avg = sum(values[:mid_point]) / mid_point
            second_half_avg = sum(values[mid_point:]) / (len(values) - mid_point)
            if second_half_avg > first_half_avg * 1.1:  # 增长超过10%
                trend = 'increasing'
            elif second_half_avg < first_half_avg * 0.9:  # 下降超过10%
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'min': round(min(values), 2),
            'max': round(max(values), 2),
            'avg': round(sum(values) / len(values), 2),
            'current': round(values[-1], 2) if values else 0,
            'trend': trend
        }
    
    def _identify_risk_points(self, cpu_data, memory_data, disk_data):
        """识别风险点"""
        risk_points = []
        
        # CPU风险检查
        cpu_values = [item['cpu_percent'] for item in cpu_data if item.get('cpu_percent') is not None]
        if cpu_values:
            cpu_avg = sum(cpu_values) / len(cpu_values)
            if cpu_avg > self.config.CPU_THRESHOLD:
                risk_points.append({
                    'type': 'cpu',
                    'description': f'CPU Avg Usage({cpu_avg:.2f}%) exceeds threshold({self.config.CPU_THRESHOLD}%)',
                    'severity': 'high' if cpu_avg > self.config.CPU_THRESHOLD * 1.2 else 'medium'
                })
            elif max(cpu_values) > self.config.CPU_THRESHOLD:
                risk_points.append({
                    'type': 'cpu',
                    'description': f'CPU Peak Usage({max(cpu_values):.2f}%) exceeds threshold({self.config.CPU_THRESHOLD}%)',
                    'severity': 'medium'
                })
        
        # 内存风险检查
        memory_values = [item['percent'] for item in memory_data if item.get('percent') is not None]
        if memory_values:
            memory_avg = sum(memory_values) / len(memory_values)
            if memory_avg > self.config.MEMORY_THRESHOLD:
                risk_points.append({
                    'type': 'memory',
                    'description': f'Memory Avg Usage({memory_avg:.2f}%) exceeds threshold({self.config.MEMORY_THRESHOLD}%)',
                    'severity': 'high' if memory_avg > self.config.MEMORY_THRESHOLD * 1.2 else 'medium'
                })
            elif max(memory_values) > self.config.MEMORY_THRESHOLD:
                risk_points.append({
                    'type': 'memory',
                    'description': f'Memory Peak Usage({max(memory_values):.2f}%) exceeds threshold({self.config.MEMORY_THRESHOLD}%)',
                    'severity': 'medium'
                })
        
        # 磁盘风险检查
        disk_values = [item['percent'] for item in disk_data if item.get('percent') is not None]
        if disk_values:
            disk_avg = sum(disk_values) / len(disk_values)
            if disk_avg > self.config.DISK_THRESHOLD:
                risk_points.append({
                    'type': 'disk',
                    'description': f'Disk Avg Usage({disk_avg:.2f}%) exceeds threshold({self.config.DISK_THRESHOLD}%)',
                    'severity': 'high' if disk_avg > self.config.DISK_THRESHOLD * 1.2 else 'medium'
                })
            elif max(disk_values) > self.config.DISK_THRESHOLD:
                risk_points.append({
                    'type': 'disk',
                    'description': f'Disk Peak Usage({max(disk_values):.2f}%) exceeds threshold({self.config.DISK_THRESHOLD}%)',
                    'severity': 'medium'
                })
        
        # 持续高负载检查
        if cpu_values and len([v for v in cpu_values if v > self.config.CPU_THRESHOLD * 0.8]) > len(cpu_values) * 0.7:
            risk_points.append({
                'type': 'cpu',
                'description': 'CPU under high load for extended period (over 70% of time above 80% of threshold)',
                'severity': 'medium'
            })
        
        if memory_values and len([v for v in memory_values if v > self.config.MEMORY_THRESHOLD * 0.8]) > len(memory_values) * 0.7:
            risk_points.append({
                'type': 'memory',
                'description': 'Memory under high usage for extended period (over 70% of time above 80% of threshold)',
                'severity': 'medium'
            })
        
        return risk_points
    
    def generate_trend_chart(self, ip_address, resource_type='cpu'):
        """生成趋势图并返回base64编码的图片"""
        try:
            # 获取一周的数据
            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)
            
            if resource_type == 'cpu':
                data = self.db_manager.get_cpu_history_by_time_range(ip_address, start_time, end_time)
                values = [item['cpu_percent'] for item in data if item.get('cpu_percent') is not None]
                title = 'CPU Usage Trend'
                color = '#0d6efd'
                threshold = self.config.CPU_THRESHOLD
            elif resource_type == 'memory':
                data = self.db_manager.get_memory_history_by_time_range(ip_address, start_time, end_time)
                values = [item['percent'] for item in data if item.get('percent') is not None]
                title = 'Memory Usage Trend'
                color = '#ffc107'
                threshold = self.config.MEMORY_THRESHOLD
            elif resource_type == 'disk':
                data = self.db_manager.get_disk_history_by_time_range(ip_address, start_time, end_time)
                values = [item['percent'] for item in data if item.get('percent') is not None]
                title = 'Disk Usage Trend'
                color = '#198754'
                threshold = self.config.DISK_THRESHOLD
            else:
                return None
            
            if not values:
                return None
            
            # 创建图表
            plt.figure(figsize=(10, 6))
            plt.plot(values, color=color, linewidth=2, marker='o', markersize=3)
            
            # 添加阈值线
            plt.axhline(y=threshold, color='red', linestyle='--', alpha=0.7, label=f'Threshold ({threshold}%)')
            
            # 设置图表样式
            plt.title(title, fontsize=16, pad=20)
            plt.xlabel('Time Points', fontsize=12)
            plt.ylabel('Usage (%)', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # 设置y轴范围
            plt.ylim(0, max(100, max(values) * 1.1))
            
            # 优化x轴显示
            if len(values) > 20:
                step = len(values) // 10
                plt.xticks(range(0, len(values), step))
            
            # 调整布局
            plt.tight_layout()
            
            # 保存为base64编码的图片
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return img_base64
        except Exception as e:
            monitor_logger.error(f"生成趋势图失败: {e}")
            return None
    
    def get_html_weekly_report_template(self, report_data):
        """获取HTML周报模板"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>服务器资源使用周报</title>
            <style>
                body {{
                    font-family: 'Microsoft YaHei', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background-color: #ffffff;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 16px;
                }}
                .content {{
                    padding: 40px;
                }}
                .report-period {{
                    background-color: #e7f3ff;
                    padding: 15px 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    text-align: center;
                    font-weight: 500;
                }}
                .server-section {{
                    margin-bottom: 40px;
                    border: 1px solid #e9ecef;
                    border-radius: 10px;
                    overflow: hidden;
                }}
                .server-header {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-bottom: 1px solid #e9ecef;
                }}
                .server-header h2 {{
                    margin: 0;
                    color: #212529;
                    font-size: 22px;
                }}
                .server-content {{
                    padding: 25px;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 25px;
                    margin-bottom: 30px;
                }}
                .metric-card {{
                    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                    border-radius: 12px;
                    padding: 25px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    border: 1px solid #e9ecef;
                }}
                .metric-card h3 {{
                    margin: 0 0 15px 0;
                    font-size: 18px;
                    color: #495057;
                }}
                .metric-value {{
                    font-size: 28px;
                    font-weight: 700;
                    margin: 10px 0;
                }}
                .metric-cpu {{ color: #0d6efd; }}
                .metric-memory {{ color: #ffc107; }}
                .metric-disk {{ color: #198754; }}
                .metric-stats {{
                    display: flex;
                    justify-content: space-between;
                    margin-top: 15px;
                    font-size: 14px;
                }}
                .stat-item {{
                    text-align: center;
                }}
                .stat-label {{
                    color: #6c757d;
                    font-size: 12px;
                }}
                .stat-value {{
                    font-weight: 600;
                    margin-top: 3px;
                }}
                .trend-section {{
                    margin: 30px 0;
                }}
                .trend-section h3 {{
                    margin: 0 0 20px 0;
                    color: #495057;
                }}
                .chart-container {{
                    text-align: center;
                    margin-bottom: 25px;
                }}
                .chart-container img {{
                    max-width: 100%;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .risk-section {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 20px;
                    border-radius: 0 8px 8px 0;
                    margin: 25px 0;
                }}
                .risk-section.high {{
                    background-color: #f8d7da;
                    border-left-color: #dc3545;
                }}
                .risk-section.medium {{
                    background-color: #fff3cd;
                    border-left-color: #ffc107;
                }}
                .risk-section h3 {{
                    margin: 0 0 15px 0;
                    color: #495057;
                }}
                .risk-item {{
                    padding: 12px 15px;
                    background-color: rgba(255,255,255,0.7);
                    border-radius: 6px;
                    margin-bottom: 10px;
                }}
                .risk-item:last-child {{
                    margin-bottom: 0;
                }}
                .risk-high {{ border-left: 3px solid #dc3545; }}
                .risk-medium {{ border-left: 3px solid #ffc107; }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 30px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                    border-top: 1px solid #e9ecef;
                }}
                .no-data {{
                    text-align: center;
                    padding: 40px;
                    color: #6c757d;
                }}
                @media (max-width: 768px) {{
                    .metrics-grid {{
                        grid-template-columns: 1fr;
                    }}
                    .header, .content, .footer {{
                        padding: 20px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🖥️ 服务器资源使用周报</h1>
                    <p>本周服务器资源使用情况分析报告</p>
                </div>
                
                <div class="content">
                    <div class="report-period">
                        报告周期: {(datetime.now() - timedelta(days=7)).strftime('%Y年%m月%d日')} - {datetime.now().strftime('%Y年%m月%d日')}
                    </div>
                    
                    {self._generate_server_sections(report_data)}
                </div>
                
                <div class="footer">
                    <p>此邮件由服务器监控系统自动生成，请勿回复。</p>
                    <p style="margin: 5px 0 0 0;">如有疑问，请联系系统管理员。</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content
    
    def _generate_server_sections(self, report_data):
        """生成服务器部分"""
        if not report_data:
            return '<div class="no-data"><h3>暂无服务器数据</h3><p>系统中没有找到任何服务器信息</p></div>'
        
        sections = []
        for server_data in report_data:
            server_section = f"""
            <div class="server-section">
                <div class="server-header">
                    <h2>📡 {server_data['server_info']['hostname']} ({server_data['server_info']['ip_address']})</h2>
                </div>
                <div class="server-content">
                    <div class="metrics-grid">
                        {self._generate_metric_card('CPU使用率', server_data['cpu_analysis'], 'cpu')}
                        {self._generate_metric_card('内存使用率', server_data['memory_analysis'], 'memory')}
                        {self._generate_metric_card('磁盘使用率', server_data['disk_analysis'], 'disk')}
                    </div>
                    
                    {self._generate_trend_charts(server_data['server_info']['ip_address'])}
                    
                    {self._generate_risk_section(server_data['risk_points'])}
                </div>
            </div>
            """
            sections.append(server_section)
        
        return ''.join(sections)
    
    def _generate_metric_card(self, title, analysis, metric_type):
        """生成指标卡片"""
        trend_icon = {
            'increasing': '📈',
            'decreasing': '📉',
            'stable': '➡️',
            'unknown': '❓'
        }.get(analysis['trend'], '❓')
        
        trend_text = {
            'increasing': '上升趋势',
            'decreasing': '下降趋势',
            'stable': '稳定',
            'unknown': '未知'
        }.get(analysis['trend'], '未知')
        
        metric_class = f"metric-{metric_type}"
        
        card = f"""
        <div class="metric-card">
            <h3>{title}</h3>
            <div class="metric-value {metric_class}">{analysis['current']}%</div>
            <div class="metric-stats">
                <div class="stat-item">
                    <div class="stat-label">最低</div>
                    <div class="stat-value">{analysis['min']}%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">平均</div>
                    <div class="stat-value">{analysis['avg']}%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">最高</div>
                    <div class="stat-value">{analysis['max']}%</div>
                </div>
            </div>
            <div style="margin-top: 15px; text-align: center; font-size: 14px; color: #6c757d;">
                {trend_icon} {trend_text}
            </div>
        </div>
        """
        return card
    
    def _generate_trend_charts(self, ip_address):
        """生成趋势图部分"""
        cpu_chart = self.generate_trend_chart(ip_address, 'cpu')
        memory_chart = self.generate_trend_chart(ip_address, 'memory')
        disk_chart = self.generate_trend_chart(ip_address, 'disk')
        
        charts_section = """
        <div class="trend-section">
            <h3>📈 一周资源使用趋势</h3>
        """
        
        if cpu_chart:
            charts_section += f"""
            <div class="chart-container">
                <h4>CPU使用率趋势</h4>
                <img src="data:image/png;base64,{cpu_chart}" alt="CPU使用率趋势图">
            </div>
            """
        
        if memory_chart:
            charts_section += f"""
            <div class="chart-container">
                <h4>内存使用率趋势</h4>
                <img src="data:image/png;base64,{memory_chart}" alt="内存使用率趋势图">
            </div>
            """
        
        if disk_chart:
            charts_section += f"""
            <div class="chart-container">
                <h4>磁盘使用率趋势</h4>
                <img src="data:image/png;base64,{disk_chart}" alt="磁盘使用率趋势图">
            </div>
            """
        
        charts_section += """
        </div>
        """
        
        return charts_section
    
    def _generate_risk_section(self, risk_points):
        """生成风险点部分"""
        if not risk_points:
            return """
            <div class="risk-section" style="background-color: #d1ecf1; border-left-color: #0dcaf0;">
                <h3>✅ 系统状态良好</h3>
                <p>本周服务器运行稳定，未发现明显风险点。</p>
            </div>
            """
        
        # 按严重程度分组
        high_risks = [r for r in risk_points if r['severity'] == 'high']
        medium_risks = [r for r in risk_points if r['severity'] == 'medium']
        
        risk_section = '<div class="risk-section'
        
        if high_risks:
            risk_section += ' high"><h3>⚠️ 发现高风险问题</h3>'
            for risk in high_risks:
                risk_section += f'<div class="risk-item risk-high"><strong>{risk["description"]}</strong></div>'
        elif medium_risks:
            risk_section += ' medium"><h3>⚠️ 发现中等风险问题</h3>'
            for risk in medium_risks:
                risk_section += f'<div class="risk-item risk-medium"><strong>{risk["description"]}</strong></div>'
        
        risk_section += '</div>'
        return risk_section
    
    def send_weekly_report_email(self):
        """发送周报邮件"""
        try:
            # 检查邮件配置是否完整
            if not all([self.config.MAIL_SERVER, self.config.MAIL_USERNAME, 
                       self.config.MAIL_PASSWORD, self.config.ADMIN_EMAIL]):
                monitor_logger.warning("邮件配置不完整，跳过周报邮件发送")
                return False
            
            # 生成周报数据
            report_data = self.generate_weekly_report_data()
            
            # 生成HTML邮件内容
            html_content = self.get_html_weekly_report_template(report_data)
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config.MAIL_DEFAULT_SENDER
            msg['To'] = self.config.ADMIN_EMAIL
            msg['Subject'] = f"【服务器监控周报】{datetime.now().strftime('%Y年%m月%d日')}"
            
            # 添加HTML内容
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # 发送邮件
            if self.config.MAIL_PORT == 465:
                server = smtplib.SMTP_SSL(self.config.MAIL_SERVER, self.config.MAIL_PORT)
            else:
                server = smtplib.SMTP(self.config.MAIL_SERVER, self.config.MAIL_PORT)
                server.starttls()
            
            server.login(self.config.MAIL_USERNAME, self.config.MAIL_PASSWORD)
            server.sendmail(self.config.MAIL_DEFAULT_SENDER, self.config.ADMIN_EMAIL, msg.as_string())
            server.quit()
            
            monitor_logger.info("周报邮件发送成功")
            return True
            
        except Exception as e:
            monitor_logger.error(f"发送周报邮件失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        self.db_manager.close()
        self.chart_service.close()