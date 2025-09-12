# 懒猫应用 GitHub Stars 显示器

一个浏览器插件，用于在懒猫应用商店的应用详情页自动显示 GitHub 项目的 star 数量。

## 功能特性

- 🌟 自动显示 GitHub star 和 fork 数量
- 💾 智能缓存机制，首次访问自动获取，后续使用缓存
- 🔄 手动刷新按钮，随时更新最新数据
- 📅 显示最后更新时间
- 🎨 优雅的渐变UI设计，与懒猫网站风格融合
- 📱 响应式设计，支持移动端

## 安装方法

### 开发者模式安装（Chrome/Edge）

1. 打开浏览器扩展管理页面
   - Chrome: 访问 `chrome://extensions/`
   - Edge: 访问 `edge://extensions/`

2. 开启"开发者模式"（通常在页面右上角）

3. 点击"加载已解压的扩展程序"

4. 选择 `lazycat-github-stars` 文件夹

5. 插件安装完成！

## 使用说明

1. 访问懒猫应用商店的任意应用详情页，例如：
   - https://lazycat.cloud/appstore/detail/in.zhaoj.castopod

2. 如果应用关联了 GitHub 仓库：
   - **首次访问**：自动获取并显示 GitHub 数据
   - **再次访问**：显示缓存的数据，可点击刷新按钮更新

3. 点击 GitHub 链接可直接跳转到对应的仓库页面

## 工作原理

1. 检测当前页面是否为懒猫应用详情页
2. 从 URL 提取应用 ID（如 `in.zhaoj.castopod`）
3. 调用懒猫 API 获取应用元数据：
   ```
   https://dl.lazycat.cloud/appstore/metarepo/zh/v3/app_{app_id}.json
   ```
4. 解析元数据中的 GitHub 仓库地址
5. 调用 GitHub API 获取仓库统计信息
6. 在页面上显示星标数量和其他信息

## 数据缓存策略

- 首次访问应用时自动获取数据
- 数据保存在浏览器本地存储中
- 用户可以通过刷新按钮手动更新数据
- 缓存数据包含获取时间，方便查看数据新鲜度

## 文件结构

```
lazycat-github-stars/
├── manifest.json      # 插件配置文件
├── content.js         # 内容脚本，注入到页面
├── background.js      # 后台脚本，处理 API 请求
├── styles.css         # 样式文件
├── popup.html         # 插件弹窗页面
├── icons/            # 插件图标
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md         # 说明文档
```

## 开发说明

### 修改插件

1. 编辑相应的文件
2. 在扩展管理页面点击"重新加载"按钮
3. 刷新懒猫应用页面查看效果

### 调试

- 打开浏览器开发者工具（F12）
- 在 Console 中查看插件日志（以 "LazyCAT GitHub Stars:" 开头）
- 在 Network 标签页查看 API 请求

### 配置 GitHub Token（推荐）

GitHub API 有访问频率限制（未认证：60次/小时），建议配置个人 Token：

1. **打开设置页面**
   - 右键点击插件图标 → 选择"选项"

2. **获取 GitHub Token**
   - 访问 https://github.com/settings/tokens/new
   - 描述：LazyCAT GitHub Stars
   - 权限：只勾选 `public_repo`
   - 生成并复制 Token

3. **保存配置**
   - 在设置页面粘贴 Token
   - 点击"保存设置"
   - 配置后 API 限制将提升到 5000次/小时

## 故障排除

### 复制功能显示错误内容

如果复制按钮复制的内容不是 GitHub URL，可能是缓存问题：

1. **清除缓存方法一：使用调试工具**
   - 在扩展管理页面点击"检查视图"下的 background.html
   - 在控制台输入 `chrome.tabs.create({url: chrome.runtime.getURL('debug.html')})`
   - 使用调试页面清除缓存

2. **清除缓存方法二：手动清除**
   - 右键插件图标 → 选项
   - 在浏览器控制台运行：
   ```javascript
   chrome.storage.local.clear(() => {
     console.log('缓存已清除');
   });
   ```

3. **重新加载插件**
   - 在扩展管理页面点击"重新加载"按钮
   - 刷新懒猫应用页面

### GitHub API 限制

如果遇到 API 限制错误，请配置 GitHub Token（见上方说明）。

## 后续优化建议

1. **图标优化**：替换占位图标为专业设计的图标
2. **更多平台支持**：支持 GitLab、Gitee 等其他代码托管平台
3. **批量处理**：在应用列表页显示所有应用的 star 数量
4. **数据统计**：添加 star 增长趋势图表
5. **缓存过期**：添加自动缓存过期机制（如7天）

## License

MIT

## 作者

天天