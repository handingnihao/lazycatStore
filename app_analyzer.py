#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
懒猫应用商店差异分析工具
分析selfh.csv和lazycat20250625.csv两个文件，找出selfh.csv中有但懒猫商店没有的应用
"""

import csv
import re
from difflib import SequenceMatcher
import json

def normalize_name(name):
    """标准化应用名称，去除特殊字符、转小写，便于比较"""
    if not name:
        return ""
    # 移除特殊字符，保留字母数字和空格
    normalized = re.sub(r'[^\w\s-]', '', name.lower())
    # 移除多余空格
    normalized = ' '.join(normalized.split())
    return normalized

def similarity(a, b):
    """计算两个字符串的相似度（0-1之间）"""
    return SequenceMatcher(None, a, b).ratio()

def load_lazycat_apps(filename):
    """加载懒猫官方应用列表"""
    apps = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row.get('name', '').strip()
                if name:
                    normalized_name = normalize_name(name)
                    apps[normalized_name] = {
                        'original_name': name,
                        'brief': row.get('brief', ''),
                        'count': row.get('count', ''),
                        'href': row.get('tablescraper-selected-row href', '')
                    }
    except Exception as e:
        print(f"读取懒猫应用文件时出错: {e}")
    return apps

def load_selfh_apps(filename):
    """加载selfh应用列表"""
    apps = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row.get('project-name', '').strip()
                if name:
                    apps.append({
                        'name': name,
                        'normalized_name': normalize_name(name),
                        'description': row.get('project-description', ''),
                        'stars': row.get('star-count', ''),
                        'language': row.get('Language:', ''),
                        'license': row.get('License:', ''),
                        'tag': row.get('tag-link', ''),
                        'github': row.get('source-link href', ''),
                        'homepage': row.get('project-name href', '')
                    })
    except Exception as e:
        print(f"读取selfh应用文件时出错: {e}")
    return apps

def find_missing_apps(lazycat_apps, selfh_apps, similarity_threshold=0.8):
    """找出selfh中存在但懒猫商店中没有的应用"""
    missing_apps = []
    similar_apps = []
    
    for selfh_app in selfh_apps:
        selfh_normalized = selfh_app['normalized_name']
        found_exact = False
        max_similarity = 0
        most_similar_app = None
        
        # 首先检查是否有完全匹配
        if selfh_normalized in lazycat_apps:
            found_exact = True
        else:
            # 检查相似度
            for lazycat_normalized, lazycat_info in lazycat_apps.items():
                sim = similarity(selfh_normalized, lazycat_normalized)
                if sim > max_similarity:
                    max_similarity = sim
                    most_similar_app = lazycat_info
        
        if not found_exact:
            if max_similarity >= similarity_threshold:
                # 相似但不完全相同的应用
                similar_apps.append({
                    'selfh_app': selfh_app,
                    'similar_lazycat_app': most_similar_app,
                    'similarity': max_similarity
                })
            else:
                # 完全缺失的应用
                missing_apps.append(selfh_app)
    
    return missing_apps, similar_apps

def format_app_info(app):
    """格式化应用信息为可读字符串"""
    info = f"名称: {app['name']}"
    if app.get('description'):
        info += f"\n描述: {app['description']}"
    if app.get('stars'):
        info += f"\nGitHub Stars: {app['stars']}"
    if app.get('language'):
        info += f"\n开发语言: {app['language']}"
    if app.get('license'):
        info += f"\n许可证: {app['license']}"
    if app.get('tag'):
        info += f"\n分类: {app['tag']}"
    if app.get('github'):
        info += f"\nGitHub: {app['github']}"
    if app.get('homepage'):
        info += f"\n官网: {app['homepage']}"
    return info

def save_results_to_json(missing_apps, similar_apps, filename='analysis_results.json'):
    """将结果保存为JSON文件"""
    results = {
        'summary': {
            'missing_apps_count': len(missing_apps),
            'similar_apps_count': len(similar_apps),
            'total_analyzed': len(missing_apps) + len(similar_apps)
        },
        'missing_apps': missing_apps,
        'similar_apps': similar_apps
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"详细结果已保存到: {filename}")

def main():
    print("=" * 60)
    print("懒猫应用商店差异分析工具")
    print("=" * 60)
    
    # 加载应用数据
    print("正在加载懒猫官方应用列表...")
    lazycat_apps = load_lazycat_apps('lazycat20250625.csv')
    print(f"已加载 {len(lazycat_apps)} 个懒猫官方应用")
    
    print("正在加载selfh应用列表...")
    selfh_apps = load_selfh_apps('selfh.csv')
    print(f"已加载 {len(selfh_apps)} 个selfh应用")
    
    # 分析差异
    print("\n正在分析应用差异...")
    missing_apps, similar_apps = find_missing_apps(lazycat_apps, selfh_apps)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("分析结果")
    print("=" * 60)
    
    print(f"\n📊 统计信息:")
    print(f"   - selfh应用总数: {len(selfh_apps)}")
    print(f"   - 懒猫官方应用总数: {len(lazycat_apps)}")
    print(f"   - 完全缺失的应用数: {len(missing_apps)}")
    print(f"   - 相似但不完全相同的应用数: {len(similar_apps)}")
    
    if missing_apps:
        print(f"\n🚫 懒猫商店中完全缺失的应用 ({len(missing_apps)}个):")
        print("-" * 50)
        for i, app in enumerate(missing_apps, 1):
            print(f"\n{i}. {format_app_info(app)}")
            print("-" * 30)
    
    if similar_apps:
        print(f"\n⚠️  相似但可能不完全相同的应用 ({len(similar_apps)}个):")
        print("-" * 50)
        for i, item in enumerate(similar_apps, 1):
            print(f"\n{i}. selfh应用: {item['selfh_app']['name']}")
            print(f"   相似的懒猫应用: {item['similar_lazycat_app']['original_name']}")
            print(f"   相似度: {item['similarity']:.2%}")
            print("-" * 30)
    
    # 保存详细结果
    save_results_to_json(missing_apps, similar_apps)
    
    # 生成推荐报告
    print(f"\n📋 移植建议:")
    if missing_apps:
        high_priority = [app for app in missing_apps if app.get('stars') and int(app['stars'].replace('k', '000').replace(',', '')) > 10000]
        if high_priority:
            print(f"   🔥 高优先级应用 (GitHub Stars > 10k): {len(high_priority)}个")
            for app in sorted(high_priority, key=lambda x: int(x['stars'].replace('k', '000').replace(',', '')), reverse=True)[:5]:
                stars = app.get('stars', '0')
                print(f"      - {app['name']} ({stars} stars) - {app.get('tag', 'N/A')}")
        
        popular_categories = {}
        for app in missing_apps:
            category = app.get('tag', 'Other')
            popular_categories[category] = popular_categories.get(category, 0) + 1
        
        top_categories = sorted(popular_categories.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"   📂 热门缺失分类:")
        for category, count in top_categories:
            print(f"      - {category}: {count}个应用")
    
    print(f"\n✅ 分析完成！")

if __name__ == "__main__":
    main() 