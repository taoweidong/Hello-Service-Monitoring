"""测试SSH连接失败情况"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.server_info_service import ServerInfoService

def test_ssh_failure():
    """测试SSH连接失败情况"""
    print("测试SSH连接失败情况...")
    
    # 使用一个不存在的IP地址来模拟连接失败
    invalid_ip = "192.168.999.999"
    
    print(f"测试无效IP地址: {invalid_ip}")
    
    try:
        # 创建服务器信息服务
        server_info_service = ServerInfoService(invalid_ip)
        
        # 获取详细信息（应该会失败并标记连接失败）
        detailed_info = server_info_service.get_detailed_server_info()
        server_info_service.close()
        
        # 检查连接状态
        connection_failed = detailed_info.get('connection_failed', False)
        
        print(f"主机名: {detailed_info.get('hostname', 'Unknown')}")
        print(f"连接状态: {'异常' if connection_failed else '正常'}")
        
        if connection_failed:
            print(">>> 成功检测到连接失败状态")
        else:
            print(">>> 未能正确检测到连接失败状态")
            
        # 打印详细信息
        print("\n详细信息:")
        for key, value in detailed_info.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ssh_failure()