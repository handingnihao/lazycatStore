// 调试页面脚本

// 清除所有缓存
document.getElementById('clearAllCache').addEventListener('click', async () => {
    const output = document.getElementById('cacheOutput');
    output.style.display = 'block';
    output.innerHTML = '正在清除缓存...';
    
    try {
        const items = await chrome.storage.local.get(null);
        const keys = Object.keys(items).filter(key => 
            !key.startsWith('setting_') && key !== 'githubToken'
        );
        
        if (keys.length === 0) {
            output.innerHTML = '<span class="info">没有缓存需要清除</span>';
            return;
        }
        
        await chrome.storage.local.remove(keys);
        output.innerHTML = `<span class="success">✅ 已清除 ${keys.length} 个应用的缓存</span>\n清除的应用ID:\n${keys.join('\n')}`;
    } catch (error) {
        output.innerHTML = `<span class="error">❌ 清除失败: ${error.message}</span>`;
    }
});

// 查看缓存内容
document.getElementById('viewCache').addEventListener('click', async () => {
    const output = document.getElementById('cacheOutput');
    const list = document.getElementById('cacheList');
    output.style.display = 'block';
    list.style.display = 'block';
    output.innerHTML = '正在加载缓存...';
    list.innerHTML = '';
    
    try {
        const items = await chrome.storage.local.get(null);
        const cacheItems = Object.entries(items).filter(([key]) => 
            !key.startsWith('setting_') && key !== 'githubToken'
        );
        
        if (cacheItems.length === 0) {
            output.innerHTML = '<span class="info">当前没有缓存数据</span>';
            list.style.display = 'none';
            return;
        }
        
        output.innerHTML = `<span class="success">找到 ${cacheItems.length} 个缓存项目：</span>`;
        
        cacheItems.forEach(([appId, data]) => {
            const item = document.createElement('div');
            item.className = 'cache-item';
            
            const info = document.createElement('div');
            info.innerHTML = `
                <strong>${appId}</strong><br>
                <small>GitHub: ${data.githubUrl || '未找到'}</small><br>
                <small>Stars: ${data.stars || 0} | 更新时间: ${new Date(data.fetchTime).toLocaleString()}</small>
            `;
            
            const clearBtn = document.createElement('button');
            clearBtn.textContent = '清除';
            clearBtn.onclick = async () => {
                await chrome.storage.local.remove(appId);
                item.remove();
                output.innerHTML = `<span class="success">已清除 ${appId} 的缓存</span>`;
            };
            
            item.appendChild(info);
            item.appendChild(clearBtn);
            list.appendChild(item);
        });
    } catch (error) {
        output.innerHTML = `<span class="error">❌ 加载失败: ${error.message}</span>`;
    }
});

// 测试特定应用
document.getElementById('testApp').addEventListener('click', async () => {
    const appId = document.getElementById('appIdInput').value.trim();
    const output = document.getElementById('testOutput');
    const results = document.getElementById('testResults');
    
    if (!appId) {
        output.style.display = 'block';
        output.innerHTML = '<span class="error">请输入应用ID</span>';
        return;
    }
    
    output.style.display = 'block';
    output.innerHTML = '正在测试...';
    
    try {
        // 发送消息到background script
        chrome.runtime.sendMessage(
            { 
                action: 'fetchGitHubData', 
                appId: appId,
                forceRefresh: true 
            },
            (response) => {
                if (chrome.runtime.lastError) {
                    output.innerHTML = `<span class="error">❌ 错误: ${chrome.runtime.lastError.message}</span>`;
                    return;
                }
                
                if (response && response.success) {
                    output.innerHTML = `<span class="success">✅ 测试成功！</span>`;
                    
                    // 显示详细结果
                    const resultDiv = document.createElement('div');
                    resultDiv.className = 'test-result';
                    resultDiv.innerHTML = `
                        <h3>应用: ${appId}</h3>
                        <p><strong>GitHub URL:</strong> ${response.data.githubUrl}</p>
                        <p><strong>Stars:</strong> ${response.data.stars}</p>
                        <p><strong>Forks:</strong> ${response.data.forks}</p>
                        <p><strong>语言:</strong> ${response.data.language || '未知'}</p>
                        <p><strong>描述:</strong> ${response.data.description || '无'}</p>
                        <p><strong>最后更新:</strong> ${new Date(response.data.updatedAt).toLocaleString()}</p>
                        <hr>
                        <p><strong>复制文本预览:</strong></p>
                        <pre>GitHub地址：${response.data.githubUrl}</pre>
                    `;
                    results.innerHTML = '';
                    results.appendChild(resultDiv);
                } else if (response) {
                    output.innerHTML = `<span class="error">❌ 测试失败: ${response.error || '未知错误'}</span>`;
                } else {
                    output.innerHTML = '<span class="error">❌ 无响应，请检查插件是否正常运行</span>';
                }
            }
        );
    } catch (error) {
        output.innerHTML = `<span class="error">❌ 测试失败: ${error.message}</span>`;
    }
});

// 清除特定应用缓存
document.getElementById('clearAppCache').addEventListener('click', async () => {
    const appId = document.getElementById('appIdInput').value.trim();
    const output = document.getElementById('testOutput');
    
    if (!appId) {
        output.style.display = 'block';
        output.innerHTML = '<span class="error">请输入应用ID</span>';
        return;
    }
    
    output.style.display = 'block';
    
    try {
        await chrome.storage.local.remove(appId);
        output.innerHTML = `<span class="success">✅ 已清除 ${appId} 的缓存</span>`;
    } catch (error) {
        output.innerHTML = `<span class="error">❌ 清除失败: ${error.message}</span>`;
    }
});

// 检查插件状态
document.getElementById('checkStatus').addEventListener('click', async () => {
    const output = document.getElementById('statusOutput');
    output.style.display = 'block';
    output.innerHTML = '正在检查...';
    
    try {
        // 获取插件信息
        const manifest = chrome.runtime.getManifest();
        
        // 获取存储信息
        const localData = await chrome.storage.local.get(null);
        const syncData = await chrome.storage.sync.get(null);
        
        const cacheCount = Object.keys(localData).filter(key => 
            !key.startsWith('setting_') && key !== 'githubToken'
        ).length;
        
        const hasToken = !!syncData.githubToken;
        
        output.innerHTML = `
<span class="success">✅ 插件状态正常</span>

插件版本: ${manifest.version}
插件名称: ${manifest.name}
缓存应用数: ${cacheCount}
GitHub Token: ${hasToken ? '已配置' : '未配置'}
复制模板: ${syncData.copyTemplate ? '已自定义' : '使用默认'}
        `;
    } catch (error) {
        output.innerHTML = `<span class="error">❌ 检查失败: ${error.message}</span>`;
    }
});

// 重新加载插件
document.getElementById('reloadExtension').addEventListener('click', () => {
    const output = document.getElementById('statusOutput');
    output.style.display = 'block';
    output.innerHTML = '<span class="success">✅ 正在重新加载插件...</span>';
    
    setTimeout(() => {
        chrome.runtime.reload();
    }, 500);
});

// 页面加载时自动检查状态
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('checkStatus').click();
});