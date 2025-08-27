#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移植评估系统
综合评估GitHub应用的移植优先级和难度
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import math
from difflib import SequenceMatcher
from database_manager import DatabaseManager
from docker_compose_analyzer import DockerComposeAnalyzer, DockerComposeAnalysis

@dataclass 
class GitHubMetrics:
    """GitHub指标数据类"""
    stars: int
    forks: int
    open_issues: int
    created_at: str
    updated_at: str
    language: str
    topics: List[str]
    license: Optional[str]
    size: int  # KB

@dataclass
class MigrationScore:
    """移植评分数据类"""
    popularity_score: float  # 受欢迎程度 (0-30)
    activity_score: float    # 活跃度 (0-20)
    quality_score: float     # 质量分数 (0-20) 
    complexity_penalty: float # 复杂度惩罚 (0-20)
    uniqueness_bonus: float  # 独特性奖励 (0-10)
    total_score: float       # 总分 (0-100)
    priority_level: str      # 优先级等级

@dataclass
class MigrationEvaluation:
    """移植评估结果数据类"""
    repo_name: str
    repo_url: str
    description: str
    github_metrics: GitHubMetrics
    docker_analysis: Optional[DockerComposeAnalysis]
    migration_score: MigrationScore
    existing_similar_apps: List[Dict]
    effort_estimation: str  # 工作量预估: 低/中/高
    migration_risks: List[str]
    recommendations: List[str]
    evaluation_date: str

