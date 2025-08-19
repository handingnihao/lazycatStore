#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
懒猫应用商店缺失应用优先级列表生成器
按照GitHub Stars数量和分类热度对缺失应用进行优先级排序
"""

import json
import csv
from datetime import datetime

def get_star_count(star_str):
    """将星数字符串转换为数字"""
    if not star_str:
        return 0
    # 处理 "25k" 这样的格式
    star_str = str(star_str).replace(',', '').lower()
    if 'k' in star_str:
        return int(float(star_str.replace('k', '')) * 1000)
    try:
        return int(star_str)
    except:
        return 0

def get_priority_level(stars):
    """根据星数确定优先级"""
    if stars >= 50000:
        return "🔥🔥🔥 超高优先级"
    elif stars >= 20000:
        return "🔥🔥 高优先级"
    elif stars >= 10000:
        return "🔥 较高优先级"
    elif stars >= 5000:
        return "⭐ 中优先级"
    elif stars >= 1000:
        return "💡 一般优先级"
    else:
        return "📝 低优先级"

def get_category_weight(category, category_counts):
    """根据分类热度确定权重"""
    return category_counts.get(category, 0)

def load_analysis_results():
    """加载分析结果"""
    try:
        with open('analysis_results.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("错误：找不到 analysis_results.json 文件，请先运行 app_analyzer.py")
        return None

def generate_priority_list():
    """生成按优先级排序的应用列表"""
    # 加载分析结果
    results = load_analysis_results()
    if not results:
        return
    
    missing_apps = results.get('missing_apps', [])
    
    # 统计分类热度
    category_counts = {}
    for app in missing_apps:
        category = app.get('tag', 'Other')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # 为每个应用计算综合评分
    scored_apps = []
    for app in missing_apps:
        stars = get_star_count(app.get('stars', 0))
        category = app.get('tag', 'Other')
        category_weight = get_category_weight(category, category_counts)
        
        # 综合评分 = Stars权重(90%) + 分类热度权重(10%)
        score = stars * 0.9 + category_weight * 100 * 0.1
        
        scored_app = {
            'name': app.get('name', ''),
            'description': app.get('description', ''),
            'stars': stars,
            'stars_display': app.get('stars', '0'),
            'category': category,
            'language': app.get('language', ''),
            'license': app.get('license', ''),
            'github': app.get('github', ''),
            'homepage': app.get('homepage', ''),
            'priority_level': get_priority_level(stars),
            'score': score,
            'category_count': category_weight
        }
        scored_apps.append(scored_app)
    
    # 按综合评分排序
    scored_apps.sort(key=lambda x: x['score'], reverse=True)
    
    return scored_apps, category_counts

def save_to_csv(apps, filename='missing_apps_priority_list.csv'):
    """保存到CSV文件"""
    fieldnames = [
        '排名', '应用名称', '描述', 'GitHub Stars', '优先级', 
        '分类', '开发语言', '许可证', 'GitHub链接', '官网链接'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, app in enumerate(apps, 1):
            writer.writerow({
                '排名': i,
                '应用名称': app['name'],
                '描述': app['description'][:100] + '...' if len(app['description']) > 100 else app['description'],
                'GitHub Stars': app['stars_display'],
                '优先级': app['priority_level'],
                '分类': app['category'],
                '开发语言': app['language'],
                '许可证': app['license'],
                'GitHub链接': app['github'],
                '官网链接': app['homepage']
            })
    
    print(f"✅ 优先级列表已保存到: {filename}")

def print_priority_summary(apps, category_counts):
    """打印优先级摘要"""
    print("\n" + "=" * 80)
    print("🎯 懒猫应用商店缺失应用优先级排序")
    print("=" * 80)
    
    # 统计各优先级数量
    priority_stats = {}
    for app in apps:
        priority = app['priority_level']
        priority_stats[priority] = priority_stats.get(priority, 0) + 1
    
    print(f"\n📊 优先级统计:")
    for priority, count in sorted(priority_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   {priority}: {count} 个应用")
    
    print(f"\n🔥 超高优先级应用 (Top 20):")
    print("-" * 80)
    
    top_apps = apps[:20]
    for i, app in enumerate(top_apps, 1):
        print(f"{i:2d}. {app['name']}")
        print(f"    ⭐ {app['stars_display']} stars | 📂 {app['category']} | 💻 {app['language']}")
        if app['description']:
            desc = app['description'][:80] + "..." if len(app['description']) > 80 else app['description']
            print(f"    📝 {desc}")
        if app['github']:
            print(f"    🔗 {app['github']}")
        print()
    
    print(f"\n📂 热门缺失分类 (Top 10):")
    print("-" * 50)
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (category, count) in enumerate(sorted_categories, 1):
        print(f"{i:2d}. {category}: {count} 个应用")

def generate_markdown_report(apps, category_counts):
    """生成Markdown格式的报告"""
    markdown_content = f"""# 懒猫应用商店缺失应用优先级报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 总计缺失应用: {len(apps)} 个

## 📊 优先级分布

"""
    
    # 统计各优先级数量
    priority_stats = {}
    for app in apps:
        priority = app['priority_level']
        priority_stats[priority] = priority_stats.get(priority, 0) + 1
    
    for priority, count in sorted(priority_stats.items(), key=lambda x: x[1], reverse=True):
        markdown_content += f"- **{priority}**: {count} 个应用\n"
    
    markdown_content += "\n## 🔥 高优先级应用推荐 (Top 50)\n\n"
    
    for i, app in enumerate(apps[:50], 1):
        markdown_content += f"### {i}. {app['name']}\n\n"
        markdown_content += f"- **⭐ GitHub Stars**: {app['stars_display']}\n"
        markdown_content += f"- **📂 分类**: {app['category']}\n"
        if app['language']:
            markdown_content += f"- **💻 开发语言**: {app['language']}\n"
        if app['license']:
            markdown_content += f"- **📄 许可证**: {app['license']}\n"
        if app['description']:
            markdown_content += f"- **📝 描述**: {app['description']}\n"
        if app['github']:
            markdown_content += f"- **🔗 GitHub**: {app['github']}\n"
        if app['homepage']:
            markdown_content += f"- **🌐 官网**: {app['homepage']}\n"
        markdown_content += "\n---\n\n"
    
    markdown_content += "## 📂 热门缺失分类统计\n\n"
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (category, count) in enumerate(sorted_categories, 1):
        markdown_content += f"{i}. **{category}**: {count} 个应用\n"
    
    # 保存Markdown文件
    with open('missing_apps_priority_report.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print("✅ Markdown报告已保存到: missing_apps_priority_report.md")

def main():
    print("🚀 正在生成懒猫应用商店缺失应用优先级列表...")
    
    # 生成优先级列表
    apps, category_counts = generate_priority_list()
    if not apps:
        return
    
    # 打印摘要
    print_priority_summary(apps, category_counts)
    
    # 保存CSV文件
    save_to_csv(apps)
    
    # 生成Markdown报告
    generate_markdown_report(apps, category_counts)
    
    print(f"\n🎉 完成！共处理 {len(apps)} 个缺失应用")
    print("📁 生成的文件:")
    print("   - missing_apps_priority_list.csv (Excel可打开)")
    print("   - missing_apps_priority_report.md (详细报告)")

if __name__ == "__main__":
    main() 