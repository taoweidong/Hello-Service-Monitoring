from app.services.database import DatabaseManager
from app.utils.logger import monitor_logger
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config.config import Config

def check_and_alert(app, ip_address, alert_type, message):
    """检查并触发预警"""
    try:
        # 保存预警信息到数据库
        db_manager = DatabaseManager()
        
        alert_info = {
            'ip_address': ip_address,
            'timestamp': datetime.now(),
            'alert_type': alert_type,
            'alert_message': message,
            'is_sent': 0
        }
        
        db_manager.save_alert_info(alert_info)
        db_manager.close()
        
        # 发送邮件预警
        send_email_alert(app, alert_type, message)
        
        monitor_logger.info(f"预警已触发: {ip_address} - {alert_type} - {message}")
    except Exception as e:
        monitor_logger.error(f"预警触发失败: {e}")

def send_email_alert(app, alert_type, message):
    """发送邮件预警"""
    try:
        # 检查邮件配置是否完整
        if not all([Config.MAIL_SERVER, Config.MAIL_USERNAME, Config.MAIL_PASSWORD, Config.ADMIN_EMAIL]):
            monitor_logger.warning("邮件配置不完整，跳过邮件发送")
            return
            
        # 创建邮件内容
        msg = MIMEMultipart()
        msg['From'] = Config.MAIL_DEFAULT_SENDER
        msg['To'] = Config.ADMIN_EMAIL
        msg['Subject'] = f"服务器监控预警 - {alert_type}"
        
        body = f"""
        预警类型: {alert_type}
        预警信息: {message}
        时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        请及时处理此预警信息。
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 连接SMTP服务器并发送邮件
        server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
        server.starttls()
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(Config.MAIL_DEFAULT_SENDER, Config.ADMIN_EMAIL, text)
        server.quit()
        
        monitor_logger.info(f"预警邮件已发送: {alert_type} - {message}")
    except Exception as e:
        monitor_logger.error(f"发送预警邮件失败: {e}")

def process_unsent_alerts(app):
    """处理未发送的预警信息"""
    try:
        db_manager = DatabaseManager()
        unsent_alerts = db_manager.get_unsent_alerts()
        
        for alert in unsent_alerts:
            # 尝试重新发送邮件
            send_email_alert(app, alert.alert_type, alert.alert_message)
            # 标记为已发送
            db_manager.mark_alert_as_sent(alert.id)
        
        db_manager.close()
        monitor_logger.info(f"处理了 {len(unsent_alerts)} 条未发送的预警信息")
    except Exception as e:
        monitor_logger.error(f"处理未发送预警信息失败: {e}")