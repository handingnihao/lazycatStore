# 更新说明 - v1.2.1

## 问题修复
已修复复制功能复制错误内容的问题。现在复制按钮会正确复制 GitHub URL 而不是应用描述。

## 更新步骤

### 1. 重新加载插件
1. 打开浏览器扩展管理页面
   - Chrome: `chrome://extensions/`
   - Edge: `edge://extensions/`
2. 找到"懒猫应用 GitHub Stars 显示器"
3. 点击"重新加载"按钮（🔄 图标）

### 2. 清除旧缓存（重要！）
由于修复了 URL 提取逻辑，需要清除旧的缓存数据：

**方法一：使用调试工具（推荐）**
1. 在扩展管理页面，点击插件的"检查视图 - background.html"
2. 在打开的控制台中输入：
   ```javascript
   chrome.tabs.create({url: chrome.runtime.getURL('debug.html')})
   ```
3. 在打开的调试页面中：
   - 点击"清除所有缓存"按钮
   - 或在"测试特定应用"中输入 `cloud.lazycat.app.spacebin` 并点击"测试应用"

**方法二：手动清除**
1. 在任意网页打开开发者工具（F12）
2. 在控制台输入：
   ```javascript
   chrome.storage.local.clear(() => {
     console.log('缓存已清除');
   });
   ```

### 3. 测试复制功能
1. 访问 spacebin 应用页面：https://lazycat.cloud/appstore/detail/cloud.lazycat.app.spacebin
2. 等待 GitHub 信息加载
3. 点击复制按钮
4. 粘贴内容应该是：
   ```
   GitHub地址：https://github.com/lukewhrit/spacebin
   
   给这个项目写一篇推荐文章...（后续提示文本）
   ```

## 新功能：调试工具

插件现在包含一个调试工具页面，可以：
- 查看和管理缓存
- 测试特定应用的 GitHub URL 提取
- 检查插件状态
- 清除缓存

访问方法：
1. 在扩展管理页面点击"检查视图 - background.html"
2. 在控制台输入：`chrome.tabs.create({url: chrome.runtime.getURL('debug.html')})`

## 验证修复

使用调试工具测试 spacebin 应用：
1. 打开调试页面
2. 在"测试特定应用"输入：`cloud.lazycat.app.spacebin`
3. 点击"测试应用"
4. 应该看到：
   - GitHub URL: https://github.com/lukewhrit/spacebin
   - Stars 数量正确显示

## 问题反馈

如果问题仍然存在：
1. 确保插件已重新加载
2. 确保缓存已清除
3. 检查浏览器控制台是否有错误信息
4. 使用调试工具测试并截图结果