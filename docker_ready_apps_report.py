#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
懒猫应用Docker就绪报告生成器
专门分析有Docker支持的应用，按移植难易程度排序
"""

import json
import csv
from datetime import datetime

class DockerReadyReporter:
    def __init__(self):
        self.apps = []
        self.docker_ready_apps = []
        self.easy_migration_apps = []
    
    def load_analysis_results(self):
        """加载移植难度分析结果"""
        try:
            with open('migration_difficulty_analysis.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('apps', [])
        except FileNotFoundError:
            print("错误：找不到 migration_difficulty_analysis.json 文件")
            print("请先运行 migration_difficulty_analyzer.py")
            return []
    
    def categorize_apps(self):
        """按Docker支持情况分类应用"""
        self.apps = self.load_analysis_results()
        if not self.apps:
            return
        
        # 筛选有Docker支持的应用
        self.docker_ready_apps = []
        for app in self.apps:
            if (app['has_dockerfile'] or 
                app['has_docker_compose'] or 
                app['official_image']):
                self.docker_ready_apps.append(app)
        
        # 按移植难度和优先级排序
        # 优先级 = Stars数量 / 移植难度分数 * Docker支持加权
        for app in self.docker_ready_apps:
            docker_boost = 1.0
            if app['official_image']:
                docker_boost = 2.0  # 官方镜像加权最高
            elif app['has_docker_compose']:
                docker_boost = 1.5  # docker-compose次之
            elif app['has_dockerfile']:
                docker_boost = 1.2  # 仅Dockerfile最低
            
            app['weighted_score'] = (app['stars'] / app['difficulty_score']) * docker_boost
        
        # 按加权分数排序
        self.docker_ready_apps.sort(key=lambda x: x['weighted_score'], reverse=True)
        
        # 筛选最容易移植的应用（难度分数 <= 4 且有Docker支持）
        self.easy_migration_apps = [
            app for app in self.docker_ready_apps 
            if app['difficulty_score'] <= 4
        ]
    
    def get_migration_priority(self, app):
        """获取移植优先级标签"""
        if app['weighted_score'] > 50000:
            return "🔥 极高优先级"
        elif app['weighted_score'] > 20000:
            return "⚡ 高优先级"
        elif app['weighted_score'] > 10000:
            return "✨ 中高优先级"
        elif app['weighted_score'] > 5000:
            return "💫 中等优先级"
        else:
            return "💡 一般优先级"
    
    def get_docker_deployment_info(self, app):
        """获取Docker部署信息"""
        deployment_info = {
            'type': '',
            'command': '',
            'description': '',
            'complexity': app['difficulty_score']
        }
        
        if app['official_image']:
            deployment_info['type'] = "🐳 官方镜像"
            # 简化的镜像名（取第一个）
            image_name = app['docker_images'][0] if app['docker_images'] else app['name'].lower()
            deployment_info['command'] = f"docker run -d --name {app['name'].lower().replace(' ', '-')} {image_name}"
            deployment_info['description'] = "可直接使用Docker Hub官方镜像部署"
            
        elif app['has_docker_compose']:
            deployment_info['type'] = f"📦 Docker Compose ({app['compose_complexity']}复杂度)"
            deployment_info['command'] = "docker-compose up -d"
            if app['compose_complexity'] <= 1:
                deployment_info['description'] = "简单的docker-compose配置，易于部署"
            elif app['compose_complexity'] <= 3:
                deployment_info['description'] = "中等复杂度的docker-compose配置，可能需要环境变量配置"
            else:
                deployment_info['description'] = "复杂的docker-compose配置，需要仔细配置多个服务"
                
        elif app['has_dockerfile']:
            deployment_info['type'] = "🔧 需构建镜像"
            deployment_info['command'] = "docker build -t app . && docker run -d app"
            deployment_info['description'] = "需要从源码构建Docker镜像"
        
        return deployment_info
    
    def generate_markdown_report(self):
        """生成Markdown格式的详细报告"""
        if not self.docker_ready_apps:
            return
        
        report_content = f"""# 懒猫应用商店 - Docker就绪应用移植指南

