from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.config import Config
from app.utils.logger import monitor_logger
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

class User(Base):
    """用户表"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime)
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
    
    def set_password(self, password):
        """设置密码哈希"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        from werkzeug.security import check_password_hash
        return check_password_hash(str(self.password_hash), password)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

class RemoteServer(Base):
    """远程服务器表"""
    __tablename__ = 'remote_servers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    ip_address = Column(String(50), unique=True, nullable=False)
    username = Column(String(80), nullable=False)
    password = Column(String(255), nullable=False)  # 加密存储
    port = Column(Integer, default=22)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    def __repr__(self):
        return f"<RemoteServer(name='{self.name}', ip_address='{self.ip_address}')>"
    
    def set_password(self, password):
        """设置密码哈希"""
        from werkzeug.security import generate_password_hash
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        from werkzeug.security import check_password_hash
        return check_password_hash(str(self.password), password)

# 创建数据库引擎
# 更新数据库路径指向新的db目录
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'db', 'monitoring.db')
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