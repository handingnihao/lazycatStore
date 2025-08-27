#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Token 设置助手
帮助用户快速设置和验证GitHub Token
"""

import os
import sys
import requests
import subprocess

def check_token_exists():
    """检查token是否已设置"""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            if 'GITHUB_TOKEN=' in content and 'your_github_token_here' not in content:
                return True
    return False

def setup_env_file():
    """设置.env文件"""
    print("🔧 设置GitHub Token...")
    
    if not os.path.exists('.env.example'):
        print("❌ .env.example文件不存在")
        return False
    
    # 复制示例文件
    if not os.path.exists('.env'):
        import shutil
        shutil.copy('.env.example', '.env')
        print("✅ 已创建.env配置文件")
    
    print("\n📝 接下来需要你手动编辑.env文件:")
    print("1. 打开.env文件")
    print("2. 将 'your_github_token_here' 替换为你的真实GitHub Token")
    print("3. 保存文件")
    
    return True

def test_token():
    """测试token是否有效"""
    # 加载.env文件
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    token = os.getenv('GITHUB_TOKEN')
    if not token or token == 'your_github_token_here':
        print("❌ Token尚未设置或仍为示例值")
        return False
    
    print(f"🔍 测试Token（长度: {len(token)}）...")
    
    try:
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Token有效! 用户: {user_info.get('login', 'Unknown')}")
            
            # 测试搜索API
            search_response = requests.get(
                'https://api.github.com/search/repositories',
                headers=headers,
                params={'q': 'filename:docker-compose.yml', 'per_page': 1},
                timeout=10
            )
            
            if search_response.status_code == 200:
                print("✅ 搜索API访问正常")
                return True
            else:
                print("⚠️ 搜索API访问异常")
                return False
        
        elif response.status_code == 401:
            print("❌ Token无效或已过期")
            return False
        else:
            print(f"⚠️ API访问异常: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 网络请求失败: {e}")
        return False

def start_web_app():
    """启动Web应用"""
    print("\n🚀 启动懒猫应用商店...")
    try:
        # 检查虚拟环境
        if 'venv' in sys.executable or 'VIRTUAL_ENV' in os.environ:
            print("✅ 检测到虚拟环境")
        else:
            print("⚠️ 建议在虚拟环境中运行")
        
        print("启动Web应用，请访问: http://localhost:5000/github_search")
        subprocess.run([sys.executable, 'web_app.py'])
        
    except KeyboardInterrupt:
        print("\n👋 Web应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("🎯 GitHub Token 设置助手")
    print("=" * 40)
    
    # 检查是否已设置
    if check_token_exists():
        print("✅ 检测到已配置的GitHub Token")
        
        if test_token():
            print("\n🎉 配置验证成功!")
            
            choice = input("\n是否启动Web应用? (y/n): ").lower().strip()
            if choice == 'y':
                start_web_app()
        else:
            print("\n❌ Token验证失败，请检查配置")
    else:
        print("ℹ️ 未检测到GitHub Token配置")
        
        print("\n📖 获取GitHub Token步骤:")
        print("1. 访问: https://github.com/settings/tokens")
        print("2. 点击 'Generate new token' -> 'Generate new token (classic)'")
        print("3. 设置名称: Lazycat-Migration-Tool")
        print("4. 勾选权限: public_repo")
        print("5. 生成并复制token")
        
        choice = input("\n已获取Token? 继续设置配置文件? (y/n): ").lower().strip()
        if choice == 'y':
            setup_env_file()
            print("\n⚠️ 请编辑.env文件设置你的Token，然后重新运行此脚本验证")

if __name__ == "__main__":
    main()