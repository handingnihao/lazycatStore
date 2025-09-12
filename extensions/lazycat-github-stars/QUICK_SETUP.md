# 快速解决 GitHub API 限制问题

## 问题原因
GitHub API 对未认证用户有访问限制（60次/小时），很容易达到上限。

## 解决方案：配置 GitHub Token

### 步骤 1：获取 GitHub Token

1. **点击下面的链接直接创建 Token**：
   https://github.com/settings/tokens/new?description=LazyCAT%20GitHub%20Stars&scopes=public_repo

2. **或手动创建**：
   - 登录 GitHub
   - 访问 Settings → Developer settings → Personal access tokens → Tokens (classic)
   - 点击 "Generate new token"
   - 描述：输入 "LazyCAT GitHub Stars"
   - 权限：只勾选 `public_repo`
   - 点击 "Generate token"
   - **复制生成的 Token**（格式：`ghp_xxxxxxxxxxxxxxxxxxxx`）

### 步骤 2：配置插件

1. **打开插件设置**：
   - 方法1：点击插件图标 → 点击"⚙️ 打开设置"
   - 方法2：右键插件图标 → 选择"选项"
   - 方法3：访问 `chrome://extensions/` → 找到插件 → 点击"详情" → "扩展程序选项"

2. **输入 Token**：
   - 在设置页面的 Token 输入框中粘贴你的 Token
   - 点击"保存设置"

3. **测试连接**：
   - 点击"测试连接"按钮
   - 如果显示"✅ Token 有效！限制：5000/5000"，说明配置成功

### 步骤 3：重新访问应用页面

1. 刷新懒猫应用详情页
2. 现在应该能正常显示 GitHub star 数量了

## Token 的好处

- **更高的 API 限制**：从 60次/小时 提升到 5000次/小时
- **更稳定的服务**：避免频繁遇到限制
- **支持私有仓库**：如果应用链接到私有仓库，也能获取信息

## 常见问题

### Q: Token 安全吗？
A: 安全。Token 只保存在你的浏览器本地，不会上传到任何服务器。且只申请了 `public_repo` 权限，只能读取公开仓库信息。

### Q: 如何删除 Token？
A: 在设置页面清空 Token 输入框并保存即可。或在 GitHub 设置中撤销 Token。

### Q: 还是显示 API 限制？
A: 
1. 确认 Token 输入正确（包括 `ghp_` 前缀）
2. 点击"测试连接"检查 Token 是否有效
3. 清除缓存后重试（设置页面有"清除缓存"按钮）

## 测试地址

配置完成后，可以访问以下地址测试：
- https://lazycat.cloud/appstore/detail/cloud.lazycat.app.spacebin
- https://lazycat.cloud/appstore/detail/in.zhaoj.castopod

应该能看到 GitHub star 数量显示在"来源"字段旁边。