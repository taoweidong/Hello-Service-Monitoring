"""测试SMTP连接"""
import os
import socket
import smtplib
from dotenv import load_dotenv

def test_smtp():
    """测试SMTP连接"""
    # 加载环境变量
    load_dotenv('.env', encoding='utf-8')
    
    # 获取配置
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '465'))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '546642132@qq.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'luspyjrneugabgaj')
    
    print(f"测试配置:")
    print(f"  MAIL_SERVER: {MAIL_SERVER}")
    print(f"  MAIL_PORT: {MAIL_PORT}")
    print(f"  MAIL_USERNAME: {MAIL_USERNAME}")
    
    try:
        # 测试DNS解析
        print(f"\n1. 测试DNS解析 {MAIL_SERVER}...")
        result = socket.getaddrinfo(MAIL_SERVER, None)
        print(f"   ✅ DNS解析成功: {MAIL_SERVER} -> {result[0][4][0]}")
        
        # 测试SMTP连接
        print(f"\n2. 测试SMTP连接 {MAIL_SERVER}:{MAIL_PORT}...")
        if MAIL_PORT == 465:
            server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, timeout=30)
        else:
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=30)
            server.starttls()
        
        print("   ✅ SMTP连接成功")
        
        # 测试登录
        print(f"\n3. 测试登录 {MAIL_USERNAME}...")
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.quit()
        
        print("   ✅ SMTP登录成功")
        print("\n🎉 所有测试通过，邮件功能应该可以正常工作")
        
    except socket.gaierror as e:
        print(f"   ❌ DNS解析失败: {e}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ SMTP登录失败 - 认证错误: {e}")
    except smtplib.SMTPException as e:
        print(f"   ❌ SMTP连接失败 - SMTP错误: {e}")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")

if __name__ == "__main__":
    test_smtp()