```markdown
你是一名专业的Python工程师，请开发一个服务器监控系统，用于采集服务器关键指标，内存，硬盘空间，进程等信息。该系统需要支持以下功能：

1. 定时采集服务器关键指标（如内存使用率、硬盘空间、进程状态等信息）用于页面展示，使用`psutil`库进行采集。
2. 实现资源预警机制：当内存或硬盘使用率超过80%时，每小时通过钉钉机器人发送一条预警消息。
3. 每周自动生成一份服务器使用周报，内容包括服务器的基本信息、内存使用率曲线图、硬盘使用率曲线图以及对服务器风险的简要分析。报告将以邮件形式发送给指定的接收者。
4. 开发一个基于Flask的Web页面，允许用户查询服务器的实时信息。页面上的数据每5秒自动刷新一次，展示的信息包括服务器的基本信息（如Python、Java、Docker版本，若无相关应用则显示"未安装"）、内存和硬盘使用状况、进程列表等，使用图表形式展示这些信息。
5. 将所有采集的数据存储在本地的SQLite数据库中。

注意事项：
- 系统仅监控当前服务器的信息。
- 支持Linux和Windows操作系统下的监控，需提供一键启动服务脚本，该脚本应包括虚拟环境创建、依赖项安装、服务启动等功能，以简化部署过程。
- 使用`uv`管理Python项目。
- python使用面向对象的方式编写，注意一个类一个文件

具体实现建议：
- 使用Flask框架结合Jinja2模板引擎来构建Web界面，避免引入Vue等复杂前端框架。
- 钉钉消息推送可通过调用钉钉API实现。
- 数据存储方面，建议使用SQLAlchemy ORM来操作SQLite数据库，以简化数据库操作。
- 考虑使用APScheduler库来安排定时任务，如定期收集数据、发送预警通知及生成周报。
- 为了使图表可视化，可以考虑使用 PLOTLY 库生成内存和硬盘使用率的图表，并将其嵌入到周报邮件中。
- 为方便部署，确保提供详细的README文档，说明如何使用一键启动脚本以及配置钉钉机器人的步骤。
- 代码要求全部使用类型提示，以提高代码的可读性和可维护性。
- 所有的业务代码放在app目录下
- web页面使用 Bootstrap 页面现代化，美观

## 项目结构

```
Hello-Service-Monitoring/
├── app/                    # 主应用目录
│   ├── __init__.py         # 应用初始化
│   ├── config.py           # 配置文件
│   ├── models.py           # 数据模型
│   ├── collector.py        # 数据采集器
│   ├── database.py         # 数据库操作
│   ├── routes.py           # 路由定义
│   ├── api/                # API接口
│   ├── services/           # 业务逻辑
│   ├── templates/          # HTML模板
│   └── static/             # 静态资源
├── monitoring/             # 监控相关
│   └── scheduler.py        # 定时任务调度器
├── logs/                   # 日志目录
├── app.py                  # 应用入口
├── start.sh                # Linux启动脚本
├── start.bat               # Windows启动脚本
├── requirements.txt        # 依赖包列表
├── pyproject.toml          # 项目配置文件
└── README.md               # 项目说明文档
```

## 快速开始

### 环境要求
- Python 3.10+
- uv 包管理工具

### 安装步骤

1. 克隆项目代码：
   ```bash
   git clone <repository-url>
   cd Hello-Service-Monitoring
   ```

2. 使用一键启动脚本：
   - Linux/macOS系统：
     ```bash
     chmod +x start.sh
     ./start.sh
     ```
   - Windows系统：
     ```cmd
     start.bat
     ```

### 手动安装

1. 创建虚拟环境：
   ```bash
   python -m venv venv
   ```

2. 激活虚拟环境：
   - Linux/macOS：
     ```bash
     source venv/bin/activate
     ```
   - Windows：
     ```cmd
     venv\Scripts\activate
     ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 启动应用：
   ```bash
   python app.py
   ```

### 访问应用

启动成功后，打开浏览器访问 `http://localhost:5000` 查看监控界面。

## 配置说明

系统支持通过环境变量进行配置：

- `DATABASE_URL`: 数据库连接字符串，默认为 `sqlite:///../monitoring/monitoring.db`
- `MEMORY_THRESHOLD`: 内存使用率预警阈值，默认为 80.0
- `DISK_THRESHOLD`: 磁盘使用率预警阈值，默认为 80.0
- `DINGTALK_WEBHOOK`: 钉钉机器人Webhook地址
- `HOST`: 服务监听地址，默认为 0.0.0.0
- `PORT`: 服务监听端口，默认为 5000
- `DEBUG`: 是否开启调试模式，默认为 False

## 功能特性

1. **实时监控**: 每5秒自动刷新系统状态
2. **数据采集**: 定时收集CPU、内存、磁盘、进程等信息
3. **预警机制**: 资源使用率超过阈值时发送钉钉通知
4. **可视化展示**: 使用Bootstrap和Plotly展示数据图表
5. **响应式设计**: 支持各种设备屏幕尺寸
```