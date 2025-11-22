# 服务器监控系统

## 项目简介

服务器监控系统是一个用于实时监控服务器状态的工具，可以监控CPU、内存、磁盘、进程等资源使用情况，并提供预警机制。

## 项目要求

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
.
├── app/
│   ├── monitoring/
│   │   └── scheduler.py
│   ├── templates/
│   │   └── index.html
│   ├── __init__.py
│   ├── collector.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── routes.py
│   ├── utils.py
│   └── db_init.py
├── db/
│   └── monitoring.db
├── static/bootstrap-5.3.0-alpha1-dist/
│   ├── css/
│   └── js/
├── templates/
│   └── index.html
├── README.md
├── app.py
├── main.py
├── pyproject.toml
├── requirements.txt
├── start.bat
├── start.sh
└── uv.lock
```

## 功能特性

1. **实时监控**: 每5秒自动刷新系统状态
2. **数据采集**: 定时收集CPU、内存、磁盘、进程等信息
3. **预警机制**: 资源使用率超过阈值时发送钉钉通知
4. **可视化展示**: 使用Bootstrap和Plotly展示数据图表
5. **响应式设计**: 支持各种设备屏幕尺寸

## 安装和部署

### 使用uv安装（推荐）

1. 安装uv包管理器：
   ```bash
   pip install uv
   ```

2. 克隆项目：
   ```bash
   git clone <项目地址>
   cd Hello-Service-Monitoring
   ```

3. 安装依赖：
   ```bash
   uv sync
   ```

4. 初始化数据库：
   ```bash
   python init_db.py
   ```

5. 启动服务：
   ```bash
   python app.py
   ```

### 使用传统pip安装

1. 克隆项目：
   ```bash
   git clone <项目地址>
   cd Hello-Service-Monitoring
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 初始化数据库：
   ```bash
   python init_db.py
   ```

5. 启动服务：
   ```bash
   python app.py
   ```

## 数据库管理

本系统使用SQLite数据库存储监控数据，并通过Alembic进行数据库迁移管理。

### 数据库位置

数据库文件现在位于项目根目录下的 `db` 目录中：`db/monitoring.db`

### 数据库特性

- **数据持久化**: 服务重启不会丢失数据
- **结构升级**: 数据库结构可以随着代码更新而自动升级
- **向后兼容**: 新的数据库结构不会影响现有数据

### 初始化数据库

首次运行系统前需要初始化数据库：

```bash
python init_db.py
```

### 数据库迁移

当模型结构发生变化时，需要创建新的迁移脚本：

```bash
alembic revision --autogenerate -m "描述变更内容"
alembic upgrade head
```

## 配置说明

系统配置项位于 `app/config.py` 文件中，可以通过环境变量覆盖默认配置：

- `DATABASE_URL`: 数据库连接URL
- `HOST`: 服务监听地址
- `PORT`: 服务监听端口
- `DEBUG`: 是否启用调试模式
- `DINGTALK_WEBHOOK`: 钉钉机器人Webhook地址
- `MEMORY_THRESHOLD`: 内存使用率预警阈值
- `DISK_THRESHOLD`: 磁盘使用率预警阈值

## API接口

- `/`: 主页
- `/api/server-ip`: 获取服务器IP地址
- `/api/system-info`: 获取系统信息
- `/api/cpu-info`: 获取CPU信息
- `/api/memory-info`: 获取内存信息
- `/api/disk-info`: 获取磁盘信息
- `/api/processes`: 获取进程信息
- `/api/detailed-system-info`: 获取详细系统信息

## 预警机制

当系统资源使用率超过设定阈值时，会通过钉钉机器人发送预警消息。

## 开发指南

### 代码结构

- `app/`: 主要应用代码
- `app/collector.py`: 系统信息采集器
- `app/database.py`: 数据库管理器
- `app/models.py`: 数据库模型定义
- `app/routes.py`: Web路由定义
- `app/monitoring/scheduler.py`: 定时任务调度器
- `templates/`: HTML模板文件

### 添加新功能

1. 在 `app/models.py` 中添加新的数据模型
2. 在 `app/collector.py` 中添加数据采集方法
3. 在 `app/database.py` 中添加数据保存方法
4. 在 `app/routes.py` 中添加API接口
5. 创建Alembic迁移脚本更新数据库结构

## 贡献

欢迎提交Issue和Pull Request来改进本项目。