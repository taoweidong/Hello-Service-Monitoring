"""简单的邮件发送测试"""
import smtplib
import os
from dotenv import load_dotenv

# 加载环境变量
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path, encoding='utf-8')

# 获取配置
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.qq.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', '465'))
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '546642132@qq.com')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'luspyjrneugabgaj')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', '546642132@qq.com')

print(f"测试配置:")
print(f"  MAIL_SERVER: {MAIL_SERVER}")
print(f"  MAIL_PORT: {MAIL_PORT}")
print(f"  MAIL_USERNAME: {MAIL_USERNAME}")
print(f"  ADMIN_EMAIL: {ADMIN_EMAIL}")

try:
    print(f"\n连接到SMTP服务器 {MAIL_SERVER}:{MAIL_PORT}...")
    if MAIL_PORT == 465:
        server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, timeout=30)
    else:
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=30)
        server.starttls()
    
    print("✅ 连接成功")
    
    print(f"登录 {MAIL_USERNAME}...")
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    print("✅ 登录成功")
    
    server.quit()
    print("✅ 连接已关闭")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")