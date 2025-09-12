#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
懒猫应用商店Web管理界面
基于Flask的可视化数据库管理工具
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
from werkzeug.utils import secure_filename
from database_manager import DatabaseManager
from datetime import datetime
from github_app_finder import GitHubAppFinder
from docker_compose_analyzer import DockerComposeAnalyzer
from migration_evaluator import MigrationEvaluator

# 加载.env文件中的环境变量
def load_env_file():
    """加载.env文件中的环境变量"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# 初始化时加载环境变量
load_env_file()

app = Flask(__name__)
app.secret_key = 'lazycat_secret_key_2024'

# 文件上传配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 初始化数据库管理器
db = DatabaseManager()

@app.route('/')
def index():
    """主页 - 显示应用列表"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort', 'count', type=str)
    per_page = 20
    
    offset = (page - 1) * per_page
    apps, total = db.search_apps(search, per_page, offset, sort_by)
    
    # 计算分页信息
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('index.html', 
                         apps=apps, 
                         page=page, 
                         total_pages=total_pages,
                         total=total,
                         search=search,
                         sort_by=sort_by,
                         per_page=per_page)

@app.route('/statistics')
def statistics():
    """统计页面"""
    stats = db.get_statistics()
    return render_template('statistics.html', stats=stats)

@app.route('/guide_stats')
def guide_stats():
    """攻略统计页面"""
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'count', type=str)
    sort_order = request.args.get('order', 'desc', type=str)
    per_page = 50
    
    stats = db.get_guide_statistics()
    
    # 计算偏移量
    offset = (page - 1) * per_page
    missing, total_missing = db.get_apps_without_guides(limit=per_page, offset=offset, sort_by=sort_by, sort_order=sort_order)
    
    # 计算分页信息
    total_pages = (total_missing + per_page - 1) // per_page
    
    return render_template('guide_stats.html', 
                         stats=stats, 
                         missing=missing,
                         page=page,
                         total_pages=total_pages,
                         total_missing=total_missing,
                         per_page=per_page)

