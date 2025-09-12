(() => {
  'use strict';

  // 工具函数：格式化数字
  function formatNumber(num) {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  }

  // 工具函数：格式化时间
  function formatTime(timestamp) {
    const now = Date.now();
    const diff = now - timestamp;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}天前更新`;
    if (hours > 0) return `${hours}小时前更新`;
    if (minutes > 0) return `${minutes}分钟前更新`;
    return '刚刚更新';
  }

  // 从URL提取app_id
  function getAppId() {
    const match = window.location.pathname.match(/\/appstore\/detail\/(.+)/);
    return match ? match[1] : null;
  }

  // 从缓存获取数据
  async function getFromCache(appId) {
    return new Promise((resolve) => {
      chrome.storage.local.get(appId, (result) => {
        resolve(result[appId] || null);
      });
    });
  }

  // 保存到缓存
  async function saveToCache(appId, data) {
    const cacheData = {
      ...data,
      fetchTime: Date.now()
    };
    return new Promise((resolve) => {
      chrome.storage.local.set({ [appId]: cacheData }, resolve);
    });
  }

  // 创建GitHub信息组件
  function createGitHubWidget(data) {
    const widget = document.createElement('div');
    widget.className = 'github-stars-widget';
    
    if (data.loading) {
      widget.innerHTML = `
        <div class="github-info loading">
          <span class="loading-text">正在获取 GitHub 数据...</span>
        </div>
      `;
    } else if (data.error) {
      widget.innerHTML = `
        <div class="github-info error">
          <span class="error-text">${data.error}</span>
          <button class="refresh-btn" title="重试">
            <svg class="refresh-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 4v6h6M23 20v-6h-6"/>
              <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
            </svg>
          </button>
        </div>
      `;
    } else {
      const starsText = formatNumber(data.stars || 0);
      const forksText = formatNumber(data.forks || 0);
      const updateTime = formatTime(data.fetchTime || Date.now());
      
      widget.innerHTML = `
        <div class="github-info">
          <a href="${data.githubUrl}" target="_blank" class="github-link">
            <svg class="github-icon" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            <span class="stars-count">⭐ ${starsText}</span>
            <span class="forks-count">🔱 ${forksText}</span>
          </a>
          <button class="copy-btn" title="复制推荐文本" data-github-url="${data.githubUrl}">
            <svg class="copy-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
          </button>
          <button class="refresh-btn" title="刷新数据">
            <svg class="refresh-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 4v6h6M23 20v-6h-6"/>
              <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
            </svg>
          </button>
        </div>
        <div class="last-updated" title="${new Date(data.fetchTime).toLocaleString()}">
          ${updateTime}
        </div>
      `;
      widget.dataset.githubUrl = data.githubUrl;
    }
    
    return widget;
  }

  // 复制到剪贴板
  async function copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      // 备用方案
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand('copy');
        document.body.removeChild(textarea);
        return true;
      } catch (err) {
        document.body.removeChild(textarea);
        return false;
      }
    }
  }

  // 更新显示
  function updateWidget(container, data) {
    const widget = createGitHubWidget(data);
    container.innerHTML = '';
    container.appendChild(widget);
    
    // 添加刷新按钮事件
    const refreshBtn = widget.querySelector('.refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        await refreshGitHubData(container);
      });
    }
    
    // 添加复制按钮事件
    const copyBtn = widget.querySelector('.copy-btn');
    if (copyBtn && data.githubUrl) {
      copyBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        // 获取复制模板
        chrome.storage.sync.get(['copyTemplate'], async (result) => {
          const defaultTemplate = `GitHub地址：{github_url}

给这个项目写一篇推荐文章，要着重实用性介绍，要支持markdown格式，要尽量口语化，让小白也能看懂，不要说教，要[去爹味]，你可以从网上搜索其他的文章，取长补短，你要添加一些实用的使用方法为出发点进行编写攻略，这样其他用户使用应用您的攻略也大大的帮助到其他用户了。`;
          
          const template = result.copyTemplate || defaultTemplate;
          const textToCopy = template.replace(/{github_url}/g, data.githubUrl);
          
          const success = await copyToClipboard(textToCopy);
          
          // 显示复制成功提示
          if (success) {
            const originalTitle = copyBtn.title;
            copyBtn.title = '✅ 已复制到剪贴板！';
            copyBtn.classList.add('copied');
            
            setTimeout(() => {
              copyBtn.title = originalTitle;
              copyBtn.classList.remove('copied');
            }, 2000);
          } else {
            copyBtn.title = '❌ 复制失败，请重试';
            setTimeout(() => {
              copyBtn.title = '复制推荐文本';
            }, 2000);
          }
        });
      });
    }
  }

  // 记录最后一次刷新时间，防止频繁请求
  let lastRefreshTime = 0;
  const MIN_REFRESH_INTERVAL = 5000; // 最小刷新间隔5秒
  
  // 刷新GitHub数据
  async function refreshGitHubData(container, isAutoFetch = false) {
    const appId = getAppId();
    if (!appId) return;
    
    // 防止频繁刷新
    const now = Date.now();
    if (!isAutoFetch && (now - lastRefreshTime) < MIN_REFRESH_INTERVAL) {
      console.log('LazyCAT GitHub Stars: 请求过于频繁，请稍后再试');
      return;
    }
    lastRefreshTime = now;
    
    // 显示加载状态
    updateWidget(container, { loading: true });
    
    // 发送消息到background script获取数据
    chrome.runtime.sendMessage(
      { 
        action: 'fetchGitHubData', 
        appId: appId,
        forceRefresh: true 
      },
      async (response) => {
        if (response && response.success) {
          // 保存到缓存
          await saveToCache(appId, response.data);
          // 更新显示
          updateWidget(container, response.data);
        } else if (response) {
          updateWidget(container, { error: response.error || '获取数据失败' });
        } else {
          // 如果没有响应，可能是扩展更新或重载
          updateWidget(container, { error: '插件需要重新加载，请刷新页面' });
        }
      }
    );
  }

  // 初始化函数
  async function init() {
    const appId = getAppId();
    if (!appId) {
      console.log('LazyCAT GitHub Stars: 不是应用详情页');
      return;
    }

    console.log('LazyCAT GitHub Stars: 检测到应用ID:', appId);

    // 创建容器 - 使用span以便内联显示
    const container = document.createElement('span');
    container.id = 'github-stars-container';
    container.style.marginLeft = '10px';
    container.style.display = 'inline-block';
    
    // 查找"来源"字段的位置
    let inserted = false;
    
    // 方法1：查找包含"来源"文本的元素
    const allElements = document.querySelectorAll('*');
    for (const element of allElements) {
      // 查找"来源"标签
      if (element.textContent === '来源' && element.childNodes.length === 1 && !element.querySelector('*')) {
        console.log('LazyCAT GitHub Stars: 找到"来源"标签');
        
        // 查找包含来源值的相邻元素
        let valueElement = null;
        
        // 检查下一个兄弟元素
        if (element.nextElementSibling) {
          valueElement = element.nextElementSibling;
        } 
        // 检查父元素的下一个兄弟元素（表格结构）
        else if (element.parentElement && element.parentElement.nextElementSibling) {
          valueElement = element.parentElement.nextElementSibling;
        }
        // 检查是否在表格行中
        else {
          const row = element.closest('tr');
          if (row) {
            const cells = row.querySelectorAll('td');
            for (let i = 0; i < cells.length - 1; i++) {
              if (cells[i].textContent === '来源') {
                valueElement = cells[i + 1];
                break;
              }
            }
          }
        }
        
        if (valueElement) {
          console.log('LazyCAT GitHub Stars: 找到来源值元素:', valueElement.textContent);
          valueElement.appendChild(container);
          inserted = true;
          break;
        }
      }
    }
    
    // 方法2：如果没找到，尝试通过文本内容查找
    if (!inserted) {
      console.log('LazyCAT GitHub Stars: 尝试通过文本内容查找');
      const textNodes = document.evaluate(
        "//text()[contains(., 'castopod') or contains(., 'github.com') or contains(., 'gitlab')]",
        document,
        null,
        XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE,
        null
      );
      
      for (let i = 0; i < textNodes.snapshotLength; i++) {
        const textNode = textNodes.snapshotItem(i);
        const parent = textNode.parentElement;
        if (parent && !parent.querySelector('#github-stars-container')) {
          console.log('LazyCAT GitHub Stars: 找到源文本:', textNode.textContent);
          parent.appendChild(container);
          inserted = true;
          break;
        }
      }
    }
    
    // 方法3：如果还是没找到，查找应用信息表格
    if (!inserted) {
      console.log('LazyCAT GitHub Stars: 查找应用信息表格');
      const tables = document.querySelectorAll('table');
      for (const table of tables) {
        const cells = table.querySelectorAll('td');
        for (let i = 0; i < cells.length; i++) {
          if (cells[i].textContent.includes('来源') || cells[i].textContent.includes('castopod')) {
            cells[i].appendChild(container);
            inserted = true;
            console.log('LazyCAT GitHub Stars: 插入到表格单元格');
            break;
          }
        }
        if (inserted) break;
      }
    }
    
    if (!inserted) {
      console.log('LazyCAT GitHub Stars: 未找到合适的插入位置，使用默认位置');
      // 如果还是没找到，插入到页面顶部
      const body = document.body;
      body.insertBefore(container, body.firstChild);
    }

    // 检查缓存
    const cachedData = await getFromCache(appId);
    
    if (cachedData) {
      // 显示缓存数据
      console.log('LazyCAT GitHub Stars: 使用缓存数据');
      updateWidget(container, cachedData);
    } else {
      // 首次访问，自动获取数据
      console.log('LazyCAT GitHub Stars: 首次访问，自动获取数据');
      await refreshGitHubData(container, true); // 传递isAutoFetch=true
    }
  }

  // 等待页面加载完成
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    // 延迟执行，确保页面元素已加载
    setTimeout(init, 500);
  }

  // 监听URL变化（SPA应用）
  let lastUrl = location.href;
  new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
      lastUrl = url;
      // URL变化，重新初始化
      const existingContainer = document.getElementById('github-stars-container');
      if (existingContainer) {
        existingContainer.remove();
      }
      setTimeout(init, 500);
    }
  }).observe(document, { subtree: true, childList: true });
})();