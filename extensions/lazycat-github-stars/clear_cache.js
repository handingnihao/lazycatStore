// 清除缓存脚本
// 在浏览器控制台中运行此脚本来清除插件缓存

// 清除特定应用的缓存
async function clearAppCache(appId) {
  return new Promise((resolve) => {
    chrome.storage.local.remove(appId, () => {
      console.log(`已清除 ${appId} 的缓存`);
      resolve();
    });
  });
}

// 清除所有缓存
async function clearAllCache() {
  return new Promise((resolve) => {
    chrome.storage.local.get(null, async (items) => {
      const keys = Object.keys(items).filter(key => 
        !key.startsWith('setting_') && key !== 'githubToken'
      );
      
      if (keys.length === 0) {
        console.log('没有缓存需要清除');
        resolve();
        return;
      }
      
      chrome.storage.local.remove(keys, () => {
        console.log(`已清除 ${keys.length} 个应用的缓存`);
        console.log('清除的应用ID:', keys);
        resolve();
      });
    });
  });
}

// 使用示例：
// 清除 spacebin 的缓存
// clearAppCache('cloud.lazycat.app.spacebin');

// 清除所有缓存
// clearAllCache();

console.log('缓存清除脚本已加载');
console.log('使用方法:');
console.log('  clearAppCache("cloud.lazycat.app.spacebin") - 清除特定应用缓存');
console.log('  clearAllCache() - 清除所有应用缓存');