> 🕐 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}  
> 📊 分析应用总数: {len(self.apps)}  
> 🐳 Docker就绪应用: {len(self.docker_ready_apps)}  
> ⚡ 易于移植应用: {len(self.easy_migration_apps)}

## 📋 总览统计

| 分类 | 数量 | 百分比 |
|------|------|--------|
| 总分析应用 | {len(self.apps)} | 100% |
| Docker就绪应用 | {len(self.docker_ready_apps)} | {len(self.docker_ready_apps)/len(self.apps)*100:.1f}% |
| 有官方镜像 | {len([app for app in self.docker_ready_apps if app['official_image']])} | {len([app for app in self.docker_ready_apps if app['official_image']])/len(self.apps)*100:.1f}% |
| 有Docker Compose | {len([app for app in self.docker_ready_apps if app['has_docker_compose']])} | {len([app for app in self.docker_ready_apps if app['has_docker_compose']])/len(self.apps)*100:.1f}% |
| 有Dockerfile | {len([app for app in self.docker_ready_apps if app['has_dockerfile']])} | {len([app for app in self.docker_ready_apps if app['has_dockerfile']])/len(self.apps)*100:.1f}% |

---

## 🚀 推荐优先移植应用 (Top 30)

> ⚡ 按 **移植价值评分** 排序（Stars数量 ÷ 移植难度 × Docker支持加权）

"""
        
        # 生成Top 30推荐应用
        for i, app in enumerate(self.docker_ready_apps[:30], 1):
            priority = self.get_migration_priority(app)
            deployment = self.get_docker_deployment_info(app)
            
            report_content += f"""### {i}. {app['name']} {priority}

**⭐ GitHub Stars:** {app['stars_display']} | **📂 分类:** {app['category']} | **💻 语言:** {app['language']}

**📝 描述:** {app['description'][:150]}{'...' if len(app['description']) > 150 else ''}

**🐳 Docker部署信息:**
- **类型:** {deployment['type']}
- **部署命令:** `{deployment['command']}`
- **说明:** {deployment['description']}

**📊 移植评估:**
- **移植难度:** {app['difficulty_level']}
- **价值评分:** {app['weighted_score']:.0f}

**🔗 链接:**
- GitHub: {app['github']}
{f"- 官网: {app['homepage']}" if app['homepage'] else ""}

---

"""
        
        # 添加分类统计
        category_stats = {}
        for app in self.docker_ready_apps:
            category = app['category']
            if category not in category_stats:
                category_stats[category] = {'count': 0, 'apps': []}
            category_stats[category]['count'] += 1
            category_stats[category]['apps'].append(app['name'])
        
        report_content += """## 📊 Docker就绪应用分类统计

"""
        for category, info in sorted(category_stats.items(), key=lambda x: x[1]['count'], reverse=True):
            if info['count'] >= 2:  # 只显示有2个或以上应用的分类
                report_content += f"### {category} ({info['count']} 个应用)\n\n"
                for app_name in info['apps'][:5]:  # 最多显示5个应用
                    report_content += f"- {app_name}\n"
                if len(info['apps']) > 5:
                    report_content += f"- ... 还有 {len(info['apps']) - 5} 个应用\n"
                report_content += "\n"
        
        # 添加移植指南
        report_content += """## 🛠️ 移植部署指南

### 1. 官方镜像应用 (推荐优先移植)
这些应用在Docker Hub或GitHub Container Registry有官方镜像，可以直接部署：

```bash
# 通用部署命令模板
docker run -d \\
  --name app-name \\
  -p 8080:8080 \\
  -v /path/to/data:/app/data \\
  official-image:latest
```

### 2. Docker Compose应用
这些应用提供了docker-compose.yml文件，便于快速部署：

```bash
# 下载项目
git clone [github-url]
cd project-directory

# 配置环境变量（如需要）
cp .env.example .env
nano .env

# 启动服务
docker-compose up -d
```

### 3. 需要构建的应用
这些应用需要从源码构建Docker镜像：

```bash
# 下载源码
git clone [github-url]
cd project-directory

# 构建镜像
docker build -t app-name .

# 运行容器
docker run -d --name app-name -p 8080:8080 app-name
```

### 4. 移植注意事项

