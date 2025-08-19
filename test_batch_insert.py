#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试批量插入功能
"""

from database_manager import DatabaseManager

def test_batch_insert():
    """测试批量插入缺失应用功能"""
    print("🧪 测试批量插入功能")
    print("=" * 50)
    
    # 初始化数据库管理器
    db = DatabaseManager()
    
    # 测试应用列表
    test_apps = [
        "TestApp1",
        "TestApp2", 
        "TestApp3",
        "懒猫网盘",  # 这个应该已存在，会被跳过
        "TestApp4"
    ]
    
    print(f"📝 准备测试的应用列表:")
    for i, app in enumerate(test_apps, 1):
        print(f"   {i}. {app}")
    
    print(f"\n🚀 开始批量插入...")
    
    # 执行批量插入
    result = db.batch_add_missing_apps(test_apps)
    
    print(f"\n📊 插入结果:")
    print(f"   ✅ 成功添加: {result['total_added']} 个应用")
    print(f"   ⏭️  跳过已存在: {result['total_skipped']} 个应用")
    
    if result['added']:
        print(f"\n📝 新添加的应用:")
        for app_id, app_name in result['added']:
            print(f"   • {app_name} (ID: {app_id})")
    
    if result['skipped']:
        print(f"\n⏭️  跳过的应用:")
        for app_name in result['skipped']:
            print(f"   • {app_name} (已存在)")
    
    # 验证自定义ID范围
    print(f"\n🔍 验证自定义ID范围:")
    for app_id, app_name in result['added']:
        if app_id >= 1000000:
            print(f"   ✅ {app_name}: ID {app_id} 在正确范围内")
        else:
            print(f"   ❌ {app_name}: ID {app_id} 不在自定义范围内")
    
    # 查询验证
    print(f"\n🔍 数据库验证:")
    for app_id, app_name in result['added']:
        app_data = db.get_app_by_id(app_id)
        if app_data:
            print(f"   ✅ {app_name}: 数据库中存在，描述为 '{app_data[2]}'")
        else:
            print(f"   ❌ {app_name}: 数据库中未找到")
    
    print(f"\n✅ 测试完成！")

if __name__ == "__main__":
    test_batch_insert() 