#!/usr/bin/env python3
"""
懒猫应用商店数据分析系统 - 主入口
支持OIDC认证和文件关联
"""

import os
import sys
import json
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
from functools import wraps
import requests
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# 导入现有模块
from database_manager import DatabaseManager

# 加载环境变量
load_dotenv()

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

# 确保目录存在
for path in [os.path.dirname(DATABASE_PATH), UPLOAD_PATH, CONFIG_PATH]:
    os.makedirs(path, exist_ok=True)

# 初始化数据库管理器
db_manager = None

# OIDC配置
OIDC_ENABLED = all([
    os.environ.get('OIDC_CLIENT_ID'),
    os.environ.get('OIDC_CLIENT_SECRET'),
    os.environ.get('OIDC_ISSUER')
])

if OIDC_ENABLED:
    oauth = OAuth(app)
    oauth.register(
        name='lazycat',
        client_id=os.environ.get('OIDC_CLIENT_ID'),
        client_secret=os.environ.get('OIDC_CLIENT_SECRET'),
        server_metadata_url=f"{os.environ.get('OIDC_ISSUER')}/.well-known/openid-configuration",
        client_kwargs={
            'scope': 'openid profile email'
        }
    )
    logger.info("OIDC认证已启用")
else:
    logger.info("OIDC认证未配置，使用开放模式")

# 认证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if OIDC_ENABLED and 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 健康检查端点
@app.route('/api/health')
def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
        if db_manager:
            db_manager.get_all_apps(page=1, per_page=1)
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'oidc_enabled': OIDC_ENABLED,
            'database': 'connected'
        }), 200
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

# OIDC认证路由
@app.route('/login')
def login():
    """登录页面"""
    if not OIDC_ENABLED:
        # 如果没有配置OIDC，直接设置默认用户
        session['user'] = {'name': 'Guest', 'email': 'guest@local'}
        return redirect(url_for('index'))
    
    redirect_uri = url_for('auth_callback', _external=True)
    return oauth.lazycat.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    """OIDC认证回调"""
    if not OIDC_ENABLED:
        return redirect(url_for('index'))
    
    try:
        token = oauth.lazycat.authorize_access_token()
        user_info = token.get('userinfo')
        if not user_info:
            # 如果token中没有userinfo，尝试从userinfo端点获取
            resp = oauth.lazycat.get('userinfo')
            user_info = resp.json()
        
        session['user'] = user_info
        session['token'] = token
        logger.info(f"用户登录成功: {user_info.get('email', 'unknown')}")
        
        # 检查是否是从文件导入跳转过来的
        if 'pending_import' in session:
            file_path = session.pop('pending_import')
            return redirect(url_for('import_file', file=file_path))
        
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"认证失败: {e}")
        return f"认证失败: {e}", 500

@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    return redirect(url_for('index'))

# 文件导入功能（支持网盘右键菜单）
@app.route('/import')
@login_required
def import_file():
    """从网盘导入CSV文件"""
    file_path = request.args.get('file', '')
    
    if not file_path:
        return jsonify({'error': '未指定文件'}), 400
    
    # 处理文件路径
    if file_path.startswith('/lzcapp/run/mnt/home/'):
        # 这是从网盘右键菜单打开的文件
        actual_path = file_path
    else:
        # 相对路径，添加用户目录前缀
        username = session.get('user', {}).get('name', 'guest')
        actual_path = f"/lzcapp/run/mnt/home/{username}/{file_path}"
    
    try:
        # 检查文件是否存在
        if not os.path.exists(actual_path):
            return jsonify({'error': f'文件不存在: {file_path}'}), 404
        
        # 检查文件类型
        if not actual_path.lower().endswith(('.csv', '.xlsx', '.xls')):
            return jsonify({'error': '不支持的文件类型，仅支持CSV和Excel文件'}), 400
        
        # 读取文件
        if actual_path.lower().endswith('.csv'):
            df = pd.read_csv(actual_path, encoding='utf-8-sig')
        else:
            df = pd.read_excel(actual_path)
        
        # 导入到数据库
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                # 尝试添加到数据库
                app_data = {
                    'name': str(row.get('应用名称', row.get('name', ''))),
                    'description': str(row.get('应用描述', row.get('description', ''))),
                    'icon': str(row.get('图标', row.get('icon', ''))),
                    'downloads': int(row.get('下载量', row.get('downloads', 0))),
                    'status': str(row.get('状态', row.get('status', '已上架')))
                }
                
                if app_data['name']:
                    result = db_manager.add_app(
                        app_data['name'],
                        app_data['description'],
                        app_data['icon'],
                        app_data['downloads'],
                        app_data['status']
                    )
                    if result:
                        imported_count += 1
                    else:
                        skipped_count += 1
                else:
                    skipped_count += 1
                    
            except Exception as e:
                errors.append(f"导入失败 {row.get('应用名称', 'unknown')}: {str(e)}")
                logger.error(f"导入行失败: {e}")
        
        # 返回导入结果页面
        return render_template('import_result.html',
                             file_name=os.path.basename(file_path),
                             total_rows=len(df),
                             imported=imported_count,
                             skipped=skipped_count,
                             errors=errors)
        
    except Exception as e:
        logger.error(f"文件导入失败: {e}")
        return jsonify({'error': f'文件导入失败: {str(e)}'}), 500

# 主页路由
@app.route('/')
@login_required
def index():
    """主页 - 应用列表"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    
    if search_query:
        apps, total_pages = db_manager.search_apps(search_query, page)
    else:
        apps, total_pages = db_manager.get_all_apps(page)
    
    # 获取用户信息
    user = session.get('user', {'name': 'Guest'})
    
    return render_template('index.html',
                         apps=apps,
                         current_page=page,
                         total_pages=total_pages,
                         search_query=search_query,
                         user=user,
                         oidc_enabled=OIDC_ENABLED)

# 注册现有的Web应用路由
def register_existing_routes():
    """注册现有web_app.py中的路由"""
    from app_adapter import AppAdapter
    adapter = AppAdapter(app, db_manager)
    logger.info("已注册所有应用路由")

# 初始化应用
def initialize_app():
    """初始化应用"""
    global db_manager
    
    try:
        # 初始化数据库
        logger.info(f"初始化数据库: {DATABASE_PATH}")
        db_manager = DatabaseManager(DATABASE_PATH)
        
        # 检查是否需要初始化数据
        apps, _ = db_manager.get_all_apps(page=1, per_page=1)
        if not apps:
            logger.info("数据库为空，尝试导入初始数据...")
            # 尝试导入初始CSV数据
            csv_files = [
                '/app/data/lazycat20250625.csv',
                '/app/data/selfh.csv'
            ]
            
            for csv_file in csv_files:
                if os.path.exists(csv_file):
                    try:
                        logger.info(f"导入CSV文件: {csv_file}")
                        db_manager.import_from_csv(csv_file)
                    except Exception as e:
                        logger.error(f"导入CSV失败 {csv_file}: {e}")
        
        logger.info("应用初始化完成")
        
    except Exception as e:
        logger.error(f"应用初始化失败: {e}")
        raise

# 主函数
def main():
    """主函数"""
    # 初始化应用
    initialize_app()
    
    # 注册现有路由
    register_existing_routes()
    
    # 启动Flask应用
    host = '0.0.0.0'
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"启动应用服务器 {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()