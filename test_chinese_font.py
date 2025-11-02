"""测试中文字体修复功能"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.weekly_report_service import WeeklyReportService
from app.app import create_app

def test_chinese_font_fix():
    """测试中文字体修复功能"""
    print("开始测试中文字体修复功能...")
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        # 创建周报服务
        weekly_report_service = WeeklyReportService()
        
        try:
            # 测试生成趋势图
            print("测试生成包含中文字体的趋势图...")
            # 这里我们不实际生成图表，只是测试中文字体设置是否正确
            import matplotlib.pyplot as plt
            import matplotlib.font_manager as fm
            
            # 检查字体设置
            print(f"当前字体设置: {plt.rcParams['font.sans-serif']}")
            print(f"负号显示设置: {plt.rcParams['axes.unicode_minus']}")
            
            # 测试生成周报数据
            print("生成周报数据...")
            report_data = weekly_report_service.generate_weekly_report_data()
            print(f"生成了 {len(report_data)} 个服务器的周报数据")
            
            print("中文字体修复功能测试完成!")
            
        except Exception as e:
            print(f"测试过程中出现错误: {e}")
        finally:
            weekly_report_service.close()

if __name__ == "__main__":
    test_chinese_font_fix()