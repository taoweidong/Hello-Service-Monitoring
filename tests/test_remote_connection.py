"""测试远程服务器连接失败处理"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.remote_collector import RemoteSystemCollector
from app.models.models import RemoteServer

def test_remote_connection_failure():
    """测试远程服务器连接失败处理"""
    print("测试远程服务器连接失败处理...")
    
    # 创建一个无效的远程服务器配置
    remote_server = RemoteServer(
        ip_address="192.168.999.999",  # 无效IP地址
        username="test",
        password="test",
        port=22
    )
    
    print(f"测试远程服务器: {remote_server.ip_address}")
    
    try:
        # 创建远程采集器
        collector = RemoteSystemCollector(remote_server)
        
        # 采集所有信息
        all_info = collector.collect_all_info()
        
        print(f"采集结果: {all_info}")
        
        # 检查连接失败状态
        connection_failed = all_info.get('connection_failed', False)
        
        print(f"连接状态: {'异常' if connection_failed else '正常'}")
        
        if connection_failed:
            print(">>> 成功检测到连接失败状态")
        else:
            print(">>> 未能正确检测到连接失败状态")
            
        # 打印详细信息
        print("\n详细信息:")
        for key, value in all_info.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_remote_connection_failure()