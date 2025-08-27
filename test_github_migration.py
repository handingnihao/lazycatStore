#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub应用移植系统测试脚本
测试所有组件的功能
"""

import sys
import os
import traceback
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("📦 测试模块导入...")
    
    try:
        from github_app_finder import GitHubAppFinder
        print("  ✅ GitHubAppFinder 导入成功")
    except ImportError as e:
        print(f"  ❌ GitHubAppFinder 导入失败: {e}")
        return False
    
    try:
        from docker_compose_analyzer import DockerComposeAnalyzer
        print("  ✅ DockerComposeAnalyzer 导入成功")
    except ImportError as e:
        print(f"  ❌ DockerComposeAnalyzer 导入失败: {e}")
        return False
    
    try:
        from migration_evaluator import MigrationEvaluator
        print("  ✅ MigrationEvaluator 导入成功")
    except ImportError as e:
        print(f"  ❌ MigrationEvaluator 导入失败: {e}")
        return False
    
    try:
        from database_manager import DatabaseManager
        print("  ✅ DatabaseManager 导入成功")
    except ImportError as e:
        print(f"  ❌ DatabaseManager 导入失败: {e}")
        return False
    
    return True

def test_database():
    """测试数据库功能"""
    print("\n🗄️ 测试数据库功能...")
    
    try:
        from database_manager import DatabaseManager
        db = DatabaseManager('test_lazycat.db')
        
        # 测试GitHub表是否创建成功
        import sqlite3
        conn = sqlite3.connect('test_lazycat.db')
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='github_candidates'")
        if cursor.fetchone():
            print("  ✅ GitHub候选应用表创建成功")
        else:
            print("  ❌ GitHub候选应用表创建失败")
            return False
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='docker_analysis'")
        if cursor.fetchone():
            print("  ✅ Docker分析表创建成功")
        else:
            print("  ❌ Docker分析表创建失败")
            return False
        
        conn.close()
        
        # 清理测试数据库
        try:
            os.remove('test_lazycat.db')
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"  ❌ 数据库测试失败: {e}")
        return False

def test_docker_analyzer():
    """测试Docker分析器"""
    print("\n🐳 测试Docker Compose分析器...")
    
    try:
        from docker_compose_analyzer import DockerComposeAnalyzer
        
        analyzer = DockerComposeAnalyzer()
        
        # 测试用的docker-compose.yml内容
        test_compose = """
version: '3.8'
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./data:/usr/share/nginx/html
    restart: unless-stopped
  
  app:
    build:
      context: .
    environment:
      - NODE_ENV=production
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
"""
        
        analysis = analyzer.analyze_docker_compose(test_compose)
        
        print(f"  ✅ 成功分析Docker Compose配置")
        print(f"     服务数量: {analysis.services_count}")
        print(f"     复杂度: {analysis.complexity_level} ({analysis.complexity_score}/100)")
        print(f"     端口数量: {analysis.total_ports}")
        print(f"     需要构建: {analysis.requires_build}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Docker分析器测试失败: {e}")
        print(f"     错误详情: {traceback.format_exc()}")
        return False

def test_migration_evaluator():
    """测试移植评估器"""
    print("\n⚖️ 测试移植评估器...")
    
    try:
        from migration_evaluator import MigrationEvaluator
        
        evaluator = MigrationEvaluator()
        
        # 模拟GitHub仓库数据
        test_repo = {
            'full_name': 'test/awesome-app',
            'name': 'awesome-app', 
            'description': 'An awesome self-hosted productivity application',
            'url': 'https://github.com/test/awesome-app',
            'stars': 1500,
            'forks': 300,
            'open_issues': 25,
            'created_at': '2022-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
            'language': 'JavaScript',
            'topics': ['productivity', 'self-hosted', 'web'],
            'license': 'MIT',
            'size': 2048
        }
        
        # 测试用的docker-compose内容
        test_compose = """
version: '3.8'
services:
  app:
    image: node:16-alpine
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    volumes:
      - ./data:/app/data
