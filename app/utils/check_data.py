#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的数据
"""

from app.database.database_manager import DatabaseManager
from app.database.models import SystemInfo, DiskInfo, ProcessInfo
from loguru import logger

def check_data():
    """检查数据库中的数据"""
    try:
        db_manager = DatabaseManager()
        
        with db_manager.get_session() as session:
            # 查询系统信息
            system_records = session.query(SystemInfo).all()
            print(f"系统信息记录数: {len(system_records)}")
            if system_records:
                print("最新的系统信息:")
                latest_record = system_records[-1]  # 最后一条记录
                print(f"  时间: {latest_record.timestamp}")
                print(f"  CPU使用率: {latest_record.cpu_percent}%")
                print(f"  内存使用率: {latest_record.memory_percent}%")
                print(f"  磁盘使用率: {latest_record.disk_percent}%")
            
            # 查询磁盘信息
            disk_records = session.query(DiskInfo).all()
            print(f"\n磁盘信息记录数: {len(disk_records)}")
            if disk_records:
                print("最新的磁盘信息:")
                # 按设备分组显示
                disk_by_device = {}
                for record in disk_records:
                    if record.device not in disk_by_device:
                        disk_by_device[record.device] = []
                    disk_by_device[record.device].append(record)
                
                for device, records in disk_by_device.items():
                    latest_record = records[-1]  # 最后一条记录
                    print(f"  设备: {latest_record.device}")
                    print(f"    时间: {latest_record.timestamp}")
                    print(f"    使用率: {latest_record.percent}%")
            
            # 查询进程信息
            process_records = session.query(ProcessInfo).all()
            print(f"\n进程信息记录数: {len(process_records)}")
            
    except Exception as e:
        logger.error(f"检查数据时出错: {e}")
        raise

if __name__ == "__main__":
    check_data()