@app.route('/add', methods=['GET', 'POST'])
def add_app():
    """添加应用"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        brief = request.form.get('brief', '').strip()
        count = request.form.get('count', 0, type=int)
        href = request.form.get('href', '').strip()
        icon_src = request.form.get('icon_src', '').strip()
        
        if name:
            app_id = db.add_app(name, brief, count, href, icon_src)
            flash(f'应用 "{name}" 添加成功！', 'success')
            return redirect(url_for('view_app', app_id=app_id))
        else:
            flash('应用名称不能为空！', 'error')
    
    return render_template('add_app.html')

@app.route('/app/<int:app_id>')
def view_app(app_id):
    """查看应用详情"""
    app_data = db.get_app_by_id(app_id)
    if app_data:
        return render_template('view_app.html', app=app_data)
    else:
        flash('应用不存在！', 'error')
        return redirect(url_for('index'))

@app.route('/edit/<int:app_id>', methods=['GET', 'POST'])
def edit_app(app_id):
    """编辑应用"""
    app_data = db.get_app_by_id(app_id)
    if not app_data:
        flash('应用不存在！', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        brief = request.form.get('brief', '').strip()
        count = request.form.get('count', 0, type=int)
        href = request.form.get('href', '').strip()
        icon_src = request.form.get('icon_src', '').strip()
        
        if name:
            if db.update_app(app_id, name, brief, count, href, icon_src):
                flash(f'应用 "{name}" 更新成功！', 'success')
                return redirect(url_for('view_app', app_id=app_id))
            else:
                flash('更新失败！', 'error')
        else:
            flash('应用名称不能为空！', 'error')
    
    return render_template('edit_app.html', app=app_data)

@app.route('/delete/<int:app_id>', methods=['POST'])
def delete_app(app_id):
    """删除应用"""
    app_data = db.get_app_by_id(app_id)
    if app_data:
        if db.delete_app(app_id):
            flash(f'应用 "{app_data[1]}" 删除成功！', 'success')
        else:
            flash('删除失败！', 'error')
    else:
        flash('应用不存在！', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/search')
def api_search():
    """API - 搜索应用"""
    keyword = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort', 'count', type=str)
    
    offset = (page - 1) * per_page
    apps, total = db.search_apps(keyword, per_page, offset, sort_by)
    
    # 转换为JSON格式
    apps_list = []
    for app in apps:
        apps_list.append({
            'id': app[0],
            'name': app[1],
            'brief': app[2],
            'count': app[3],
            'href': app[4],
            'icon_src': app[5],
            'created_at': app[6],
            'star_count': app[7] if len(app) > 7 else 0,
            'github_repo': app[8] if len(app) > 8 else None,
            'source_type': app[9] if len(app) > 9 else None
        })
    
    return jsonify({
        'apps': apps_list,
        'total': total,
        'page': page,
        'per_page': per_page,
        'sort_by': sort_by,
        'total_pages': (total + per_page - 1) // per_page
    })

@app.route('/api/statistics')
def api_statistics():
    """API - 获取实时统计数据"""
    try:
        stats = db.get_guide_statistics()
        return jsonify({
            'success': True,
            'data': {
                'total_apps': stats['total_apps'],
                'apps_with_guides': stats['apps_with_guides'],
                'apps_without_guides': stats['apps_without_guides'],
                'apps_skipped_guides': stats['apps_skipped_guides'],
                'apps_pending_guides': stats['apps_pending_guides']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/guide_stats')
def api_guide_stats():
    """API - 获取攻略统计数据（Ajax分页用）"""
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'count', type=str)
    sort_order = request.args.get('order', 'desc', type=str)
    per_page = 50
    
    # 计算偏移量
    offset = (page - 1) * per_page
    missing, total_missing = db.get_apps_without_guides(limit=per_page, offset=offset, sort_by=sort_by, sort_order=sort_order)
    
    # 计算分页信息
    total_pages = (total_missing + per_page - 1) // per_page
    
    # 转换为JSON格式
    apps_list = []
    for app in missing:
        apps_list.append({
            'id': app[0],
            'name': app[1],
            'brief': app[2],
            'count': app[3],
            'href': app[4],
            'icon_src': app[5],
            'star_count': app[6] if len(app) > 6 else 0,
            'github_repo': app[7] if len(app) > 7 else None,
            'source_type': app[8] if len(app) > 8 else None
        })
    
    return jsonify({
        'apps': apps_list,
        'page': page,
        'total_pages': total_pages,
        'total_missing': total_missing,
        'per_page': per_page,
        'success': True
    })

@app.route('/batch_check', methods=['GET', 'POST'])
def batch_check():
    """批量检查应用"""
    if request.method == 'POST':
        app_list = request.form.get('app_list', '').strip()
        if app_list:
            apps_to_check = [line.strip() for line in app_list.split('\n') if line.strip()]
            
            results = []
            for app_name in apps_to_check:
                # 搜索数据库中是否存在
                found_apps, _ = db.search_apps(app_name, 5, 0)
                
                best_match = None
                best_similarity = 0
                
                for found_app in found_apps:
                    # 简单的相似度计算
                    similarity = calculate_similarity(app_name.lower(), found_app[1].lower())
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = found_app
                
                results.append({
                    'input_name': app_name,
                    'exists': best_similarity >= 0.7,
                    'similarity': best_similarity,
                    'match': best_match
                })
            
            return render_template('batch_check_results.html', results=results, app_list=app_list)
    
    return render_template('batch_check.html')

def calculate_similarity(str1, str2):
    """计算字符串相似度"""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, str1, str2).ratio()

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/import', methods=['GET', 'POST'])
def import_file():
    """一键导入页面"""
    if request.method == 'POST':
        # 检查是否有文件
        if 'file' not in request.files:
            flash('请选择要上传的文件！', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # 检查文件是否被选择
        if file.filename == '':
            flash('请选择要上传的文件！', 'error')
            return redirect(request.url)
        
        # 检查文件类型
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 添加时间戳避免文件名冲突
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                # 保存文件
                file.save(filepath)
                
                # 导入数据
                result = db.import_excel_csv(filepath)
                
                # 删除临时文件
                try:
                    os.remove(filepath)
                except:
                    pass
                
                if result['success']:
                    stats = result['stats']
                    flash(f"导入成功！{result['message']}", 'success')
                    if stats.get('errors'):
                        flash(f"注意：有 {len(stats['errors'])} 个错误", 'warning')
                    
                    return render_template('import_results.html', 
                                         result=result, 
                                         stats=stats)
                else:
                    flash(f"导入失败：{result['message']}", 'error')
                    return redirect(request.url)
                    
            except Exception as e:
                # 清理文件
                try:
                    os.remove(filepath)
                except:
                    pass
                flash(f'文件处理失败：{str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('不支持的文件格式！请上传 .xlsx, .xls 或 .csv 文件', 'error')
            return redirect(request.url)
    
    return render_template('import_file.html')

@app.route('/import_data')
def import_data():
    """重新导入CSV数据"""
    if db.import_csv_data():
        flash('数据导入成功！', 'success')
    else:
        flash('数据导入失败！', 'error')
    
    return redirect(url_for('index'))

@app.route('/batch_add_missing', methods=['POST'])
def batch_add_missing():
    """批量添加缺失应用"""
    missing_apps = request.json.get('missing_apps', [])
    
    if not missing_apps:
        return jsonify({'success': False, 'message': '没有提供应用列表'})
    
    try:
        result = db.batch_add_missing_apps(missing_apps)
        
        message = f"成功添加 {result['total_added']} 个应用"
        if result['total_skipped'] > 0:
            message += f"，跳过 {result['total_skipped']} 个已存在的应用"
        
        return jsonify({
            'success': True,
            'message': message,
            'added': result['added'],
            'skipped': result['skipped'],
            'total_added': result['total_added'],
            'total_skipped': result['total_skipped']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'})

@app.route('/update_guides', methods=['POST'])
def update_guides():
    """抓取并更新攻略链接，然后返回统计结果（用于按钮触发）"""
    try:
        result = db.update_guides_from_playground()
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/mark_skip_guide/<int:app_id>', methods=['POST'])
def mark_skip_guide(app_id):
    """标记应用为暂时不写攻略"""
    try:
        success = db.mark_app_skip_guide(app_id, True)
        if success:
            return jsonify({'success': True, 'message': '已标记为暂时不写攻略'})
        else:
            return jsonify({'success': False, 'message': '应用不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/unmark_skip_guide/<int:app_id>', methods=['POST'])
def unmark_skip_guide(app_id):
    """取消标记应用为暂时不写攻略"""
    try:
        success = db.mark_app_skip_guide(app_id, False)
        if success:
            return jsonify({'success': True, 'message': '已取消暂时不写攻略标记'})
        else:
            return jsonify({'success': False, 'message': '应用不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/pending_guides')
def pending_guides():
    """待写攻略列表页面"""
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'count', type=str)
    sort_order = request.args.get('order', 'desc', type=str)
    per_page = 50
    
    stats = db.get_guide_statistics()
    
    # 计算偏移量
    offset = (page - 1) * per_page
    pending_apps, total_pending = db.get_pending_guide_apps(limit=per_page, offset=offset, sort_by=sort_by, sort_order=sort_order)
    
    # 计算分页信息
    total_pages = (total_pending + per_page - 1) // per_page
    
    return render_template('pending_guides.html', 
                         stats=stats, 
                         pending_apps=pending_apps,
                         page=page,
                         total_pages=total_pages,
                         total_pending=total_pending,
                         per_page=per_page)

@app.route('/api/pending_guides')
def api_pending_guides():
    """API - 获取待写攻略数据（Ajax分页用）"""
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'count', type=str)
    sort_order = request.args.get('order', 'desc', type=str)
    per_page = 50
    
    # 计算偏移量
    offset = (page - 1) * per_page
    pending_apps, total_pending = db.get_pending_guide_apps(limit=per_page, offset=offset, sort_by=sort_by, sort_order=sort_order)
    
    # 计算分页信息
    total_pages = (total_pending + per_page - 1) // per_page
    
    # 转换为JSON格式
    apps_list = []
    for app in pending_apps:
        apps_list.append({
            'id': app[0],
            'name': app[1],
            'brief': app[2],
            'count': app[3],
            'href': app[4],
            'icon_src': app[5],
            'star_count': app[6] if len(app) > 6 else 0,
            'github_repo': app[7] if len(app) > 7 else None,
            'source_type': app[8] if len(app) > 8 else None
        })
    
    return jsonify({
        'apps': apps_list,
        'page': page,
        'total_pages': total_pages,
        'total_pending': total_pending,
        'per_page': per_page,
        'success': True
    })

@app.route('/mark_pending_guide/<int:app_id>', methods=['POST'])
def mark_pending_guide(app_id):
    """标记应用为待写攻略"""
    try:
        success = db.mark_app_pending_guide(app_id, True)
        if success:
            return jsonify({'success': True, 'message': '已加入待写列表'})
        else:
            return jsonify({'success': False, 'message': '应用不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/unmark_pending_guide/<int:app_id>', methods=['POST'])
def unmark_pending_guide(app_id):
    """取消标记应用为待写攻略"""
    try:
        success = db.mark_app_pending_guide(app_id, False)
        if success:
            return jsonify({'success': True, 'message': '已从待写列表移除'})
        else:
            return jsonify({'success': False, 'message': '应用不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/mark_guide_completed/<int:app_id>', methods=['POST'])
def mark_guide_completed(app_id):
    """标记攻略为已完成"""
    try:
        success = db.mark_guide_completed(app_id)
        if success:
            return jsonify({'success': True, 'message': '攻略已标记为完成'})
        else:
            return jsonify({'success': False, 'message': '应用不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/skipped_guides')
def skipped_guides():
    """暂时不写攻略列表页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    stats = db.get_guide_statistics()
    
    # 计算偏移量
    offset = (page - 1) * per_page
    skipped_apps, total_skipped = db.get_skipped_guide_apps(limit=per_page, offset=offset)
    
    # 计算分页信息
    total_pages = (total_skipped + per_page - 1) // per_page
    
    return render_template('skipped_guides.html', 
                         stats=stats, 
                         skipped_apps=skipped_apps,
                         page=page,
                         total_pages=total_pages,
                         total_skipped=total_skipped,
                         per_page=per_page)

