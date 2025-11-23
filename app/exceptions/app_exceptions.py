# app/exceptions/app_exceptions.py
"""应用异常定义模块"""

from typing import Optional


class AppException(Exception):
    """应用基础异常类"""
    
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DatabaseException(AppException):
    """数据库相关异常"""
    
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message, code or "DB_ERROR")


class ConfigException(AppException):
    """配置相关异常"""
    
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message, code or "CONFIG_ERROR")


class MonitoringException(AppException):
    """监控相关异常"""
    
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message, code or "MONITORING_ERROR")


class NotificationException(AppException):
    """通知相关异常"""
    
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message, code or "NOTIFICATION_ERROR")


class ReportException(AppException):
    """报告相关异常"""
    
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message, code or "REPORT_ERROR")