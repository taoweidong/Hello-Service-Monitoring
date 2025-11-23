# app/utils/email_utils.py
"""邮件发送工具类"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import Optional, List
from loguru import logger

from ..config.config import Config


class EmailSender:
    """邮件发送器"""
    
    def __init__(self):
        """初始化邮件发送器"""
        self.mail_server = Config.MAIL_SERVER
        self.mail_port = Config.MAIL_PORT
        self.mail_username = Config.MAIL_USERNAME
        self.mail_password = Config.MAIL_PASSWORD
        self.mail_default_sender = Config.MAIL_DEFAULT_SENDER
        
    def is_configured(self) -> bool:
        """
        检查邮件配置是否完整
        
        Returns:
            bool: 配置是否完整
        """
        return bool(self.mail_server and self.mail_username and self.mail_password)
    
    def send_email(
        self,
        subject: str,
        html_content: str,
        recipients: Optional[List[str]] = None,
        images: Optional[List[tuple]] = None
    ) -> bool:
        """
        发送邮件
        
        Args:
            subject: 邮件主题
            html_content: HTML内容
            recipients: 收件人列表，默认为发件人自己
            images: 图片附件列表，每个元素为(文件路径, content_id)元组
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 检查邮件配置
            if not self.is_configured():
                logger.warning("邮件配置不完整，无法发送邮件")
                return False
            
            # 设置收件人
            if recipients is None:
                recipients = [self.mail_default_sender or self.mail_username]
            
            # 创建邮件
            msg = MIMEMultipart('related')
            msg['Subject'] = subject
            msg['From'] = self.mail_default_sender or self.mail_username
            msg['To'] = ', '.join(recipients)
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 添加图片附件
            if images:
                for image_path, content_id in images:
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', f'<{content_id}>')
                            msg.attach(img)
            
            # 发送邮件
            server = smtplib.SMTP(self.mail_server, self.mail_port)
            server.starttls()
            server.login(self.mail_username, self.mail_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"邮件发送成功: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件时出错: {e}")
            return False