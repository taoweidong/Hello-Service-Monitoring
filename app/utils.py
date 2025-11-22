# app/utils.py
"""工具函数模块"""

from datetime import datetime
import time
from typing import Union


def to_local_time(dt: Union[datetime, str, None]) -> Union[datetime, None]:
    """
    将UTC时间转换为本地时间
    
    Args:
        dt: UTC时间，可以是datetime对象、ISO格式字符串或None
        
    Returns:
        本地时间的datetime对象，如果输入为None则返回None
    """
    if dt is None:
        return None
    
    if isinstance(dt, str):
        # 如果是字符串，先转换为datetime对象
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    
    # 如果已经是datetime对象，假设它是UTC时间，转换为本地时间
    if dt.tzinfo is None:
        # 没有时区信息，假设是UTC时间
        return dt
    else:
        # 有时区信息，转换为本地时区
        return dt.astimezone()


def format_local_time(dt: Union[datetime, str, None], format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    格式化时间为本地时间字符串
    
    Args:
        dt: 时间对象
        format_str: 格式化字符串
        
    Returns:
        格式化后的本地时间字符串
    """
    local_dt = to_local_time(dt)
    if local_dt is None:
        return "未知时间"
    
    return local_dt.strftime(format_str)


def get_current_local_time() -> datetime:
    """
    获取当前本地时间
    
    Returns:
        当前本地时间的datetime对象
    """
    return datetime.fromtimestamp(time.time())