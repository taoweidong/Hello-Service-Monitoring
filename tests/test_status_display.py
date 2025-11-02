"""测试状态显示修复"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_template_logic():
    """测试模板中的状态显示逻辑"""
    print("测试模板中的状态显示逻辑...")
    
    # 模拟服务器数据
    test_servers = [
        {
            'ip_address': '192.168.1.100',
            'hostname': 'server1',
            'connection_failed': False  # 正常连接
        },
        {
            'ip_address': '192.168.1.101', 
            'hostname': 'server2',
            'connection_failed': True   # 连接失败
        },
        {
            'ip_address': 'dadad',
            'hostname': 'invalid',
            'connection_failed': True   # 无效IP
        }
    ]
    
    print("模拟服务器状态显示:")
    for server in test_servers:
        status_text = "异常" if server['connection_failed'] else "在线"
        status_class = "bg-danger-subtle text-danger" if server['connection_failed'] else "bg-success-subtle text-success"
        status_icon = "exclamation-circle-fill" if server['connection_failed'] else "circle-fill"
        
        print(f"  IP: {server['ip_address']}")
        print(f"  主机名: {server['hostname']}")
        print(f"  状态: {status_text}")
        print(f"  HTML显示: <span class='badge {status_class}'><i class='bi bi-{status_icon} me-1'></i>{status_text}</span>")
        print()

if __name__ == "__main__":
    test_template_logic()