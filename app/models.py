# app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()


class SystemInfo(Base):
    """系统信息模型"""
    __tablename__ = 'system_info'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_percent = Column(Float)
    uptime = Column(Float)  # 系统运行时间
    load_average = Column(String(100))  # 系统负载
    
    def __repr__(self) -> str:
        return f"<SystemInfo(id={self.id}, timestamp={self.timestamp}, memory={self.memory_percent}%)"


class ProcessInfo(Base):
    """进程信息模型"""
    __tablename__ = 'process_info'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    pid = Column(Integer)
    name = Column(String(100))
    status = Column(String(50))
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    create_time = Column(Float)  # 进程创建时间
    
    def __repr__(self) -> str:
        return f"<ProcessInfo(id={self.id}, pid={self.pid}, name={self.name})"


class DiskInfo(Base):
    """磁盘信息模型"""
    __tablename__ = 'disk_info'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    device = Column(String(100))  # 设备名
    mountpoint = Column(String(200))  # 挂载点
    total = Column(Float)  # 总空间
    used = Column(Float)  # 已使用
    free = Column(Float)  # 剩余空间
    percent = Column(Float)  # 使用百分比
    
    def __repr__(self) -> str:
        return f"<DiskInfo(id={self.id}, device={self.device}, percent={self.percent}%)"


class AlertRecord(Base):
    """预警记录模型"""
    __tablename__ = 'alert_record'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    alert_type = Column(String(50))  # 预警类型
    message = Column(Text)  # 预警信息
    is_sent = Column(Integer, default=0)  # 是否已发送
    
    def __repr__(self) -> str:
        return f"<AlertRecord(id={self.id}, type={self.alert_type}, sent={bool(self.is_sent)})>"