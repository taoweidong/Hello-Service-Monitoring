# 服务器监控系统

一个基于Python的服务器监控系统，支持Web访问、定时数据采集、数据趋势展示和资源不足预警等功能。

## 功能特性

- **实时监控**: 监控CPU、内存、磁盘和进程等系统资源
- **Web界面**: 基于Flask的Web界面，支持响应式设计
- **数据可视化**: 使用Chart.js展示数据趋势图
- **定时采集**: 使用APScheduler定时采集数据（默认每2分钟）
- **预警机制**: 资源使用超过阈值时触发预警并通过邮件通知
- **数据存储**: 使用SQLite数据库存储历史数据
- **多服务器支持**: 支持监控多台服务器（通过IP地址区分）

## 技术栈

- **后端**: Python, Flask, SQLAlchemy, APScheduler, psutil
- **前端**: Bootstrap, Chart.js
- **数据库**: SQLite
- **其他**: loguru（日志记录）, python-dotenv（配置管理）

## 安装和配置

### 1. 克隆项目

```bash
git clone <repository-url>
cd Hello-Service-Monitoring
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

编辑 [.env](file:///E:/GitHub/Hello-Service-Monitoring/.env) 文件，根据需要修改配置：

```env
# 数据库配置
DATABASE_URL=sqlite:///db/monitoring.db

# 定时任务配置
SCHEDULE_INTERVAL_MINUTES=2

# 预警阈值配置
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
DISK_THRESHOLD=80

# 邮件配置（用于预警）
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your_username
MAIL_PASSWORD=your_password
MAIL_DEFAULT_SENDER=monitor@example.com
ADMIN_EMAIL=admin@example.com
```

### 4. 创建必要的目录

```bash
mkdir logs db
```

## 运行系统

```bash
python run.py
```

系统将在 `http://localhost:5000` 启动。

## 使用说明

1. **首页**: 显示所有被监控的服务器列表
2. **服务器详情页**: 显示特定服务器的详细监控信息和趋势图
3. **数据采集**: 系统会自动每2分钟采集一次数据
4. **预警**: 当资源使用超过阈值时，系统会记录预警信息并通过邮件通知管理员

## API接口

- `GET /api/server/list` - 获取服务器列表
- `GET /api/cpu/history/<ip_address>` - 获取CPU历史数据
- `GET /api/memory/history/<ip_address>` - 获取内存历史数据
- `GET /api/disk/history/<ip_address>` - 获取磁盘历史数据

## 项目结构

```
Hello-Service-Monitoring/
├── run.py                 # 启动脚本
├── requirements.txt       # 依赖列表
├── .env                   # 环境配置文件
├── README.md             # 使用说明
├── logs/                 # 日志目录
├── db/                   # 数据库文件目录
├── docs/                 # 文档目录
├── static/               # 静态文件
│   ├── css/
│   └── js/
├── templates/            # 模板文件
│   ├── base.html
│   ├── index.html
│   └── server_detail.html
└── app/                  # 业务代码目录
    ├── __init__.py
    ├── app.py            # 应用入口
    ├── config.py         # 配置管理
    ├── collector.py      # 数据采集模块
    ├── database.py       # 数据库操作模块
    ├── models.py         # 数据库模型
    ├── routes.py         # Flask路由
    ├── logger.py         # 日志模块
    └── monitoring/       # 监控相关模块
        ├── __init__.py
        ├── scheduler.py   # 定时任务调度
        └── alert.py      # 预警机制
```

## 扩展功能

1. **添加更多监控指标**: 可以在 [collector.py](file:///E:/GitHub/Hello-Service-Monitoring/app/collector.py) 中添加更多系统信息采集
2. **自定义预警阈值**: 修改 [.env](file:///E:/GitHub/Hello-Service-Monitoring/.env) 文件中的阈值配置
3. **支持更多数据库**: 修改 [config.py](file:///E:/GitHub/Hello-Service-Monitoring/app/config.py) 中的数据库配置
4. **添加用户认证**: 可以集成Flask-Login等认证模块

## 注意事项

1. 确保系统有足够的权限访问系统资源信息
2. 邮件配置需要根据实际使用的邮件服务商进行调整
3. 定时任务间隔可以根据需要在 [.env](file:///E:/GitHub/Hello-Service-Monitoring/.env) 文件中调整
4. SQLite数据库适用于小型部署，大型部署建议使用MySQL或PostgreSQL

## 故障排除

1. **无法启动应用**: 检查是否已安装所有依赖
2. **数据采集失败**: 检查系统权限和psutil库是否正常工作
3. **邮件预警不工作**: 检查邮件配置是否正确
4. **图表不显示**: 检查网络连接和JavaScript是否启用

## 许可证

MIT License