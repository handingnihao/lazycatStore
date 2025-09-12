// background.js - 处理API请求和跨域通信

// 解析GitHub URL
function parseGitHubUrl(url) {
  if (!url) return null;
  
  // 清理URL - 移除可能的额外路径部分
  let cleanUrl = url;
  
  // 如果URL包含/blob/、/tree/、/issues/等路径，只保留仓库部分
  const repoUrlMatch = url.match(/(https?:\/\/)?github\.com\/([^\/]+)\/([^\/\s\?#]+)/i);
  if (repoUrlMatch) {
    cleanUrl = `https://github.com/${repoUrlMatch[2]}/${repoUrlMatch[3]}`;
  }
  
  // 支持多种GitHub URL格式
  const patterns = [
    /github\.com\/([^\/]+)\/([^\/\s\?#]+)/i,
    /github\.com\/([^\/]+)\/([^\/\s\?#]+)\.git/i,
  ];
  
  for (const pattern of patterns) {
    const match = cleanUrl.match(pattern);
    if (match) {
      // 清理仓库名称，移除.git后缀和其他可能的后缀
      let repoName = match[2].replace(/\.git$/, '');
      // 移除可能的路径分隔符
      repoName = repoName.split('/')[0];
      
      return {
        owner: match[1],
        repo: repoName
      };
    }
  }
  
  return null;
}

// 获取懒猫应用元数据
async function fetchLazyCatMetadata(appId) {
  const apiUrl = `https://dl.lazycat.cloud/appstore/metarepo/zh/v3/app_${appId}.json`;
  
  try {
    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('获取懒猫应用元数据失败:', error);
    throw error;
  }
}

// 获取GitHub仓库信息
async function fetchGitHubRepo(owner, repo) {
  const apiUrl = `https://api.github.com/repos/${owner}/${repo}`;
  
  try {
    // 获取保存的token
    const settings = await chrome.storage.sync.get(['githubToken']);
    const headers = {
      'Accept': 'application/vnd.github.v3+json'
    };
    
    if (settings.githubToken) {
      headers['Authorization'] = `token ${settings.githubToken}`;
      console.log('使用GitHub Token进行API请求');
    } else {
      console.log('未配置GitHub Token，使用默认限制');
    }
    
    const response = await fetch(apiUrl, { headers });
    
    if (!response.ok) {
      if (response.status === 403) {
        const rateLimitReset = response.headers.get('X-RateLimit-Reset');
        if (rateLimitReset) {
          const resetTime = new Date(parseInt(rateLimitReset) * 1000);
          throw new Error(`GitHub API 请求限制，请在 ${resetTime.toLocaleTimeString()} 后重试`);
        }
        throw new Error('GitHub API 请求限制');
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return {
      stars: data.stargazers_count,
      forks: data.forks_count,
      watchers: data.watchers_count,
      openIssues: data.open_issues_count,
      language: data.language,
      description: data.description,
      updatedAt: data.updated_at,
      createdAt: data.created_at,
      defaultBranch: data.default_branch,
      topics: data.topics || []
    };
  } catch (error) {
    console.error('获取GitHub仓库信息失败:', error);
    throw error;
  }
}

// 处理消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'fetchGitHubData') {
    (async () => {
      try {
        console.log('开始获取应用数据:', request.appId);
        
        // 1. 获取懒猫应用元数据
        const metadata = await fetchLazyCatMetadata(request.appId);
        console.log('懒猫应用元数据:', metadata);
        console.log('元数据所有字段:', Object.keys(metadata));
        
        // 2. 查找GitHub URL
        let githubUrl = null;
        let githubInfo = null;
        
        // 打印所有可能包含URL的字段以便调试
        console.log('查找GitHub URL...');
        console.log('sourceCode:', metadata.sourceCode);
        console.log('webSite:', metadata.webSite);
        console.log('repoUrl:', metadata.repoUrl);
        console.log('repository:', metadata.repository);
        console.log('homepage:', metadata.homepage);
        console.log('url:', metadata.url);
        console.log('source:', metadata.source);
        console.log('git:', metadata.git);
        console.log('gitUrl:', metadata.gitUrl);
        console.log('repo:', metadata.repo);
        
        // 检查多个可能包含GitHub URL的字段
        const possibleUrls = [
          metadata.sourceCode,
          metadata.webSite,
          metadata.repoUrl,
          metadata.repository,
          metadata.homepage,
          metadata.url,
          metadata.source,
          metadata.git,
          metadata.gitUrl,
          metadata.repo,
          // 检查嵌套对象
          metadata.links?.github,
          metadata.links?.source,
          metadata.links?.repo,
          metadata.project?.github,
          metadata.project?.source,
          metadata.project?.repo
        ];
        
        console.log('所有可能的URL:', possibleUrls);
        
        for (const url of possibleUrls) {
          if (url && typeof url === 'string' && url.includes('github.com')) {
            console.log('找到GitHub URL:', url);
            githubUrl = url;
            githubInfo = parseGitHubUrl(url);
            if (githubInfo) {
              console.log('成功解析GitHub信息:', githubInfo);
              break;
            }
          }
        }
        
        // 如果没有找到GitHub URL，也检查描述和其他字段
        if (!githubInfo) {
          console.log('在标准字段中未找到GitHub URL，检查描述字段...');
          const descFields = [metadata.description, metadata.summary, metadata.about];
          for (const desc of descFields) {
            if (desc && typeof desc === 'string') {
              const urlMatch = desc.match(/github\.com\/[^\s]+/i);
              if (urlMatch) {
                githubUrl = `https://${urlMatch[0]}`;
                githubInfo = parseGitHubUrl(githubUrl);
                if (githubInfo) {
                  console.log('从描述中找到GitHub URL:', githubUrl);
                  break;
                }
              }
            }
          }
        }
        
        // 深度搜索整个对象寻找GitHub URL
        if (!githubInfo) {
          console.log('深度搜索元数据对象...');
          function findGitHubUrl(obj, depth = 0) {
            if (depth > 5) return null; // 防止无限递归
            for (const key in obj) {
              const value = obj[key];
              if (typeof value === 'string' && value.includes('github.com')) {
                console.log(`在 ${key} 字段找到包含github.com的文本:`, value);
                
                // 尝试从文本中提取有效的GitHub URL
                // 匹配完整的GitHub URL（如 https://github.com/user/repo）
                const urlPattern = /https?:\/\/github\.com\/[^\/\s]+\/[^\/\s\?#]+/gi;
                const matches = value.match(urlPattern);
                
                if (matches && matches.length > 0) {
                  // 返回第一个匹配的完整URL
                  const validUrl = matches[0];
                  console.log(`提取到有效的GitHub URL:`, validUrl);
                  return validUrl;
                } else if (value.startsWith('github.com/')) {
                  // 如果是以github.com开头但没有协议的URL
                  const validUrl = 'https://' + value.split(/[\s,;]/)[0];
                  console.log(`补全GitHub URL:`, validUrl);
                  return validUrl;
                }
              } else if (typeof value === 'object' && value !== null) {
                const result = findGitHubUrl(value, depth + 1);
                if (result) return result;
              }
            }
            return null;
          }
          
          const foundUrl = findGitHubUrl(metadata);
          if (foundUrl) {
            githubUrl = foundUrl;
            githubInfo = parseGitHubUrl(foundUrl);
          }
        }
        
        if (!githubInfo) {
          sendResponse({
            success: false,
            error: '该应用未关联GitHub仓库'
          });
          return;
        }
        
        console.log('解析的GitHub信息:', githubInfo);
        
        // 确保GitHub URL是标准格式
        const standardGithubUrl = `https://github.com/${githubInfo.owner}/${githubInfo.repo}`;
        console.log('标准化的GitHub URL:', standardGithubUrl);
        
        // 3. 获取GitHub仓库信息
        const repoData = await fetchGitHubRepo(githubInfo.owner, githubInfo.repo);
        
        // 4. 返回数据
        const responseData = {
          success: true,
          data: {
            githubUrl: standardGithubUrl,  // 使用标准化的URL
            repoOwner: githubInfo.owner,
            repoName: githubInfo.repo,
            stars: repoData.stars,
            forks: repoData.forks,
            watchers: repoData.watchers,
            openIssues: repoData.openIssues,
            language: repoData.language,
            description: repoData.description,
            updatedAt: repoData.updatedAt,
            topics: repoData.topics
          }
        };
        
        console.log('返回数据:', responseData);
        sendResponse(responseData);
        
      } catch (error) {
        console.error('处理请求时出错:', error);
        sendResponse({
          success: false,
          error: error.message || '获取数据失败'
        });
      }
    })();
    
    // 返回true表示异步处理
    return true;
  }
});

// 安装时的处理
chrome.runtime.onInstalled.addListener(() => {
  console.log('LazyCAT GitHub Stars 扩展已安装');
});