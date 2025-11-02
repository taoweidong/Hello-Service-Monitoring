from flask import Flask
from app.config.config import Config
from app.api import main_bp
from app.auth import auth_bp, login_manager
from app.api import api_bp
from app.monitoring.scheduler import start_scheduler
import os

def create_app():
    # 获取项目根目录
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    app = Flask(__name__, 
                template_folder=os.path.join(basedir, 'app', 'templates'),
                static_folder=os.path.join(basedir, 'app', 'static'))
    app.config.from_object(Config)
    
    # 设置密钥以启用会话
    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # 初始化登录管理器
    login_manager.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    
    # 启动定时任务
    start_scheduler(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)