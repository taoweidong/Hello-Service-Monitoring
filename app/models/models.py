from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Index, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.config import Config
from app.utils.logger import monitor_logger
import os
import pymysql
import datetime

# 配置PyMySQL作为MySQL驱动
pymysql.install_as_MySQLdb()

# 创建基类
Base = declarative_base()

class ServerInfo(Base):
    """服务器信息表"""
    __tablename__ = 'server_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(50), unique=True, nullable=False)
    hostname = Column(String(100))
    created_at = Column(DateTime)
    
    # MySQL特定配置
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    
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
    cpu_max_freq = Column(BigInteger)
    cpu_min_freq = Column(BigInteger)
    cpu_current_freq = Column(BigInteger)
    
    # 添加索引以提高查询性能
    __table_args__ = (
        Index('idx_cpu_ip_timestamp', 'ip_address', 'timestamp'),
        Index('idx_cpu_timestamp', 'timestamp'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    )
    
    def __repr__(self):
        return f"<CPUInfo(ip_address='{self.ip_address}', cpu_percent={self.cpu_percent})>"

class MemoryInfo(Base):
    """内存信息表"""
    __tablename__ = 'memory_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    total = Column(BigInteger)
    available = Column(BigInteger)
    used = Column(BigInteger)
    free = Column(BigInteger)
    percent = Column(Float)
    
    # 添加索引以提高查询性能
    __table_args__ = (
        Index('idx_memory_ip_timestamp', 'ip_address', 'timestamp'),
        Index('idx_memory_timestamp', 'timestamp'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    )
    
    def __repr__(self):
        return f"<MemoryInfo(ip_address='{self.ip_address}', percent={self.percent})>"

class DiskInfo(Base):
    """磁盘信息表"""
    __tablename__ = 'disk_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    total = Column(BigInteger)
    used = Column(BigInteger)
    free = Column(BigInteger)
    percent = Column(Float)
    
    # 添加索引以提高查询性能
    __table_args__ = (
        Index('idx_disk_ip_timestamp', 'ip_address', 'timestamp'),
        Index('idx_disk_timestamp', 'timestamp'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    )
    
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
    
    # MySQL特定配置
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    
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
    
    # MySQL特定配置
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    
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
    
    # MySQL特定配置
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    
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
    
    # MySQL特定配置
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    
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
# 从配置中获取数据库URL
from app.config.config import Config
DATABASE_URL = Config.DATABASE_URL

# 对于MySQL，需要添加一些额外的参数以确保兼容性
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True, pool_recycle=3600)

# 创建所有表
def init_db():
    """初始化数据库"""
    try:
        # 对于MySQL，我们可能需要先创建数据库
        # 首先尝试连接到服务器（不指定数据库）
        try:
            # 获取不带数据库名的URL
            base_url = Config.DATABASE_URL.rsplit('/', 1)[0]
            base_engine = create_engine(base_url, echo=False)
            
            # 创建数据库（如果不存在）
            with base_engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("CREATE DATABASE IF NOT EXISTS monitoring CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                conn.commit()
        except Exception as db_create_error:
            monitor_logger.info(f"数据库创建检查完成或无需创建: {db_create_error}")
        
        # 创建表
        Base.metadata.create_all(engine)
        
        # 创建初始管理员账号（如果不存在）
        create_initial_admin()
        
        monitor_logger.info("数据库初始化成功")
    except Exception as e:
        monitor_logger.error(f"数据库初始化失败: {e}")

def create_initial_admin():
    """创建初始管理员账号"""
    try:
        from app.config.config import Config
        from sqlalchemy.orm import sessionmaker
        
        # 创建会话
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # 检查是否已存在管理员账号
        existing_user = session.query(User).filter_by(username=Config.INITIAL_ADMIN_USERNAME).first()
        if not existing_user:
            # 创建初始管理员账号
            admin_user = User(
                username=Config.INITIAL_ADMIN_USERNAME,
                email=Config.INITIAL_ADMIN_EMAIL,
                created_at=datetime.datetime.now()
            )
            admin_user.set_password(Config.INITIAL_ADMIN_PASSWORD)
            session.add(admin_user)
            session.commit()
            monitor_logger.info(f"初始管理员账号创建成功: {Config.INITIAL_ADMIN_USERNAME}")
        else:
            monitor_logger.info(f"初始管理员账号已存在: {Config.INITIAL_ADMIN_USERNAME}")
        
        session.close()
    except Exception as e:
        monitor_logger.error(f"创建初始管理员账号失败: {e}")

# 创建会话
Session = sessionmaker(bind=engine)