"""
        
        evaluation = evaluator.evaluate_migration(test_repo, test_compose)
        
        print(f"  ✅ 成功评估移植优先级")
        print(f"     应用: {evaluation.repo_name}")
        print(f"     总分: {evaluation.migration_score.total_score:.1f}/100")
        print(f"     优先级: {evaluation.migration_score.priority_level}")
        print(f"     工作量预估: {evaluation.effort_estimation}")
        print(f"     相似应用数: {len(evaluation.existing_similar_apps)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 移植评估器测试失败: {e}")
        print(f"     错误详情: {traceback.format_exc()}")
        return False

def test_github_finder():
    """测试GitHub搜索器（不使用真实API）"""
    print("\n🔍 测试GitHub搜索器...")
    
    try:
        from github_app_finder import GitHubAppFinder
        
        # 不使用token创建搜索器
        finder = GitHubAppFinder()
        
        print("  ✅ GitHub搜索器创建成功")
        print("  ℹ️ 需要设置GITHUB_TOKEN环境变量才能进行实际搜索")
        
        # 测试内部方法
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
        
        processed = finder._process_repo_info(test_item)
        if processed:
            print("  ✅ 仓库信息处理功能正常")
            print(f"     处理结果: {processed['name']} ({processed['stars']} stars)")
        else:
            print("  ❌ 仓库信息处理失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ GitHub搜索器测试失败: {e}")
        print(f"     错误详情: {traceback.format_exc()}")
        return False

def test_web_app_imports():
    """测试Web应用导入"""
    print("\n🌐 测试Web应用导入...")
    
    try:
        from web_app import app
        print("  ✅ Flask应用创建成功")
        
        # 检查新路由是否存在
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        expected_routes = [
            '/github_search',
            '/migration_finder', 
            '/migration_candidates',
            '/migration_report',
            '/api/github_search',
            '/api/evaluate_migration'
        ]
        
        missing_routes = []
        for route in expected_routes:
            if route in routes:
                print(f"  ✅ 路由 {route} 已注册")
            else:
                missing_routes.append(route)
                print(f"  ❌ 路由 {route} 缺失")
        
        if missing_routes:
            print(f"  ❌ 有 {len(missing_routes)} 个路由缺失")
            return False
        else:
            print("  ✅ 所有GitHub相关路由都已注册")
            return True
        
    except Exception as e:
        print(f"  ❌ Web应用测试失败: {e}")
        print(f"     错误详情: {traceback.format_exc()}")
        return False

def run_comprehensive_test():
    """运行综合测试"""
    print("🚀 开始GitHub移植系统综合测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("模块导入", test_imports),
        ("数据库功能", test_database),
        ("Docker分析器", test_docker_analyzer),
        ("移植评估器", test_migration_evaluator),
        ("GitHub搜索器", test_github_finder),
        ("Web应用", test_web_app_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统准备就绪")
        print("\n🔧 使用说明:")
        print("1. 设置GITHUB_TOKEN环境变量（用于访问GitHub API）")
        print("2. 运行 python web_app.py 启动Web界面")  
        print("3. 访问 http://localhost:5000/github_search 开始搜索")
        return True
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
        return False

def show_feature_summary():
    """显示功能总结"""
    print("\n🌟 GitHub移植系统功能总结")
    print("=" * 60)
    
    features = [
        ("🔍 GitHub应用搜索", "搜索包含docker-compose.yml的GitHub仓库"),
        ("🐳 Docker配置分析", "自动分析部署复杂度和技术要求"),
        ("⚖️ 移植优先级评估", "综合评估应用的移植价值和难度"),
        ("🗄️ 候选应用管理", "保存和管理移植候选应用"),
        ("📊 移植报告生成", "生成详细的移植优先级报告"),
        ("🌐 可视化Web界面", "直观的操作界面和结果展示"),
        ("📈 统计分析功能", "移植进度和成果统计"),
        ("🔄 数据库集成", "与现有懒猫应用数据库无缝集成")
    ]
    
    for feature, description in features:
        print(f"{feature}: {description}")
    
    print("\n📋 新增页面:")
    print("• /github_search - GitHub应用搜索")
    print("• /migration_finder - 移植应用查找")
    print("• /migration_candidates - 移植候选应用")
    print("• /migration_report - 移植优先级报告")

if __name__ == "__main__":
    success = run_comprehensive_test()
    show_feature_summary()
    
    if success:
        print(f"\n✨ 恭喜天天！GitHub移植系统开发完成")
        print("现在你可以方便地找到适合移植到懒猫微服的优质应用了！")
    else:
        print(f"\n⚠️ 系统测试未完全通过，请检查上述错误")
    
    sys.exit(0 if success else 1)