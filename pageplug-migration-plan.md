# PagePlug移植到懒猫微服完整方案

## 项目概述
PagePlug是一个低代码平台，基于Appsmith进行中国化改造。该项目已经具备完整的容器化部署能力，非常适合移植到懒猫微服平台。

## 移植准备工作

### 1. 环境要求确认
- **服务器配置**：至少4G内存 + 2核CPU（官方推荐）
- **存储需求**：MongoDB数据库 + Redis缓存
- **网络要求**：支持HTTP/HTTPS访问

### 2. 代码结构分析
```
pageplug/
├── app/
│   ├── client/          # React前端项目
│   ├── server/          # Java后端项目  
│   └── taro/           # Taro移动端项目（小程序）
├── demo/               # 示例项目JSON文件
└── deploy/             # 部署相关文件
```

## 移植实施步骤

### 第一步：创建懒猫微服应用结构

```bash
# 创建工作目录
mkdir -p pageplug-lzc
cd pageplug-lzc

# 创建必要的目录结构
mkdir -p data/mongodb
mkdir -p data/redis
mkdir -p logs
```

### 第二步：准备manifest.yml文件

```yaml
lzc-sdk-version: 0.1
name: PagePlug低代码平台
package: com.cloudtogo.pageplug
version: 1.9.38
description: 基于Appsmith的中国化低代码开发平台，支持快速构建Web应用和小程序
license: Apache-2.0
homepage: https://github.com/cloudtogo/pageplug
author: CloudToGo Team
application:
  subdomain: pageplug
  routes:
    - /=http://localhost:3000/
    - /api=http://localhost:8080/api/
  environment:
    - NODE_ENV=production
    - JAVA_OPTS=-Xmx2g
  volumes:
    - /lzcapp/data/mongodb:/data/mongodb
    - /lzcapp/data/redis:/data/redis
    - /lzcapp/logs:/app/logs
  ports:
    - 3000:3000    # 前端服务
    - 8080:8080    # 后端API
    - 27017:27017  # MongoDB
    - 6379:6379    # Redis
```

### 第三步：创建Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'
services:
  mongodb:
    image: mongo:4.4
    container_name: pageplug-mongodb
    environment:
      MONGO_INITDB_DATABASE: appsmith
    volumes:
      - ./data/mongodb:/data/db
    ports:
      - "27017:27017"

  redis:
    image: redis:6.2-alpine
    container_name: pageplug-redis
    volumes:
      - ./data/redis:/data
    ports:
      - "6379:6379"

  pageplug-server:
    build: ./app/server
    container_name: pageplug-backend
    environment:
      - APPSMITH_MONGODB_URI=mongodb://mongodb:27017/appsmith
      - APPSMITH_REDIS_URL=redis://redis:6379
      - SPRING_PROFILES_ACTIVE=production
    depends_on:
      - mongodb
      - redis
    ports:
      - "8080:8080"
    volumes:
      - ./logs:/app/logs

  pageplug-client:
    build: ./app/client
    container_name: pageplug-frontend
    environment:
      - REACT_APP_SERVER_URL=http://localhost:8080
    ports:
      - "3000:3000"
    depends_on:
      - pageplug-server
```

### 第四步：构建和打包

```bash
# 克隆项目源代码
git clone https://github.com/cloudtogo/pageplug.git
cd pageplug

# 构建前端项目
cd app/client
npm install
npm run build

# 构建后端项目
cd ../server
mvn clean package -DskipTests

# 回到根目录准备打包
cd ../../

# 创建content.tar
tar -cf content.tar app/ demo/ docker-compose.yml

# 准备图标（可以从项目中提取或自己制作）
cp app/client/public/favicon.ico icon.png
```

### 第五步：创建LPK包

```bash
# 打包为LPK格式
zip -r pageplug.lpk manifest.yml content.tar icon.png docker-compose.yml
```

### 第六步：部署到懒猫微服

```bash
# 连接到懒猫微服
ssh root@你的微服名称.heiyu.space

# 安装应用
lzc-cli app install pageplug.lpk

# 检查应用状态
lzc-cli app status com.cloudtogo.pageplug

# 查看应用日志
lzc-cli app logs com.cloudtogo.pageplug
```

## 配置优化

### 1. 性能优化设置

```bash
# 在manifest.yml中添加性能配置
application:
  environment:
    - JAVA_OPTS=-Xmx2g -Xms1g
    - NODE_OPTIONS=--max-old-space-size=2048
  resource_limits:
    memory: 4096Mi
    cpu: 2000m
```

### 2. 数据持久化配置

```bash
# 确保数据目录持久化
volumes:
  - /lzcapp/data:/app/data
  - /lzcapp/config:/app/config
```

### 3. 访问域名配置

```bash
# 访问地址
https://pageplug.你的微服名称.heiyu.space
```

## 功能验证

### 1. 基础功能测试
- [ ] Web界面正常访问
- [ ] 用户注册和登录
- [ ] 应用创建和编辑
- [ ] 数据源连接
- [ ] 组件拖拽和配置

### 2. 高级功能测试
- [ ] 自定义组件开发
- [ ] JavaScript代码执行
- [ ] API接口调用
- [ ] 数据库操作
- [ ] 应用发布和分享

### 3. 性能测试
- [ ] 页面加载速度
- [ ] 应用响应时间
- [ ] 并发用户支持
- [ ] 资源使用情况

## 常见问题解决

### 1. 内存不足
```bash
# 增加交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 2. 端口冲突
```bash
# 修改manifest.yml中的端口映射
ports:
  - 3001:3000    # 改用3001端口
  - 8081:8080    # 改用8081端口
```

### 3. 数据库连接问题
```bash
# 检查MongoDB和Redis状态
docker ps | grep mongo
docker ps | grep redis

# 查看容器日志
docker logs pageplug-mongodb
docker logs pageplug-redis
```

## 后续维护

### 1. 定期备份
```bash
# 备份MongoDB数据
mongodump --host localhost:27017 --db appsmith --out backup/

# 备份应用配置
cp -r /lzcapp/data backup/
```

### 2. 版本更新
```bash
# 停止应用
lzc-cli app stop com.cloudtogo.pageplug

# 更新代码
git pull origin master

# 重新构建和部署
# ... 重复上述构建步骤
```

### 3. 监控和日志
```bash
# 查看应用状态
lzc-cli app status com.cloudtogo.pageplug

# 查看详细日志
tail -f /lzcapp/logs/application.log
```

## 总结

PagePlug是一个非常适合懒猫微服的项目，因为：

✅ **架构匹配**：Web应用架构完全适合微服环境  
✅ **容器化就绪**：已支持Docker部署  
✅ **功能完整**：提供完整的低代码开发能力  
✅ **实用价值高**：可以用来快速开发各种Web应用  
✅ **技术栈现代**：React + Java Spring + MongoDB的现代技术栈  

通过以上步骤，可以成功将PagePlug部署到懒猫微服上，为用户提供强大的低代码开发能力。 