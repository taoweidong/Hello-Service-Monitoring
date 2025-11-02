"""测试周报按钮功能"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.weekly_report_service import WeeklyReportService
from app.app import create_app

def test_weekly_report_button():
    """测试周报按钮功能"""
    print("开始测试周报按钮功能...")
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        # 创建周报服务
        weekly_report_service = WeeklyReportService()
        
        try:
            # 测试发送周报邮件
            print("测试发送周报邮件...")
            success = weekly_report_service.send_weekly_report_email()
            print(f"周报邮件发送{'成功' if success else '失败'}")
            
            print("周报按钮功能测试完成!")
            
        except Exception as e:
            print(f"测试过程中出现错误: {e}")
        finally:
            weekly_report_service.close()

if __name__ == "__main__":
    test_weekly_report_button()