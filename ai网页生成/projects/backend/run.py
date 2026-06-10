# -*- coding: utf-8 -*-
"""
后端服务启动入口
大数据舆情可视化分析系统
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

# 获取端口配置
PORT = int(os.environ.get('PORT', 5000))


if __name__ == '__main__':
    print("=" * 50)
    print("大数据舆情可视化分析系统 - 后端服务")
    print("=" * 50)
    print(f"服务地址: http://0.0.0.0:{PORT}")
    print(f"健康检查: http://0.0.0.0:{PORT}/api/health")
    print("=" * 50)

    # 启动服务
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=True,
        threaded=True
    )
