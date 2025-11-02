"""诊断网络连接问题"""
import os
import socket
import smtplib
import time
from dotenv import load_dotenv

def diagnose_network():
    """诊断网络连接"""
    # 加载环境变量
    load_dotenv('.env', encoding='utf-8')
    
    # 获取配置
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '465'))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '546642132@qq.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'luspyjrneugabgaj')
    
    print(f"诊断配置:")
    print(f"  MAIL_SERVER: {MAIL_SERVER}")
    print(f"  MAIL_PORT: {MAIL_PORT}")
    print(f"  MAIL_USERNAME: {MAIL_USERNAME}")
    
    # 1. 测试基本网络连接
    print(f"\n=== 1. 测试基本网络连接 ===")
    try:
        print(f"测试DNS解析 {MAIL_SERVER}...")
        start_time = time.time()
        result = socket.getaddrinfo(MAIL_SERVER, None)
        end_time = time.time()
        print(f"  ✅ DNS解析成功 (耗时: {end_time - start_time:.2f}秒)")
        for res in result:
            print(f"     -> {res[4][0]}")
    except Exception as e:
        print(f"  ❌ DNS解析失败: {e}")
        return
    
    # 2. 测试端口连通性
    print(f"\n=== 2. 测试端口连通性 ===")
    try:
        ip_address = result[0][4][0]
        print(f"测试连接到 {ip_address}:{MAIL_PORT}...")
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((ip_address, MAIL_PORT))
        end_time = time.time()
        sock.close()
        
        if result == 0:
            print(f"  ✅ 端口连接成功 (耗时: {end_time - start_time:.2f}秒)")
        else:
            print(f"  ❌ 端口连接失败 (错误码: {result})")
    except Exception as e:
        print(f"  ❌ 端口连接测试失败: {e}")
    
    # 3. 测试SMTP连接
    print(f"\n=== 3. 测试SMTP连接 ===")
    try:
        print(f"连接到SMTP服务器 {MAIL_SERVER}:{MAIL_PORT}...")
        start_time = time.time()
        if MAIL_PORT == 465:
            server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, timeout=30)
        else:
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=30)
            server.starttls()
        end_time = time.time()
        print(f"  ✅ SMTP连接成功 (耗时: {end_time - start_time:.2f}秒)")
        
        # 测试登录
        print(f"测试登录 {MAIL_USERNAME}...")
        start_time = time.time()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        end_time = time.time()
        print(f"  ✅ SMTP登录成功 (耗时: {end_time - start_time:.2f}秒)")
        server.quit()
        
    except Exception as e:
        print(f"  ❌ SMTP测试失败: {e}")
    
    print(f"\n=== 诊断完成 ===")

if __name__ == "__main__":
    diagnose_network()