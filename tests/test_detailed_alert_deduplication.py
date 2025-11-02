"""详细测试预警去重功能"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import EmailService
from app.services.database import DatabaseManager
from app.models.models import AlertInfo

def test_detailed_alert_deduplication():
    """详细测试预警去重功能"""
    print("开始详细测试预警去重功能...")
    
    # 创建数据库管理器和邮件服务
    db_manager = DatabaseManager()
    email_service = EmailService()
    
    try:
        # 创建测试IP和预警类型
        test_ip = "192.168.1.100"
        test_alert_type = "cpu"
        
        # 1. 测试没有近期预警的情况
        print("\n=== 测试1: 没有近期预警 ===")
        should_send = email_service._should_send_alert(test_ip, test_alert_type)
        print(f"没有近期预警时是否应该发送: {should_send}")
        
        # 2. 创建一个近期的预警记录（1小时内）
        print("\n=== 测试2: 有近期预警 ===")
        recent_alert = AlertInfo(
            ip_address=test_ip,
            timestamp=datetime.now() - timedelta(minutes=30),  # 30分钟前
            alert_type=test_alert_type,
            alert_message="测试预警",
            is_sent=1  # 标记为已发送
        )
        db_manager.session.add(recent_alert)
        db_manager.session.commit()
        print(f"已添加近期预警记录: {recent_alert.timestamp}")
        
        # 重新测试
        should_send = email_service._should_send_alert(test_ip, test_alert_type)
        print(f"有近期预警时是否应该发送: {should_send}")
        
        # 3. 测试不同类型预警
        print("\n=== 测试3: 不同类型预警 ===")
        different_alert_type = "memory"
        should_send = email_service._should_send_alert(test_ip, different_alert_type)
        print(f"不同类型预警是否应该发送: {should_send}")
        
        # 4. 测试不同IP地址
        print("\n=== 测试4: 不同IP地址 ===")
        different_ip = "192.168.1.101"
        should_send = email_service._should_send_alert(different_ip, test_alert_type)
        print(f"不同IP地址预警是否应该发送: {should_send}")
        
        # 5. 创建一个较早的预警记录（超过1小时）
        print("\n=== 测试5: 较早预警记录 ===")
        old_alert = AlertInfo(
            ip_address=test_ip,
            timestamp=datetime.now() - timedelta(hours=2),  # 2小时前
            alert_type=test_alert_type,
            alert_message="测试预警",
            is_sent=1  # 标记为已发送
        )
        db_manager.session.add(old_alert)
        db_manager.session.commit()
        print(f"已添加较早预警记录: {old_alert.timestamp}")
        
        # 重新测试
        should_send = email_service._should_send_alert(test_ip, test_alert_type)
        print(f"有较早预警但没有近期预警时是否应该发送: {should_send}")
        
        # 6. 测试未发送的预警
        print("\n=== 测试6: 未发送的预警 ===")
        unsent_alert = AlertInfo(
            ip_address=test_ip,
            timestamp=datetime.now() - timedelta(minutes=15),  # 15分钟前
            alert_type=test_alert_type,
            alert_message="测试预警",
            is_sent=0  # 标记为未发送
        )
        db_manager.session.add(unsent_alert)
        db_manager.session.commit()
        print(f"已添加未发送预警记录: {unsent_alert.timestamp}")
        
        # 重新测试
        should_send = email_service._should_send_alert(test_ip, test_alert_type)
        print(f"有未发送预警时是否应该发送: {should_send}")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理测试数据
        try:
            # 删除测试预警记录
            db_manager.session.query(AlertInfo).filter(
                AlertInfo.ip_address.in_(["192.168.1.100", "192.168.1.101"])
            ).delete(synchronize_session=False)
            db_manager.session.commit()
            print("测试数据已清理")
        except Exception as e:
            print(f"清理测试数据时出错: {e}")
        
        db_manager.close()
        email_service.close()

if __name__ == "__main__":
    test_detailed_alert_deduplication()