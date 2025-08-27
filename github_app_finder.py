#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub应用搜索引擎
用于搜索包含docker-compose.yml的GitHub仓库，专门为懒猫微服移植候选应用
"""

import requests
import time
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import base64

class GitHubAppFinder:
    def __init__(self, token: Optional[str] = None):
        """
        初始化GitHub搜索器
        :param token: GitHub Personal Access Token
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        
        self.base_url = 'https://api.github.com'
        self.search_cache = {}
        
    def search_docker_compose_apps(self, 
                                 keywords: List[str] = None,
                                 min_stars: int = 100,
                                 max_results: int = 100,
                                 languages: List[str] = None) -> List[Dict]:
        """
        搜索包含docker-compose.yml的GitHub仓库
        
        :param keywords: 搜索关键词列表
        :param min_stars: 最小Stars数量
        :param max_results: 最大结果数量
        :param languages: 编程语言过滤
        :return: 搜索结果列表
        """
        print(f"🔍 开始搜索Docker Compose应用...")
        
        # 使用更宽松的搜索策略
        if keywords:
            # 如果有关键词，搜索包含关键词和docker-compose的项目
            keyword_str = ' '.join(keywords)
            query = f'docker-compose {keyword_str} stars:>={min_stars}'
        else:
            # 否则搜索一般的docker-compose项目
            query = f'docker-compose stars:>={min_stars}'
        
        # 添加语言过滤
        if languages:
            for lang in languages:
                query += f' language:{lang}'
        
        print(f"📝 搜索查询: {query}")
        
        return self._execute_search(query, max_results)
    
    def search_by_category(self, category: str, max_results: int = 50) -> List[Dict]:
        """
        按应用类别搜索
        
        :param category: 应用类别
        :param max_results: 最大结果数量
        :return: 搜索结果列表
        """
        category_keywords = {
            'productivity': ['note', 'task', 'todo', 'productivity', 'workspace', 'collaboration'],
            'media': ['media', 'streaming', 'video', 'audio', 'music', 'player', 'plex'],
            'development': ['code', 'git', 'ci', 'deployment', 'development', 'devops'],
            'monitoring': ['monitoring', 'metrics', 'dashboard', 'observability', 'grafana'],
            'storage': ['storage', 'backup', 'sync', 'cloud', 'file', 'nextcloud'],
            'security': ['password', 'auth', 'security', 'vault', 'bitwarden'],
            'communication': ['chat', 'message', 'communication', 'mail', 'slack'],
            'database': ['database', 'db', 'mysql', 'postgres', 'mongodb', 'redis']
        }
        
        keywords = category_keywords.get(category.lower(), [category])
        return self.search_docker_compose_apps(keywords=keywords, max_results=max_results)
    
    def _execute_search(self, query: str, max_results: int) -> List[Dict]:
        """
        执行GitHub搜索
        """
        results = []
        page = 1
        per_page = min(100, max_results)  # GitHub API最大支持100
        
        while len(results) < max_results:
            try:
                url = f"{self.base_url}/search/repositories"
                params = {
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'page': page,
                    'per_page': per_page
                }
                
                print(f"📄 获取第{page}页结果...")
                response = self.session.get(url, params=params)
                
                if response.status_code == 403:
                    # 遇到速率限制
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    wait_time = reset_time - int(time.time()) + 1
                    if wait_time > 0:
                        print(f"⏳ 遇到速率限制，等待{wait_time}秒...")
                        time.sleep(wait_time)
                        continue
                
                response.raise_for_status()
                data = response.json()
                
                if not data.get('items'):
                    break
                
                # 处理搜索结果
                for item in data['items']:
                    if len(results) >= max_results:
                        break
                        
                    repo_info = self._process_repo_info(item)
                    if repo_info:
                        results.append(repo_info)
                
                page += 1
                
                # GitHub搜索API限制每次查询最多1000个结果
                if page > 10:  # 10页 * 100 = 1000
                    break
                    
                # 避免触发速率限制
                time.sleep(1)
                
            except requests.RequestException as e:
                print(f"❌ 搜索请求失败: {e}")
                break
        
        print(f"✅ 搜索完成，找到{len(results)}个仓库")
        return results
    
    def _process_repo_info(self, item: Dict) -> Optional[Dict]:
        """
        处理仓库信息
        """
        try:
            # 基本信息
            repo_info = {
                'id': item['id'],
                'name': item['name'],
                'full_name': item['full_name'],
                'description': item.get('description', ''),
                'url': item['html_url'],
                'clone_url': item['clone_url'],
                'stars': item['stargazers_count'],
                'forks': item['forks_count'],
                'language': item.get('language', 'Unknown'),
                'topics': item.get('topics', []),
                'created_at': item['created_at'],
                'updated_at': item['updated_at'],
                'size': item['size'],
                'open_issues': item['open_issues_count'],
                'license': item['license']['name'] if item.get('license') else None,
                'archived': item.get('archived', False),
                'disabled': item.get('disabled', False),
                'docker_compose_url': f"{item['html_url']}/blob/{item['default_branch']}/docker-compose.yml"
            }
            
            # 过滤掉已归档或禁用的仓库
            if repo_info['archived'] or repo_info['disabled']:
                return None
            
            return repo_info
            
        except KeyError as e:
            print(f"⚠️  处理仓库信息时缺少字段: {e}")
            return None
    
    def get_docker_compose_content(self, repo_full_name: str, branch: str = 'main') -> Optional[str]:
        """
        获取仓库的docker-compose.yml内容
        
        :param repo_full_name: 仓库全名 (owner/repo)
        :param branch: 分支名称
        :return: docker-compose.yml内容
        """
        try:
            # 尝试main分支
            for branch_name in ['main', 'master']:
                url = f"{self.base_url}/repos/{repo_full_name}/contents/docker-compose.yml"
                params = {'ref': branch_name}
                
                response = self.session.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    # Base64解码内容
                    content = base64.b64decode(data['content']).decode('utf-8')
                    return content
                elif response.status_code == 404:
                    continue  # 尝试下一个分支
                else:
                    response.raise_for_status()
            
            print(f"❌ 在仓库 {repo_full_name} 中未找到docker-compose.yml")
            return None
            
        except requests.RequestException as e:
            print(f"❌ 获取docker-compose.yml失败: {e}")
            return None
    
    def save_search_results(self, results: List[Dict], filename: str = None) -> str:
        """
        保存搜索结果到JSON文件
        
        :param results: 搜索结果
        :param filename: 文件名
        :return: 保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'github_search_results_{timestamp}.json'
        
        filepath = os.path.join(os.getcwd(), filename)
        
        # 添加元数据
        output_data = {
            'search_timestamp': datetime.now().isoformat(),
            'total_results': len(results),
            'results': results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 搜索结果已保存到: {filepath}")
        return filepath
    
    def get_trending_apps(self, time_range: str = 'weekly') -> List[Dict]:
        """
        获取趋势应用
        
        :param time_range: 时间范围 (daily, weekly, monthly)
        :return: 趋势应用列表
        """
        # GitHub Trending不是官方API的一部分，这里使用搜索API模拟
        if time_range == 'weekly':
            date_filter = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        elif time_range == 'monthly':
            date_filter = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        else:  # daily
            date_filter = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        query = f'filename:docker-compose.yml stars:>50 pushed:>={date_filter}'
        return self._execute_search(query, max_results=50)

def main():
    """
    测试函数
    """
    print("🔍 GitHub Docker Compose应用搜索器")
    print("=" * 50)
    
    # 创建搜索器实例
    finder = GitHubAppFinder()
    
    # 搜索生产力应用
    print("\n📝 搜索生产力应用...")
    productivity_apps = finder.search_by_category('productivity', max_results=10)
    
    print(f"\n✅ 找到 {len(productivity_apps)} 个生产力应用:")
    for app in productivity_apps[:5]:
        print(f"⭐ {app['full_name']} - {app['stars']} stars")
        print(f"   📝 {app['description'][:100]}...")
        print(f"   🔗 {app['url']}")
        print()
    
    # 保存结果
    if productivity_apps:
        filename = finder.save_search_results(productivity_apps, 'productivity_apps.json')
        print(f"💾 结果已保存到: {filename}")

if __name__ == '__main__':
    main()