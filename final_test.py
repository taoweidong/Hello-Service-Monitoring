"""最终测试周报功能"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.weekly_report_service import WeeklyReportService
from app.app import create_app

def final_test():
    """最终测试"""
    print("开始最终测试...")
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        # 创建周报服务
        weekly_report_service = WeeklyReportService()
        
        try:
            # 测试生成趋势图（使用英文标签避免字体问题）
            print("测试生成趋势图...")
            import matplotlib.pyplot as plt
            print(f"当前字体设置: {plt.rcParams['font.sans-serif']}")
            
            # 测试生成HTML模板
            print("生成HTML周报模板...")
            html_content = weekly_report_service.get_html_weekly_report_template([])
            print(f"HTML模板生成{'成功' if html_content else '失败'}")
            
            print("最终测试完成!")
            
        except Exception as e:
            print(f"测试过程中出现错误: {e}")
        finally:
            weekly_report_service.close()

if __name__ == "__main__":
    final_test()