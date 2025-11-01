#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务器监控系统启动脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from app.app import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)