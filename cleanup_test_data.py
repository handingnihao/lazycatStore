#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理测试数据
"""

from database_manager import DatabaseManager

def cleanup_test_data():
    """清理测试数据"""
    print("🧹 清理测试数据")
    print("=" * 50)
    
    # 初始化数据库管理器
    db = DatabaseManager()
    
    # 测试应用列表
    test_apps = ["TestApp1", "TestApp2", "TestApp3", "TestApp4"]
    
    print(f"📝 准备删除的测试应用:")
    for i, app in enumerate(test_apps, 1):
        print(f"   {i}. {app}")
    
    # 查找并删除测试应用
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    deleted_count = 0
    for app_name in test_apps:
        cursor.execute('SELECT id FROM apps WHERE name = ?', (app_name,))
        result = cursor.fetchone()
        if result:
            app_id = result[0]
            cursor.execute('DELETE FROM apps WHERE id = ?', (app_id,))
            print(f"   ✅ 删除 {app_name} (ID: {app_id})")
            deleted_count += 1
        else:
            print(f"   ⏭️  {app_name} 不存在，跳过")
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 清理结果:")
    print(f"   🗑️  成功删除: {deleted_count} 个测试应用")
    print(f"\n✅ 清理完成！")

if __name__ == "__main__":
    cleanup_test_data() 