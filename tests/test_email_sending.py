"""测试邮件发送功能"""
import sys
import os
import traceback
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# 切换到项目根目录
os.chdir(project_root)

# 加载环境变量
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path, encoding='utf-8')

from app.services.email_service import EmailService
from datetime import datetime

def test_email_sending():
    """测试邮件发送功能"""
    print("测试邮件发送功能...")
    
    try:
        # 创建邮件服务实例
        email_service = EmailService()
        
        # 检查邮件配置
        print(f"邮件配置:")
        print(f"  MAIL_SERVER: {email_service.config.MAIL_SERVER}")
        print(f"  MAIL_PORT: {email_service.config.MAIL_PORT}")
        print(f"  MAIL_USERNAME: {email_service.config.MAIL_USERNAME}")
        print(f"  ADMIN_EMAIL: {email_service.config.ADMIN_EMAIL}")
        
        # 创建测试预警信息
        alert_info = {
            'ip_address': '192.168.1.100',
            'alert_type': 'cpu',
            'alert_message': 'CPU使用率过高测试',
            'timestamp': datetime.now()
        }
        
        # 创建测试服务器信息
        server_info = {
            'ip_address': '192.168.1.100',
            'hostname': 'test-server',
            'system_version': 'Ubuntu 20.04',
            'kernel_version': '5.4.0',
            'platform': 'Linux',
            'architecture': 'x86_64',
            'processor': 'Intel Core i7',
            'cpu_count': 4,
            'cpu_count_logical': 8,
            'total_memory': '16.00 GB',
            'total_disk': '500.00 GB',
            'uptime': '5天 3小时 20分钟',
            'boot_time': '2023-01-01 10:00:00',
            'connection_failed': False
        }
        
        # 创建测试监控数据
        monitor_data = {
            'cpu_info': {
                'cpu_percent': 85.5,
                'cpu_count': 8,
                'cpu_current_freq': 3200
            },
            'memory_info': {
                'percent': 75.2,
                'total': 17179869184,
                'used': 12883869184,
                'free': 4296000000
            },
            'disk_info': {
                'percent': 65.8,
                'total': 536870912000,
                'used': 353687091200,
                'free': 183183820800
            }
        }
        
        print(f"发送测试邮件到: {email_service.config.ADMIN_EMAIL}")
        print(f"使用SMTP服务器: {email_service.config.MAIL_SERVER}:{email_service.config.MAIL_PORT}")
        
        # 发送邮件
        success = email_service.send_alert_email(alert_info, server_info, monitor_data)
        
        if success:
            print("✅ 邮件发送成功")
        else:
            print("❌ 邮件发送失败")
            
        # 关闭邮件服务
        email_service.close()
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_email_sending()