from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from app.models.models import User, Session
from app.utils.logger import monitor_logger
from datetime import datetime

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 初始化登录管理器
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录以访问此页面。'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """加载用户"""
    try:
        session = Session()
        user = session.query(User).get(int(user_id))
        session.close()
        return user
    except Exception as e:
        monitor_logger.error(f"加载用户失败: {e}")
        return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    # 如果用户已经登录，直接重定向到主页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('login.html')
        
        try:
            session = Session()
            user = session.query(User).filter_by(username=username).first()
            session.close()
            
            if user and user.check_password(password):
                login_user(user)
                flash('登录成功', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.index'))
            else:
                flash('用户名或密码错误', 'error')
        except Exception as e:
            monitor_logger.error(f"用户登录失败: {e}")
            flash('登录过程中发生错误，请稍后重试', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('您已成功登出', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    # 如果用户已经登录，直接重定向到主页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证输入
        if not username or not email or not password:
            flash('请填写所有必填字段', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('密码和确认密码不匹配', 'error')
            return render_template('register.html')
        
        try:
            session = Session()
            
            # 检查用户名和邮箱是否已存在
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                session.close()
                flash('用户名已存在', 'error')
                return render_template('register.html')
            
            existing_email = session.query(User).filter_by(email=email).first()
            if existing_email:
                session.close()
                flash('邮箱已被注册', 'error')
                return render_template('register.html')
            
            # 创建新用户
            user = User(
                username=username,
                email=email,
                created_at=datetime.now()
            )
            user.set_password(password)
            
            session.add(user)
            session.commit()
            session.close()
            
            flash('注册成功，请登录', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            monitor_logger.error(f"用户注册失败: {e}")
            flash('注册过程中发生错误，请稍后重试', 'error')
    
    return render_template('register.html')