class MigrationEvaluator:
    def __init__(self, db_path: str = 'lazycat_apps.db'):
        """
        初始化移植评估器
        
        :param db_path: 数据库路径
        """
        self.db = DatabaseManager(db_path)
        self.docker_analyzer = DockerComposeAnalyzer()
        
        # 评分权重配置
        self.weights = {
            'popularity': 0.30,    # 受欢迎程度权重
            'activity': 0.20,      # 活跃度权重
            'quality': 0.20,       # 质量权重
            'complexity': -0.20,   # 复杂度惩罚权重
            'uniqueness': 0.10     # 独特性奖励权重
        }
        
        # 应用类别关键词映射
        self.category_keywords = {
            'productivity': ['note', 'task', 'todo', 'productivity', 'workspace', 'office'],
            'media': ['media', 'streaming', 'video', 'audio', 'music', 'player'],
            'development': ['code', 'git', 'ci', 'deployment', 'development', 'devops', 'build'],
            'monitoring': ['monitoring', 'metrics', 'dashboard', 'observability', 'alert'],
            'storage': ['storage', 'backup', 'sync', 'cloud', 'file', 'drive'],
            'security': ['password', 'auth', 'security', 'vault', 'encryption'],
            'communication': ['chat', 'message', 'communication', 'mail', 'forum'],
            'database': ['database', 'db', 'mysql', 'postgres', 'mongodb'],
            'analytics': ['analytics', 'statistics', 'data', 'visualization', 'report'],
            'automation': ['automation', 'workflow', 'scheduler', 'cron', 'task']
        }
    
    def evaluate_migration(self, repo_info: Dict, docker_compose_content: str = None) -> MigrationEvaluation:
        """
        评估单个应用的移植优先级
        
        :param repo_info: GitHub仓库信息
        :param docker_compose_content: Docker Compose内容
        :return: 移植评估结果
        """
        
        # 提取GitHub指标
        github_metrics = GitHubMetrics(
            stars=repo_info.get('stars', 0),
            forks=repo_info.get('forks', 0),
            open_issues=repo_info.get('open_issues', 0),
            created_at=repo_info.get('created_at', ''),
            updated_at=repo_info.get('updated_at', ''),
            language=repo_info.get('language', ''),
            topics=repo_info.get('topics', []),
            license=repo_info.get('license'),
            size=repo_info.get('size', 0)
        )
        
        # Docker分析
        docker_analysis = None
        if docker_compose_content:
            try:
                docker_analysis = self.docker_analyzer.analyze_docker_compose(docker_compose_content)
            except Exception as e:
                print(f"⚠️  Docker分析失败: {e}")
        
        # 检查相似应用
        similar_apps = self._find_similar_apps(
            repo_info.get('name', ''),
            repo_info.get('description', ''),
            github_metrics.topics
        )
        
        # 计算移植评分
        migration_score = self._calculate_migration_score(
            github_metrics, docker_analysis, similar_apps
        )
        
        # 评估工作量和风险
        effort_estimation = self._estimate_effort(github_metrics, docker_analysis)
        migration_risks = self._identify_risks(github_metrics, docker_analysis)
        recommendations = self._generate_recommendations(
            github_metrics, docker_analysis, similar_apps, migration_score
        )
        
        return MigrationEvaluation(
            repo_name=repo_info.get('full_name', ''),
            repo_url=repo_info.get('url', ''),
            description=repo_info.get('description', ''),
            github_metrics=github_metrics,
            docker_analysis=docker_analysis,
            migration_score=migration_score,
            existing_similar_apps=similar_apps,
            effort_estimation=effort_estimation,
            migration_risks=migration_risks,
            recommendations=recommendations,
            evaluation_date=datetime.now().isoformat()
        )
    
    def _calculate_migration_score(self, 
                                 github_metrics: GitHubMetrics,
                                 docker_analysis: Optional[DockerComposeAnalysis],
                                 similar_apps: List[Dict]) -> MigrationScore:
        """计算移植评分"""
        
        # 1. 受欢迎程度评分 (0-30分)
        popularity_score = min(30, math.log10(max(1, github_metrics.stars)) * 10)
        
        # 2. 活跃度评分 (0-20分)
        activity_score = self._calculate_activity_score(github_metrics)
        
        # 3. 质量评分 (0-20分) 
        quality_score = self._calculate_quality_score(github_metrics)
        
        # 4. 复杂度惩罚 (0-20分)
        complexity_penalty = 0
        if docker_analysis:
            # 复杂度越高，惩罚越大
            complexity_penalty = (docker_analysis.complexity_score / 100) * 20
        
        # 5. 独特性奖励 (0-10分)
        uniqueness_bonus = self._calculate_uniqueness_bonus(similar_apps)
        
        # 计算总分
        total_score = max(0, min(100, 
            popularity_score + 
            activity_score + 
            quality_score - 
            complexity_penalty + 
            uniqueness_bonus
        ))
        
        # 确定优先级等级
        if total_score >= 80:
            priority_level = "极高"
        elif total_score >= 65:
            priority_level = "高"
        elif total_score >= 50:
            priority_level = "中等"
        elif total_score >= 35:
            priority_level = "低"
        else:
            priority_level = "不推荐"
        
        return MigrationScore(
            popularity_score=popularity_score,
            activity_score=activity_score,
            quality_score=quality_score,
            complexity_penalty=complexity_penalty,
            uniqueness_bonus=uniqueness_bonus,
            total_score=total_score,
            priority_level=priority_level
        )
    
    def _calculate_activity_score(self, metrics: GitHubMetrics) -> float:
        """计算活跃度评分"""
        try:
            updated_date = datetime.fromisoformat(metrics.updated_at.replace('Z', '+00:00'))
            days_since_update = (datetime.now().replace(tzinfo=updated_date.tzinfo) - updated_date).days
            
            # 更新越频繁，分数越高
            if days_since_update <= 30:
                return 20.0
            elif days_since_update <= 90:
                return 15.0
            elif days_since_update <= 180:
                return 10.0
            elif days_since_update <= 365:
                return 5.0
            else:
                return 0.0
        except:
            return 5.0  # 默认分数
    
    def _calculate_quality_score(self, metrics: GitHubMetrics) -> float:
        """计算质量评分"""
        score = 0.0
        
        # 有许可证 +5分
        if metrics.license:
            score += 5.0
        
        # Fork数量评分 +0-5分
        score += min(5.0, math.log10(max(1, metrics.forks)) * 2)
        
        # Issue数量适中 +0-5分
        if metrics.open_issues < 50:
            score += 5.0
        elif metrics.open_issues < 100:
            score += 3.0
        elif metrics.open_issues < 200:
            score += 1.0
        
        # 有topic标签 +0-5分
        if metrics.topics:
            score += min(5.0, len(metrics.topics))
        
        return min(20.0, score)
    
    def _calculate_uniqueness_bonus(self, similar_apps: List[Dict]) -> float:
        """计算独特性奖励"""
        if not similar_apps:
            return 10.0  # 完全独特
        
        # 相似应用越少，奖励越高
        similarity_penalty = len(similar_apps) * 2
        return max(0.0, 10.0 - similarity_penalty)
    
    def _find_similar_apps(self, name: str, description: str, topics: List[str]) -> List[Dict]:
        """查找相似的现有应用"""
        similar_apps = []
        
        try:
            # 搜索现有应用
            all_apps, _ = self.db.search_apps('', limit=1000, offset=0)
            
            for app in all_apps:
                app_name = app[1]  # name字段
                app_brief = app[2] or ''  # brief字段
                
                # 计算名称相似度
                name_similarity = SequenceMatcher(None, name.lower(), app_name.lower()).ratio()
                
                # 计算描述相似度
                desc_similarity = SequenceMatcher(None, description.lower(), app_brief.lower()).ratio()
                
                # 检查topic匹配
                topic_match = 0
                if topics:
                    for topic in topics:
                        if topic.lower() in app_name.lower() or topic.lower() in app_brief.lower():
                            topic_match += 1
                    topic_similarity = topic_match / len(topics) if topics else 0
                else:
                    topic_similarity = 0
                
                # 综合相似度
                overall_similarity = max(name_similarity, desc_similarity, topic_similarity)
                
                # 如果相似度超过阈值，认为是相似应用
                if overall_similarity > 0.6:
                    similar_apps.append({
                        'id': app[0],
                        'name': app_name,
                        'brief': app_brief,
                        'similarity': overall_similarity,
                        'count': app[3]  # 下载量
                    })
                    
        except Exception as e:
            print(f"⚠️  查找相似应用失败: {e}")
        
        # 按相似度排序
        similar_apps.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_apps[:5]  # 最多返回5个相似应用
    
    def _estimate_effort(self, 
                        github_metrics: GitHubMetrics,
                        docker_analysis: Optional[DockerComposeAnalysis]) -> str:
        """评估移植工作量"""
        effort_factors = []
        
        # Docker复杂度影响
        if docker_analysis:
            if docker_analysis.complexity_level == "复杂":
                effort_factors.append("high")
            elif docker_analysis.complexity_level == "中等":
                effort_factors.append("medium")
            else:
                effort_factors.append("low")
            
            # 需要构建的情况
            if docker_analysis.requires_build:
                effort_factors.append("high")
        
        # 项目规模影响
        if github_metrics.size > 10000:  # 大于10MB
            effort_factors.append("high")
        elif github_metrics.size > 1000:  # 大于1MB
            effort_factors.append("medium")
        else:
            effort_factors.append("low")
        
        # 语言影响
        complex_languages = ['C++', 'C', 'Rust', 'Go', 'Java', 'Scala']
        if github_metrics.language in complex_languages:
            effort_factors.append("medium")
        
        # 综合评估
        if "high" in effort_factors:
            return "高"
        elif effort_factors.count("medium") >= 2:
            return "高" 
        elif "medium" in effort_factors:
            return "中"
        else:
            return "低"
    
    def _identify_risks(self, 
                       github_metrics: GitHubMetrics,
                       docker_analysis: Optional[DockerComposeAnalysis]) -> List[str]:
        """识别移植风险"""
        risks = []
        
        # GitHub相关风险
        if github_metrics.open_issues > 100:
            risks.append("项目存在大量未解决问题，可能影响稳定性")
        
        if github_metrics.stars < 50:
            risks.append("项目关注度较低，缺乏社区支持")
        
        if not github_metrics.license:
            risks.append("缺少明确的开源许可证，存在法律风险")
        
        # 更新频率风险
        try:
            updated_date = datetime.fromisoformat(github_metrics.updated_at.replace('Z', '+00:00'))
            days_since_update = (datetime.now().replace(tzinfo=updated_date.tzinfo) - updated_date).days
            
            if days_since_update > 365:
                risks.append("项目超过一年未更新，可能已停止维护")
            elif days_since_update > 180:
                risks.append("项目更新频率较低，维护活跃度不高")
        except:
            risks.append("无法确定项目更新状态")
        
        # Docker相关风险
        if docker_analysis:
            if docker_analysis.requires_build:
                risks.append("需要本地构建，可能存在构建环境兼容性问题")
            
            if docker_analysis.complexity_level == "复杂":
                risks.append("Docker配置复杂，部署和维护难度较高")
            
            if len(docker_analysis.external_dependencies) > 3:
                risks.append("外部依赖过多，可能影响系统稳定性")
        
        return risks
    
    def _generate_recommendations(self, 
                                github_metrics: GitHubMetrics,
                                docker_analysis: Optional[DockerComposeAnalysis],
                                similar_apps: List[Dict],
                                migration_score: MigrationScore) -> List[str]:
        """生成移植建议"""
        recommendations = []
        
        # 基于评分的建议
        if migration_score.total_score >= 80:
            recommendations.append("🌟 强烈推荐移植，这是一个高质量的热门应用")
        elif migration_score.total_score >= 65:
            recommendations.append("👍 推荐移植，具有较好的用户需求和技术可行性")
        elif migration_score.total_score >= 50:
            recommendations.append("⚖️ 可以考虑移植，但需要评估资源投入")
        else:
            recommendations.append("❌ 暂不建议移植，投入产出比不理想")
        
        # 相似应用建议
        if similar_apps:
            top_similar = similar_apps[0]
            recommendations.append(f"⚠️ 注意：已存在相似应用'{top_similar['name']}'，相似度{top_similar['similarity']:.2f}")
        
        # Docker相关建议
        if docker_analysis:
            if docker_analysis.complexity_level == "简单":
                recommendations.append("✅ Docker配置简单，易于部署")
            elif docker_analysis.complexity_level == "复杂":
                recommendations.append("⚠️ Docker配置复杂，建议分阶段实施")
            
            if docker_analysis.requires_build:
                recommendations.append("🔧 需要本地构建，确保构建环境准备就绪")
        
        # 社区活跃度建议
        if github_metrics.stars > 1000:
            recommendations.append("👥 项目拥有活跃的用户社区，有利于问题解决")
        
        return recommendations
    
    def batch_evaluate(self, repo_list: List[Dict], docker_contents: Dict[str, str] = None) -> List[MigrationEvaluation]:
        """
        批量评估多个应用
        
        :param repo_list: GitHub仓库列表
        :param docker_contents: Docker Compose内容字典 {repo_name: content}
        :return: 评估结果列表
        """
        evaluations = []
        
        print(f"📊 开始批量评估 {len(repo_list)} 个应用...")
        
        for i, repo_info in enumerate(repo_list, 1):
            try:
                repo_name = repo_info.get('full_name', '')
                docker_content = docker_contents.get(repo_name) if docker_contents else None
                
                print(f"[{i}/{len(repo_list)}] 评估 {repo_name}...")
                
                evaluation = self.evaluate_migration(repo_info, docker_content)
                evaluations.append(evaluation)
                
            except Exception as e:
                print(f"❌ 评估 {repo_info.get('full_name', '未知')} 失败: {e}")
                continue
        
        # 按评分排序
        evaluations.sort(key=lambda x: x.migration_score.total_score, reverse=True)
        
        print(f"✅ 批量评估完成，共评估 {len(evaluations)} 个应用")
        return evaluations
    
    def generate_migration_report(self, evaluations: List[MigrationEvaluation], 
                                save_path: str = None) -> str:
        """
        生成移植优先级报告
        
        :param evaluations: 评估结果列表
        :param save_path: 保存路径
        :return: 报告内容
        """
        lines = []
        lines.append("# 懒猫微服应用移植优先级报告")
        lines.append("=" * 60)
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"评估应用数量: {len(evaluations)}")
        lines.append("")
        
        # 统计概览
        priority_counts = {}
        for eval_result in evaluations:
            level = eval_result.migration_score.priority_level
            priority_counts[level] = priority_counts.get(level, 0) + 1
        
        lines.append("## 📊 优先级分布")
        for level, count in priority_counts.items():
            lines.append(f"- **{level}**: {count} 个应用")
        lines.append("")
        
        # Top 10推荐
        lines.append("## 🏆 Top 10 推荐移植应用")
        lines.append("")
        
        for i, eval_result in enumerate(evaluations[:10], 1):
            score = eval_result.migration_score
            lines.append(f"### {i}. {eval_result.repo_name}")
            lines.append(f"**评分**: {score.total_score:.1f}/100 ({score.priority_level})")
            lines.append(f"**描述**: {eval_result.description[:100]}...")
            lines.append(f"**GitHub**: ⭐ {eval_result.github_metrics.stars} | 🍴 {eval_result.github_metrics.forks}")
            
            if eval_result.docker_analysis:
                lines.append(f"**部署复杂度**: {eval_result.docker_analysis.complexity_level}")
            
            lines.append(f"**工作量预估**: {eval_result.effort_estimation}")
            lines.append(f"**相似应用**: {len(eval_result.existing_similar_apps)} 个")
            lines.append(f"🔗 {eval_result.repo_url}")
            lines.append("")
        
        # 详细分析
        lines.append("## 📋 详细评估结果")
        lines.append("")
        
        for eval_result in evaluations:
            lines.append(f"### {eval_result.repo_name}")
            
            score = eval_result.migration_score
            lines.append(f"- **总评分**: {score.total_score:.1f}/100 ({score.priority_level})")
            lines.append(f"  - 受欢迎程度: {score.popularity_score:.1f}/30")
            lines.append(f"  - 活跃度: {score.activity_score:.1f}/20")  
            lines.append(f"  - 质量评分: {score.quality_score:.1f}/20")
            lines.append(f"  - 复杂度惩罚: -{score.complexity_penalty:.1f}")
            lines.append(f"  - 独特性奖励: +{score.uniqueness_bonus:.1f}")
            
            if eval_result.migration_risks:
                lines.append(f"- **移植风险**:")
                for risk in eval_result.migration_risks:
                    lines.append(f"  - ⚠️ {risk}")
            
            if eval_result.recommendations:
                lines.append(f"- **建议**:")
                for rec in eval_result.recommendations:
                    lines.append(f"  - {rec}")
            
            lines.append("")
        
        report_content = "\n".join(lines)
        
        # 保存报告
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"📄 报告已保存到: {save_path}")
        
        return report_content

