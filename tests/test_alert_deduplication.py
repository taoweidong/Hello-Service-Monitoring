"""测试预警去重功能"""
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
        
        # 2. 创建一个近期的预警记录（1小时内）
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
        
        # 3. 测试有近期预警的情况
        should_send = email_service._should_send_alert(test_ip, test_alert_type)
        print(f"有近期预警时是否应该发送: {should_send}")
        
        # 4. 创建一个较早的预警记录（超过1小时）
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
        
        # 5. 测试有较早预警但没有近期预警的情况
        should_send = email_service._should_send_alert(test_ip, test_alert_type)
        print(f"有较早预警但没有近期预警时是否应该发送: {should_send}")
        
        # 6. 再添加一个近期预警
        recent_alert2 = AlertInfo(
            ip_address=test_ip,
            timestamp=datetime.now() - timedelta(minutes=15),  # 15分钟前
            alert_type=test_alert_type,
            alert_message="测试预警2",
            is_sent=1  # 标记为已发送
        )
        db_manager.session.add(recent_alert2)
        db_manager.session.commit()
        print(f"已添加第二个近期预警记录: {recent_alert2.timestamp}")
        
        # 7. 测试有多个近期预警的情况
        should_send = email_service._should_send_alert(test_ip, test_alert_type)
        print(f"有多个近期预警时是否应该发送: {should_send}")
        
        print("预警去重功能测试完成!")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理测试数据
        try:
            # 删除测试预警记录
            db_manager.session.query(AlertInfo).filter(
                AlertInfo.ip_address == "192.168.1.100"
            ).delete()
            db_manager.session.commit()
            print("测试数据已清理")
        except Exception as e:
            print(f"清理测试数据时出错: {e}")
        
        db_manager.close()
        email_service.close()

if __name__ == "__main__":
    test_alert_deduplication()