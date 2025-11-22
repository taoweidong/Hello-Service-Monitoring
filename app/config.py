# app/config.py
import os
from typing import Optional


class Config:
    """应用配置类"""
    
    # 获取项目根目录
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    MONITORING_DIR = os.path.join(BASE_DIR, 'app', 'monitoring')
    
    # 确保monitoring目录存在
    if not os.path.exists(MONITORING_DIR):
        os.makedirs(MONITORING_DIR)
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        'DATABASE_URL') or f'sqlite:///{os.path.join(MONITORING_DIR, "monitoring.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    
    # 定时任务配置
    SCHEDULER_API_ENABLED: bool = True
    
    # 邮件配置
    MAIL_SERVER: Optional[str] = os.environ.get('MAIL_SERVER')
    MAIL_PORT: int = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS: bool = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USERNAME: Optional[str] = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD: Optional[str] = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER: Optional[str] = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # 钉钉配置
    DINGTALK_WEBHOOK: Optional[str] = os.environ.get('DINGTALK_WEBHOOK')
    
    # 监控阈值配置
    MEMORY_THRESHOLD: float = float(os.environ.get('MEMORY_THRESHOLD') or 80.0)
    DISK_THRESHOLD: float = float(os.environ.get('DISK_THRESHOLD') or 80.0)