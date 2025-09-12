// 测试脚本：检查 spacebin 应用的 GitHub URL 提取
const appId = 'cloud.lazycat.app.spacebin';

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

// 深度搜索GitHub URL
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

// 主测试函数
async function testSpacebin() {
  try {
    console.log('开始测试 spacebin 应用...\n');
    
    // 1. 获取元数据
    const metadata = await fetchLazyCatMetadata(appId);
    console.log('成功获取元数据\n');
    
    // 2. 打印所有可能包含URL的字段
    console.log('检查标准字段:');
    const fields = [
      'sourceCode', 'webSite', 'repoUrl', 'repository', 
      'homepage', 'url', 'source', 'git', 'gitUrl', 'repo'
    ];
    
    for (const field of fields) {
      if (metadata[field]) {
        console.log(`  ${field}: ${metadata[field]}`);
      }
    }
    
    // 3. 查找GitHub URL
    console.log('\n查找GitHub URL...');
    let githubUrl = null;
    let githubInfo = null;
    
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
    
    // 4. 如果没找到，使用深度搜索
    if (!githubInfo) {
      console.log('\n使用深度搜索...');
      const foundUrl = findGitHubUrl(metadata);
      if (foundUrl) {
        githubUrl = foundUrl;
        githubInfo = parseGitHubUrl(foundUrl);
        console.log('深度搜索找到URL:', foundUrl);
        console.log('解析结果:', githubInfo);
      }
    }
    
    // 5. 输出最终结果
    if (githubInfo) {
      const standardGithubUrl = `https://github.com/${githubInfo.owner}/${githubInfo.repo}`;
      console.log('\n✅ 最终标准化的GitHub URL:', standardGithubUrl);
      console.log('\n复制文本应该包含:');
      console.log(`GitHub地址：${standardGithubUrl}`);
    } else {
      console.log('\n❌ 未找到GitHub URL');
    }
    
  } catch (error) {
    console.error('测试失败:', error);
  }
}

// 运行测试
testSpacebin();