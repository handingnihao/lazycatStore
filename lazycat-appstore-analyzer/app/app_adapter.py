#!/usr/bin/env python3
"""
应用适配器 - 整合现有web_app.py的功能
"""

import os
import sys
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
import pandas as pd
from datetime import datetime
import json

# 添加父目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入数据库管理器
from database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class AppAdapter:
    """应用适配器类，整合所有功能"""
    
    def __init__(self, app, db_manager):
        self.app = app
        self.db_manager = db_manager
        self.register_routes()
    
    def register_routes(self):
        """注册所有路由"""
        
        # 添加应用
        @self.app.route('/add', methods=['GET', 'POST'])
        def add_app():
            if request.method == 'POST':
                try:
                    name = request.form.get('name')
                    description = request.form.get('description', '')
                    icon = request.form.get('icon', '')
                    downloads = int(request.form.get('downloads', 0))
                    status = request.form.get('status', '已上架')
                    
                    result = self.db_manager.add_app(name, description, icon, downloads, status)
                    
                    if result:
                        flash('应用添加成功！', 'success')
                        return redirect(url_for('index'))
                    else:
                        flash('应用已存在！', 'warning')
                        return redirect(url_for('add_app'))
                        
                except Exception as e:
                    logger.error(f"添加应用失败: {e}")
                    flash(f'添加失败: {str(e)}', 'danger')
                    return redirect(url_for('add_app'))
            
            return render_template('add_app.html')
        
        # 编辑应用
        @self.app.route('/edit/<int:app_id>', methods=['GET', 'POST'])
        def edit_app(app_id):
            if request.method == 'POST':
                try:
                    app_data = {
                        'name': request.form.get('name'),
                        'description': request.form.get('description', ''),
                        'icon': request.form.get('icon', ''),
                        'downloads': int(request.form.get('downloads', 0)),
                        'status': request.form.get('status', '已上架')
                    }
                    
                    result = self.db_manager.update_app(app_id, app_data)
                    
                    if result:
                        flash('应用更新成功！', 'success')
                        return redirect(url_for('view_app', app_id=app_id))
                    else:
                        flash('更新失败！', 'danger')
                        return redirect(url_for('edit_app', app_id=app_id))
                        
                except Exception as e:
                    logger.error(f"编辑应用失败: {e}")
                    flash(f'更新失败: {str(e)}', 'danger')
                    return redirect(url_for('edit_app', app_id=app_id))
            
            app = self.db_manager.get_app_by_id(app_id)
            if not app:
                flash('应用不存在！', 'warning')
                return redirect(url_for('index'))
            
            return render_template('edit_app.html', app=app)
        
        # 查看应用详情
        @self.app.route('/view/<int:app_id>')
        def view_app(app_id):
            app = self.db_manager.get_app_by_id(app_id)
            if not app:
                flash('应用不存在！', 'warning')
                return redirect(url_for('index'))
            
            return render_template('view_app.html', app=app)
        
        # 删除应用
        @self.app.route('/delete/<int:app_id>', methods=['POST'])
        def delete_app(app_id):
            try:
                result = self.db_manager.delete_app(app_id)
                
                if result:
                    return jsonify({'success': True, 'message': '应用删除成功'})
                else:
                    return jsonify({'success': False, 'message': '删除失败'})
                    
            except Exception as e:
                logger.error(f"删除应用失败: {e}")
                return jsonify({'success': False, 'message': str(e)})
        
        # 统计页面
        @self.app.route('/statistics')
        def statistics():
            stats = self.db_manager.get_statistics()
            
            # 获取热门应用
            top_apps = self.db_manager.get_top_apps(limit=10)
            
            return render_template('statistics.html', 
                                 stats=stats,
                                 top_apps=top_apps)
        
        # 批量检查页面
        @self.app.route('/batch_check')
        def batch_check():
            return render_template('batch_check.html')
        
        # 批量检查API
        @self.app.route('/api/batch_check', methods=['POST'])
        def api_batch_check():
            try:
                data = request.get_json()
                app_names = data.get('apps', [])
                
                if not app_names:
                    return jsonify({'error': '请输入应用名称'}), 400
                
                results = []
                for name in app_names:
                    name = name.strip()
                    if name:
                        # 搜索应用
                        found = self.db_manager.search_app_by_name(name)
                        results.append({
                            'name': name,
                            'found': found is not None,
                            'data': found
                        })
                
                # 统计结果
                found_count = sum(1 for r in results if r['found'])
                missing_count = len(results) - found_count
                
                return jsonify({
                    'success': True,
                    'results': results,
                    'summary': {
                        'total': len(results),
                        'found': found_count,
                        'missing': missing_count
                    }
                })
                
            except Exception as e:
                logger.error(f"批量检查失败: {e}")
                return jsonify({'error': str(e)}), 500
        
        # 批量添加缺失应用
        @self.app.route('/batch_add_missing', methods=['POST'])
        def batch_add_missing():
            try:
                data = request.get_json()
                missing_apps = data.get('missing_apps', [])
                
                added = []
                skipped = []
                
                for app_name in missing_apps:
                    app_name = app_name.strip()
                    if app_name:
                        # 检查是否已存在
                        existing = self.db_manager.search_app_by_name(app_name)
                        if existing:
                            skipped.append(app_name)
                        else:
                            # 添加为"暂不适合"状态
                            result = self.db_manager.add_app(
                                name=app_name,
                                description='待评估应用',
                                icon='',
                                downloads=0,
                                status='暂不适合'
                            )
                            if result:
                                added.append(app_name)
                            else:
                                skipped.append(app_name)
                
                return jsonify({
                    'success': True,
                    'added': added,
                    'skipped': skipped,
                    'summary': {
                        'added_count': len(added),
                        'skipped_count': len(skipped)
                    }
                })
                
            except Exception as e:
                logger.error(f"批量添加失败: {e}")
                return jsonify({'error': str(e)}), 500
        
        # API搜索接口
        @self.app.route('/api/search')
        def api_search():
            query = request.args.get('q', '')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            if query:
                apps, total_pages = self.db_manager.search_apps(query, page, per_page)
            else:
                apps, total_pages = self.db_manager.get_all_apps(page, per_page)
            
            return jsonify({
                'success': True,
                'apps': apps,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'per_page': per_page
                }
            })
        
        # API统计接口
        @self.app.route('/api/statistics')
        def api_statistics():
            stats = self.db_manager.get_statistics()
            top_apps = self.db_manager.get_top_apps(limit=10)
            
            return jsonify({
                'success': True,
                'statistics': stats,
                'top_apps': top_apps
            })
        
        # 导出CSV功能
        @self.app.route('/export')
        def export_csv():
            try:
                # 获取所有应用数据
                all_apps = self.db_manager.export_all_apps()
                
                # 转换为DataFrame
                df = pd.DataFrame(all_apps)
                
                # 生成CSV
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                
                # 返回CSV文件
                from flask import Response
                response = Response(csv_data, mimetype='text/csv')
                response.headers['Content-Disposition'] = f'attachment; filename=lazycat_apps_{datetime.now().strftime("%Y%m%d")}.csv'
                
                return response
                
            except Exception as e:
                logger.error(f"导出失败: {e}")
                flash(f'导出失败: {str(e)}', 'danger')
                return redirect(url_for('index'))
        
        # 数据同步功能（从官方商店同步）
        @self.app.route('/sync')
        def sync_data():
            """同步官方商店数据（预留接口）"""
            # TODO: 实现从官方API同步数据
            flash('数据同步功能开发中...', 'info')
            return redirect(url_for('index'))
        
        logger.info("所有路由注册完成")