@app.route('/api/skipped_guides')
def api_skipped_guides():
    """API - 获取暂时不写攻略数据（Ajax分页用）"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # 计算偏移量
    offset = (page - 1) * per_page
    skipped_apps, total_skipped = db.get_skipped_guide_apps(limit=per_page, offset=offset)
    
    # 计算分页信息
    total_pages = (total_skipped + per_page - 1) // per_page
    
    # 转换为JSON格式
    apps_list = []
    for app in skipped_apps:
        apps_list.append({
            'id': app[0],
            'name': app[1],
            'brief': app[2],
            'count': app[3],
            'href': app[4],
            'icon_src': app[5]
        })
    
    return jsonify({
        'apps': apps_list,
        'page': page,
        'total_pages': total_pages,
        'total_skipped': total_skipped,
        'per_page': per_page,
        'success': True
    })

@app.route('/with_guides')
def with_guides():
    """有攻略应用列表页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    stats = db.get_guide_statistics()
    
    # 计算偏移量
    offset = (page - 1) * per_page
    with_guide_apps, total_with_guides = db.get_with_guide_apps(limit=per_page, offset=offset)
    
    # 计算分页信息
    total_pages = (total_with_guides + per_page - 1) // per_page
    
    return render_template('with_guides.html', 
                         stats=stats, 
                         with_guide_apps=with_guide_apps,
                         page=page,
                         total_pages=total_pages,
                         total_with_guides=total_with_guides,
                         per_page=per_page)

