#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试磁盘趋势数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.api.handlers.disk_handler import DiskHandler
from app.database.database_manager import DatabaseManager

def debug_disk_trend_api(app):
    """调试磁盘趋势API"""
    print("调试磁盘趋势API...")
    try:
        with app.app_context():
            db_manager = DatabaseManager()
            disk_handler = DiskHandler(db_manager)
            
            # 调用获取磁盘趋势数据的方法
            result, status_code = disk_handler.get_trend_disk()
            print(f"磁盘趋势API返回状态码: {status_code}")
            if hasattr(result, 'get_json'):
                data = result.get_json()
                print(f"磁盘趋势数据结构: {data.keys() if data else '无数据'}")
                if data and 'history' in data:
                    history = data['history']
                    print(f"历史数据设备数: {len(history)}")
                    for device, records in history.items():
                        print(f"  设备: {device}")
                        print(f"    记录数: {len(records)}")
                        if records:
                            print(f"    第一条记录: {records[0]}")
                            print(f"    最后一条记录: {records[-1]}")
                else:
                    print(f"数据格式不正确: {data}")
            else:
                print(f"返回数据: {result}")
        
    except Exception as e:
        print(f"调试磁盘趋势API时出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("=== 调试磁盘趋势数据 ===")
    
    # 创建Flask应用
    app = create_app()
    
    # 调试磁盘趋势API
    debug_disk_trend_api(app)

if __name__ == "__main__":
    main()