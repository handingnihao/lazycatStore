# Overleaf移植到懒猫微服完整方案

## 项目概述
Overleaf是一个开源的在线LaTeX编辑器，支持实时协作编辑。该项目已经完全容器化，官方提供完整的Docker部署方案，非常适合移植到懒猫微服平台。

## 项目优势分析

### 技术优势
- **纯Web应用**：完全基于Web的架构，无桌面依赖
- **官方Docker支持**：提供完整的容器化部署方案
- **微服务架构**：多个独立服务，易于管理和扩展
- **实时协作**：支持多人同时编辑LaTeX文档
- **完整LaTeX环境**：内置完整的TeX Live发行版

### 实用价值
- **学术写作**：论文、报告、书籍的专业排版
- **数学公式**：复杂数学公式的精确表达
- **科研协作**：团队协作编写学术文档
- **教育应用**：数学、物理等学科的教学材料制作

## 移植实施步骤

### 第一步：环境准备

```bash
# 创建工作目录
mkdir -p overleaf-lzc
cd overleaf-lzc

# 创建数据目录
mkdir -p data/sharelatex
mkdir -p data/mongo
mkdir -p data/redis
mkdir -p logs
```

### 第二步：准备manifest.yml文件

```yaml
lzc-sdk-version: 0.1
name: Overleaf在线LaTeX编辑器
package: com.overleaf.overleaf
version: 5.0.0
description: 开源的在线实时协作LaTeX编辑器，支持多人同时编辑学术文档
license: AGPL-3.0
homepage: https://github.com/overleaf/overleaf
author: Overleaf Team
application:
  subdomain: overleaf
  routes:
    - /=http://localhost:80/
  environment:
    - OVERLEAF_APP_NAME=Overleaf Community Edition
    - OVERLEAF_MONGO_URL=mongodb://mongo:27017/sharelatex
    - OVERLEAF_REDIS_HOST=redis
    - OVERLEAF_REDIS_PORT=6379
    - OVERLEAF_SITE_URL=https://overleaf.你的微服名称.heiyu.space
    - OVERLEAF_NAV_TITLE=Overleaf CE
  volumes:
    - /lzcapp/data/sharelatex:/var/lib/sharelatex
    - /lzcapp/data/mongo:/data/db
    - /lzcapp/data/redis:/data
    - /lzcapp/logs:/var/log
  ports:
    - 80:80       # Overleaf主服务
    - 27017:27017 # MongoDB
    - 6379:6379   # Redis
```

### 第三步：创建Docker Compose配置

```yaml
# docker-compose.yml
version: '2.2'
services:
    sharelatex:
        restart: always
        image: sharelatex/sharelatex:latest
        container_name: sharelatex
        depends_on:
            mongo:
                condition: service_healthy
            redis:
                condition: service_started
        ports:
            - 80:80
        links:
            - mongo
            - redis
        volumes:
            - ./data/sharelatex:/var/lib/sharelatex
            - ./logs:/var/log/sharelatex
        environment:
            OVERLEAF_APP_NAME: Overleaf Community Edition
            OVERLEAF_MONGO_URL: mongodb://mongo:27017/sharelatex
            OVERLEAF_REDIS_HOST: redis
            OVERLEAF_REDIS_PORT: 6379
            OVERLEAF_SITE_URL: https://overleaf.你的微服名称.heiyu.space
            OVERLEAF_NAV_TITLE: Overleaf CE
            # 邮件配置（可选）
            # OVERLEAF_EMAIL_FROM_ADDRESS: noreply@your-domain.com
            # OVERLEAF_EMAIL_SMTP_HOST: smtp.your-domain.com
            # OVERLEAF_EMAIL_SMTP_PORT: 587
            # OVERLEAF_EMAIL_SMTP_SECURE: false
            # OVERLEAF_EMAIL_SMTP_USER: your-smtp-username
            # OVERLEAF_EMAIL_SMTP_PASS: your-smtp-password
            
            # LaTeX编译超时设置
            OVERLEAF_COMPILE_TIMEOUT: 60000
            OVERLEAF_COMPILE_MEMORY_MAX: 1000

    mongo:
        restart: always
        image: mongo:4.4
        container_name: mongo
        expose:
            - 27017
        volumes:
            - ./data/mongo:/data/db
        healthcheck:
            test: echo 'db.stats().ok' | mongo localhost:27017/test --quiet
            interval: 10s
            timeout: 10s
            retries: 5
        command: --replSet overleaf

    redis:
        restart: always
        image: redis:6.2
        container_name: redis
        expose:
            - 6379
        volumes:
            - ./data/redis:/data

    # MongoDB副本集初始化（仅在首次部署时需要）
    mongo-init:
        image: mongo:4.4
        depends_on:
            - mongo
        command: >
            bash -c "
                sleep 10;
                mongo --host mongo:27017 --eval '
                    rs.initiate({
                        _id: \"overleaf\",
                        members: [
                            { _id: 0, host: \"mongo:27017\" }
                        ]
                    })
                '
            "
        restart: "no"
```

### 第四步：准备部署文件

