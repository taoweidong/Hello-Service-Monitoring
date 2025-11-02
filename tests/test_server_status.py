"""测试服务器状态显示"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.server_info_service import ServerInfoService
from app.services.database import DatabaseManager
from app.models.models import ServerInfo

def test_server_status():
    """测试服务器状态显示"""
    print("测试服务器状态显示...")
    
    try:
        # 创建数据库管理器
        db_manager = DatabaseManager()
        
        # 获取所有服务器
        servers = db_manager.session.query(ServerInfo).all()
        
        if not servers:
            print("没有找到服务器")
            return
        
        print(f"找到 {len(servers)} 个服务器:")
        
        for server in servers:
            print(f"\n测试服务器: {server.ip_address}")
            
            # 创建服务器信息服务
            server_info_service = ServerInfoService(server.ip_address)
            
            # 获取详细信息（包括连接状态）
            detailed_info = server_info_service.get_detailed_server_info()
            server_info_service.close()
            
            # 检查连接状态
            connection_failed = detailed_info.get('connection_failed', False)
            
            print(f"  主机名: {detailed_info.get('hostname', 'Unknown')}")
            print(f"  连接状态: {'异常' if connection_failed else '正常'}")
            
            if connection_failed:
                print(f"  >>> 服务器 {server.ip_address} 连接失败")
            else:
                print(f"  >>> 服务器 {server.ip_address} 连接正常")
        
        db_manager.close()
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_server_status()