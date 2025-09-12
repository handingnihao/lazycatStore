# 故障排除指南

## 问题：点击"打开设置"按钮没反应

### 解决方法 1：重新加载插件
1. 打开 `chrome://extensions/`
2. 找到"懒猫应用 GitHub Stars 显示器"
3. 点击刷新按钮（🔄）
4. 再次点击插件图标，尝试"打开设置"按钮

### 解决方法 2：手动访问设置页面

#### Chrome 浏览器：
1. **方法A：通过扩展管理页面**
   - 访问 `chrome://extensions/`
   - 找到"懒猫应用 GitHub Stars 显示器"
   - 点击"详情"
   - 点击"扩展程序选项"

2. **方法B：右键菜单**
   - 右键点击插件图标
   - 选择"选项"

3. **方法C：直接访问URL**
   - 在地址栏输入：
   ```
   chrome-extension://[插件ID]/options.html
   ```
   - 插件ID可以在 `chrome://extensions/` 页面找到

#### Edge 浏览器：
1. 访问 `edge://extensions/`
2. 找到插件，点击"详细信息"
3. 点击"扩展选项"

### 解决方法 3：使用快速设置页面
如果上述方法都不行，可以直接在地址栏访问：
1. 打开 `chrome://extensions/`
2. 找到插件ID（类似：`abcdefghijklmnopqrstuvwxyz`）
3. 在新标签页访问：`chrome-extension://[你的插件ID]/popup_simple.html`
4. 在这个页面可以直接输入和保存 Token

## 问题：显示"GitHub API 请求限制"

### 立即解决：
1. 使用上述任一方法打开设置页面
2. 获取 GitHub Token：
   - 访问：https://github.com/settings/tokens/new
   - 描述：LazyCAT GitHub Stars
   - 权限：勾选 `public_repo`
   - 点击"Generate token"
   - 复制 Token
3. 在设置页面粘贴 Token 并保存
4. 刷新懒猫应用页面

## 问题：插件没有显示在应用详情页

### 检查步骤：
1. **确认URL正确**
   - 必须是：`https://lazycat.cloud/appstore/detail/xxx`
   
2. **查看控制台日志**
   - 按 F12 打开开发者工具
   - 切换到 Console 标签
   - 查找"LazyCAT GitHub Stars:"开头的日志

3. **检查插件状态**
   - 确保插件已启用
   - 重新加载插件

## 快速测试

配置完成后，访问以下页面测试：
- https://lazycat.cloud/appstore/detail/cloud.lazycat.app.spacebin （应显示 123 stars）
- https://lazycat.cloud/appstore/detail/in.zhaoj.castopod

## 需要更多帮助？

1. 查看控制台错误信息（F12 → Console）
2. 截图错误信息
3. 记录你的浏览器版本和操作系统