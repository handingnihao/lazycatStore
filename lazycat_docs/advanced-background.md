---
source: https://developer.lazycat.cloud/advanced-background.html
downloaded: 2025-09-02 16:56:15
---

章节导航

# 后台常驻 ​

微服系统具备先进的 `服务调度机制`， 当某个应用长期不活跃时， 微服系统会自动停止对应的应用， 提升系统的整体响应速度。

当我们开发某些特殊应用时， 比如下载器， 需要长时间后台下载文件。 这时我们并不希望微服系统按照活跃度来调度我们的应用。

只需在 `lzc-manifest.yml` 文件中的 `application` 字段下加一个 `background_task` 子字段即可， 举例：

yml
    
    
    application:
      background_task: true
    
    
    application:
      background_task: true

1  
2  


小技巧

小贴士: 目前的微服版本中 `background_task` 参数还会影响应用是否自启动 (需要注意， 自启动行为仅针对 [单实例](<./advanced-multi-instance.html>) 应用有效)， 当然用户可以在微服的应用管理中手动禁用应用自启行为。
