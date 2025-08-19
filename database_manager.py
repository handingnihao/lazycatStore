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
    
    def search_apps(self, keyword='', limit=50, offset=0):
        """搜索应用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if keyword:
            cursor.execute('''
                SELECT id, name, brief, count, href, icon_src, created_at
                FROM apps
                WHERE name LIKE ? OR brief LIKE ?
                ORDER BY count DESC, name
                LIMIT ? OFFSET ?
            ''', (f'%{keyword}%', f'%{keyword}%', limit, offset))
        else:
            cursor.execute('''
                SELECT id, name, brief, count, href, icon_src, created_at
                FROM apps
                ORDER BY count DESC, name
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
    
    def get_apps_without_guides(self, limit: int = 50, offset: int = 0):
        """列出没有攻略的应用，支持分页，按下载量排序，排除被标记为暂时不写攻略的应用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取数据
        cursor.execute(
            '''
            SELECT id, name, brief, count, href, icon_src FROM apps
            WHERE (has_guide IS NULL OR has_guide = 0)
              AND (guide_url IS NULL OR guide_url = '')
              AND (skip_guide IS NULL OR skip_guide = 0)
              AND (pending_guide IS NULL OR pending_guide = 0)
            ORDER BY count DESC, name
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
    
    def get_pending_guide_apps(self, limit: int = 50, offset: int = 0):
        """获取待写攻略的应用列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取数据
        cursor.execute(
            '''
            SELECT id, name, brief, count, href, icon_src FROM apps
            WHERE pending_guide = 1
            ORDER BY count DESC, name
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