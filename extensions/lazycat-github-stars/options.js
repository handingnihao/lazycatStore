// 加载保存的设置
async function loadSettings() {
    chrome.storage.sync.get(['githubToken', 'copyTemplate'], (result) => {
        if (result.githubToken) {
            document.getElementById('githubToken').value = result.githubToken;
            checkRateLimit(result.githubToken);
        }
        
        // 加载复制模板
        const defaultTemplate = `GitHub地址：{github_url}

给这个项目写一篇推荐文章，要着重实用性介绍，要支持markdown格式，要尽量口语化，让小白也能看懂，不要说教，要[去爹味]，你可以从网上搜索其他的文章，取长补短，你要添加一些实用的使用方法为出发点进行编写攻略，这样其他用户使用应用您的攻略也大大的帮助到其他用户了。`;
        
        const copyTemplate = result.copyTemplate || defaultTemplate;
        document.getElementById('copyTemplate').value = copyTemplate;
    });
    
    // 加载缓存统计
    updateCacheStats();
}

// 保存设置
async function saveSettings() {
    const token = document.getElementById('githubToken').value.trim();
    const copyTemplate = document.getElementById('copyTemplate').value.trim();
    
    chrome.storage.sync.set({ 
        githubToken: token,
        copyTemplate: copyTemplate 
    }, () => {
        // 显示成功消息
        const successMessage = document.getElementById('successMessage');
        successMessage.classList.add('show');
        setTimeout(() => {
            successMessage.classList.remove('show');
        }, 3000);
        
        // 检查新token的限制
        if (token) {
            checkRateLimit(token);
        }
    });
}

// 测试GitHub连接
async function testConnection() {
    const token = document.getElementById('githubToken').value.trim();
    const button = document.getElementById('testButton');
    button.textContent = '测试中...';
    button.disabled = true;
    
    try {
        const headers = {
            'Accept': 'application/vnd.github.v3+json'
        };
        
        if (token) {
            headers['Authorization'] = `token ${token}`;
        }
        
        const response = await fetch('https://api.github.com/rate_limit', { headers });
        const data = await response.json();
        
        if (response.ok) {
            const rate = data.rate || data.resources?.core;
            const remaining = rate.remaining;
            const limit = rate.limit;
            const reset = new Date(rate.reset * 1000).toLocaleTimeString();
            
            const info = document.getElementById('rateLimitInfo');
            const text = document.getElementById('rateLimitText');
            
            info.style.display = 'block';
            if (limit > 60) {
                info.className = 'rate-limit-info good';
                text.textContent = `✅ Token 有效！限制：${remaining}/${limit} 次剩余，重置时间：${reset}`;
            } else {
                info.className = 'rate-limit-info';
                text.textContent = `⚠️ 未使用 Token。限制：${remaining}/${limit} 次剩余，重置时间：${reset}`;
            }
        } else {
            throw new Error('Token 无效');
        }
    } catch (error) {
        const info = document.getElementById('rateLimitInfo');
        const text = document.getElementById('rateLimitText');
        info.style.display = 'block';
        info.className = 'rate-limit-info';
        text.textContent = `❌ 测试失败：${error.message}`;
    } finally {
        button.textContent = '测试连接';
        button.disabled = false;
    }
}

// 检查API限制
async function checkRateLimit(token) {
    try {
        const headers = {
            'Accept': 'application/vnd.github.v3+json'
        };
        
        if (token) {
            headers['Authorization'] = `token ${token}`;
        }
        
        const response = await fetch('https://api.github.com/rate_limit', { headers });
        if (response.ok) {
            const data = await response.json();
            const rate = data.rate || data.resources?.core;
            const remaining = rate.remaining;
            const limit = rate.limit;
            
            if (remaining < 10) {
                const info = document.getElementById('rateLimitInfo');
                const text = document.getElementById('rateLimitText');
                info.style.display = 'block';
                info.className = 'rate-limit-info';
                text.textContent = `⚠️ API 请求即将用完：${remaining}/${limit} 次剩余`;
            }
        }
    } catch (error) {
        console.error('检查API限制失败:', error);
    }
}

// 清除缓存
async function clearCache() {
    if (confirm('确定要清除所有缓存的 GitHub 数据吗？')) {
        chrome.storage.local.get(null, (items) => {
            const keysToRemove = [];
            for (const key in items) {
                // 只删除应用数据，保留设置
                if (!key.startsWith('setting_') && key !== 'githubToken') {
                    keysToRemove.push(key);
                }
            }
            
            chrome.storage.local.remove(keysToRemove, () => {
                alert(`已清除 ${keysToRemove.length} 个应用的缓存数据`);
                updateCacheStats();
            });
        });
    }
}

// 更新缓存统计
async function updateCacheStats() {
    chrome.storage.local.get(null, (items) => {
        let count = 0;
        let totalSize = 0;
        
        for (const key in items) {
            if (!key.startsWith('setting_') && key !== 'githubToken') {
                count++;
                // 估算每个缓存项的大小
                totalSize += JSON.stringify(items[key]).length;
            }
        }
        
        document.getElementById('cacheCount').textContent = count;
        
        // 显示缓存大小
        const sizeElement = document.getElementById('cacheSize');
        if (totalSize > 0) {
            const sizeKB = (totalSize / 1024).toFixed(2);
            sizeElement.textContent = `缓存大小：约 ${sizeKB} KB`;
        } else {
            sizeElement.textContent = '暂无缓存数据';
        }
    });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    
    // 绑定事件
    document.getElementById('saveButton').addEventListener('click', saveSettings);
    document.getElementById('testButton').addEventListener('click', testConnection);
    document.getElementById('clearCacheButton').addEventListener('click', clearCache);
    
    // Token 输入框回车保存
    document.getElementById('githubToken').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            saveSettings();
        }
    });
});