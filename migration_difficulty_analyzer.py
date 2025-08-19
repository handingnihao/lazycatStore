#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
懒猫应用移植难易程度分析器
根据Docker镜像可用性、docker-compose复杂度等因素评估移植难度
"""

import json
import requests
import time
import re
from urllib.parse import urlparse
import csv
from datetime import datetime

class MigrationAnalyzer:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def load_apps(self):
        """加载分析结果中的应用"""
        try:
            with open('analysis_results.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('missing_apps', [])
        except FileNotFoundError:
            print("错误：找不到 analysis_results.json 文件")
            return []
    
    def get_star_count(self, star_str):
        """将星数字符串转换为数字"""
        if not star_str:
            return 0
        star_str = str(star_str).replace(',', '').lower()
        if 'k' in star_str:
            return int(float(star_str.replace('k', '')) * 1000)
        try:
            return int(star_str)
        except:
            return 0
    
    def extract_github_info(self, github_url):
        """从GitHub URL提取仓库信息"""
        if not github_url:
            return None, None
        
        # 匹配GitHub URL格式
        match = re.search(r'github\.com/([^/]+)/([^/?]+)', github_url)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
    def check_docker_support(self, github_url):
        """检查GitHub仓库的Docker支持情况"""
        owner, repo = self.extract_github_info(github_url)
        if not owner or not repo:
            return {
                'has_dockerfile': False,
                'has_docker_compose': False,
                'compose_complexity': 0,
                'docker_images': [],
                'official_image': False,
                'error': 'Invalid GitHub URL'
            }
        
        result = {
            'has_dockerfile': False,
            'has_docker_compose': False,
            'compose_complexity': 0,
            'docker_images': [],
            'official_image': False,
            'error': None
        }
        
        try:
            # 检查是否有Dockerfile
            dockerfile_url = f"https://api.github.com/repos/{owner}/{repo}/contents/Dockerfile"
            response = self.session.get(dockerfile_url)
            if response.status_code == 200:
                result['has_dockerfile'] = True
            
            # 检查是否有docker-compose文件
            compose_files = ['docker-compose.yml', 'docker-compose.yaml', 'compose.yml', 'compose.yaml']
            for compose_file in compose_files:
                compose_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{compose_file}"
                response = self.session.get(compose_url)
                if response.status_code == 200:
                    result['has_docker_compose'] = True
                    # 分析compose文件复杂度
                    try:
                        content_info = response.json()
                        if content_info.get('content'):
                            import base64
                            content = base64.b64decode(content_info['content']).decode('utf-8')
                            result['compose_complexity'] = self.analyze_compose_complexity(content)
                    except:
                        pass
                    break
            
            # 检查Docker Hub上是否有官方镜像
            dockerhub_url = f"https://hub.docker.com/v2/repositories/{repo}/"
            response = self.session.get(dockerhub_url)
            if response.status_code == 200:
                result['official_image'] = True
                result['docker_images'].append(f"{repo}:latest")
            
            # 检查GitHub官方Docker镜像
            ghcr_patterns = [
                f"ghcr.io/{owner}/{repo}",
                f"ghcr.io/{owner}/{repo.lower()}"
            ]
            for pattern in ghcr_patterns:
                result['docker_images'].append(pattern)
            
            time.sleep(0.1)  # 避免API限制
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def analyze_compose_complexity(self, compose_content):
        """分析docker-compose文件的复杂度"""
        if not compose_content:
            return 0
        
        complexity = 0
        
        # 计算服务数量
        services_count = len(re.findall(r'^\s+\w+:', compose_content, re.MULTILINE))
        complexity += services_count
        
        # 检查是否有数据库
        if re.search(r'(postgres|mysql|mongodb|redis|elasticsearch)', compose_content, re.IGNORECASE):
            complexity += 2
        
        # 检查是否有卷挂载
        volumes_count = len(re.findall(r'volumes:', compose_content))
        complexity += volumes_count * 0.5
        
        # 检查是否有网络配置
        if 'networks:' in compose_content:
            complexity += 1
        
        # 检查是否有环境变量
        env_count = len(re.findall(r'environment:', compose_content))
        complexity += env_count * 0.3
        
        return int(complexity)
    
    def calculate_migration_difficulty(self, app, docker_info):
        """计算移植难度评分 (越低越容易)"""
        score = 10  # 基础难度
        
        # Docker支持情况 (最重要)
        if docker_info['official_image']:
            score -= 4  # 有官方镜像，大幅降低难度
        elif docker_info['has_dockerfile']:
            score -= 3  # 有Dockerfile，降低难度
        
        if docker_info['has_docker_compose']:
            score -= 2  # 有docker-compose，降低难度
            # 根据compose复杂度调整
            complexity = docker_info['compose_complexity']
            if complexity <= 1:
                score -= 1  # 简单配置
            elif complexity <= 3:
                score += 0  # 中等复杂度
            else:
                score += 1  # 复杂配置
        
        # 根据应用类型调整难度
        category = app.get('tag', '').lower()
        if any(keyword in category for keyword in ['blog', 'static', 'wiki', 'cms']):
            score -= 1  # 静态/简单应用更容易
        elif any(keyword in category for keyword in ['database', 'big data', 'machine learning']):
            score += 2  # 复杂应用更难
        
        # 根据开发语言调整
        language = app.get('language', '').lower()
        if language in ['javascript', 'python', 'php', 'go']:
            score -= 0.5  # 常见语言更容易
        elif language in ['rust', 'c++', 'c']:
            score += 1  # 编译型语言可能更复杂
        
        # 确保评分在合理范围内
        return max(1, min(10, score))
    
    def get_difficulty_level(self, score):
        """根据评分获取难度等级"""
        if score <= 2:
            return "🟢 极易移植"
        elif score <= 4:
            return "🟡 容易移植"
        elif score <= 6:
            return "🟠 中等难度"
        elif score <= 8:
            return "🔴 较难移植"
        else:
            return "⚫ 高难度"
    
    def analyze_app(self, app):
        """分析单个应用的移植难度"""
        print(f"正在分析: {app['name']}")
        
        # 检查Docker支持
        docker_info = self.check_docker_support(app.get('github', ''))
        
        # 计算移植难度
        difficulty_score = self.calculate_migration_difficulty(app, docker_info)
        difficulty_level = self.get_difficulty_level(difficulty_score)
        
        # 计算综合评分 (优先级 * 移植容易程度)
        stars = self.get_star_count(app.get('stars', 0))
        priority_score = stars / 1000  # 将stars转换为优先级评分
        
        # 综合评分 = 优先级评分 / 移植难度 (越高越值得优先移植)
        migration_score = priority_score / difficulty_score if difficulty_score > 0 else 0
        
        result = {
            'name': app['name'],
            'description': app.get('description', ''),
            'category': app.get('tag', ''),
            'language': app.get('language', ''),
            'stars': stars,
            'stars_display': app.get('stars', '0'),
            'github': app.get('github', ''),
            'homepage': app.get('homepage', ''),
            
            # Docker相关信息
            'has_dockerfile': docker_info['has_dockerfile'],
            'has_docker_compose': docker_info['has_docker_compose'],
            'compose_complexity': docker_info['compose_complexity'],
            'official_image': docker_info['official_image'],
            'docker_images': docker_info['docker_images'],
            
            # 移植难度评估
            'difficulty_score': difficulty_score,
            'difficulty_level': difficulty_level,
            'migration_score': migration_score,
            'docker_error': docker_info.get('error')
        }
        
        return result
    
    def analyze_all_apps(self):
        """分析所有应用"""
        apps = self.load_apps()
        if not apps:
            return
        
        print(f"开始分析 {len(apps)} 个应用的移植难度...")
        
        # 只分析前100个高优先级应用，避免API限制
        high_priority_apps = sorted(apps, key=lambda x: self.get_star_count(x.get('stars', 0)), reverse=True)[:100]
        
        for i, app in enumerate(high_priority_apps, 1):
            try:
                result = self.analyze_app(app)
                self.results.append(result)
                print(f"  {i}/100 - {app['name']} - {result['difficulty_level']}")
                
                # 每10个应用休息一下，避免API限制
                if i % 10 == 0:
                    print(f"  已完成 {i} 个，休息 2 秒...")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"  分析 {app['name']} 时出错: {e}")
                continue
        
        # 按移植评分排序
        self.results.sort(key=lambda x: x['migration_score'], reverse=True)
    
    def save_results(self):
        """保存分析结果"""
        # 保存CSV文件
        csv_filename = 'migration_difficulty_analysis.csv'
        fieldnames = [
            '排名', '应用名称', '描述', '分类', 'GitHub Stars', '开发语言',
            '有Dockerfile', '有Docker Compose', 'Compose复杂度', '有官方镜像',
            '移植难度', '移植评分', 'GitHub链接', '官网链接'
        ]
        
        with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, app in enumerate(self.results, 1):
                writer.writerow({
                    '排名': i,
                    '应用名称': app['name'],
                    '描述': app['description'][:100] + '...' if len(app['description']) > 100 else app['description'],
                    '分类': app['category'],
                    'GitHub Stars': app['stars_display'],
                    '开发语言': app['language'],
                    '有Dockerfile': '✓' if app['has_dockerfile'] else '✗',
                    '有Docker Compose': '✓' if app['has_docker_compose'] else '✗',
                    'Compose复杂度': app['compose_complexity'],
                    '有官方镜像': '✓' if app['official_image'] else '✗',
                    '移植难度': app['difficulty_level'],
                    '移植评分': f"{app['migration_score']:.2f}",
                    'GitHub链接': app['github'],
                    '官网链接': app['homepage']
                })
        
        print(f"✅ CSV结果已保存到: {csv_filename}")
        
        # 保存JSON文件
        json_filename = 'migration_difficulty_analysis.json'
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'analysis_date': datetime.now().isoformat(),
                'total_analyzed': len(self.results),
                'apps': self.results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON结果已保存到: {json_filename}")
    
    def print_summary(self):
        """打印分析摘要"""
        if not self.results:
            return
        
        print("\n" + "=" * 80)
        print("🚀 懒猫应用移植难易程度分析结果")
        print("=" * 80)
        
        # 统计各难度等级数量
        difficulty_stats = {}
        docker_support_count = 0
        compose_support_count = 0
        official_image_count = 0
        
        for app in self.results:
            level = app['difficulty_level']
            difficulty_stats[level] = difficulty_stats.get(level, 0) + 1
            
            if app['has_dockerfile']:
                docker_support_count += 1
            if app['has_docker_compose']:
                compose_support_count += 1
            if app['official_image']:
                official_image_count += 1
        
        print(f"\n📊 分析统计:")
        print(f"   - 总分析应用数: {len(self.results)}")
        print(f"   - 有Dockerfile支持: {docker_support_count} ({docker_support_count/len(self.results)*100:.1f}%)")
        print(f"   - 有Docker Compose: {compose_support_count} ({compose_support_count/len(self.results)*100:.1f}%)")
        print(f"   - 有官方镜像: {official_image_count} ({official_image_count/len(self.results)*100:.1f}%)")
        
        print(f"\n📈 移植难度分布:")
        for level, count in sorted(difficulty_stats.items()):
            print(f"   - {level}: {count} 个应用")
        
        print(f"\n🎯 推荐优先移植 (Top 20):")
        print("-" * 80)
        
        for i, app in enumerate(self.results[:20], 1):
            docker_status = ""
            if app['official_image']:
                docker_status = "🐳官方镜像"
            elif app['has_docker_compose']:
                docker_status = f"📦Compose({app['compose_complexity']})"
            elif app['has_dockerfile']:
                docker_status = "🔧Dockerfile"
            else:
                docker_status = "❌无Docker"
            
            print(f"{i:2d}. {app['name']}")
            print(f"    ⭐ {app['stars_display']} stars | {app['difficulty_level']} | {docker_status}")
            print(f"    📂 {app['category']} | 💻 {app['language']}")
            if app['github']:
                print(f"    🔗 {app['github']}")
            print()

def main():
    analyzer = MigrationAnalyzer()
    
    print("🔍 开始分析懒猫应用移植难易程度...")
    print("注意: 这个过程可能需要几分钟时间，因为需要检查每个应用的GitHub仓库")
    
    # 分析所有应用
    analyzer.analyze_all_apps()
    
    if analyzer.results:
        # 打印摘要
        analyzer.print_summary()
        
        # 保存结果
        analyzer.save_results()
        
        print(f"\n🎉 分析完成！共分析了 {len(analyzer.results)} 个应用")
        print("📁 生成的文件:")
        print("   - migration_difficulty_analysis.csv (Excel可打开)")
        print("   - migration_difficulty_analysis.json (详细数据)")
    else:
        print("❌ 没有成功分析任何应用")

if __name__ == "__main__":
    main()