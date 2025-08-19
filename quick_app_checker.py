#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速应用检查器 - 命令行版本
直接输出未匹配的应用，方便复制
"""

import csv
import re
from difflib import SequenceMatcher

class QuickAppChecker:
    def __init__(self):
        self.lazycat_apps = []
        self.load_lazycat_data()
    
    def load_lazycat_data(self):
        """加载懒猫应用商店数据"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        
        for encoding in encodings:
            try:
                with open('lazycat20250625.csv', 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    self.lazycat_apps = []
                    
                    for row in reader:
                        if row.get('name'):  # 确保有应用名称
                            self.lazycat_apps.append({
                                'name': row.get('name', '').strip(),
                                'brief': row.get('brief', '').strip(),
                                'count': row.get('count', '').strip()
                            })
                
                print(f"✅ 成功加载懒猫应用商店数据: {len(self.lazycat_apps)} 个应用 (编码: {encoding})")
                
                # 显示前几个应用名称以验证编码正确
                if self.lazycat_apps:
                    print("📝 前5个应用示例:")
                    for i, app in enumerate(self.lazycat_apps[:5]):
                        print(f"   {i+1}. {app['name']}")
                
                return True
                
            except (UnicodeDecodeError, FileNotFoundError) as e:
                if encoding == encodings[-1]:  # 最后一个编码也失败
                    print(f"❌ 所有编码尝试失败，最后错误：{str(e)}")
                    return False
                continue
            except Exception as e:
                print(f"❌ 加载数据时出错：{str(e)}")
                return False
        
        return False
    
    def normalize_name(self, name):
        """标准化应用名称"""
        if not name:
            return ""
        
        # 转换为小写
        name = name.lower().strip()
        
        # 移除常见的前缀和后缀
        prefixes = ['the ', 'a ', 'an ']
        suffixes = [' app', ' application', ' tool', ' service', ' platform', ' by gethomepage', ' by tomershvueli']
        
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
        
        # 移除特殊字符，只保留字母数字和空格
        name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        
        # 移除多余的空格
        name = ' '.join(name.split())
        
        return name
    
    def calculate_similarity(self, name1, name2):
        """计算两个名称的相似度"""
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        if not norm1 or not norm2:
            return 0.0
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def check_app_exists(self, app_name):
        """检查应用是否在懒猫商店中存在"""
        app_name = app_name.strip()
        if not app_name:
            return None
        
        best_match = None
        best_similarity = 0.0
        
        # 检查懒猫应用
        for lazycat_app in self.lazycat_apps:
            lazycat_name = lazycat_app.get('name', '')
            similarity = self.calculate_similarity(app_name, lazycat_name)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = lazycat_app
        
        return {
            'input_name': app_name,
            'similarity': best_similarity,
            'match': best_match,
            'exists': best_similarity >= 0.7  # 70%相似度认为存在
        }
    
    def batch_check(self, app_list):
        """批量检查应用"""
        results = []
        missing_apps = []
        existing_apps = []
        
        print(f"\n🔍 开始检查 {len(app_list)} 个应用...")
        print("=" * 60)
        
        for i, app_name in enumerate(app_list, 1):
            result = self.check_app_exists(app_name)
            if result:
                results.append(result)
                
                if result['exists']:
                    existing_apps.append(result)
                    status = "✅ 已存在"
                    match_info = f" (匹配: {result['match']['name']}, 相似度: {result['similarity']:.1%})"
                else:
                    missing_apps.append(result)
                    status = "❌ 不存在"
                    match_info = f" (最相似: {result['match']['name'] if result['match'] else 'N/A'}, 相似度: {result['similarity']:.1%})"
                
                print(f"{i:2d}. {app_name:<25} {status}{match_info}")
        
        # 输出统计结果
        print("\n" + "=" * 60)
        print(f"📊 检查结果统计:")
        print(f"   总计检查: {len(app_list)} 个应用")
        print(f"   已存在: {len(existing_apps)} 个")
        print(f"   不存在: {len(missing_apps)} 个")
        
        # 输出未匹配的应用列表（方便复制）
        if missing_apps:
            print(f"\n🎯 未在懒猫商店中找到的应用 ({len(missing_apps)} 个):")
            print("=" * 60)
            print("📋 以下列表可直接复制用于移植工作:")
            print("-" * 40)
            
            for app in missing_apps:
                print(app['input_name'])
            
            print("-" * 40)
            print("💡 建议优先移植以上应用到懒猫商店")
        
        return results, missing_apps, existing_apps

def main():
    # 测试应用列表
    test_apps = [
        "Dashy",
        "Fenrus", 
        "Glance",
        "Heimdall",
        "Hiccup",
        "Homarr",
        "Homepage by gethomepage",
        "Homepage by tomershvueli", 
        "Homer",
        "Hubleys",
        "LinkStack",
        "LittleLink",
        "Mafl",
        "portkey",
        "ryot",
        "Starbase 80",
        "Web-Portal",
        "Your Spotify"
    ]
    
    checker = QuickAppChecker()
    
    if not checker.lazycat_apps:
        print("❌ 无法加载数据，程序退出")
        return
    
    print("🚀 懒猫应用商店快速检查工具")
    print(f"📚 已加载懒猫应用商店数据: {len(checker.lazycat_apps)} 个应用")
    
    results, missing_apps, existing_apps = checker.batch_check(test_apps)
    
    # 额外输出：已存在应用的详细匹配信息
    if existing_apps:
        print(f"\n✅ 已存在应用的匹配详情:")
        print("=" * 60)
        for app in existing_apps:
            print(f"输入: {app['input_name']}")
            print(f"匹配: {app['match']['name']} (相似度: {app['similarity']:.1%})")
            if app['match'].get('brief'):
                print(f"简介: {app['match']['brief'][:100]}...")
            print("-" * 40)

if __name__ == "__main__":
    main() 