#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import re

def analyze_github_apps():
    """分析sheets_apps中的GitHub项目，找出不在apps表中的项目"""
    
    conn = sqlite3.connect('lazycat_apps.db')
    cursor = conn.cursor()
    
    # 1. 获取sheets_apps中所有包含github.com的记录
    print("📊 分析sheets_apps表中的GitHub项目...\n")
    
    cursor.execute('''
        SELECT title, url, category, free, traffic, text, long_description
        FROM sheets_apps 
        WHERE url LIKE '%github.com%'
        ORDER BY title
    ''')
    sheets_github_apps = cursor.fetchall()
    print(f"✅ 在sheets_apps中找到 {len(sheets_github_apps)} 个GitHub项目\n")
    
    # 2. 获取apps表中的所有应用名称和URL
    cursor.execute('''
        SELECT LOWER(name), LOWER(brief), href
        FROM apps
    ''')
    apps_data = cursor.fetchall()
    
    # 创建apps表的名称集合（用于快速查找）
    apps_names = set()
    apps_keywords = set()
    
    for name, brief, href in apps_data:
        apps_names.add(name)
        # 从brief中提取关键词
        if brief:
            # 提取主要关键词
            words = re.findall(r'\b[a-z]+\b', brief.lower())
            apps_keywords.update(words)
    
    print(f"✅ apps表中共有 {len(apps_data)} 个应用\n")
    
    # 3. 查找不在apps表中的GitHub项目
    not_in_apps = []
    possibly_in_apps = []
    
    for title, url, category, free, traffic, text, description in sheets_github_apps:
        # 标准化名称用于比较
        normalized_title = title.lower().strip()
        # 移除常见后缀
        search_title = normalized_title.replace(' ', '').replace('-', '').replace('_', '')
        
        # 检查是否存在于apps表
        found = False
        partial_match = False
        
        # 精确匹配
        if normalized_title in apps_names:
            found = True
        # 移除空格后匹配
        elif search_title in [n.replace(' ', '').replace('-', '').replace('_', '') for n in apps_names]:
            found = True
        # 部分匹配
        else:
            for app_name in apps_names:
                if normalized_title in app_name or app_name in normalized_title:
                    partial_match = True
                    break
        
        if not found:
            if partial_match:
                possibly_in_apps.append({
                    'title': title,
                    'url': url.strip(),
                    'category': category,
                    'free': free,
                    'traffic': traffic,
                    'text': text
                })
            else:
                not_in_apps.append({
                    'title': title,
                    'url': url.strip(),
                    'category': category,
                    'free': free,
                    'traffic': traffic,
                    'text': text
                })
    
    # 4. 生成报告
    print("=" * 80)
    print("📋 分析报告")
    print("=" * 80)
    
    print(f"\n📊 统计摘要:")
    print(f"  • sheets_apps中的GitHub项目总数: {len(sheets_github_apps)}")
    print(f"  • 确定不在apps表中的项目: {len(not_in_apps)}")
    print(f"  • 可能存在（部分匹配）的项目: {len(possibly_in_apps)}")
    print(f"  • 已存在于apps表的项目: {len(sheets_github_apps) - len(not_in_apps) - len(possibly_in_apps)}")
    
    # 按类别统计
    category_stats = {}
    for app in not_in_apps:
        cat = app['category'] or '未分类'
        category_stats[cat] = category_stats.get(cat, 0) + 1
    
    if category_stats:
        print(f"\n📂 不在apps表中的项目按类别分布:")
        sorted_cats = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
        for cat, count in sorted_cats[:10]:
            print(f"    • {cat}: {count}")
    
    # 输出详细列表
    print(f"\n🆕 不在apps表中的GitHub项目（前20个）:")
    print("-" * 80)
    
    for i, app in enumerate(not_in_apps[:20], 1):
        print(f"\n{i}. {app['title']}")
        print(f"   URL: {app['url']}")
        print(f"   类别: {app['category'] or '未分类'}")
        print(f"   免费: {'是' if app['free'] == 'TRUE' else '否' if app['free'] == 'FALSE' else '未知'}")
        print(f"   流量: {app['traffic'] or '未知'}")
        if app['text']:
            print(f"   描述: {app['text'][:100]}...")
    
    # 保存完整列表到CSV
    import csv
    
    csv_filename = 'github_apps_not_in_database.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'url', 'category', 'free', 'traffic', 'description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for app in not_in_apps:
            writer.writerow({
                'title': app['title'],
                'url': app['url'],
                'category': app['category'] or '',
                'free': app['free'] or '',
                'traffic': app['traffic'] or '',
                'description': app['text'] or ''
            })
    
    print(f"\n💾 完整列表已保存到: {csv_filename}")
    print(f"   包含 {len(not_in_apps)} 个不在apps表中的GitHub项目")
    
    # 创建SQL插入语句（可选）
    if not_in_apps:
        print(f"\n💡 提示: 可以使用以下方式将这些应用添加到apps表")
        print("   1. 运行 quick_app_checker.py 检查这些应用")
        print("   2. 使用 web_app.py 的导入功能")
        print("   3. 手动添加到数据库")
    
    conn.close()
    return not_in_apps

if __name__ == '__main__':
    analyze_github_apps()