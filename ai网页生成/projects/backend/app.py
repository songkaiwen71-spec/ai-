# -*- coding: utf-8 -*-
"""
Flask应用主文件
大数据舆情可视化分析系统 - 后端服务
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import FLASK_CONFIG, API_CONFIG
from routes import crawl_bp, data_bp, analytics_bp


def create_app():
    """创建Flask应用"""
    # 获取项目根目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    app = Flask(
        __name__,
        static_folder=os.path.join(base_dir, 'frontend', 'dist'),
        static_url_path=''
    )

    # 配置
    app.config.update(FLASK_CONFIG)
    app.config['JSON_SORT_KEYS'] = API_CONFIG['json_sort']
    app.config['MAX_CONTENT_LENGTH'] = API_CONFIG['max_content_length']

    # 跨域配置
    if API_CONFIG['cors_enabled']:
        CORS(app, resources={
            r"/api/*": {
                "origins": API_CONFIG['cors_origins']
            }
        })

    # 注册蓝图
    app.register_blueprint(crawl_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(analytics_bp)

    # 根路径 - 返回前端页面
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    # 健康检查
    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'ok',
            'service': 'weibo-sentiment-analysis-backend',
            'version': '1.0.0'
        })

    # 全局错误处理
    @app.errorhandler(404)
    def not_found(e):
        # API请求返回JSON
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': '接口不存在'
            }), 404
        # 其他请求返回前端页面
        return send_from_directory(app.static_folder, 'index.html')

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500

    return app


# 创建应用实例
app = create_app()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"启动后端服务，端口: {port}")
    print(f"API文档: http://localhost:{port}/api/health")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )
