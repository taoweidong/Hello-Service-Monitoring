"""测试周报功能"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.weekly_report_service import WeeklyReportService
from app.app import create_app

def test_weekly_report():
    """测试周报生成"""
    print("开始测试周报功能...")
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        # 创建周报服务
        weekly_report_service = WeeklyReportService()
        
        try:
            # 生成周报数据
            print("生成周报数据...")
            report_data = weekly_report_service.generate_weekly_report_data()
            print(f"生成了 {len(report_data)} 个服务器的周报数据")
            
            # 测试生成趋势图
            print("测试生成趋势图...")
            if report_data:
                first_server_ip = report_data[0]['server_info']['ip_address']
                cpu_chart = weekly_report_service.generate_trend_chart(first_server_ip, 'cpu')
                print(f"CPU趋势图生成{'成功' if cpu_chart else '失败'}")
                
                memory_chart = weekly_report_service.generate_trend_chart(first_server_ip, 'memory')
                print(f"内存趋势图生成{'成功' if memory_chart else '失败'}")
                
                disk_chart = weekly_report_service.generate_trend_chart(first_server_ip, 'disk')
                print(f"磁盘趋势图生成{'成功' if disk_chart else '失败'}")
            
            # 生成HTML模板
            print("生成HTML周报模板...")
            html_content = weekly_report_service.get_html_weekly_report_template(report_data)
            print(f"HTML模板生成{'成功' if html_content else '失败'}")
            
            print("周报功能测试完成!")
            
        except Exception as e:
            print(f"测试过程中出现错误: {e}")
        finally:
            weekly_report_service.close()

if __name__ == "__main__":
    test_weekly_report()