from loguru import logger
import sys
import os

# 获取项目根目录
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 配置loguru日志
logger.remove()  # 移除默认的日志处理器
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)

logger.add(
    os.path.join(basedir, "logs", "monitoring.log"),
    rotation="500 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)

# 导出logger实例供其他模块使用
monitor_logger = logger