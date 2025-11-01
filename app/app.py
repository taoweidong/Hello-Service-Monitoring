from flask import Flask
from app.config import Config
from app.routes import main_bp
from app.monitoring.scheduler import start_scheduler
import os

def create_app():
    # 获取项目根目录
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    app = Flask(__name__, 
                template_folder=os.path.join(basedir, 'templates'),
                static_folder=os.path.join(basedir, 'static'))
    app.config.from_object(Config)
    
    # 注册蓝图
    app.register_blueprint(main_bp)
    
    # 启动定时任务
    start_scheduler(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)