"""邮件服务模块 - 负责发送美化的预警邮件"""
from flask import render_template_string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
import socket
import time
from datetime import datetime, timedelta
from app.config.config import Config
from app.utils.logger import monitor_logger
from app.services.database import DatabaseManager
from app.models.models import ServerInfo, AlertInfo


class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self.config = Config
        self.db_manager = DatabaseManager()
    
    def get_html_email_template(self, alert_info, server_info, monitor_data):
        """获取HTML邮件模板"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>服务器监控预警</title>
            <style>
                body {{
                    font-family: 'Microsoft YaHei', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 30px;
                }}
                .alert-box {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .alert-box.critical {{
                    background-color: #f8d7da;
                    border-left-color: #dc3545;
                }}
                .alert-box.warning {{
                    background-color: #fff3cd;
                    border-left-color: #ffc107;
                }}
                .alert-type {{
                    display: inline-block;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 10px;
                }}
                .alert-type.cpu {{
                    background-color: #0d6efd;
                    color: white;
                }}
                .alert-type.memory {{
                    background-color: #ffc107;
                    color: #000;
                }}
                .alert-type.disk {{
                    background-color: #198754;
                    color: white;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                    margin: 20px 0;
                }}
                .info-card {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border: 1px solid #dee2e6;
                }}
                .info-card h3 {{
                    margin: 0 0 10px 0;
                    font-size: 14px;
                    color: #6c757d;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .info-card .value {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #212529;
                    margin: 10px 0;
                }}
                .info-card .label {{
                    font-size: 12px;
                    color: #6c757d;
                }}
                .progress-bar {{
                    width: 100%;
                    height: 10px;
                    background-color: #e9ecef;
                    border-radius: 5px;
                    overflow: hidden;
                    margin-top: 10px;
                }}
                .progress-fill {{
                    height: 100%;
                    transition: width 0.3s ease;
                }}
                .progress-fill.cpu {{
                    background-color: #0d6efd;
                }}
                .progress-fill.memory {{
                    background-color: #ffc107;
                }}
                .progress-fill.disk {{
                    background-color: #198754;
                }}
                .progress-fill.danger {{
                    background-color: #dc3545;
                }}
                .server-info {{
                    background-color: #e7f3ff;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .server-info h3 {{
                    margin-top: 0;
                    color: #0d6efd;
                }}
                .server-info table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .server-info table td {{
                    padding: 8px;
                    border-bottom: 1px solid #dee2e6;
                }}
                .server-info table td:first-child {{
                    font-weight: 600;
                    width: 150px;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 12px;
                }}
                .metric-row {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px 0;
                    border-bottom: 1px solid #e9ecef;
                }}
                .metric-row:last-child {{
                    border-bottom: none;
                }}
                .metric-label {{
                    font-weight: 600;
                    color: #495057;
                }}
                .metric-value {{
                    font-size: 18px;
                    font-weight: 700;
                }}
                @media (max-width: 600px) {{
                    .info-grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ 服务器监控预警通知</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
                </div>
                
                <div class="content">
                    <div class="alert-box {'critical' if alert_info['alert_type'] in ['cpu', 'memory', 'disk'] else 'warning'}">
                        <span class="alert-type {alert_info['alert_type']}">
                            {self._get_alert_type_icon(alert_info['alert_type'])} {self._get_alert_type_name(alert_info['alert_type'])}
                        </span>
                        <h2 style="margin: 15px 0 10px 0; color: #212529;">预警信息</h2>
                        <p style="font-size: 16px; margin: 0; color: #495057;">{alert_info['alert_message']}</p>
                        <p style="margin-top: 10px; color: #6c757d; font-size: 14px;">
                            <strong>预警时间:</strong> {alert_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(alert_info['timestamp'], datetime) else alert_info['timestamp']}
                        </p>
                    </div>

                    {self._generate_server_info_section(server_info)}
                    {self._generate_monitor_data_section(monitor_data, alert_info['alert_type'])}
                </div>
                
                <div class="footer">
                    <p>此邮件由服务器监控系统自动发送，请勿回复。</p>
                    <p style="margin: 5px 0 0 0;">如有疑问，请联系系统管理员。</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content
    
    def _get_alert_type_icon(self, alert_type):
        """获取预警类型图标"""
        icons = {
            'cpu': '🔴',
            'memory': '🟡',
            'disk': '🟢'
        }
        return icons.get(alert_type, '⚠️')
    
    def _get_alert_type_name(self, alert_type):
        """获取预警类型名称"""
        names = {
            'cpu': 'CPU使用率预警',
            'memory': '内存使用率预警',
            'disk': '磁盘使用率预警'
        }
        return names.get(alert_type, '系统预警')
    
    def _generate_server_info_section(self, server_info):
        """生成服务器信息部分"""
        if not server_info:
            return "<div class='server-info'><h3>服务器信息</h3><p>暂无服务器信息</p></div>"
        
        section = f"""
        <div class="server-info">
            <h3>📊 服务器信息</h3>
            <table>
                <tr>
                    <td>IP地址:</td>
                    <td><strong>{server_info.get('ip_address', 'N/A')}</strong></td>
                </tr>
                <tr>
                    <td>主机名:</td>
                    <td>{server_info.get('hostname', 'N/A')}</td>
                </tr>
                <tr>
                    <td>系统版本:</td>
                    <td>{server_info.get('system_version', 'N/A')}</td>
                </tr>
                <tr>
                    <td>内核版本:</td>
                    <td>{server_info.get('kernel_version', 'N/A')}</td>
                </tr>
                <tr>
                    <td>CPU核心数:</td>
                    <td>{server_info.get('cpu_count', 'N/A')}</td>
                </tr>
                <tr>
                    <td>总内存:</td>
                    <td>{server_info.get('total_memory', 'N/A')}</td>
                </tr>
                <tr>
                    <td>总磁盘:</td>
                    <td>{server_info.get('total_disk', 'N/A')}</td>
                </tr>
                <tr>
                    <td>运行时间:</td>
                    <td>{server_info.get('uptime', 'N/A')}</td>
                </tr>
                <tr>
                    <td>连接状态:</td>
                    <td>{'<span style="color: red;">连接失败</span>' if server_info.get('connection_failed', False) else '<span style="color: green;">连接成功</span>'}</td>
                </tr>
            </table>
        </div>
        """
        return section
    
    def _generate_monitor_data_section(self, monitor_data, alert_type):
        """生成监控数据部分"""
        if not monitor_data:
            return ""
        
        section = f"""
        <div style="margin-top: 30px;">
            <h3 style="color: #495057; margin-bottom: 20px;">📈 当前监控数据</h3>
            <div class="info-grid">
        """
        
        # CPU信息
        if monitor_data.get('cpu_info'):
            cpu_percent = monitor_data['cpu_info'].get('cpu_percent', 0)
            section += f"""
                <div class="info-card">
                    <h3>CPU使用率</h3>
                    <div class="value {'text-danger' if cpu_percent > self.config.CPU_THRESHOLD else ''}">{cpu_percent:.1f}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill cpu {'danger' if cpu_percent > self.config.CPU_THRESHOLD else ''}" style="width: {cpu_percent}%;"></div>
                    </div>
                    <div class="label">核心数: {monitor_data['cpu_info'].get('cpu_count', 'N/A')}</div>
                    <div class="label">频率: {monitor_data['cpu_info'].get('cpu_current_freq', 0) / 1000:.2f} GHz</div>
                </div>
            """
        
        # 内存信息
        if monitor_data.get('memory_info'):
            memory_percent = monitor_data['memory_info'].get('percent', 0)
            total_gb = monitor_data['memory_info'].get('total', 0) / (1024**3)
            used_gb = monitor_data['memory_info'].get('used', 0) / (1024**3)
            section += f"""
                <div class="info-card">
                    <h3>内存使用率</h3>
                    <div class="value {'text-danger' if memory_percent > self.config.MEMORY_THRESHOLD else ''}">{memory_percent:.1f}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill memory {'danger' if memory_percent > self.config.MEMORY_THRESHOLD else ''}" style="width: {memory_percent}%;"></div>
                    </div>
                    <div class="label">已用: {used_gb:.2f} GB / {total_gb:.2f} GB</div>
                    <div class="label">可用: {(total_gb - used_gb):.2f} GB</div>
                </div>
            """
        
        # 磁盘信息
        if monitor_data.get('disk_info'):
            disk_percent = monitor_data['disk_info'].get('percent', 0)
            total_gb = monitor_data['disk_info'].get('total', 0) / (1024**3)
            used_gb = monitor_data['disk_info'].get('used', 0) / (1024**3)
            section += f"""
                <div class="info-card">
                    <h3>磁盘使用率</h3>
                    <div class="value {'text-danger' if disk_percent > self.config.DISK_THRESHOLD else ''}">{disk_percent:.1f}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill disk {'danger' if disk_percent > self.config.DISK_THRESHOLD else ''}" style="width: {disk_percent}%;"></div>
                    </div>
                    <div class="label">已用: {used_gb:.2f} GB / {total_gb:.2f} GB</div>
                    <div class="label">可用: {(total_gb - used_gb):.2f} GB</div>
                </div>
            """
        
        section += """
            </div>
        </div>
        """
        return section
    
    def _should_send_alert(self, ip_address, alert_type):
        """检查是否应该发送预警邮件（1小时内相同类型预警不重复发送）"""
        try:
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_alerts = self.db_manager.session.query(AlertInfo).filter(
                AlertInfo.ip_address == ip_address,
                AlertInfo.alert_type == alert_type,
                AlertInfo.timestamp >= one_hour_ago,
                AlertInfo.is_sent == 1
            ).count()
            
            # 如果1小时内已经发送过相同类型的预警，则不发送
            should_send = recent_alerts == 0
            monitor_logger.info(f"检查预警发送条件: IP={ip_address}, 类型={alert_type}, 近期预警数={recent_alerts}, 是否发送={should_send}")
            return should_send
        except Exception as e:
            monitor_logger.error(f"检查预警发送条件失败: {e}")
            # 出错时默认发送
            return True
    
    def _test_smtp_connection(self):
        """测试SMTP连接"""
        try:
            # 检查DNS解析
            socket.getaddrinfo(self.config.MAIL_SERVER, None)
            monitor_logger.info(f"SMTP服务器DNS解析成功: {self.config.MAIL_SERVER}")
            
            # 测试连接
            if self.config.MAIL_PORT == 465:
                server = smtplib.SMTP_SSL(self.config.MAIL_SERVER, self.config.MAIL_PORT, timeout=10)
            else:
                server = smtplib.SMTP(self.config.MAIL_SERVER, self.config.MAIL_PORT, timeout=10)
                server.starttls()
            
            server.quit()
            monitor_logger.info(f"SMTP服务器连接测试成功: {self.config.MAIL_SERVER}:{self.config.MAIL_PORT}")
            return True
        except socket.gaierror as e:
            monitor_logger.error(f"SMTP服务器DNS解析失败: {self.config.MAIL_SERVER}, 错误: {e}")
            return False
        except Exception as e:
            monitor_logger.error(f"SMTP服务器连接测试失败: {self.config.MAIL_SERVER}:{self.config.MAIL_PORT}, 错误: {e}")
            return False
    
    def _send_email_with_retry(self, msg):
        """带重试机制的邮件发送"""
        max_retries = 3
        retry_delay = 5  # 重试间隔（秒）
        
        for attempt in range(max_retries):
            try:
                monitor_logger.info(f"尝试发送邮件 (第{attempt + 1}/{max_retries}次)")
                if self.config.MAIL_PORT == 465:
                    server = smtplib.SMTP_SSL(self.config.MAIL_SERVER, self.config.MAIL_PORT, timeout=30)
                else:
                    server = smtplib.SMTP(self.config.MAIL_SERVER, self.config.MAIL_PORT, timeout=30)
                    server.starttls()
                
                server.login(self.config.MAIL_USERNAME, self.config.MAIL_PASSWORD)
                server.sendmail(self.config.MAIL_DEFAULT_SENDER, self.config.ADMIN_EMAIL, msg.as_string())
                server.quit()
                
                monitor_logger.info(f"邮件发送成功")
                return True
                
            except socket.gaierror as e:
                monitor_logger.error(f"邮件发送失败 - DNS解析错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    monitor_logger.info(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    return False
            except smtplib.SMTPAuthenticationError as e:
                monitor_logger.error(f"邮件发送失败 - SMTP认证错误: {e}")
                return False
            except smtplib.SMTPException as e:
                monitor_logger.error(f"邮件发送失败 - SMTP错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    monitor_logger.info(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    return False
            except Exception as e:
                monitor_logger.error(f"邮件发送失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    monitor_logger.info(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    return False
        
        return False
    
    def send_alert_email(self, alert_info, server_info=None, monitor_data=None):
        """发送预警邮件"""
        try:
            # 检查邮件配置是否完整
            if not all([self.config.MAIL_SERVER, self.config.MAIL_USERNAME, 
                       self.config.MAIL_PASSWORD, self.config.ADMIN_EMAIL]):
                monitor_logger.warning("邮件配置不完整，跳过邮件发送")
                return False
            
            # 检查1小时内是否已发送相同类型的预警
            if not self._should_send_alert(alert_info['ip_address'], alert_info['alert_type']):
                monitor_logger.info(f"1小时内已发送过相同类型的预警邮件，跳过发送: {alert_info['ip_address']} - {alert_info['alert_type']}")
                return False
            
            # 如果没有提供服务器信息，从数据库获取
            if not server_info:
                server = self.db_manager.session.query(ServerInfo).filter_by(
                    ip_address=alert_info['ip_address']
                ).first()
                if server:
                    server_info = {
                        'ip_address': server.ip_address,
                        'hostname': server.hostname or 'Unknown'
                    }
                else:
                    server_info = {
                        'ip_address': alert_info['ip_address'],
                        'hostname': 'Unknown'
                    }
            
            # 生成HTML邮件内容
            html_content = self.get_html_email_template(alert_info, server_info, monitor_data)
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config.MAIL_DEFAULT_SENDER
            msg['To'] = self.config.ADMIN_EMAIL
            msg['Subject'] = f"【服务器监控预警】{self._get_alert_type_name(alert_info['alert_type'])} - {alert_info['ip_address']}"
            
            # 添加HTML内容
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # 发送邮件（带重试机制）
            monitor_logger.info(f"开始发送预警邮件: {alert_info['ip_address']} - {alert_info['alert_type']}")
            success = self._send_email_with_retry(msg)
            
            if success:
                monitor_logger.info(f"预警邮件发送成功: {alert_info['ip_address']} - {alert_info['alert_type']}")
            else:
                monitor_logger.error(f"预警邮件发送失败: {alert_info['ip_address']} - {alert_info['alert_type']}")
            
            return success
            
        except Exception as e:
            monitor_logger.error(f"发送预警邮件失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        self.db_manager.close()