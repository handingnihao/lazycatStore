#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
懒猫应用商店GitHub Star数据抓取器
从应用详情API获取源码信息并抓取GitHub star数据
"""

import sqlite3
import requests
import json
import time
import re
import os
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置常量
BATCH_SIZE = 20  # 每批处理20个应用
REQUEST_DELAY = 0.5  # 请求间隔500ms
GITHUB_API_DELAY = 1  # GitHub API间隔1秒
TIMEOUT = 10  # 请求超时时间
MAX_RETRIES = 3  # 最大重试次数

class GitHubStarFetcher:
    def __init__(self, db_path='lazycat_apps.db'):
        self.db_path = db_path
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.session = requests.Session()
        
        # 设置GitHub API请求头
        if self.github_token:
            self.session.headers.update({
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            })
            print("✅ GitHub Token配置成功")
        else:
            print("⚠️  未检测到GitHub Token，将使用匿名访问（限制较严）")
        
        # 统计信息
        self.stats = {
            'total_processed': 0,
            'success': 0,
            'failed': 0,
            'github_found': 0,
            'stars_fetched': 0,
            'errors': []
        }
    
    def extract_package_from_href(self, href):
        """从href链接提取package名称"""
        if not href:
            return None
        
        # 匹配格式: https://lazycat.cloud/appstore/detail/{package}
        match = re.search(r'/detail/([^/]+)$', href)
        if match:
            return match.group(1)
        return None
    
    def fetch_app_detail(self, package_name):
        """获取应用详情JSON"""
        if not package_name:
            return None, "Package名称为空"
        
        url = f"https://dl.lazycat.cloud/appstore/metarepo/zh/v3/app_{package_name}.json"
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=TIMEOUT)
                if response.status_code == 200:
                    return response.json(), None
                elif response.status_code == 404:
                    return None, f"应用详情不存在: {package_name}"
                else:
                    return None, f"HTTP错误: {response.status_code}"
            except requests.exceptions.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    return None, f"网络请求失败: {str(e)}"
                time.sleep(REQUEST_DELAY * (attempt + 1))
        
        return None, "获取失败"
    
    def parse_github_source(self, source):
        """解析GitHub源信息"""
        if not source:
            return None, None, None
        
        # 识别GitHub URL格式
        github_patterns = [
            r'https?://github\.com/([^/]+)/([^/]+)/?',
            r'git@github\.com:([^/]+)/([^/]+)\.git',
            r'github\.com/([^/]+)/([^/]+)'
        ]
        
        for pattern in github_patterns:
            match = re.search(pattern, source)
            if match:
                owner = match.group(1)
                repo = match.group(2).rstrip('.git')
                return f"https://github.com/{owner}/{repo}", owner, repo
        
        return None, None, None
    
    def fetch_github_stars(self, owner, repo):
        """获取GitHub仓库的star数"""
        if not owner or not repo:
            return 0, "仓库信息不完整"
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(api_url, timeout=TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    return data.get('stargazers_count', 0), None
                elif response.status_code == 404:
                    return 0, "仓库不存在或已删除"
                elif response.status_code == 403:
                    return 0, "GitHub API限制"
                else:
                    return 0, f"GitHub API错误: {response.status_code}"
            except requests.exceptions.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    return 0, f"GitHub API请求失败: {str(e)}"
                time.sleep(GITHUB_API_DELAY * (attempt + 1))
        
        return 0, "获取失败"
    
    def save_app_detail(self, app_id, package_name, detail_data, source_type, 
                       github_repo, github_owner, github_name, star_count, 
                       fetch_status, error_message=None):
        """保存应用详情到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 确保所有参数都是正确的类型
            version = str(detail_data.get('version', '')) if detail_data else ''
            # source字段在information对象中
            source = ''
            if detail_data and 'information' in detail_data:
                source = str(detail_data['information'].get('source', ''))
            json_data = json.dumps(detail_data, ensure_ascii=False) if detail_data else ''
            
            cursor.execute('''
                INSERT OR REPLACE INTO app_details 
                (app_id, package_name, version, source, source_type, github_repo,
                 github_owner, github_name, star_count, json_data, fetch_status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                app_id,
                str(package_name) if package_name else '',
                version,
                source,
                str(source_type) if source_type else 'unknown',
                str(github_repo) if github_repo else None,
                str(github_owner) if github_owner else None,
                str(github_name) if github_name else None,
                int(star_count) if star_count else 0,
                json_data,
                str(fetch_status) if fetch_status else 'unknown',
                str(error_message) if error_message else None
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ 保存数据库失败: {str(e)}")
            return False
        finally:
            conn.close()
    
    def process_single_app(self, app_id, name, href):
        """处理单个应用"""
        print(f"🔄 处理应用: {name} (ID: {app_id})")
        
        # 提取package名称
        package_name = self.extract_package_from_href(href)
        if not package_name:
            error_msg = "无法从href提取package名称"
            print(f"  ❌ {error_msg}")
            self.save_app_detail(app_id, '', None, 'error', None, None, None, 0, 'failed', error_msg)
            self.stats['failed'] += 1
            return
        
        print(f"  📦 Package: {package_name}")
        
        # 获取应用详情
        detail_data, error = self.fetch_app_detail(package_name)
        if error:
            print(f"  ❌ 获取详情失败: {error}")
            self.save_app_detail(app_id, package_name, None, 'error', None, None, None, 0, 'failed', error)
            self.stats['failed'] += 1
            return
        
        time.sleep(REQUEST_DELAY)
        
        # 获取源码信息 - source字段在information对象中
        source = ''
        if 'information' in detail_data:
            source = detail_data['information'].get('source', '')
        print(f"  🔗 源码: {source}")
        
        # 解析GitHub信息
        github_repo, github_owner, github_name = self.parse_github_source(source)
        source_type = 'github' if github_repo else ('lazycat' if 'lazycat' in source.lower() else 'other')
        
        star_count = 0
        fetch_status = 'success'
        error_message = None
        
        # 如果是GitHub源，获取star数
        if github_repo:
            print(f"  ⭐ GitHub仓库: {github_owner}/{github_name}")
            star_count, star_error = self.fetch_github_stars(github_owner, github_name)
            
            if star_error:
                print(f"  ⚠️  获取star失败: {star_error}")
                error_message = star_error
            else:
                print(f"  ✅ Star数: {star_count}")
                self.stats['stars_fetched'] += 1
            
            self.stats['github_found'] += 1
            time.sleep(GITHUB_API_DELAY)
        
        # 保存到数据库
        if self.save_app_detail(app_id, package_name, detail_data, source_type,
                               github_repo, github_owner, github_name, star_count,
                               fetch_status, error_message):
            self.stats['success'] += 1
            print(f"  ✅ 保存成功")
        else:
            self.stats['failed'] += 1
            print(f"  ❌ 保存失败")
        
        self.stats['total_processed'] += 1
    
    def get_pending_apps(self, limit=BATCH_SIZE):
        """获取待处理的应用列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查询还未处理的应用（不重复抓取）
        cursor.execute('''
            SELECT a.id, a.name, a.href 
            FROM apps a 
            LEFT JOIN app_details ad ON a.id = ad.app_id 
            WHERE ad.app_id IS NULL 
            ORDER BY a.count DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_total_pending(self):
        """获取待处理应用总数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) 
            FROM apps a 
            LEFT JOIN app_details ad ON a.id = ad.app_id 
            WHERE ad.app_id IS NULL
        ''')
        
        total = cursor.fetchone()[0]
        conn.close()
        return total
    
    def print_progress(self, batch_num, total_batches):
        """打印进度信息"""
        print(f"\n📊 批次 {batch_num}/{total_batches} 完成")
        print(f"  总处理: {self.stats['total_processed']}")
        print(f"  成功: {self.stats['success']}")
        print(f"  失败: {self.stats['failed']}")
        print(f"  GitHub源: {self.stats['github_found']}")
        print(f"  获取star: {self.stats['stars_fetched']}")
        print("-" * 50)
    
    def print_final_report(self):
        """打印最终统计报告"""
        print("\n" + "=" * 60)
        print("🎯 GitHub Star抓取完成!")
        print("=" * 60)
        print(f"📊 总处理应用数: {self.stats['total_processed']}")
        print(f"✅ 成功处理: {self.stats['success']}")
        print(f"❌ 失败处理: {self.stats['failed']}")
        print(f"🔗 GitHub源应用: {self.stats['github_found']}")
        print(f"⭐ 成功获取star: {self.stats['stars_fetched']}")
        
        if self.stats['github_found'] > 0:
            success_rate = (self.stats['stars_fetched'] / self.stats['github_found']) * 100
            print(f"📈 Star获取成功率: {success_rate:.1f}%")
        
        # 显示top star排行榜
        self.show_top_starred_apps()
    
    def show_top_starred_apps(self, limit=10):
        """显示star数最高的应用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.name, ad.github_repo, ad.star_count
            FROM apps a
            JOIN app_details ad ON a.id = ad.app_id
            WHERE ad.source_type = 'github' AND ad.star_count > 0
            ORDER BY ad.star_count DESC
            LIMIT ?
        ''', (limit,))
        
        top_apps = cursor.fetchall()
        conn.close()
        
        if top_apps:
            print(f"\n🏆 Top {len(top_apps)} GitHub应用 (按star数排序):")
            for i, (name, repo, stars) in enumerate(top_apps, 1):
                print(f"  {i:2d}. {name:<30} | {stars:>6} ⭐ | {repo}")
    
    def run_test_mode(self, test_count=5):
        """测试模式：处理少量数据"""
        print(f"🧪 测试模式：处理前{test_count}个应用")
        
        apps = self.get_pending_apps(test_count)
        if not apps:
            print("❌ 没有待处理的应用")
            return
        
        print(f"📋 找到 {len(apps)} 个待处理应用")
        
        for i, (app_id, name, href) in enumerate(apps, 1):
            print(f"\n[{i}/{len(apps)}] ", end="")
            self.process_single_app(app_id, name, href)
        
        self.print_final_report()
    
    def run_full_mode(self):
        """全量模式：处理所有应用"""
        total_pending = self.get_total_pending()
        if total_pending == 0:
            print("✅ 所有应用都已处理完成")
            return
        
        total_batches = (total_pending + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"🚀 开始全量处理：{total_pending}个应用，分{total_batches}批次处理")
        
        batch_num = 0
        while True:
            batch_num += 1
            apps = self.get_pending_apps(BATCH_SIZE)
            
            if not apps:
                break
            
            print(f"\n📦 批次 {batch_num}/{total_batches}: 处理{len(apps)}个应用")
            
            for i, (app_id, name, href) in enumerate(apps, 1):
                print(f"\n[{i}/{len(apps)}] ", end="")
                self.process_single_app(app_id, name, href)
            
            self.print_progress(batch_num, total_batches)
            
            # 批次间休息
            if batch_num < total_batches:
                print("😴 批次间休息2秒...")
                time.sleep(2)
        
        self.print_final_report()

def main():
    print("🚀 懒猫应用商店 GitHub Star 抓取器")
    print("=" * 50)
    
    fetcher = GitHubStarFetcher()
    
    # 检查待处理应用数
    total_pending = fetcher.get_total_pending()
    print(f"📊 待处理应用数: {total_pending}")
    
    if total_pending == 0:
        print("✅ 所有应用都已处理完成")
        fetcher.show_top_starred_apps()
        return
    
    # 用户选择处理模式
    print("\n选择处理模式:")
    print("1. 测试模式 (处理前5个应用)")
    print("2. 全量模式 (处理所有应用)")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == '1':
        fetcher.run_test_mode()
    elif choice == '2':
        fetcher.run_full_mode()
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()