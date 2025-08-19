#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
懒猫应用商店Web管理系统启动脚本
"""

import os
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """延迟打开浏览器"""
    webbrowser.open('http://localhost:5001')

def main():
    print("🚀 懒猫应用商店Web管理系统")
    print("=" * 50)
    
    # 检查数据库是否存在
    if not os.path.exists('lazycat_apps.db'):
        print("📊 初始化数据库...")
        from database_manager import DatabaseManager
        db = DatabaseManager()
        if not db.import_csv_data():
            print("❌ 数据库初始化失败！")
            return
        print("✅ 数据库初始化完成")
    
    # 检查模板目录
    if not os.path.exists('templates'):
        print("❌ 错误：找不到templates目录")
        print("请确保所有模板文件都已创建")
        return
    
    print("🌐 启动Web服务器...")
    print("📱 浏览器将自动打开 http://localhost:5001")
    print("💡 按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    # 延迟3秒后打开浏览器
    Timer(3.0, open_browser).start()
    
    # 启动Flask应用
    try:
        from web_app import app
        app.run(debug=False, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败：{str(e)}")

if __name__ == "__main__":
    main() 