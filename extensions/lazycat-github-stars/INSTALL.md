# 安装和测试指南

## 快速安装

1. **打开浏览器扩展管理页面**
   - Chrome: 地址栏输入 `chrome://extensions/`
   - Edge: 地址栏输入 `edge://extensions/`

2. **开启开发者模式**
   - 在页面右上角找到"开发者模式"开关并打开

3. **加载插件**
   - 点击"加载已解压的扩展程序"
   - 选择文件夹：`/Users/txj/Documents/GitHub/lazycatStore/extensions/lazycat-github-stars`

4. **重新加载插件**（如果已安装需要更新）
   - 在扩展列表中找到"懒猫应用 GitHub Stars 显示器"
   - 点击刷新按钮（🔄）

## 测试步骤

1. **访问测试页面**
   打开：https://lazycat.cloud/appstore/detail/in.zhaoj.castopod

2. **查看控制台日志**
   - 按 F12 打开开发者工具
   - 切换到 Console 标签
   - 查看以"LazyCAT GitHub Stars:"开头的日志

3. **检查显示位置**
   - 组件应显示在"来源"字段旁边
   - 如果没有显示，检查控制台是否有错误信息

## 调试信息

插件会输出详细的调试日志，包括：
- 检测到的应用ID
- 懒猫API返回的元数据
- 所有字段的URL检查
- GitHub URL的查找过程
- GitHub API的响应

## 常见问题

### 1. 没有看到GitHub星标显示

**可能原因：**
- 应用没有关联GitHub仓库
- GitHub URL字段名称不匹配
- API返回的数据结构不同

**解决方法：**
1. 打开控制台查看日志
2. 查看"元数据所有字段"日志，了解实际的字段名
3. 如果发现新的字段名，请告知以便更新插件

### 2. 显示"GitHub API 请求限制"

**原因：** GitHub API有访问频率限制（未认证用户60次/小时）

**解决方法：**
1. 等待一段时间后重试
2. 或在background.js中添加GitHub token：
   ```javascript
   // 第52行附近
   'Authorization': 'token YOUR_GITHUB_TOKEN'
   ```

### 3. 组件位置不正确

**解决方法：**
1. 查看控制台日志，看插件找到了哪个元素
2. 如果位置不对，可能需要调整选择器

## 获取GitHub Token（可选）

如果需要更高的API限制：
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token"
3. 选择 "public_repo" 权限
4. 复制token
5. 在background.js第52行添加token

## 反馈问题

如果遇到问题，请提供：
1. 访问的应用URL
2. 控制台的完整日志
3. 截图（如果有显示问题）