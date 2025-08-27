#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker Compose分析器
分析docker-compose.yml文件，评估部署复杂度和移植难度
"""

import yaml
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import json

@dataclass
class ServiceInfo:
    """服务信息数据类"""
    name: str
    image: str
    ports: List[str]
    volumes: List[str]
    environment: Dict[str, str]
    depends_on: List[str]
    networks: List[str]
    restart_policy: str
    build_context: Optional[str] = None

@dataclass
class DockerComposeAnalysis:
    """Docker Compose分析结果数据类"""
    services_count: int
    total_ports: int
    exposed_ports: List[int]
    requires_build: bool
    external_dependencies: List[str]
    storage_requirements: List[str]
    network_requirements: List[str]
    complexity_level: str  # 简单/中等/复杂
    complexity_score: int  # 0-100
    deployment_notes: List[str]
    migration_warnings: List[str]
    services: List[ServiceInfo]

class DockerComposeAnalyzer:
    def __init__(self):
        """初始化分析器"""
        self.common_databases = [
            'mysql', 'postgres', 'postgresql', 'mongodb', 'redis', 
            'elasticsearch', 'mariadb', 'influxdb', 'clickhouse'
        ]
        self.common_services = [
            'nginx', 'apache', 'traefik', 'caddy', 'haproxy',
            'rabbitmq', 'kafka', 'prometheus', 'grafana'
        ]
        
    def analyze_docker_compose(self, content: str) -> DockerComposeAnalysis:
        """
        分析docker-compose.yml内容
        
        :param content: docker-compose.yml文件内容
        :return: 分析结果
        """
        try:
            # 解析YAML
            compose_data = yaml.safe_load(content)
            
            if not compose_data or 'services' not in compose_data:
                raise ValueError("无效的docker-compose.yml文件")
            
            services = compose_data['services']
            services_info = []
            
            # 分析每个服务
            for service_name, service_config in services.items():
                service_info = self._analyze_service(service_name, service_config)
                services_info.append(service_info)
            
            # 生成整体分析
            return self._generate_analysis(services_info, compose_data)
            
        except yaml.YAMLError as e:
            raise ValueError(f"YAML解析错误: {e}")
    
    def _analyze_service(self, name: str, config: Dict) -> ServiceInfo:
        """分析单个服务"""
        return ServiceInfo(
            name=name,
            image=config.get('image', ''),
            ports=self._extract_ports(config.get('ports', [])),
            volumes=self._extract_volumes(config.get('volumes', [])),
            environment=self._extract_environment(config.get('environment', {})),
            depends_on=config.get('depends_on', []) if isinstance(config.get('depends_on', []), list) else list(config.get('depends_on', {}).keys()),
            networks=config.get('networks', []) if isinstance(config.get('networks', []), list) else list(config.get('networks', {}).keys()),
            restart_policy=config.get('restart', 'no'),
            build_context=config.get('build', {}).get('context') if isinstance(config.get('build'), dict) else config.get('build')
        )
    
    def _extract_ports(self, ports: List) -> List[str]:
        """提取端口映射"""
        port_list = []
        for port in ports:
            if isinstance(port, str):
                port_list.append(port)
            elif isinstance(port, int):
                port_list.append(str(port))
            elif isinstance(port, dict):
                target = port.get('target', '')
                published = port.get('published', '')
                if target and published:
                    port_list.append(f"{published}:{target}")
        return port_list
    
    def _extract_volumes(self, volumes: List) -> List[str]:
        """提取卷映射"""
        volume_list = []
        for volume in volumes:
            if isinstance(volume, str):
                volume_list.append(volume)
            elif isinstance(volume, dict):
                source = volume.get('source', '')
                target = volume.get('target', '')
                if source and target:
                    volume_list.append(f"{source}:{target}")
        return volume_list
    
    def _extract_environment(self, env) -> Dict[str, str]:
        """提取环境变量"""
        if isinstance(env, list):
            env_dict = {}
            for item in env:
                if '=' in str(item):
                    key, value = str(item).split('=', 1)
                    env_dict[key] = value
            return env_dict
        elif isinstance(env, dict):
            return {k: str(v) for k, v in env.items()}
        return {}
    
    def _generate_analysis(self, services_info: List[ServiceInfo], compose_data: Dict) -> DockerComposeAnalysis:
        """生成分析结果"""
        
        # 统计基本信息
        services_count = len(services_info)
        all_ports = []
        requires_build = False
        external_deps = []
        storage_reqs = []
        network_reqs = []
        deployment_notes = []
        migration_warnings = []
        
        # 分析每个服务
        for service in services_info:
            # 收集端口
            for port in service.ports:
                if ':' in port:
                    external_port = port.split(':')[0]
                    try:
                        all_ports.append(int(external_port))
                    except ValueError:
                        pass
                else:
                    try:
                        all_ports.append(int(port))
                    except ValueError:
                        pass
            
            # 检查是否需要构建
            if service.build_context:
                requires_build = True
                deployment_notes.append(f"服务 '{service.name}' 需要本地构建")
            
            # 检查外部依赖
            image = service.image.lower()
            for db in self.common_databases:
                if db in image:
                    external_deps.append(f"数据库: {db}")
                    break
            
            for svc in self.common_services:
                if svc in image:
                    external_deps.append(f"服务: {svc}")
                    break
            
            # 存储需求
            for volume in service.volumes:
                if not volume.startswith('/tmp') and ':' in volume:
                    host_path = volume.split(':')[0]
                    if not host_path.startswith('.') and not host_path.startswith('/'):
                        storage_reqs.append(f"持久化存储: {volume}")
                    else:
                        storage_reqs.append(f"本地存储: {volume}")
        
        # 网络需求
        if 'networks' in compose_data:
            for network_name, network_config in compose_data['networks'].items():
                if isinstance(network_config, dict) and network_config.get('external'):
                    network_reqs.append(f"外部网络: {network_name}")
                else:
                    network_reqs.append(f"内部网络: {network_name}")
        
        # 计算复杂度分数
        complexity_score = self._calculate_complexity_score(
            services_count, len(all_ports), requires_build, 
            len(external_deps), len(storage_reqs), len(network_reqs)
        )
        
        # 确定复杂度等级
        if complexity_score <= 30:
            complexity_level = "简单"
        elif complexity_score <= 60:
            complexity_level = "中等"
        else:
            complexity_level = "复杂"
        
        # 生成部署注意事项
        if services_count > 5:
            deployment_notes.append("服务数量较多，建议分阶段部署")
        
        if len(all_ports) > 10:
            migration_warnings.append("端口数量较多，需要检查端口冲突")
        
        if requires_build:
            migration_warnings.append("需要本地构建镜像，确保构建环境正确")
        
        if external_deps:
            deployment_notes.append("依赖外部服务，需要预先准备")
        
        # 去重
        external_deps = list(set(external_deps))
        storage_reqs = list(set(storage_reqs))
        network_reqs = list(set(network_reqs))
        
        return DockerComposeAnalysis(
            services_count=services_count,
            total_ports=len(all_ports),
            exposed_ports=sorted(set(all_ports)),
            requires_build=requires_build,
            external_dependencies=external_deps,
            storage_requirements=storage_reqs,
            network_requirements=network_reqs,
            complexity_level=complexity_level,
            complexity_score=complexity_score,
            deployment_notes=deployment_notes,
            migration_warnings=migration_warnings,
            services=services_info
        )
    
    def _calculate_complexity_score(self, services_count: int, ports_count: int, 
                                  requires_build: bool, deps_count: int,
                                  storage_count: int, network_count: int) -> int:
        """
        计算复杂度分数 (0-100)
        """
        score = 0
        
        # 服务数量权重 (0-30分)
        score += min(services_count * 5, 30)
        
        # 端口数量权重 (0-15分)
        score += min(ports_count * 2, 15)
        
        # 构建需求权重 (0-20分)
        if requires_build:
            score += 20
        
        # 外部依赖权重 (0-20分)
        score += min(deps_count * 5, 20)
        
        # 存储需求权重 (0-10分)
        score += min(storage_count * 2, 10)
        
        # 网络需求权重 (0-5分)
        score += min(network_count * 1, 5)
        
        return min(score, 100)
    
    def generate_deployment_preview(self, analysis: DockerComposeAnalysis) -> str:
        """
        生成部署预览文档
        
        :param analysis: 分析结果
        :return: 部署预览文本
        """
        lines = []
        lines.append("# Docker Compose 部署分析报告")
        lines.append("=" * 50)
        lines.append("")
        
        # 基本信息
        lines.append("## 基本信息")
        lines.append(f"- **服务数量**: {analysis.services_count}")
        lines.append(f"- **复杂度等级**: {analysis.complexity_level} ({analysis.complexity_score}/100)")
        lines.append(f"- **端口需求**: {analysis.total_ports} 个端口")
        lines.append(f"- **需要构建**: {'是' if analysis.requires_build else '否'}")
        lines.append("")
        
        # 端口映射
        if analysis.exposed_ports:
            lines.append("## 端口映射")
            for port in analysis.exposed_ports:
                lines.append(f"- `{port}`")
            lines.append("")
        
        # 外部依赖
        if analysis.external_dependencies:
            lines.append("## 外部依赖")
            for dep in analysis.external_dependencies:
                lines.append(f"- {dep}")
            lines.append("")
        
        # 存储需求
        if analysis.storage_requirements:
            lines.append("## 存储需求")
            for storage in analysis.storage_requirements:
                lines.append(f"- {storage}")
            lines.append("")
        
        # 网络需求
        if analysis.network_requirements:
            lines.append("## 网络需求")
            for network in analysis.network_requirements:
                lines.append(f"- {network}")
            lines.append("")
        
        # 部署注意事项
        if analysis.deployment_notes:
            lines.append("## 部署注意事项")
            for note in analysis.deployment_notes:
                lines.append(f"- ⚠️  {note}")
            lines.append("")
        
        # 迁移警告
        if analysis.migration_warnings:
            lines.append("## 迁移警告")
            for warning in analysis.migration_warnings:
                lines.append(f"- ❌ {warning}")
            lines.append("")
        
        # 服务详情
        lines.append("## 服务详情")
        for service in analysis.services:
            lines.append(f"### {service.name}")
            lines.append(f"- **镜像**: `{service.image}`")
            if service.ports:
                lines.append(f"- **端口**: {', '.join(service.ports)}")
            if service.volumes:
                lines.append(f"- **卷**: {len(service.volumes)} 个")
            if service.environment:
                lines.append(f"- **环境变量**: {len(service.environment)} 个")
            if service.depends_on:
                lines.append(f"- **依赖服务**: {', '.join(service.depends_on)}")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_analysis(self, analysis: DockerComposeAnalysis, filepath: str):
        """
        保存分析结果到文件
        
        :param analysis: 分析结果
        :param filepath: 文件路径
        """
        # 转换为可序列化的字典
        analysis_dict = asdict(analysis)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 分析结果已保存到: {filepath}")

def main():
    """测试函数"""
    print("🔍 Docker Compose 分析器测试")
    print("=" * 50)
    
    # 示例docker-compose.yml内容
    sample_compose = """
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - app
    restart: unless-stopped

  app:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./data:/app/data
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - db_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  db_data:
  redis_data:

networks:
  default:
    driver: bridge
"""
    
    # 创建分析器并分析
    analyzer = DockerComposeAnalyzer()
    
    try:
        analysis = analyzer.analyze_docker_compose(sample_compose)
        
        print(f"✅ 分析完成!")
        print(f"服务数量: {analysis.services_count}")
        print(f"复杂度: {analysis.complexity_level} ({analysis.complexity_score}/100)")
        print(f"端口数量: {analysis.total_ports}")
        print(f"需要构建: {analysis.requires_build}")
        print()
        
        # 生成预览
        preview = analyzer.generate_deployment_preview(analysis)
        print("📋 部署预览:")
        print(preview[:500] + "..." if len(preview) > 500 else preview)
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")

if __name__ == '__main__':
    main()