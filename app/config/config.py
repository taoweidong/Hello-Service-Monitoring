import os
from dotenv import load_dotenv

# 获取项目根目录
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 加载.env文件
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-please-change-in-production')
    
    # 数据库配置
    db_path = os.path.join(basedir, 'db', 'monitoring.db')
    DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')
    
    # 定时任务配置
    SCHEDULE_INTERVAL_MINUTES = int(os.getenv('SCHEDULE_INTERVAL_MINUTES', 2))
    
    # 预警阈值配置
    CPU_THRESHOLD = int(os.getenv('CPU_THRESHOLD', 80))
    MEMORY_THRESHOLD = int(os.getenv('MEMORY_THRESHOLD', 80))
    DISK_THRESHOLD = int(os.getenv('DISK_THRESHOLD', 80))
    
    # 邮件配置
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your_username')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your_password')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'monitor@example.com')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')