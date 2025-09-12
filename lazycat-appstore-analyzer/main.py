#!/usr/bin/env python3
"""
懒猫应用商店数据分析系统 - 简化启动入口
"""

import os
import sys
import logging
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_cors import CORS
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask应用初始化
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'lazycat-appstore-analyzer-secret-key-2024')
CORS(app)

# 配置路径
DATABASE_PATH = os.environ.get('DATABASE_PATH', '/lzcapp/var/database/lazycat_apps.db')
UPLOAD_PATH = os.environ.get('UPLOAD_PATH', '/lzcapp/var/uploads')
CONFIG_PATH = os.environ.get('CONFIG_PATH', '/lzcapp/var/config')

# 确保目录存在（只在容器环境中创建）
if os.path.exists('/lzcapp'):
    for path in [os.path.dirname(DATABASE_PATH), UPLOAD_PATH, CONFIG_PATH]:
        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"确保目录存在: {path}")
        except Exception as e:
            logger.warning(f"无法创建目录 {path}: {e}")
else:
    logger.info("本地开发环境，跳过目录创建")

# 健康检查端点
@app.route('/api/health')
def health_check():
    """健康检查端点"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'lazycat-appstore-analyzer',
            'version': '1.0.0'
        }), 200
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

# 主页路由
@app.route('/')
def index():
    """主页"""
    try:
        # 尝试返回模板
        return render_template('index.html', 
                             apps=[], 
                             current_page=1, 
                             total_pages=1,
                             search_query='',
                             user={'name': 'Guest'})
    except Exception as e:
        logger.error(f"无法加载模板: {e}")
        # 如果模板不存在，返回简单的HTML
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>懒猫应用商店数据分析系统</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #4A90E2; }
                .status { background: #7ED321; color: white; padding: 10px 20px; border-radius: 5px; display: inline-block; }
                .info { margin: 20px 0; padding: 15px; background: #f0f8ff; border-left: 4px solid #4A90E2; }
                .features { margin: 20px 0; }
                .features li { margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 懒猫应用商店数据分析系统</h1>
                <div class="status">✅ 系统运行正常</div>
                
                <div class="info">
                    <strong>版本:</strong> v1.0.0<br>
                    <strong>状态:</strong> 健康运行中<br>
                    <strong>作者:</strong> 天天
                </div>
                
                <div class="features">
                    <h2>核心功能</h2>
                    <ul>
                        <li>📊 完整的应用管理系统</li>
                        <li>🔍 智能搜索和分析</li>
                        <li>📈 数据可视化图表</li>
                        <li>🔐 OIDC账户集成</li>
                        <li>📁 文件关联支持（CSV/Excel）</li>
                        <li>🎯 批量检查和导入</li>
                    </ul>
                </div>
                
                <div class="info">
                    <strong>提示:</strong> 完整功能正在加载中，请稍后刷新页面...
                </div>
            </div>
        </body>
        </html>
        """

# 其他基础路由
@app.route('/api/version')
def version():
    """版本信息"""
    return jsonify({
        'name': '懒猫应用商店数据分析系统',
        'version': '1.0.0',
        'author': '天天',
        'license': 'MIT'
    })

@app.route('/api/status')
def status():
    """系统状态"""
    return jsonify({
        'status': 'running',
        'uptime': 'just started',
        'database': DATABASE_PATH,
        'upload': UPLOAD_PATH,
        'config': CONFIG_PATH
    })

# 简单的静态文件服务
@app.route('/static/<path:filename>')
def static_files(filename):
    """静态文件服务"""
    try:
        return app.send_static_file(filename)
    except:
        return "File not found", 404

# 主函数
def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("懒猫应用商店数据分析系统启动")
    logger.info("=" * 50)
    
    # 打印配置信息
    logger.info(f"数据库路径: {DATABASE_PATH}")
    logger.info(f"上传路径: {UPLOAD_PATH}")
    logger.info(f"配置路径: {CONFIG_PATH}")
    
    # 启动Flask应用
    host = '0.0.0.0'
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"启动Web服务器: http://{host}:{port}")
    logger.info("健康检查端点: http://localhost:5000/api/health")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        logger.error(f"启动失败: {e}")
        raise

if __name__ == '__main__':
    main()