@app.route('/api/with_guides')
def api_with_guides():
    """API - 获取有攻略应用数据（Ajax分页用）"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # 计算偏移量
    offset = (page - 1) * per_page
    with_guide_apps, total_with_guides = db.get_with_guide_apps(limit=per_page, offset=offset)
    
    # 计算分页信息
    total_pages = (total_with_guides + per_page - 1) // per_page
    
    # 转换为JSON格式
    apps_list = []
    for app in with_guide_apps:
        apps_list.append({
            'id': app[0],
            'name': app[1],
            'brief': app[2],
            'count': app[3],
            'href': app[4],
            'icon_src': app[5],
            'guide_url': app[6]
        })
    
    return jsonify({
        'apps': apps_list,
        'page': page,
        'total_pages': total_pages,
        'total_with_guides': total_with_guides,
        'per_page': per_page,
        'success': True
    })

# GitHub搜索和移植评估相关路由
@app.route('/github_search')
def github_search():
    """GitHub应用搜索页面"""
    return render_template('github_search.html')

@app.route('/api/github_search', methods=['POST'])
def api_github_search():
    """执行GitHub搜索API"""
    try:
        data = request.json
        keywords = data.get('keywords', [])
        category = data.get('category', '')
        min_stars = data.get('min_stars', 100)
        max_results = data.get('max_results', 50)
        
        # 创建GitHub搜索器
        github_token = os.getenv('GITHUB_TOKEN')
        finder = GitHubAppFinder(github_token)
        
        # 执行搜索
        if category:
            results = finder.search_by_category(category, max_results)
        else:
            results = finder.search_docker_compose_apps(keywords, min_stars, max_results)
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results),
            'message': f'找到 {len(results)} 个符合条件的应用'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'搜索失败: {str(e)}',
            'results': []
        })

@app.route('/migration_finder')
def migration_finder():
    """移植应用查找页面"""
    stats = db.get_github_statistics()
    return render_template('migration_finder.html', stats=stats)

@app.route('/api/evaluate_migration', methods=['POST'])
def api_evaluate_migration():
    """评估移植优先级API"""
    try:
        data = request.json
        repo_list = data.get('repos', [])
        
        if not repo_list:
            return jsonify({
                'success': False,
                'message': '没有提供仓库列表'
            })
        
        # 创建评估器
        evaluator = MigrationEvaluator()
        github_finder = GitHubAppFinder(os.getenv('GITHUB_TOKEN'))
        
        evaluations = []
        
        for repo_info in repo_list:
            try:
                # 获取Docker Compose内容
                docker_content = github_finder.get_docker_compose_content(repo_info['full_name'])
                
                # 评估移植
                evaluation = evaluator.evaluate_migration(repo_info, docker_content)
                
                # 转换为可序列化的格式
                eval_dict = {
                    'repo_name': evaluation.repo_name,
                    'repo_url': evaluation.repo_url,
                    'description': evaluation.description,
                    'stars': evaluation.github_metrics.stars,
                    'forks': evaluation.github_metrics.forks,
                    'language': evaluation.github_metrics.language,
                    'total_score': evaluation.migration_score.total_score,
                    'priority_level': evaluation.migration_score.priority_level,
                    'effort_estimation': evaluation.effort_estimation,
                    'complexity_level': evaluation.docker_analysis.complexity_level if evaluation.docker_analysis else None,
                    'services_count': evaluation.docker_analysis.services_count if evaluation.docker_analysis else 0,
                    'similar_apps_count': len(evaluation.existing_similar_apps),
                    'risks_count': len(evaluation.migration_risks),
                    'recommendations': evaluation.recommendations[:3]  # 只返回前3个建议
                }
                evaluations.append(eval_dict)
                
            except Exception as e:
                print(f"评估 {repo_info.get('full_name')} 失败: {e}")
                continue
        
        # 按评分排序
        evaluations.sort(key=lambda x: x['total_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'evaluations': evaluations,
            'total': len(evaluations),
            'message': f'成功评估 {len(evaluations)} 个应用'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'评估失败: {str(e)}',
            'evaluations': []
        })

@app.route('/migration_candidates')
def migration_candidates():
    """移植候选应用列表页面"""
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'priority_score', type=str)
    min_stars = request.args.get('min_stars', 0, type=int)
    per_page = 20
    
    offset = (page - 1) * per_page
    candidates, total = db.get_github_candidates(per_page, offset, sort_by, True, min_stars)
    
    # 计算分页信息
    total_pages = (total + per_page - 1) // per_page
    
    # 获取统计信息
    stats = db.get_github_statistics()
    
    return render_template('migration_candidates.html',
                         candidates=candidates,
                         page=page,
                         total_pages=total_pages,
                         total=total,
                         sort_by=sort_by,
                         min_stars=min_stars,
                         per_page=per_page,
                         stats=stats)

@app.route('/api/save_candidates', methods=['POST'])
def api_save_candidates():
    """保存GitHub候选应用到数据库"""
    try:
        data = request.json
        evaluations_data = data.get('evaluations', [])
        
        if not evaluations_data:
            return jsonify({
                'success': False,
                'message': '没有提供评估数据'
            })
        
        # 转换数据格式以匹配MigrationEvaluation结构
        # 这里需要模拟完整的评估结果结构
        saved_count = 0
        
        for eval_data in evaluations_data:
            try:
                # 构建基本仓库信息
                repo_info = {
                    'name': eval_data['repo_name'].split('/')[-1],
                    'full_name': eval_data['repo_name'],
                    'description': eval_data['description'],
                    'url': eval_data['repo_url'],
                    'stars': eval_data['stars'],
                    'forks': eval_data['forks'],
                    'language': eval_data['language'],
                    'topics': [],
                    'license': None,
                    'size': 0,
                    'open_issues': 0,
                    'created_at': '',
                    'updated_at': ''
                }
                
                # 创建简化的评估结果
                class SimpleEvaluation:
                    def __init__(self, data):
                        self.repo_name = data['repo_name']
                        self.repo_url = data['repo_url']
                        self.description = data['description']
                        self.effort_estimation = data['effort_estimation']
                        self.docker_analysis = None
                        
                        # 模拟GitHub指标
                        class GitHubMetrics:
                            def __init__(self):
                                self.stars = data['stars']
                                self.forks = data['forks']
                                self.language = data['language']
                                self.topics = []
                                self.license = None
                                self.size = 0
                                self.open_issues = 0
                                self.created_at = ''
                                self.updated_at = ''
                        
                        self.github_metrics = GitHubMetrics()
                        
                        # 模拟移植评分
                        class MigrationScore:
                            def __init__(self):
                                self.total_score = data['total_score']
                                self.priority_level = data['priority_level']
                        
                        self.migration_score = MigrationScore()
                
                evaluation = SimpleEvaluation(eval_data)
                candidate_id = db.add_github_candidate(repo_info, evaluation)
                
                if candidate_id:
                    saved_count += 1
                
            except Exception as e:
                print(f"保存候选应用失败: {e}")
                continue
        
        return jsonify({
            'success': True,
            'message': f'成功保存 {saved_count} 个候选应用',
            'saved_count': saved_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'保存失败: {str(e)}'
        })

@app.route('/candidate_detail/<int:candidate_id>')
def candidate_detail(candidate_id):
    """候选应用详情页面"""
    candidate = db.get_github_candidate_by_id(candidate_id)
    
    if not candidate:
        flash('候选应用不存在！', 'error')
        return redirect(url_for('migration_candidates'))
    
    return render_template('candidate_detail.html', candidate=candidate)

@app.route('/api/mark_candidate_suitable/<int:candidate_id>', methods=['POST'])
def api_mark_candidate_suitable(candidate_id):
    """标记候选应用是否适合移植"""
    try:
        data = request.json
        is_suitable = data.get('is_suitable', True)
        notes = data.get('notes', '')
        
        success = db.mark_github_candidate_suitable(candidate_id, is_suitable, notes)
        
        if success:
            return jsonify({
                'success': True,
                'message': '标记成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '候选应用不存在'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        })

@app.route('/migration_report')
def migration_report():
    """移植优先级报告页面"""
    # 获取所有适合移植的候选应用
    candidates, _ = db.get_github_candidates(limit=100, filter_suitable=True)
    
    # 获取统计信息
    stats = db.get_github_statistics()
    
    return render_template('migration_report.html', 
                         candidates=candidates,
                         stats=stats)

if __name__ == '__main__':
    # 确保模板目录存在
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("🚀 启动懒猫应用商店Web管理界面")
    print("📱 访问地址: http://localhost:5001")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001) 