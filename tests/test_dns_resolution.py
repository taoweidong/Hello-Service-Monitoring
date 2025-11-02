"""测试DNS解析问题"""
import sys
import os
import socket
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

from app.config.config import Config

def test_dns_resolution():
    """测试DNS解析"""
    print("测试DNS解析...")
    
    try:
        # 获取邮件服务器配置
        mail_server = Config.MAIL_SERVER
        print(f"邮件服务器: {mail_server}")
        
        # 测试DNS解析
        print(f"测试DNS解析 {mail_server}...")
        result = socket.getaddrinfo(mail_server, None)
        print(f"✅ DNS解析成功")
        for res in result:
            print(f"  -> {res[4][0]}")
            
    except socket.gaierror as e:
        print(f"❌ DNS解析失败: {e}")
        print(f"错误代码: {e.errno}")
        if e.errno == 11001:
            print("  这是WSAHOST_NOT_FOUND错误，表示主机未找到")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        traceback.print_exc()

def test_with_different_dns():
    """使用不同方法测试DNS解析"""
    print("\n使用不同方法测试DNS解析...")
    
    mail_server = Config.MAIL_SERVER
    
    try:
        # 方法1: 使用socket.gethostbyname
        print("方法1: socket.gethostbyname")
        ip = socket.gethostbyname(mail_server)
        print(f"✅ 解析成功: {mail_server} -> {ip}")
        
    except socket.gaierror as e:
        print(f"❌ socket.gethostbyname解析失败: {e}")
    except Exception as e:
        print(f"方法1出现错误: {e}")
    
    try:
        # 方法2: 使用socket.getaddrinfo with AF_INET
        print("\n方法2: socket.getaddrinfo with AF_INET")
        result = socket.getaddrinfo(mail_server, None, socket.AF_INET)
        print(f"✅ 解析成功")
        for res in result:
            print(f"  -> {res[4][0]}")
            
    except socket.gaierror as e:
        print(f"❌ socket.getaddrinfo解析失败: {e}")
    except Exception as e:
        print(f"方法2出现错误: {e}")

if __name__ == "__main__":
    test_dns_resolution()
    test_with_different_dns()