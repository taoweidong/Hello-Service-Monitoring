"""测试预警优化功能"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import EmailService
from app.services.database import DatabaseManager
from app.models.models import AlertInfo

def test_alert_deduplication():
    """测试预警去重功能"""
    print("开始测试预警去重功能...")
    
    # 创建数据库管理器和邮件服务
    db_manager = DatabaseManager()
    email_service = EmailService()
    
    try:
        # 创建测试IP和预警类型
        test_ip = "192.168.1.100"
        test_alert_type = "cpu"
        
        # 1. 测试没有近期预警的情况
        should_send = email_service._should_send_alert(test_ip, test_alert_type)
        print(f"没有近期预警时是否应该发送: {should_send}")
        
        # 2. 创建一个近期的预警记录
        recent_alert = AlertInfo(
            ip_address=test_ip,
            timestamp=datetime.now() - timedelta(minutes=30),  # 30分钟前
            alert_type=test_alert_type,
            alert_message="测试预警",
            is_sent=1  # 标记为已发送
        )
        db_manager.session.add(recent_alert)
        db_manager.session.commit()
        
        # 3. 测试有近期预警的情况
        should_send = email_service._should_send_alert(test_ip, test_alert_type)
        print(f"有近期预警时是否应该发送: {should_send}")
        
        # 4. 创建一个较早的预警记录
        old_alert = AlertInfo(
            ip_address=test_ip,
            timestamp=datetime.now() - timedelta(hours=2),  # 2小时前
            alert_type=test_alert_type,
            alert_message="测试预警",
            is_sent=1  # 标记为已发送
        )
        db_manager.session.add(old_alert)
        db_manager.session.commit()
        
        # 5. 测试有较早预警的情况
        should_send = email_service._should_send_alert(test_ip, test_alert_type)
        print(f"有较早预警时是否应该发送: {should_send}")
        
        print("预警去重功能测试完成!")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    finally:
        # 清理测试数据
        try:
            # 删除测试预警记录
            db_manager.session.query(AlertInfo).filter(
                AlertInfo.ip_address == "192.168.1.100"
            ).delete()
            db_manager.session.commit()
        except:
            pass
        
        db_manager.close()
        email_service.close()

def test_connection_failure_display():
    """测试连接失败显示功能"""
    print("\n开始测试连接失败显示功能...")
    
    # 模拟连接失败的服务器信息
    server_info_with_failure = {
        'ip_address': '192.168.1.101',
        'hostname': 'unknown',
        'system_version': 'Unknown',
        'kernel_version': 'Unknown',
        'cpu_count': 'N/A',
        'total_memory': 'N/A',
        'total_disk': 'N/A',
        'uptime': 'N/A',
        'connection_failed': True
    }
    
    # 模拟连接成功的服务器信息
    server_info_with_success = {
        'ip_address': '192.168.1.102',
        'hostname': 'test-server',
        'system_version': 'Ubuntu 20.04',
        'kernel_version': '5.4.0',
        'cpu_count': 4,
        'total_memory': '8GB',
        'total_disk': '500GB',
        'uptime': '5天 3小时 20分钟',
        'connection_failed': False
    }
    
    email_service = EmailService()
    
    try:
        # 生成包含连接失败信息的HTML片段
        html_section_failure = email_service._generate_server_info_section(server_info_with_failure)
        print("连接失败的服务器信息HTML片段生成成功")
        
        # 生成包含连接成功信息的HTML片段
        html_section_success = email_service._generate_server_info_section(server_info_with_success)
        print("连接成功的服务器信息HTML片段生成成功")
        
        print("连接失败显示功能测试完成!")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    finally:
        email_service.close()

if __name__ == "__main__":
    test_alert_deduplication()
    test_connection_failure_display()