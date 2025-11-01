from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import Config
from app.logger import monitor_logger
import os

# 创建基类
Base = declarative_base()

class ServerInfo(Base):
    """服务器信息表"""
    __tablename__ = 'server_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(50), unique=True, nullable=False)
    hostname = Column(String(100))
    created_at = Column(DateTime)
    
    def __repr__(self):
        return f"<ServerInfo(ip_address='{self.ip_address}', hostname='{self.hostname}')>"

class CPUInfo(Base):
    """CPU信息表"""
    __tablename__ = 'cpu_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    cpu_percent = Column(Float)
    cpu_count = Column(Integer)
    cpu_max_freq = Column(Float)
    cpu_min_freq = Column(Float)
    cpu_current_freq = Column(Float)
    
    def __repr__(self):
        return f"<CPUInfo(ip_address='{self.ip_address}', cpu_percent={self.cpu_percent})>"

class MemoryInfo(Base):
    """内存信息表"""
    __tablename__ = 'memory_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    total = Column(Integer)
    available = Column(Integer)
    used = Column(Integer)
    free = Column(Integer)
    percent = Column(Float)
    
    def __repr__(self):
        return f"<MemoryInfo(ip_address='{self.ip_address}', percent={self.percent})>"

class DiskInfo(Base):
    """磁盘信息表"""
    __tablename__ = 'disk_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    total = Column(Integer)
    used = Column(Integer)
    free = Column(Integer)
    percent = Column(Float)
    
    def __repr__(self):
        return f"<DiskInfo(ip_address='{self.ip_address}', percent={self.percent})>"

class ProcessInfo(Base):
    """进程信息表"""
    __tablename__ = 'process_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    process_count = Column(Integer)
    processes = Column(Text)  # JSON格式存储进程信息
    
    def __repr__(self):
        return f"<ProcessInfo(ip_address='{self.ip_address}', process_count={self.process_count})>"

class AlertInfo(Base):
    """预警信息表"""
    __tablename__ = 'alert_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    alert_type = Column(String(50))  # cpu, memory, disk
    alert_message = Column(Text)
    is_sent = Column(Integer, default=0)  # 0:未发送, 1:已发送
    
    def __repr__(self):
        return f"<AlertInfo(ip_address='{self.ip_address}', alert_type='{self.alert_type}')>"

# 创建数据库引擎
# 更新数据库路径指向新的db目录
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'monitoring.db')
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL, echo=False)

# 创建所有表
def init_db():
    """初始化数据库"""
    try:
        Base.metadata.create_all(engine)
        monitor_logger.info("数据库初始化成功")
    except Exception as e:
        monitor_logger.error(f"数据库初始化失败: {e}")

# 创建会话
Session = sessionmaker(bind=engine)