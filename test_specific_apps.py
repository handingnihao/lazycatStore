#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试GitHub搜索功能的具体问题
"""

import os
import sys
import requests
import json

def load_env_file():
    """加载.env文件中的环境变量"""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def test_github_api_access():
    """测试GitHub API访问"""
    print("🔍 测试GitHub API访问...")
    
    # 加载.env文件
    load_env_file()
    
    # 检查环境变量
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ 未设置GITHUB_TOKEN环境变量")
        print("📝 解决方案:")
        print("   1. 访问 https://github.com/settings/tokens")
        print("   2. 生成新的Personal Access Token")
        print("   3. 设置环境变量: export GITHUB_TOKEN=your_token")
        return False
    
    print(f"✅ GITHUB_TOKEN已设置 (长度: {len(token)})")
    
    # 测试API访问
    try:
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # 测试基本API访问
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ API访问成功, 用户: {user_info.get('login', 'Unknown')}")
        elif response.status_code == 401:
            print("❌ Token无效或已过期")
            return False
        else:
            print(f"⚠️ API访问异常: {response.status_code}")
            return False
        
        # 测试搜索API
        search_url = 'https://api.github.com/search/repositories'
        params = {
            'q': 'filename:docker-compose.yml stars:>100',
            'sort': 'stars',
            'order': 'desc',
            'page': 1,
            'per_page': 5
        }
        
        print("\n🔍 测试搜索API...")
        search_response = requests.get(search_url, headers=headers, params=params, timeout=30)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            total_count = search_data.get('total_count', 0)
            items = search_data.get('items', [])
            
            print(f"✅ 搜索成功! 找到 {total_count} 个仓库")
            print(f"📊 返回 {len(items)} 个结果:")
            
            for i, item in enumerate(items[:3], 1):
                print(f"   {i}. {item['full_name']} - {item['stargazers_count']} stars")
            
            return True
        else:
            print(f"❌ 搜索失败: {search_response.status_code}")
            if search_response.status_code == 403:
                print("   可能是API速率限制，请稍后再试")
            print(f"   错误信息: {search_response.text[:200]}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False

def test_local_search_function():
    """测试本地搜索功能"""
    print("\n🧪 测试本地搜索功能...")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from github_app_finder import GitHubAppFinder
        
        finder = GitHubAppFinder()
        
        # 模拟搜索 - 不使用真实API
        print("✅ GitHubAppFinder 初始化成功")
        
        # 测试内部函数
        test_item = {
            'id': 123,
            'name': 'test-app',
            'full_name': 'user/test-app',
            'description': 'A test application',
            'html_url': 'https://github.com/user/test-app',
            'clone_url': 'https://github.com/user/test-app.git',
            'stargazers_count': 100,
            'forks_count': 20,
            'language': 'JavaScript',
            'topics': ['test'],
            'created_at': '2023-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
            'size': 1024,
            'open_issues_count': 5,
            'license': {'name': 'MIT'},
            'default_branch': 'main',
            'archived': False,
            'disabled': False
        }
        
        result = finder._process_repo_info(test_item)
        if result:
            print("✅ 仓库信息处理正常")
            print(f"   处理结果: {result['name']} ({result['stars']} stars)")
        
        return True
        
    except Exception as e:
        print(f"❌ 本地功能测试失败: {e}")
        return False

def generate_setup_guide():
    """生成设置指南"""
    print("\n📖 GitHub Token 设置指南")
    print("=" * 50)
    
    print("步骤1: 生成GitHub Token")
    print("   1. 访问: https://github.com/settings/tokens")
    print("   2. 点击 'Generate new token' -> 'Generate new token (classic)'")
    print("   3. 设置Token名称: Lazycat-Migration-Tool")
    print("   4. 选择权限: 至少勾选 'public_repo'")
    print("   5. 点击 'Generate token' 并复制Token")
    
    print("\n步骤2: 设置环境变量")
    print("   方法1 - 临时设置 (推荐测试用):")
    print("   export GITHUB_TOKEN=your_github_token_here")
    print("   source venv/bin/activate && python web_app.py")
    
    print("\n   方法2 - 创建.env文件:")
    print("   echo 'GITHUB_TOKEN=your_github_token_here' > .env")
    
    print("\n步骤3: 验证设置")
    print("   source venv/bin/activate")
    print("   python test_specific_apps.py")

if __name__ == "__main__":
    print("🚀 GitHub搜索问题诊断工具")
    print("=" * 50)
    
    api_success = test_github_api_access()
    local_success = test_local_search_function()
    
    print("\n" + "=" * 50)
    print("📊 诊断结果:")
    print(f"   GitHub API访问: {'✅ 正常' if api_success else '❌ 失败'}")
    print(f"   本地功能: {'✅ 正常' if local_success else '❌ 失败'}")
    
    if not api_success:
        generate_setup_guide()
    else:
        print("\n🎉 GitHub API访问正常!")
        print("💡 如果Web界面仍无结果，请检查:")
        print("   1. Flask应用是否在虚拟环境中运行")
        print("   2. 环境变量是否在Flask进程中生效")
        print("   3. 浏览器开发者工具中是否有错误信息")