1. **数据持久化:** 确保重要数据目录挂载到宿主机
2. **端口配置:** 根据懒猫平台要求配置端口映射
3. **环境变量:** 检查并配置必要的环境变量
4. **依赖服务:** 注意应用可能需要的数据库、缓存等依赖
5. **资源需求:** 确认应用的CPU、内存、存储需求

---

## 📞 技术支持

如需移植特定应用或遇到技术问题，请联系懒猫技术团队。

**报告生成时间:** {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
"""
        
        # 保存报告
        with open('docker_ready_apps_report.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print("✅ Docker就绪应用报告已生成: docker_ready_apps_report.md")
    
    def generate_csv_summary(self):
        """生成CSV格式的简要列表"""
        if not self.docker_ready_apps:
            return
        
        csv_filename = 'docker_ready_apps_summary.csv'
        fieldnames = [
            '排名', '应用名称', 'GitHub Stars', '分类', '开发语言',
            'Docker类型', '移植难度', '价值评分', '优先级',
            'GitHub链接', '部署命令'
        ]
        
        with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, app in enumerate(self.docker_ready_apps, 1):
                deployment = self.get_docker_deployment_info(app)
                priority = self.get_migration_priority(app)
                
                writer.writerow({
                    '排名': i,
                    '应用名称': app['name'],
                    'GitHub Stars': app['stars_display'],
                    '分类': app['category'],
                    '开发语言': app['language'],
                    'Docker类型': deployment['type'],
                    '移植难度': app['difficulty_level'],
                    '价值评分': f"{app['weighted_score']:.0f}",
                    '优先级': priority,
                    'GitHub链接': app['github'],
                    '部署命令': deployment['command']
                })
        
        print(f"✅ Docker就绪应用CSV列表已生成: {csv_filename}")
    
    def print_summary(self):
        """打印摘要信息"""
        if not self.docker_ready_apps:
            print("❌ 没有找到Docker就绪的应用")
            return
        
        print("\n" + "=" * 80)
        print("🐳 懒猫应用商店 - Docker就绪应用分析")
        print("=" * 80)
        
        print(f"\n📊 统计摘要:")
        print(f"   - 总分析应用数: {len(self.apps)}")
        print(f"   - Docker就绪应用: {len(self.docker_ready_apps)} ({len(self.docker_ready_apps)/len(self.apps)*100:.1f}%)")
        
        official_count = len([app for app in self.docker_ready_apps if app['official_image']])
        compose_count = len([app for app in self.docker_ready_apps if app['has_docker_compose']])
        dockerfile_count = len([app for app in self.docker_ready_apps if app['has_dockerfile']])
        
        print(f"   - 有官方镜像: {official_count}")
        print(f"   - 有Docker Compose: {compose_count}")
        print(f"   - 有Dockerfile: {dockerfile_count}")
        
        print(f"\n🎯 Top 10 推荐移植应用:")
        print("-" * 80)
        
        for i, app in enumerate(self.docker_ready_apps[:10], 1):
            priority = self.get_migration_priority(app)
            deployment = self.get_docker_deployment_info(app)
            
            print(f"{i:2d}. {app['name']}")
            print(f"    ⭐ {app['stars_display']} stars | {priority}")
            print(f"    🐳 {deployment['type']} | {app['difficulty_level']}")
            print(f"    📂 {app['category']} | 💻 {app['language']}")
            print(f"    💎 价值评分: {app['weighted_score']:.0f}")
            print()

def main():
    reporter = DockerReadyReporter()
    
    print("🔍 开始分析Docker就绪应用...")
    
    # 分类应用
    reporter.categorize_apps()
    
    if reporter.docker_ready_apps:
        # 打印摘要
        reporter.print_summary()
        
        # 生成报告
        reporter.generate_markdown_report()
        reporter.generate_csv_summary()
        
        print(f"\n🎉 分析完成！")
        print("📁 生成的文件:")
        print("   - docker_ready_apps_report.md (详细移植指南)")
        print("   - docker_ready_apps_summary.csv (Excel可打开的应用列表)")
    else:
        print("❌ 没有找到任何Docker就绪的应用")

if __name__ == "__main__":
    main()