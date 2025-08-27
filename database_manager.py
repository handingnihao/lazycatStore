#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
懒猫应用商店数据库管理器
将CSV数据导入SQLite数据库，提供完整的增删改查功能
"""

import sqlite3
import csv
import os
import pandas as pd
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='lazycat_apps.db'):
        self.db_path = db_path
        self.init_database()
        self.ensure_guide_columns()
    
    def init_database(self):
        """初始化数据库和表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建应用表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brief TEXT,
                count INTEGER DEFAULT 0,
                href TEXT,
                icon_src TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON apps(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_count ON apps(count)')
        
        conn.commit()
        conn.close()
        print(f"✅ 数据库初始化完成: {self.db_path}")
    
    def ensure_guide_columns(self):
        """确保攻略相关的列存在"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查并添加攻略相关列
        try:
            # 添加guide_url列
            cursor.execute('ALTER TABLE apps ADD COLUMN guide_url TEXT')
        except sqlite3.OperationalError:
            pass  # 列已存在
        
        try:
            # 添加has_guide列
            cursor.execute('ALTER TABLE apps ADD COLUMN has_guide INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # 列已存在
        
        try:
            # 添加skip_guide列
            cursor.execute('ALTER TABLE apps ADD COLUMN skip_guide INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # 列已存在
        
        try:
            # 添加pending_guide列
            cursor.execute('ALTER TABLE apps ADD COLUMN pending_guide INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # 列已存在
        
        # 初始化GitHub候选应用表
        self._init_github_tables()
        
        conn.commit()
        conn.close()
    
    def _init_github_tables(self):
        """初始化GitHub相关表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # GitHub候选应用表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS github_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT NOT NULL,
                repo_full_name TEXT UNIQUE NOT NULL,
                description TEXT,
                url TEXT,
                stars INTEGER DEFAULT 0,
                forks INTEGER DEFAULT 0,
                language TEXT,
                topics TEXT,
                license TEXT,
                size_kb INTEGER DEFAULT 0,
                open_issues INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT,
                last_analysis TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                priority_score REAL DEFAULT 0.0,
                priority_level TEXT,
                effort_estimation TEXT,
                is_suitable INTEGER DEFAULT 1,
                notes TEXT
            )
        ''')
        
        # Docker分析结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS docker_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                services_count INTEGER DEFAULT 0,
                total_ports INTEGER DEFAULT 0,
                exposed_ports TEXT,
                complexity_level TEXT,
                complexity_score INTEGER DEFAULT 0,
                requires_build INTEGER DEFAULT 0,
                external_dependencies TEXT,
                storage_requirements TEXT,
                network_requirements TEXT,
                deployment_notes TEXT,
                migration_warnings TEXT,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES github_candidates (id)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_github_stars ON github_candidates(stars)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_github_priority ON github_candidates(priority_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_github_suitable ON github_candidates(is_suitable)')
        
        conn.commit()
        conn.close()
    
    def import_csv_data(self, csv_file='lazycat20250625.csv'):
        """从CSV文件导入数据"""
        if not os.path.exists(csv_file):
            print(f"❌ CSV文件不存在: {csv_file}")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 清空现有数据
        cursor.execute('DELETE FROM apps')
        
        # 读取CSV数据
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        
        for encoding in encodings:
            try:
                with open(csv_file, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    apps_data = []
                    
                    for row in reader:
                        if row.get('name'):  # 确保有应用名称
                            apps_data.append((
                                row.get('name', '').strip(),
                                row.get('brief', '').strip(),
                                self._parse_count(row.get('count', '0')),
                                row.get('tablescraper-selected-row href', '').strip(),
                                row.get('icon src', '').strip()
                            ))
                    
                    # 批量插入数据
                    cursor.executemany('''
                        INSERT INTO apps (name, brief, count, href, icon_src)
                        VALUES (?, ?, ?, ?, ?)
                    ''', apps_data)
                    
                    conn.commit()
                    print(f"✅ 成功导入 {len(apps_data)} 个应用 (编码: {encoding})")
                    
                    # 显示统计信息
                    cursor.execute('SELECT COUNT(*) FROM apps')
                    total = cursor.fetchone()[0]
                    
                    cursor.execute('SELECT COUNT(*) FROM apps WHERE count > 0')
                    with_downloads = cursor.fetchone()[0]
                    
                    print(f"📊 数据库统计:")
                    print(f"   总应用数: {total}")
                    print(f"   有下载量的应用: {with_downloads}")
                    
                    conn.close()
                    return True
                    
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"❌ 导入数据时出错：{str(e)}")
                conn.close()
                return False
        
        print("❌ 所有编码尝试失败")
        conn.close()
        return False
    
    def _parse_count(self, count_str):
        """解析下载数量字符串"""
        if not count_str or count_str == '-':
            return 0
        try:
            return int(count_str.replace(',', ''))
        except:
            return 0
    
    def search_apps(self, keyword='', limit=50, offset=0, sort_by='count'):
        """搜索应用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 定义排序选项
        sort_options = {
            'count': 'apps.count DESC, apps.name',
            'star': 'COALESCE(ad.star_count, 0) DESC, apps.name',
            'name': 'apps.name',
            'created': 'apps.created_at DESC'
        }
        
        # 设置排序方式
        order_by = sort_options.get(sort_by, sort_options['count'])
        
        if keyword:
            cursor.execute(f'''
                SELECT apps.id, apps.name, apps.brief, apps.count, apps.href, apps.icon_src, apps.created_at,
                       COALESCE(ad.star_count, 0) as star_count, 
                       ad.github_repo, ad.source_type
                FROM apps
                LEFT JOIN app_details ad ON apps.id = ad.app_id
                WHERE apps.name LIKE ? OR apps.brief LIKE ?
                ORDER BY {order_by}
                LIMIT ? OFFSET ?
            ''', (f'%{keyword}%', f'%{keyword}%', limit, offset))
        else:
            cursor.execute(f'''
                SELECT apps.id, apps.name, apps.brief, apps.count, apps.href, apps.icon_src, apps.created_at,
                       COALESCE(ad.star_count, 0) as star_count, 
                       ad.github_repo, ad.source_type
                FROM apps
                LEFT JOIN app_details ad ON apps.id = ad.app_id
                ORDER BY {order_by}
                LIMIT ? OFFSET ?
            ''', (limit, offset))
        
        results = cursor.fetchall()
        
        # 获取总数
        if keyword:
            cursor.execute('''
                SELECT COUNT(*)
                FROM apps
                WHERE name LIKE ? OR brief LIKE ?
            ''', (f'%{keyword}%', f'%{keyword}%'))
        else:
            cursor.execute('SELECT COUNT(*) FROM apps')
        
        total = cursor.fetchone()[0]
        conn.close()
        
        return results, total
    
    def get_app_by_id(self, app_id):
        """根据ID获取应用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, brief, count, href, icon_src, created_at, updated_at
            FROM apps
            WHERE id = ?
        ''', (app_id,))
        
        result = cursor.fetchone()
        conn.close()
        return result
    
    def add_app(self, name, brief='', count=0, href='', icon_src='', use_custom_id=False):
        """添加新应用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if use_custom_id:
            # 使用自定义ID
            app_id = self.get_next_custom_id()
            cursor.execute('''
                INSERT INTO apps (id, name, brief, count, href, icon_src)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (app_id, name, brief, count, href, icon_src))
        else:
            # 使用自动递增ID
            cursor.execute('''
                INSERT INTO apps (name, brief, count, href, icon_src)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, brief, count, href, icon_src))
            app_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        id_type = "自定义ID" if use_custom_id else "ID"
        print(f"✅ 添加应用成功: {name} ({id_type}: {app_id})")
        return app_id
    
    def update_app(self, app_id, name=None, brief=None, count=None, href=None, icon_src=None):
        """更新应用信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 构建更新语句
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        if brief is not None:
            updates.append('brief = ?')
            params.append(brief)
        if count is not None:
            updates.append('count = ?')
            params.append(count)
        if href is not None:
            updates.append('href = ?')
            params.append(href)
        if icon_src is not None:
            updates.append('icon_src = ?')
            params.append(icon_src)
        
        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            params.append(app_id)
            
            sql = f"UPDATE apps SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(sql, params)
            
            if cursor.rowcount > 0:
                conn.commit()
                print(f"✅ 更新应用成功: ID {app_id}")
                result = True
            else:
                print(f"❌ 应用不存在: ID {app_id}")
                result = False
        else:
            print("❌ 没有提供更新字段")
            result = False
        
        conn.close()
        return result
    
    def delete_app(self, app_id):
        """删除应用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM apps WHERE id = ?', (app_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ 删除应用成功: ID {app_id}")
            result = True
        else:
            print(f"❌ 应用不存在: ID {app_id}")
            result = False
        
        conn.close()
        return result
    
    def get_statistics(self):
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总应用数
        cursor.execute('SELECT COUNT(*) FROM apps')
        total_apps = cursor.fetchone()[0]
        
        # 有下载量的应用数
        cursor.execute('SELECT COUNT(*) FROM apps WHERE count > 0')
        apps_with_downloads = cursor.fetchone()[0]
        
        # 平均下载量
        cursor.execute('SELECT AVG(count) FROM apps WHERE count > 0')
        avg_downloads = cursor.fetchone()[0] or 0
        
        # 最高下载量
        cursor.execute('SELECT MAX(count) FROM apps')
        max_downloads = cursor.fetchone()[0] or 0
        
        # 最受欢迎的应用（前10）
        cursor.execute('''
            SELECT name, count FROM apps
            WHERE count > 0
            ORDER BY count DESC
            LIMIT 10
        ''')
        top_apps = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_apps': total_apps,
            'apps_with_downloads': apps_with_downloads,
            'avg_downloads': round(avg_downloads, 2),
            'max_downloads': max_downloads,
            'top_apps': top_apps
        }
    
    def get_guide_statistics(self):
        """获取攻略统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总应用数
        cursor.execute('SELECT COUNT(*) FROM apps')
        total_apps = cursor.fetchone()[0]
        
        # 有攻略的应用数
        cursor.execute('SELECT COUNT(*) FROM apps WHERE has_guide = 1 AND guide_url IS NOT NULL AND guide_url != ""')
        apps_with_guides = cursor.fetchone()[0]
        
        # 无攻略的应用数（排除被标记为暂时不写攻略和待写的）
        cursor.execute('SELECT COUNT(*) FROM apps WHERE (has_guide IS NULL OR has_guide = 0) AND (guide_url IS NULL OR guide_url = "") AND (skip_guide IS NULL OR skip_guide = 0) AND (pending_guide IS NULL OR pending_guide = 0)')
        apps_without_guides = cursor.fetchone()[0]
        
        # 被标记为暂时不写攻略的应用数
        cursor.execute('SELECT COUNT(*) FROM apps WHERE skip_guide = 1')
        apps_skipped_guides = cursor.fetchone()[0]
        
        # 待写攻略的应用数
        cursor.execute('SELECT COUNT(*) FROM apps WHERE pending_guide = 1')
        apps_pending_guides = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_apps': total_apps,
            'apps_with_guides': apps_with_guides,
            'apps_without_guides': apps_without_guides,
            'apps_skipped_guides': apps_skipped_guides,
            'apps_pending_guides': apps_pending_guides
        }
    
    def get_apps_without_guides(self, limit: int = 50, offset: int = 0, sort_by: str = 'count', sort_order: str = 'desc'):
        """列出没有攻略的应用，支持分页和排序，排除被标记为暂时不写攻略的应用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 设置排序方向
        order_dir = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
        name_order = 'ASC' if sort_by == 'name' else 'ASC'  # 名字总是升序作为第二排序
        
        # 定义排序选项
        sort_options = {
            'count': f'apps.count {order_dir}, apps.name {name_order}',
            'star': f'COALESCE(ad.star_count, 0) {order_dir}, apps.name {name_order}',
            'name': f'apps.name {order_dir}',
            'created': f'apps.created_at {order_dir}'
        }
        
        # 设置排序方式
        order_by = sort_options.get(sort_by, sort_options['count'])
        
        # 获取数据，包含star信息
        cursor.execute(
            f'''
            SELECT apps.id, apps.name, apps.brief, apps.count, apps.href, apps.icon_src,
                   COALESCE(ad.star_count, 0) as star_count, 
                   ad.github_repo, ad.source_type
            FROM apps
            LEFT JOIN app_details ad ON apps.id = ad.app_id
            WHERE (apps.has_guide IS NULL OR apps.has_guide = 0)
              AND (apps.guide_url IS NULL OR apps.guide_url = '')
              AND (apps.skip_guide IS NULL OR apps.skip_guide = 0)
              AND (apps.pending_guide IS NULL OR apps.pending_guide = 0)
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
            ''', (limit, offset)
        )
        rows = cursor.fetchall()
        
        # 获取总数
        cursor.execute(
            '''
            SELECT COUNT(*) FROM apps
            WHERE (has_guide IS NULL OR has_guide = 0)
              AND (guide_url IS NULL OR guide_url = '')
              AND (skip_guide IS NULL OR skip_guide = 0)
              AND (pending_guide IS NULL OR pending_guide = 0)
            '''
        )
        total = cursor.fetchone()[0]
        
        conn.close()
        return rows, total
    
    def mark_app_skip_guide(self, app_id: int, skip: bool):
        """标记或取消标记应用为暂时不写攻略"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'UPDATE apps SET skip_guide = ? WHERE id = ?',
                (1 if skip else 0, app_id)
            )
            
            if cursor.rowcount > 0:
                conn.commit()
                result = True
            else:
                result = False
        except Exception:
            result = False
        
        conn.close()
        return result
    
    def mark_app_pending_guide(self, app_id: int, pending: bool):
        """标记或取消标记应用为待写攻略"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'UPDATE apps SET pending_guide = ? WHERE id = ?',
                (1 if pending else 0, app_id)
            )
            
            if cursor.rowcount > 0:
                conn.commit()
                result = True
            else:
                result = False
        except Exception:
            result = False
        
        conn.close()
        return result
    
    def get_pending_guide_apps(self, limit: int = 50, offset: int = 0, sort_by: str = 'count', sort_order: str = 'desc'):
        """获取待写攻略的应用列表，支持排序"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 设置排序方向
        order_dir = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
        name_order = 'ASC' if sort_by == 'name' else 'ASC'  # 名字总是升序作为第二排序
        
        # 定义排序选项
        sort_options = {
            'count': f'apps.count {order_dir}, apps.name {name_order}',
            'star': f'COALESCE(ad.star_count, 0) {order_dir}, apps.name {name_order}',
            'name': f'apps.name {order_dir}',
            'created': f'apps.created_at {order_dir}'
        }
        
        # 设置排序方式
        order_by = sort_options.get(sort_by, sort_options['count'])
        
        # 获取数据，包含star信息
        cursor.execute(
            f'''
            SELECT apps.id, apps.name, apps.brief, apps.count, apps.href, apps.icon_src,
                   COALESCE(ad.star_count, 0) as star_count, 
                   ad.github_repo, ad.source_type
            FROM apps
            LEFT JOIN app_details ad ON apps.id = ad.app_id
            WHERE apps.pending_guide = 1
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
            ''', (limit, offset)
        )
        rows = cursor.fetchall()
        
        # 获取总数
        cursor.execute('SELECT COUNT(*) FROM apps WHERE pending_guide = 1')
        total = cursor.fetchone()[0]
        
        conn.close()
        return rows, total
    
    def get_skipped_guide_apps(self, limit: int = 50, offset: int = 0):
        """获取被标记为暂时不写攻略的应用列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取数据
        cursor.execute(
            '''
            SELECT id, name, brief, count, href, icon_src FROM apps
            WHERE skip_guide = 1
            ORDER BY count DESC, name
            LIMIT ? OFFSET ?
            ''', (limit, offset)
        )
        rows = cursor.fetchall()
        
        # 获取总数
        cursor.execute('SELECT COUNT(*) FROM apps WHERE skip_guide = 1')
        total = cursor.fetchone()[0]
        
        conn.close()
        return rows, total
    
    def get_with_guide_apps(self, limit: int = 50, offset: int = 0):
        """获取有攻略的应用列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取数据，包含guide_url
        cursor.execute(
            '''
            SELECT id, name, brief, count, href, icon_src, guide_url FROM apps
            WHERE has_guide = 1 AND guide_url IS NOT NULL AND guide_url != ""
            ORDER BY count DESC, name
            LIMIT ? OFFSET ?
            ''', (limit, offset)
        )
        rows = cursor.fetchall()
        
        # 获取总数
        cursor.execute(
            '''
            SELECT COUNT(*) FROM apps 
            WHERE has_guide = 1 AND guide_url IS NOT NULL AND guide_url != ""
            '''
        )
        total = cursor.fetchone()[0]
        
        conn.close()
        return rows, total
    
    def mark_guide_completed(self, app_id: int):
        """标记应用攻略为已完成（将pending_guide设为0，has_guide设为1）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'UPDATE apps SET pending_guide = 0, has_guide = 1, guide_url = ? WHERE id = ?',
                ('https://lazycat.cloud/playground/', app_id)
            )
            
            if cursor.rowcount > 0:
                conn.commit()
                result = True
            else:
                result = False
        except Exception:
            result = False
        
        conn.close()
        return result
    
    def update_guides_from_playground(self):
        """从官方攻略页面API更新攻略信息"""
        import requests
        import json
        from urllib.parse import parse_qs, urlparse
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            updated_count = 0
            inserted_count = 0
            total_guides = 0
            
            # 清空现有的攻略链接，重新获取最新数据
            cursor.execute('UPDATE apps SET guide_url = NULL, has_guide = 0 WHERE has_guide = 1')
            print("已清空现有攻略数据，准备重新获取...")
            
            # 分页获取所有攻略数据
            page = 1
            size = 100  # 每页获取更多数据提高效率
            
            while True:
                url = f"https://playground.api.lazycat.cloud/api/workshop/guideline/list?size={size}&sort=-createdAt&page={page}"
                print(f"正在获取第 {page} 页攻略数据...")
                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    break
                
                # 处理每个攻略
                for guide in items:
                    guide_id = guide.get('id')
                    title = guide.get('title', '')
                    products = guide.get('products', [])
                    
                    # 为每个关联的产品更新攻略信息
                    guide_url = f'https://lazycat.cloud/playground/guideline/{guide_id}'
                    
                    for product_name in products:
                        # 先尝试通过 package_name (href) 精确匹配
                        cursor.execute(
                            'SELECT id, name FROM apps WHERE href LIKE ?',
                            (f'%{product_name}%',)
                        )
                        exact_matches = cursor.fetchall()
                        
                        if exact_matches:
                            # 精确匹配到的应用
                            for app_id, app_name in exact_matches:
                                # 检查是否已有攻略URL，如果有就追加，没有就设置
                                cursor.execute('SELECT guide_url FROM apps WHERE id = ?', (app_id,))
                                current_url = cursor.fetchone()[0]
                                
                                if current_url and guide_url not in current_url:
                                    # 追加新的攻略URL
                                    new_guide_url = current_url + '|' + guide_url
                                else:
                                    # 设置新的攻略URL
                                    new_guide_url = guide_url
                                
                                cursor.execute(
                                    'UPDATE apps SET has_guide = 1, guide_url = ?, pending_guide = 0 WHERE id = ?',
                                    (new_guide_url, app_id)
                                )
                                if cursor.rowcount > 0:
                                    updated_count += 1
                                    print(f"  更新应用: {app_name} (ID: {app_id}) -> {guide_url}")
                        else:
                            # 如果没有精确匹配，尝试通过应用名称模糊匹配
                            cursor.execute(
                                'SELECT id, name FROM apps WHERE name LIKE ? OR name LIKE ?',
                                (f'%{product_name}%', f'%{title}%')
                            )
                            fuzzy_matches = cursor.fetchall()
                            
                            if fuzzy_matches:
                                # 选择最相似的一个（通常是第一个）
                                app_id, app_name = fuzzy_matches[0]
                                
                                # 检查是否已有攻略URL，如果有就追加，没有就设置
                                cursor.execute('SELECT guide_url FROM apps WHERE id = ?', (app_id,))
                                current_url = cursor.fetchone()[0]
                                
                                if current_url and guide_url not in current_url:
                                    # 追加新的攻略URL
                                    new_guide_url = current_url + '|' + guide_url
                                else:
                                    # 设置新的攻略URL
                                    new_guide_url = guide_url
                                
                                cursor.execute(
                                    'UPDATE apps SET has_guide = 1, guide_url = ?, pending_guide = 0 WHERE id = ?',
                                    (new_guide_url, app_id)
                                )
                                if cursor.rowcount > 0:
                                    updated_count += 1
                                    print(f"  模糊匹配更新应用: {app_name} (ID: {app_id}) <- {product_name} -> {guide_url}")
                
                total_guides += len(items)
                
                # 检查是否还有更多页
                if len(items) < size:
                    break
                
                page += 1
            
            conn.commit()
            
            # 获取更新后的统计信息
            stats = self.get_guide_statistics()
            
            return {
                'total_apps': stats['total_apps'],
                'apps_with_guides': stats['apps_with_guides'],
                'apps_without_guides': stats['apps_without_guides'],
                'apps_pending_guides': stats['apps_pending_guides'],
                'apps_skipped_guides': stats['apps_skipped_guides'],
                'updated_count': updated_count,
                'inserted_count': inserted_count,
                'total_guides_fetched': total_guides,
                'message': f'攻略更新完成！共获取 {total_guides} 个攻略，更新了 {updated_count} 个应用的攻略状态'
            }
            
        except requests.RequestException as e:
            conn.rollback()
            return {
                'success': False,
                'message': f'网络请求失败: {str(e)}'
            }
        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'message': f'更新失败: {str(e)}'
            }
        finally:
            conn.close()
    
    def get_next_custom_id(self):
        """获取下一个自定义ID（从1000000开始，避免与官方ID冲突）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查找最大的自定义ID
        cursor.execute('SELECT MAX(id) FROM apps WHERE id >= 1000000')
        max_custom_id = cursor.fetchone()[0]
        
        conn.close()
        
        if max_custom_id is None:
            return 1000000  # 从1000000开始
        else:
            return max_custom_id + 1
    
    def batch_add_missing_apps(self, app_names):
        """批量添加缺失的应用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        added_apps = []
        skipped_apps = []
        
        # 获取起始自定义ID
        cursor.execute('SELECT MAX(id) FROM apps WHERE id >= 1000000')
        max_custom_id = cursor.fetchone()[0]
        next_id = 1000000 if max_custom_id is None else max_custom_id + 1
        
        for app_name in app_names:
            app_name = app_name.strip()
            if not app_name:
                continue
            
            # 检查应用是否已存在
            cursor.execute('SELECT id FROM apps WHERE name = ?', (app_name,))
            existing = cursor.fetchone()
            
            if existing:
                skipped_apps.append(app_name)
                continue
            
            # 插入新应用
            cursor.execute('''
                INSERT INTO apps (id, name, brief, count, href, icon_src)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (next_id, app_name, '暂不适合', 0, '', ''))
            
            added_apps.append((next_id, app_name))
            next_id += 1  # 递增ID
        
        conn.commit()
        conn.close()
        
        return {
            'added': added_apps,
            'skipped': skipped_apps,
            'total_added': len(added_apps),
            'total_skipped': len(skipped_apps)
        }

    def import_excel_csv(self, file_path):
        """
        导入Excel或CSV文件到数据库
        支持插入新数据和更新现有数据
        """
        if not os.path.exists(file_path):
            return {
                'success': False,
                'message': f'文件不存在: {file_path}',
                'stats': {}
            }
        
        try:
            # 根据文件扩展名读取文件
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                # 读取Excel文件
                df = pd.read_excel(file_path)
            elif file_ext == '.csv':
                # 读取CSV文件，尝试不同编码
                encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
                df = None
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    return {
                        'success': False,
                        'message': '无法读取CSV文件，编码问题',
                        'stats': {}
                    }
            else:
                return {
                    'success': False,
                    'message': f'不支持的文件格式: {file_ext}',
                    'stats': {}
                }
            
            # 标准化列名映射
            column_mapping = {
                'name': ['name', '名称', '应用名称', '应用名'],
                'brief': ['brief', '简介', '描述', '说明', 'description'],
                'count': ['count', '下载量', '下载数', 'downloads'],
                'href': ['href', 'url', '链接', 'link', 'tablescraper-selected-row href'],
                'icon_src': ['icon_src', 'icon', '图标', 'icon src']
            }
            
            # 查找实际的列名
            actual_columns = {}
            for standard_name, possible_names in column_mapping.items():
                for col in df.columns:
                    if col.lower() in [name.lower() for name in possible_names]:
                        actual_columns[standard_name] = col
                        break
            
            # 检查必需的列（至少需要name列）
            if 'name' not in actual_columns:
                return {
                    'success': False,
                    'message': '文件中未找到应用名称列（name, 名称, 应用名称等）',
                    'stats': {}
                }
            
            # 处理数据
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {
                'total_rows': len(df),
                'inserted': 0,
                'updated': 0,
                'skipped': 0,
                'errors': []
            }
            
            for index, row in df.iterrows():
                try:
                    # 获取应用名称
                    name = str(row[actual_columns['name']]).strip()
                    if not name or name.lower() in ['nan', 'none', '']:
                        stats['skipped'] += 1
                        continue
                    
                    # 获取其他字段
                    brief = ''
                    if 'brief' in actual_columns:
                        brief = str(row[actual_columns['brief']]).strip()
                        if brief.lower() in ['nan', 'none']:
                            brief = ''
                    
                    count = 0
                    if 'count' in actual_columns:
                        count_val = row[actual_columns['count']]
                        if pd.notna(count_val):
                            count = self._parse_count(str(count_val))
                    
                    href = ''
                    if 'href' in actual_columns:
                        href = str(row[actual_columns['href']]).strip()
                        if href.lower() in ['nan', 'none']:
                            href = ''
                    
                    icon_src = ''
                    if 'icon_src' in actual_columns:
                        icon_src = str(row[actual_columns['icon_src']]).strip()
                        if icon_src.lower() in ['nan', 'none']:
                            icon_src = ''
                    
                    # 检查应用是否已存在
                    cursor.execute('SELECT id FROM apps WHERE name = ?', (name,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        # 更新现有应用
                        update_fields = []
                        update_params = []
                        
                        if brief:
                            update_fields.append('brief = ?')
                            update_params.append(brief)
                        if count > 0:
                            update_fields.append('count = ?')
                            update_params.append(count)
                        if href:
                            update_fields.append('href = ?')
                            update_params.append(href)
                        if icon_src:
                            update_fields.append('icon_src = ?')
                            update_params.append(icon_src)
                        
                        if update_fields:
                            update_fields.append('updated_at = CURRENT_TIMESTAMP')
                            update_params.append(existing[0])
                            
                            sql = f"UPDATE apps SET {', '.join(update_fields)} WHERE id = ?"
                            cursor.execute(sql, update_params)
                            stats['updated'] += 1
                        else:
                            stats['skipped'] += 1
                    else:
                        # 插入新应用
                        cursor.execute('''
                            INSERT INTO apps (name, brief, count, href, icon_src)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (name, brief, count, href, icon_src))
                        stats['inserted'] += 1
                
                except Exception as e:
                    stats['errors'].append(f"第{index+2}行错误: {str(e)}")
                    stats['skipped'] += 1
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f'导入完成！插入 {stats["inserted"]} 个，更新 {stats["updated"]} 个',
                'stats': stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'导入过程中出错: {str(e)}',
                'stats': {}
            }
    
    # GitHub候选应用相关方法
    def add_github_candidate(self, repo_info, evaluation_result=None):
        """添加GitHub候选应用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 准备topics字符串
            topics_str = ','.join(repo_info.get('topics', []))
            
            cursor.execute('''
                INSERT OR REPLACE INTO github_candidates 
                (repo_name, repo_full_name, description, url, stars, forks, language, 
                 topics, license, size_kb, open_issues, created_at, updated_at,
                 priority_score, priority_level, effort_estimation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                repo_info.get('name', ''),
                repo_info.get('full_name', ''),
                repo_info.get('description', ''),
                repo_info.get('url', ''),
                repo_info.get('stars', 0),
                repo_info.get('forks', 0),
                repo_info.get('language', ''),
                topics_str,
                repo_info.get('license'),
                repo_info.get('size', 0),
                repo_info.get('open_issues', 0),
                repo_info.get('created_at', ''),
                repo_info.get('updated_at', ''),
                evaluation_result.migration_score.total_score if evaluation_result else 0.0,
                evaluation_result.migration_score.priority_level if evaluation_result else '',
                evaluation_result.effort_estimation if evaluation_result else ''
            ))
            
            candidate_id = cursor.lastrowid
            
            # 如果有Docker分析结果，也保存
            if evaluation_result and evaluation_result.docker_analysis:
                docker_analysis = evaluation_result.docker_analysis
                self._save_docker_analysis(cursor, candidate_id, docker_analysis)
            
            conn.commit()
            print(f"✅ 添加GitHub候选应用: {repo_info.get('full_name', '')} (ID: {candidate_id})")
            return candidate_id
            
        except Exception as e:
            print(f"❌ 添加GitHub候选应用失败: {e}")
            return None
        finally:
            conn.close()
    
    def _save_docker_analysis(self, cursor, candidate_id, docker_analysis):
        """保存Docker分析结果"""
        cursor.execute('''
            INSERT OR REPLACE INTO docker_analysis
            (candidate_id, services_count, total_ports, exposed_ports, complexity_level,
             complexity_score, requires_build, external_dependencies, storage_requirements,
             network_requirements, deployment_notes, migration_warnings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            candidate_id,
            docker_analysis.services_count,
            docker_analysis.total_ports,
            ','.join(map(str, docker_analysis.exposed_ports)),
            docker_analysis.complexity_level,
            docker_analysis.complexity_score,
            1 if docker_analysis.requires_build else 0,
            '|'.join(docker_analysis.external_dependencies),
            '|'.join(docker_analysis.storage_requirements),
            '|'.join(docker_analysis.network_requirements),
            '|'.join(docker_analysis.deployment_notes),
            '|'.join(docker_analysis.migration_warnings)
        ))
    
    def batch_add_github_candidates(self, evaluations):
        """批量添加GitHub候选应用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        added_count = 0
        updated_count = 0
        
        try:
            for evaluation in evaluations:
                repo_info = {
                    'name': evaluation.repo_name.split('/')[-1] if '/' in evaluation.repo_name else evaluation.repo_name,
                    'full_name': evaluation.repo_name,
                    'description': evaluation.description,
                    'url': evaluation.repo_url,
                    'stars': evaluation.github_metrics.stars,
                    'forks': evaluation.github_metrics.forks,
                    'language': evaluation.github_metrics.language,
                    'topics': evaluation.github_metrics.topics,
                    'license': evaluation.github_metrics.license,
                    'size': evaluation.github_metrics.size,
                    'open_issues': evaluation.github_metrics.open_issues,
                    'created_at': evaluation.github_metrics.created_at,
                    'updated_at': evaluation.github_metrics.updated_at
                }
                
                # 检查是否已存在
                cursor.execute('SELECT id FROM github_candidates WHERE repo_full_name = ?', (evaluation.repo_name,))
                existing = cursor.fetchone()
                
                candidate_id = self.add_github_candidate(repo_info, evaluation)
                if candidate_id:
                    if existing:
                        updated_count += 1
                    else:
                        added_count += 1
            
            print(f"✅ 批量处理完成: 添加 {added_count} 个，更新 {updated_count} 个GitHub候选应用")
            return {'added': added_count, 'updated': updated_count}
            
        except Exception as e:
            print(f"❌ 批量添加GitHub候选应用失败: {e}")
            return {'added': 0, 'updated': 0}
        finally:
            conn.close()
    
    def get_github_candidates(self, limit=50, offset=0, sort_by='priority_score', 
                            filter_suitable=True, min_stars=0):
        """获取GitHub候选应用列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if filter_suitable:
            where_conditions.append('gc.is_suitable = 1')
        
        if min_stars > 0:
            where_conditions.append('gc.stars >= ?')
            params.append(min_stars)
        
        where_clause = 'WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
        
        # 排序选项
        sort_options = {
            'priority_score': 'gc.priority_score DESC',
            'stars': 'gc.stars DESC',
            'updated_at': 'gc.updated_at DESC',
            'name': 'gc.repo_name ASC'
        }
        order_by = sort_options.get(sort_by, sort_options['priority_score'])
        
        # 主查询
        query = f'''
            SELECT gc.id, gc.repo_name, gc.repo_full_name, gc.description, gc.url,
                   gc.stars, gc.forks, gc.language, gc.topics, gc.license,
                   gc.priority_score, gc.priority_level, gc.effort_estimation,
                   gc.is_suitable, gc.last_analysis,
                   da.complexity_level, da.complexity_score, da.services_count,
                   da.total_ports, da.requires_build
            FROM github_candidates gc
            LEFT JOIN docker_analysis da ON gc.id = da.candidate_id
            {where_clause}
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
        '''
        
        params.extend([limit, offset])
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # 获取总数
        count_query = f'''
            SELECT COUNT(*)
            FROM github_candidates gc
            {where_clause}
        '''
        cursor.execute(count_query, params[:-2])  # 排除limit和offset参数
        total = cursor.fetchone()[0]
        
        conn.close()
        return results, total
    
    def get_github_candidate_by_id(self, candidate_id):
        """根据ID获取GitHub候选应用详情"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gc.*, da.services_count, da.total_ports, da.exposed_ports,
                   da.complexity_level, da.complexity_score, da.requires_build,
                   da.external_dependencies, da.storage_requirements,
                   da.network_requirements, da.deployment_notes, da.migration_warnings
            FROM github_candidates gc
            LEFT JOIN docker_analysis da ON gc.id = da.candidate_id
            WHERE gc.id = ?
        ''', (candidate_id,))
        
        result = cursor.fetchone()
        conn.close()
        return result
    
    def mark_github_candidate_suitable(self, candidate_id, is_suitable=True, notes=''):
        """标记GitHub候选应用是否适合移植"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE github_candidates 
            SET is_suitable = ?, notes = ?
            WHERE id = ?
        ''', (1 if is_suitable else 0, notes, candidate_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_github_statistics(self):
        """获取GitHub候选应用统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总候选应用数
        cursor.execute('SELECT COUNT(*) FROM github_candidates')
        total_candidates = cursor.fetchone()[0]
        
        # 适合移植的应用数
        cursor.execute('SELECT COUNT(*) FROM github_candidates WHERE is_suitable = 1')
        suitable_candidates = cursor.fetchone()[0]
        
        # 按优先级分组统计
        cursor.execute('''
            SELECT priority_level, COUNT(*) 
            FROM github_candidates 
            WHERE is_suitable = 1 AND priority_level IS NOT NULL
            GROUP BY priority_level
        ''')
        priority_stats = dict(cursor.fetchall())
        
        # 按语言分组统计（Top 5）
        cursor.execute('''
            SELECT language, COUNT(*) 
            FROM github_candidates 
            WHERE is_suitable = 1 AND language IS NOT NULL
            GROUP BY language
            ORDER BY COUNT(*) DESC
            LIMIT 5
        ''')
        language_stats = cursor.fetchall()
        
        # 平均Stars数
        cursor.execute('''
            SELECT AVG(stars) 
            FROM github_candidates 
            WHERE is_suitable = 1
        ''')
        avg_stars = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_candidates': total_candidates,
            'suitable_candidates': suitable_candidates,
            'priority_stats': priority_stats,
            'language_stats': language_stats,
            'avg_stars': round(avg_stars, 1)
        }

def main():
    """主函数 - 初始化数据库并导入数据"""
    print("🚀 懒猫应用商店数据库管理器")
    print("=" * 50)
    
    db = DatabaseManager()
    
    # 导入CSV数据
    if db.import_csv_data():
        # 显示统计信息
        stats = db.get_statistics()
        print(f"\n📈 数据库统计信息:")
        print(f"   总应用数: {stats['total_apps']}")
        print(f"   有下载量的应用: {stats['apps_with_downloads']}")
        print(f"   平均下载量: {stats['avg_downloads']}")
        print(f"   最高下载量: {stats['max_downloads']}")
        
        print(f"\n🏆 最受欢迎的应用 (Top 5):")
        for i, (name, count) in enumerate(stats['top_apps'][:5], 1):
            print(f"   {i}. {name} ({count:,} 下载)")
        
        print(f"\n✅ 数据库准备完成，可以启动Web界面了！")
    else:
        print("❌ 数据导入失败")

if __name__ == "__main__":
    main()