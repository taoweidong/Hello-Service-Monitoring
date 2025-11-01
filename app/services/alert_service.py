from app.models.models import AlertInfo
from app.database import DatabaseManager
from app.logger import monitor_logger
from app.config.config import Config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

class AlertService:
    """预警服务"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.config = Config
    
    def create_alert(self, ip_address, alert_type, message):
        """创建预警信息"""
        try:
            alert_info = {
                'ip_address': ip_address,
                'timestamp': datetime.datetime.now(),
                'alert_type': alert_type,
                'alert_message': message,
                'is_sent': 0
            }
            
            self.db_manager.save_alert_info(alert_info)
            monitor_logger.info(f"创建预警信息: {ip_address} - {alert_type} - {message}")
            
            return alert_info
        except Exception as e:
            monitor_logger.error(f"创建预警信息失败: {e}")
            return None
    
    def get_unsent_alerts(self):
        """获取未发送的预警信息"""
        try:
            alerts = self.db_manager.get_unsent_alerts()
            return alerts
        except Exception as e:
            monitor_logger.error(f"获取未发送预警信息失败: {e}")
            return []
    
    def send_email_alert(self, alert):
        """发送邮件预警"""
        try:
            # 创建邮件内容
            msg = MIMEMultipart()
            msg['From'] = self.config.MAIL_DEFAULT_SENDER
            msg['To'] = self.config.ADMIN_EMAIL
            msg['Subject'] = f"服务器监控预警 - {alert.ip_address}"
            
            body = f"""
            预警类型: {alert.alert_type}
            服务器IP: {alert.ip_address}
            预警时间: {alert.timestamp}
            预警信息: {alert.alert_message}
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP(self.config.MAIL_SERVER, self.config.MAIL_PORT)
            server.starttls()
            server.login(self.config.MAIL_USERNAME, self.config.MAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(self.config.MAIL_DEFAULT_SENDER, self.config.ADMIN_EMAIL, text)
            server.quit()
            
            # 标记为已发送
            self.db_manager.mark_alert_as_sent(alert.id)
            
            monitor_logger.info(f"发送邮件预警成功: {alert.ip_address} - {alert.alert_type}")
            return True
        except Exception as e:
            monitor_logger.error(f"发送邮件预警失败: {e}")
            return False
    
    def check_and_send_alerts(self):
        """检查并发送所有未发送的预警"""
        try:
            unsent_alerts = self.get_unsent_alerts()
            
            for alert in unsent_alerts:
                self.send_email_alert(alert)
            
            monitor_logger.info(f"完成预警检查和发送，共处理 {len(unsent_alerts)} 条预警")
        except Exception as e:
            monitor_logger.error(f"检查和发送预警失败: {e}")
    
    def close(self):
        """关闭数据库连接"""
        self.db_manager.close()