def main():
    """测试函数"""
    print("🔍 移植评估系统测试")
    print("=" * 50)
    
    # 模拟GitHub仓库数据
    sample_repo = {
        'full_name': 'example/awesome-app',
        'name': 'awesome-app',
        'description': 'An awesome self-hosted productivity application',
        'url': 'https://github.com/example/awesome-app',
        'stars': 1500,
        'forks': 300,
        'open_issues': 25,
        'created_at': '2022-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z',
        'language': 'JavaScript',
        'topics': ['productivity', 'self-hosted', 'web'],
        'license': 'MIT',
        'size': 2048
    }
    
    # 模拟Docker Compose内容
    sample_docker_compose = """
version: '3.8'
services:
  app:
    image: node:16-alpine
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    volumes:
      - ./data:/app/data
"""
    
    # 创建评估器并测试
    evaluator = MigrationEvaluator()
    
    try:
        evaluation = evaluator.evaluate_migration(sample_repo, sample_docker_compose)
        
        print(f"✅ 评估完成!")
        print(f"应用: {evaluation.repo_name}")
        print(f"总分: {evaluation.migration_score.total_score:.1f}/100")
        print(f"优先级: {evaluation.migration_score.priority_level}")
        print(f"工作量: {evaluation.effort_estimation}")
        print(f"风险数量: {len(evaluation.migration_risks)}")
        print(f"相似应用: {len(evaluation.existing_similar_apps)}")
        
    except Exception as e:
        print(f"❌ 评估失败: {e}")

if __name__ == '__main__':
    main()