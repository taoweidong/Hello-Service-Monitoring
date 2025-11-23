# app/__init__.py
from flask import Flask
from .config.config import Config
import os

def create_app():
    """创建并配置Flask应用实例"""
    # 获取项目根目录
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # 指定模板和静态文件目录
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(Config)
    
    # 注册蓝图
    from .api.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app