```bash
# 克隆项目源代码（可选，用于获取最新配置）
git clone https://github.com/overleaf/overleaf.git
cd overleaf

# 复制官方配置文件
cp docker-compose.yml ../overleaf-lzc/
cp -r doc ../overleaf-lzc/

# 回到工作目录
cd ../overleaf-lzc

# 创建content.tar
tar -cf content.tar docker-compose.yml doc/ data/

# 准备图标
# 可以从官方网站下载或使用以下命令创建
echo "准备应用图标..." > icon.png
```

### 第五步：创建LPK包

```bash
# 打包为LPK格式
zip -r overleaf.lpk manifest.yml content.tar icon.png
```

### 第六步：部署到懒猫微服

```bash
# 连接到懒猫微服
ssh root@你的微服名称.heiyu.space

# 安装应用
lzc-cli app install overleaf.lpk

# 检查应用状态
lzc-cli app status com.overleaf.overleaf

# 查看应用日志
lzc-cli app logs com.overleaf.overleaf
```

## 高级配置

### 1. 管理员账户设置

```bash
# 进入Overleaf容器
docker exec -it sharelatex /bin/bash

# 创建管理员用户
cd /var/www/sharelatex
grunt user:create-admin --email=admin@example.com
```

### 2. 邮件服务配置

```yaml
# 在docker-compose.yml中添加邮件配置
environment:
  OVERLEAF_EMAIL_FROM_ADDRESS: noreply@your-domain.com
  OVERLEAF_EMAIL_SMTP_HOST: smtp.your-domain.com
  OVERLEAF_EMAIL_SMTP_PORT: 587
  OVERLEAF_EMAIL_SMTP_SECURE: false
  OVERLEAF_EMAIL_SMTP_USER: your-smtp-username
  OVERLEAF_EMAIL_SMTP_PASS: your-smtp-password
```

### 3. 资源限制优化

```yaml
# 性能优化配置
environment:
  OVERLEAF_COMPILE_TIMEOUT: 120000      # 编译超时2分钟
  OVERLEAF_COMPILE_MEMORY_MAX: 2000     # 最大内存2GB
  OVERLEAF_MAX_COMPILE_REQUESTS: 10     # 最大并发编译数
```

### 4. SSL/HTTPS配置

```bash
# 如果需要自定义SSL证书
volumes:
  - ./ssl:/etc/ssl/certs
```

## 功能验证清单

### 基础功能测试
- [ ] 网站正常访问
- [ ] 用户注册和登录
- [ ] 创建新项目
- [ ] LaTeX文档编辑
- [ ] 实时预览功能
- [ ] PDF编译和下载

### 高级功能测试
- [ ] 多人协作编辑
- [ ] 项目历史版本
- [ ] 模板库使用
- [ ] 文件上传功能
- [ ] Git集成（如果配置）
- [ ] 数学公式渲染

### 性能测试
- [ ] 文档编译速度
- [ ] 大文档处理能力
- [ ] 并发用户支持
- [ ] 内存和CPU使用情况

## 常见问题解决

### 1. MongoDB副本集问题
```bash
# 如果MongoDB副本集初始化失败
docker exec -it mongo mongo
> rs.initiate({_id: "overleaf", members: [{_id: 0, host: "mongo:27017"}]})
```

### 2. LaTeX包缺失
```bash
# 进入容器安装额外LaTeX包
docker exec -it sharelatex /bin/bash
tlmgr install [包名]
```

### 3. 编译超时问题
```bash
# 增加编译超时时间
OVERLEAF_COMPILE_TIMEOUT: 180000  # 3分钟
```

### 4. 内存不足
```bash
# 增加编译内存限制
OVERLEAF_COMPILE_MEMORY_MAX: 3000  # 3GB
```

## 维护和备份

### 数据备份
```bash
# 备份MongoDB数据
docker exec mongo mongodump --out /backup

# 备份用户文档
tar -czf backup-$(date +%Y%m%d).tar.gz data/sharelatex/
```

### 版本更新
```bash
# 停止服务
docker-compose down

# 拉取最新镜像
docker pull sharelatex/sharelatex:latest

# 重启服务
docker-compose up -d
```

### 日志监控
```bash
# 查看实时日志
docker-compose logs -f sharelatex

# 查看特定服务日志
docker logs sharelatex
```

## 使用场景

### 学术研究
- 论文写作和格式化
- 学术期刊投稿
- 学位论文撰写
- 研究报告制作

### 教育应用
- 数学课件制作
- 物理公式教学
- 计算机科学文档
- 在线LaTeX教学

### 协作写作
- 团队研究项目
- 多作者书籍编写
- 技术文档协作
- 开源项目文档

## 总结

Overleaf是一个极其适合懒猫微服的项目，具有以下优势：

✅ **完全Web化**：无任何桌面应用依赖  
✅ **官方Docker支持**：成熟的容器化方案  
✅ **实用价值极高**：学术和教育领域的刚需工具  
✅ **部署相对简单**：官方提供完整部署文档  
✅ **社区活跃**：大量用户和完善的支持  
✅ **功能完整**：提供完整的LaTeX编辑和协作环境  

通过部署Overleaf，不仅可以学习现代Web应用的部署，还能获得一个非常实用的学术写作工具。 