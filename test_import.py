#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试一键导入功能
"""

import os
from database_manager import DatabaseManager

def test_import():
    """测试导入Excel文件"""
    print("🧪 测试一键导入功能")
    print("=" * 50)
    
    # 初始化数据库管理器
    db = DatabaseManager()
    
    # 测试文件路径
    test_file = 'excel/lazycat20250708.xlsx'
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    print(f"📁 测试文件: {test_file}")
    
    # 导入前的统计
    stats_before = db.get_statistics()
    print(f"导入前应用总数: {stats_before['total_apps']}")
    
    # 执行导入
    print("🚀 开始导入...")
    result = db.import_excel_csv(test_file)
    
    # 显示结果
    if result['success']:
        print("✅ 导入成功！")
        print(f"📄 {result['message']}")
        
        stats = result['stats']
        print(f"\n📊 导入统计:")
        print(f"   总处理行数: {stats['total_rows']}")
        print(f"   新增应用: {stats['inserted']}")
        print(f"   更新应用: {stats['updated']}")
        print(f"   跳过记录: {stats['skipped']}")
        
        if stats['errors']:
            print(f"   错误数量: {len(stats['errors'])}")
            for error in stats['errors'][:5]:  # 只显示前5个错误
                print(f"     - {error}")
        
        # 导入后的统计
        stats_after = db.get_statistics()
        print(f"\n导入后应用总数: {stats_after['total_apps']}")
        print(f"增加了 {stats_after['total_apps'] - stats_before['total_apps']} 个应用")
        
    else:
        print("❌ 导入失败！")
        print(f"错误信息: {result['message']}")

if __name__ == "__main__":
    test_import() 