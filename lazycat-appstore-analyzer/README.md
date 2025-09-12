# 🎯 懒猫应用商店数据分析系统

[![懒猫微服](https://img.shields.io/badge/懒猫微服-应用商店-blue)](https://appstore.lazycat.cloud)
[![版本](https://img.shields.io/badge/版本-1.0.0-green)](https://github.com/tianxuejian/lazycat-appstore-analyzer)
[![许可证](https://img.shields.io/badge/许可证-MIT-yellow)](LICENSE)

专业的懒猫应用商店数据分析、管理和移植评估工具，帮助开发者快速找到适合移植的应用，为懒猫生态贡献力量。

## ✨ 核心特性

### 🔐 完整的账户集成
- **OIDC单点登录** - 无缝对接懒猫微服账户系统
- **多用户数据隔离** - 每个用户独立的数据空间
- **权限管理** - 区分管理员和普通用户权限

### 📁 文件关联支持
- **网盘右键菜单** - 直接从懒猫网盘导入CSV/Excel文件
- **智能识别** - 自动识别文件格式和数据结构
- **批量导入** - 支持大批量数据快速导入

### 📊 强大的分析功能
- **应用对比分析** - 比较不同来源的应用差异
- **移植优先级评估** - 基于GitHub Stars等指标排序
- **Docker兼容性检测** - 自动分析应用的容器化难度
- **智能匹配算法** - 使用相似度算法精准匹配应用

### 🎨 现代化界面
- **响应式设计** - 完美适配各种设备
- **深色模式** - 保护眼睛，夜间使用更舒适
- **实时搜索** - 快速找到目标应用
- **可视化图表** - 直观展示数据统计

## 🚀 快速开始

### 在懒猫微服中安装

1. **从应用商店安装**（推荐）
   - 打开懒猫应用商店
   - 搜索"应用商店数据分析"
   - 点击安装

2. **手动安装LPK包**
   ```bash
   # 下载LPK包
   wget https://github.com/tianxuejian/lazycat-appstore-analyzer/releases/latest/download/lazycat-appstore-analyzer.lpk
   
   # 上传到懒猫网盘并右键安装
   ```

### 本地开发

1. **克隆项目**
   ```bash
   git clone https://github.com/tianxuejian/lazycat-appstore-analyzer.git
   cd lazycat-appstore-analyzer
   ```

2. **安装lzc-cli**
   ```bash
   curl -fsSL https://get.lazycat.cloud/install.sh | bash
   ```

3. **启动开发环境**
   ```bash
   lzc-cli project devshell
   ```

4. **在容器内运行**
   ```bash
   pip install -r requirements.txt
   python app/app.py
   ```

## 📦 构建和发布

### 构建LPK包
```bash
# 构建应用包
lzc-cli project build

# 输出文件: lazycat-appstore-analyzer-1.0.0.lpk
```

### 发布到应用商店
```bash
# 提交审核
lzc-cli appstore publish ./lazycat-appstore-analyzer-1.0.0.lpk
```

## 🔧 配置说明

### 环境变量
```yaml
DATABASE_PATH: /lzcapp/var/database/lazycat_apps.db  # 数据库路径
UPLOAD_PATH: /lzcapp/var/uploads                      # 上传文件路径
CONFIG_PATH: /lzcapp/var/config                       # 配置文件路径
FLASK_PORT: 5000                                      # 服务端口
```

### OIDC配置（自动注入）
```yaml
LAZYCAT_AUTH_OIDC_CLIENT_ID     # 客户端ID
LAZYCAT_AUTH_OIDC_CLIENT_SECRET # 客户端密钥
LAZYCAT_AUTH_OIDC_ISSUER        # 认证服务器地址
```

### 文件关联
支持的文件类型：
- CSV文件 (`.csv`)
- Excel文件 (`.xlsx`, `.xls`)

## 📊 功能介绍

### 1. 应用管理
- 添加/编辑/删除应用
- 批量导入导出
- 搜索和筛选
- 分页浏览

### 2. 数据分析
- 下载量统计
- 热门应用排行
- 状态分布分析
- 趋势图表

### 3. 批量检查
- 批量检查应用存在性
- 智能相似度匹配
- 一键添加缺失应用
- 导出检查结果

### 4. 移植评估
- GitHub项目分析
- Docker支持检测
- 难度等级评估
- 优先级排序

## 🛠 技术栈

- **后端**: Python 3.9 + Flask 2.3
- **数据库**: SQLite
- **前端**: Bootstrap 5 + Chart.js
- **认证**: OIDC (OpenID Connect)
- **容器**: Docker
- **平台**: 懒猫微服 v1.3.5+

## 📝 API文档

### 认证相关
- `GET /login` - 登录页面
- `GET /auth/callback` - OIDC回调
- `GET /logout` - 退出登录

### 应用管理
- `GET /` - 应用列表
- `POST /add` - 添加应用
- `PUT /edit/<id>` - 编辑应用
- `DELETE /delete/<id>` - 删除应用
- `GET /view/<id>` - 查看详情

### 数据分析
- `GET /statistics` - 统计页面
- `GET /api/statistics` - 统计API
- `GET /api/search` - 搜索API

### 批量操作
- `GET /batch_check` - 批量检查页面
- `POST /api/batch_check` - 批量检查API
- `POST /batch_add_missing` - 批量添加

### 文件操作
- `GET /import?file=<path>` - 导入文件
- `GET /export` - 导出CSV

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👨‍💻 作者

**天天**

- GitHub: [@tianxuejian](https://github.com/tianxuejian)
- 懒猫社区: [@tiantian](https://lazycat.cloud/u/tiantian)

## 🙏 致谢

- 感谢懒猫微服团队提供的平台支持
- 感谢所有贡献者和用户的反馈

## 📞 支持

如有问题或建议，请通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/tianxuejian/lazycat-appstore-analyzer/issues)
- 懒猫社区讨论组
- 邮件: [待补充]

---

**让我们一起为懒猫生态贡献力量！** 🚀