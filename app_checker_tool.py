#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
懒猫应用商店批量检查工具
批量检查输入的应用是否已在懒猫商店中存在
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import re
from difflib import SequenceMatcher
import threading
import webbrowser
from datetime import datetime

class AppCheckerTool:
    def __init__(self, root):
        self.root = root
        self.root.title("懒猫应用商店 - 批量应用检查工具")
        self.root.geometry("1200x800")
        
        # 数据存储
        self.lazycat_apps = []
        self.selfh_apps = []
        self.missing_apps = []
        self.input_apps = []
        self.results = []
        
        # 创建界面
        self.create_widgets()
        
        # 加载数据
        self.load_data()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🔍 懒猫应用商店批量检查工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 左侧输入区域
        input_frame = ttk.LabelFrame(main_frame, text="📝 应用列表输入", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(1, weight=1)
        
        # 输入说明
        input_info = ttk.Label(input_frame, 
                              text="请输入要检查的应用名称，每行一个：",
                              font=("Arial", 10))
        input_info.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 输入文本框
        self.input_text = scrolledtext.ScrolledText(input_frame, 
                                                   width=30, height=20,
                                                   font=("Consolas", 10))
        self.input_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 示例文本
        example_text = """Dashy
Fenrus
Glance
Heimdall
Hiccup
Homarr
Homepage by gethomepage
Homepage by tomershvueli
Homer
Hubleys
LinkStack
LittleLink
Mafl
portkey
ryot
Starbase 80
Web-Portal
Your Spotify"""
        self.input_text.insert(tk.END, example_text)
        
        # 按钮区域
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, pady=(10, 0), sticky=tk.W)
        
        self.check_button = ttk.Button(button_frame, text="🔍 开始检查", 
                                      command=self.start_check)
        self.check_button.grid(row=0, column=0, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="🗑️ 清空", 
                                      command=self.clear_input)
        self.clear_button.grid(row=0, column=1, padx=(0, 10))
        
        self.export_button = ttk.Button(button_frame, text="📤 导出结果", 
                                       command=self.export_results)
        self.export_button.grid(row=0, column=2)
        
        # 右侧结果区域
        result_frame = ttk.LabelFrame(main_frame, text="📊 检查结果", padding="10")
        result_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(1, weight=1)
        
        # 结果统计
        self.stats_label = ttk.Label(result_frame, 
                                    text="等待检查...",
                                    font=("Arial", 10, "bold"))
        self.stats_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # 结果表格
        columns = ("应用名称", "状态", "相似度", "匹配的懒猫应用", "说明")
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题和宽度
        self.result_tree.heading("应用名称", text="应用名称")
        self.result_tree.heading("状态", text="状态")
        self.result_tree.heading("相似度", text="相似度")
        self.result_tree.heading("匹配的懒猫应用", text="匹配的懒猫应用")
        self.result_tree.heading("说明", text="说明")
        
        self.result_tree.column("应用名称", width=150)
        self.result_tree.column("状态", width=80)
        self.result_tree.column("相似度", width=60)
        self.result_tree.column("匹配的懒猫应用", width=150)
        self.result_tree.column("说明", width=200)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        
        self.result_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # 底部状态栏
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="就绪")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 进度条
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
        # 绑定双击事件
        self.result_tree.bind("<Double-1>", self.on_item_double_click)
    
    def load_data(self):
        """加载懒猫和selfh的应用数据"""
        try:
            # 加载分析结果
            with open('analysis_results.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.lazycat_apps = data.get('lazycat_apps', [])
                self.selfh_apps = data.get('selfh_apps', [])
                self.missing_apps = data.get('missing_apps', [])
            
            self.status_label.config(text=f"数据加载完成 - 懒猫应用: {len(self.lazycat_apps)}, selfh应用: {len(self.selfh_apps)}")
            
        except FileNotFoundError:
            messagebox.showerror("错误", "找不到 analysis_results.json 文件！\n请先运行应用分析程序。")
            self.status_label.config(text="数据加载失败")
        except Exception as e:
            messagebox.showerror("错误", f"加载数据时出错：{str(e)}")
            self.status_label.config(text="数据加载失败")
    
    def normalize_name(self, name):
        """标准化应用名称"""
        if not name:
            return ""
        
        # 转换为小写
        name = name.lower().strip()
        
        # 移除常见的前缀和后缀
        prefixes = ['the ', 'a ', 'an ']
        suffixes = [' app', ' application', ' tool', ' service', ' platform']
        
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
                best_match = {
                    'type': 'lazycat',
                    'app': lazycat_app,
                    'similarity': similarity
                }
        
        # 判断匹配结果
        if best_similarity >= 0.8:
            return {
                'status': '已存在',
                'similarity': best_similarity,
                'match': best_match['app'],
                'description': f"在懒猫商店中找到高度相似的应用"
            }
        elif best_similarity >= 0.6:
            return {
                'status': '可能存在',
                'similarity': best_similarity,
                'match': best_match['app'],
                'description': f"找到相似应用，建议人工确认"
            }
        else:
            # 检查是否在缺失应用列表中
            for missing_app in self.missing_apps:
                missing_name = missing_app.get('name', '')
                similarity = self.calculate_similarity(app_name, missing_name)
                
                if similarity >= 0.8:
                    return {
                        'status': '已分析',
                        'similarity': similarity,
                        'match': missing_app,
                        'description': f"已在缺失应用分析中，优先级: {missing_app.get('stars', 'N/A')} stars"
                    }
            
            return {
                'status': '不存在',
                'similarity': 0.0,
                'match': None,
                'description': '懒猫商店中未找到此应用'
            }
    
    def start_check(self):
        """开始检查应用"""
        # 获取输入的应用列表
        input_text = self.input_text.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showwarning("警告", "请输入要检查的应用名称！")
            return
        
        self.input_apps = [line.strip() for line in input_text.split('\n') if line.strip()]
        
        if not self.input_apps:
            messagebox.showwarning("警告", "没有有效的应用名称！")
            return
        
        # 在新线程中执行检查
        self.check_button.config(state='disabled')
        self.progress.start()
        self.status_label.config(text="正在检查应用...")
        
        thread = threading.Thread(target=self.perform_check)
        thread.daemon = True
        thread.start()
    
    def perform_check(self):
        """执行应用检查"""
        self.results = []
        
        for i, app_name in enumerate(self.input_apps):
            result = self.check_app_exists(app_name)
            
            if result:
                self.results.append({
                    'input_name': app_name,
                    'status': result['status'],
                    'similarity': result['similarity'],
                    'match': result['match'],
                    'description': result['description']
                })
            
            # 更新状态
            self.root.after(0, lambda i=i: self.status_label.config(
                text=f"正在检查应用... ({i+1}/{len(self.input_apps)})"))
        
        # 在主线程中更新UI
        self.root.after(0, self.update_results)
    
    def update_results(self):
        """更新结果显示"""
        # 清空现有结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 统计结果
        stats = {
            '已存在': 0,
            '可能存在': 0,
            '已分析': 0,
            '不存在': 0
        }
        
        # 添加结果到表格
        for result in self.results:
            status = result['status']
            stats[status] = stats.get(status, 0) + 1
            
            # 设置状态图标
            status_icon = {
                '已存在': '✅',
                '可能存在': '⚠️',
                '已分析': '📋',
                '不存在': '❌'
            }.get(status, '❓')
            
            # 格式化相似度
            similarity_text = f"{result['similarity']:.1%}" if result['similarity'] > 0 else "-"
            
            # 匹配应用名称
            match_name = ""
            if result['match']:
                match_name = result['match'].get('name', 'N/A')
            
            # 插入行
            item = self.result_tree.insert('', 'end', values=(
                result['input_name'],
                f"{status_icon} {status}",
                similarity_text,
                match_name,
                result['description']
            ))
            
            # 设置行颜色
            if status == '已存在':
                self.result_tree.set(item, "状态", f"✅ {status}")
            elif status == '可能存在':
                self.result_tree.set(item, "状态", f"⚠️ {status}")
            elif status == '已分析':
                self.result_tree.set(item, "状态", f"📋 {status}")
            else:
                self.result_tree.set(item, "状态", f"❌ {status}")
        
        # 更新统计信息
        total = len(self.results)
        stats_text = f"检查完成 - 总计: {total} | " + " | ".join([
            f"{k}: {v}" for k, v in stats.items() if v > 0
        ])
        self.stats_label.config(text=stats_text)
        
        # 重置界面状态
        self.progress.stop()
        self.check_button.config(state='normal')
        self.status_label.config(text="检查完成")
        
        # 显示结果摘要
        missing_count = stats.get('不存在', 0)
        if missing_count > 0:
            messagebox.showinfo("检查完成", 
                              f"检查完成！\n"
                              f"总计检查: {total} 个应用\n"
                              f"不存在: {missing_count} 个\n"
                              f"建议优先移植标记为'不存在'的应用。")
    
    def clear_input(self):
        """清空输入"""
        self.input_text.delete("1.0", tk.END)
    
    def export_results(self):
        """导出检查结果"""
        if not self.results:
            messagebox.showwarning("警告", "没有结果可导出！")
            return
        
        try:
            # 导出为CSV格式
            filename = f"app_check_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                import csv
                writer = csv.writer(f)
                
                # 写入标题
                writer.writerow(['应用名称', '状态', '相似度', '匹配的懒猫应用', '说明'])
                
                # 写入数据
                for result in self.results:
                    match_name = result['match'].get('name', '') if result['match'] else ''
                    similarity_text = f"{result['similarity']:.1%}" if result['similarity'] > 0 else ""
                    
                    writer.writerow([
                        result['input_name'],
                        result['status'],
                        similarity_text,
                        match_name,
                        result['description']
                    ])
            
            messagebox.showinfo("导出成功", f"结果已导出到: {filename}")
            
        except Exception as e:
            messagebox.showerror("导出失败", f"导出时出错：{str(e)}")
    
    def on_item_double_click(self, event):
        """双击表格项时的处理"""
        selection = self.result_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.result_tree.item(item, 'values')
        
        if len(values) >= 4:
            app_name = values[0]
            status = values[1]
            match_name = values[3]
            
            # 显示详细信息
            detail_text = f"应用名称: {app_name}\n"
            detail_text += f"检查状态: {status}\n"
            
            if match_name:
                detail_text += f"匹配应用: {match_name}\n"
            
            # 找到对应的结果数据
            for result in self.results:
                if result['input_name'] == app_name:
                    if result['match'] and result['match'].get('github'):
                        detail_text += f"GitHub链接: {result['match']['github']}\n"
                    break
            
            messagebox.showinfo("应用详情", detail_text)

def main():
    root = tk.Tk()
    app = AppCheckerTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()