#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
from datetime import datetime

def create_sheets_table(conn):
    """创建存储Google Sheets数据的表"""
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sheets_apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT,
            text TEXT,
            long_description TEXT,
            category TEXT,
            product_category TEXT,
            hide TEXT,
            proprietary TEXT,
            free TEXT,
            traffic TEXT,
            img_url TEXT,
            page TEXT,
            link_type TEXT,
            unique_id TEXT,
            slugified_title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sheets_title ON sheets_apps(title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sheets_category ON sheets_apps(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sheets_free ON sheets_apps(free)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sheets_page ON sheets_apps(page)')
    
    conn.commit()
    print("✅ 表 sheets_apps 创建成功")

def import_data(conn, json_file):
    """导入JSON数据到数据库"""
    cursor = conn.cursor()
    
    # 读取JSON数据
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 检查数据格式
    if 'items' not in data:
        print("❌ 数据格式错误：未找到 'items' 字段")
        return
    
    items = data['items']
    print(f"📊 找到 {len(items)} 条记录")
    
    # 清空现有数据
    cursor.execute('DELETE FROM sheets_apps')
    
    # 批量插入数据
    success_count = 0
    error_count = 0
    
    for item in items:
        try:
            cursor.execute('''
                INSERT INTO sheets_apps (
                    title, url, text, long_description, category,
                    product_category, hide, proprietary, free, traffic,
                    img_url, page, link_type, unique_id, slugified_title
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get('title', ''),
                item.get('url', '').strip(),
                item.get('text', '').strip(),
                item.get('longdescription', '').strip(),
                item.get('category', ''),
                item.get('productcategory', ''),
                item.get('hide', ''),
                item.get('proprietary', ''),
                item.get('free', ''),
                item.get('traffic', ''),
                item.get('imgurl', ''),
                item.get('page', ''),
                item.get('linktype', ''),
                item.get('uniqueid', ''),
                item.get('slugified_title', '')
            ))
            success_count += 1
            
            # 每100条记录提交一次
            if success_count % 100 == 0:
                conn.commit()
                print(f"  ✓ 已导入 {success_count} 条记录...")
                
        except Exception as e:
            error_count += 1
            print(f"  ❌ 导入失败 ({item.get('title', 'Unknown')}): {str(e)}")
    
    # 最终提交
    conn.commit()
    
    print(f"\n✅ 导入完成！")
    print(f"   - 成功: {success_count} 条")
    print(f"   - 失败: {error_count} 条")
    
    # 显示统计信息
    show_statistics(conn)

def show_statistics(conn):
    """显示统计信息"""
    cursor = conn.cursor()
    
    print("\n📊 数据统计：")
    
    # 总记录数
    cursor.execute('SELECT COUNT(*) FROM sheets_apps')
    total = cursor.fetchone()[0]
    print(f"   - 总记录数: {total}")
    
    # 按类别统计
    cursor.execute('''
        SELECT category, COUNT(*) as count 
        FROM sheets_apps 
        WHERE category IS NOT NULL AND category != ''
        GROUP BY category 
        ORDER BY count DESC 
        LIMIT 10
    ''')
    categories = cursor.fetchall()
    
    if categories:
        print("\n   按类别分布（Top 10）:")
        for cat, count in categories:
            print(f"     • {cat}: {count}")
    
    # 免费应用统计
    cursor.execute('''
        SELECT free, COUNT(*) as count
        FROM sheets_apps
        WHERE free IS NOT NULL AND free != ''
        GROUP BY free
    ''')
    free_stats = cursor.fetchall()
    
    if free_stats:
        print("\n   收费模式分布:")
        for is_free, count in free_stats:
            label = "免费" if is_free.upper() == 'TRUE' else "付费" if is_free.upper() == 'FALSE' else is_free
            print(f"     • {label}: {count}")
    
    # 流量分布
    cursor.execute('''
        SELECT traffic, COUNT(*) as count
        FROM sheets_apps
        WHERE traffic IS NOT NULL AND traffic != ''
        GROUP BY traffic
        ORDER BY count DESC
        LIMIT 5
    ''')
    traffic_stats = cursor.fetchall()
    
    if traffic_stats:
        print("\n   流量分布（Top 5）:")
        for traffic, count in traffic_stats:
            print(f"     • {traffic}: {count}")

def main():
    """主函数"""
    db_path = 'lazycat_apps.db'
    json_file = 'api_response.json'
    
    print("🔧 开始导入Google Sheets数据...")
    print(f"   数据库: {db_path}")
    print(f"   数据文件: {json_file}")
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    
    try:
        # 创建表
        create_sheets_table(conn)
        
        # 导入数据
        import_data(conn, json_file)
        
    except Exception as e:
        print(f"❌ 操作失败: {str(e)}")
        conn.rollback()
    finally:
        conn.close()
    
    print("\n✅ 所有操作完成！")

if __name__ == '__main__':
    main()