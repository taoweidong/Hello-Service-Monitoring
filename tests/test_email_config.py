"""测试邮件配置和连接"""
import sys
import os
import socket
import smtplib
from dotenv import load_dotenv

# 获取项目根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(f"项目根目录: {project_root}")

# 加载环境变量
env_path = os.path.join(project_root, '.env')
print(f".env文件路径: {env_path}")

# 检查.env文件是否存在
if os.path.exists(env_path):
    print("✅ .env文件存在")
    load_dotenv(env_path, encoding='utf-8')
else:
    print("❌ .env文件不存在")

# 从环境变量获取配置
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.example.com')
MAIL_PORT = os.getenv('MAIL_PORT', '587')
MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your_username')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your_password')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'monitor@example.com')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')

print(f"环境变量值:")
print(f"  MAIL_SERVER: {MAIL_SERVER}")
print(f"  MAIL_PORT: {MAIL_PORT}")
print(f"  MAIL_USERNAME: {MAIL_USERNAME}")
#print(f"  MAIL_PASSWORD: {'*' * len(MAIL_PASSWORD) if MAIL_PASSWORD else None}")
print(f"  MAIL_DEFAULT_SENDER: {MAIL_DEFAULT_SENDER}")
print(f"  ADMIN_EMAIL: {ADMIN_EMAIL}")

# 确保端口是整数
try:
    MAIL_PORT = int(MAIL_PORT)
except (ValueError, TypeError):
    MAIL_PORT = 587

def test_email_configuration():
    """测试邮件配置"""
    print("\n开始测试邮件配置...")
    
    print(f"MAIL_SERVER: {MAIL_SERVER}")
    print(f"MAIL_PORT: {MAIL_PORT}")
    print(f"MAIL_USERNAME: {MAIL_USERNAME}")
    print(f"MAIL_DEFAULT_SENDER: {MAIL_DEFAULT_SENDER}")
    print(f"ADMIN_EMAIL: {ADMIN_EMAIL}")
    
    # 检查配置是否完整
    if not all([MAIL_SERVER, MAIL_USERNAME, 
                MAIL_PASSWORD, ADMIN_EMAIL]):
        print("❌ 邮件配置不完整")
        return False
    
    print("✅ 邮件配置完整")
    return True

def test_dns_resolution():
    """测试DNS解析"""
    print("\n开始测试DNS解析...")
    
    try:
        # 测试DNS解析
        result = socket.getaddrinfo(MAIL_SERVER, None)
        print(f"✅ DNS解析成功: {MAIL_SERVER} -> {result[0][4][0]}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS解析失败: {MAIL_SERVER}, 错误: {e}")
        return False
    except Exception as e:
        print(f"❌ DNS解析出错: {e}")
        return False

def test_smtp_connection():
    """测试SMTP连接"""
    print("\n开始测试SMTP连接...")
    
    try:
        print(f"连接到SMTP服务器: {MAIL_SERVER}:{MAIL_PORT}")
        if MAIL_PORT == 465:
            server = smtplib.SMTP_SSL(str(MAIL_SERVER), int(MAIL_PORT), timeout=30)
        else:
            server = smtplib.SMTP(str(MAIL_SERVER), int(MAIL_PORT), timeout=30)
            server.starttls()
        
        print("连接成功，开始登录...")
        server.login(str(MAIL_USERNAME), str(MAIL_PASSWORD))
        server.quit()
        
        print("✅ SMTP连接和登录成功")
        return True
    except socket.gaierror as e:
        print(f"❌ SMTP连接失败 - DNS解析错误: {e}")
        return False
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP登录失败 - 认证错误: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP连接失败 - SMTP错误: {e}")
        return False
    except Exception as e:
        print(f"❌ SMTP连接失败: {e}")
        return False

def main():
    """主函数"""
    print("=== 邮件配置和连接测试 ===")
    
    # 测试配置
    config_ok = test_email_configuration()
    if not config_ok:
        return
    
    # 测试DNS解析
    dns_ok = test_dns_resolution()
    
    # 测试SMTP连接
    smtp_ok = test_smtp_connection()
    
    print("\n=== 测试结果 ===")
    if config_ok and dns_ok and smtp_ok:
        print("🎉 所有测试通过，邮件功能应该可以正常工作")
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接")
        if not dns_ok:
            print("  - 请检查网络连接和DNS设置")
        if not smtp_ok:
            print("  - 请检查邮件服务器配置和认证信息")

if __name__ == "__main__":
    main()