---
source: https://developer.lazycat.cloud/devshell-local.html
downloaded: 2025-09-02 16:56:11
---

章节导航

# devshell本地开发配置 ​

Hello World 示例讲解了怎么在微服中开发应用， 您只需要在远程终端中编辑源码后， Vue 会自动构建新的页面预览服务。

但是在远端服务器直接编辑代码没有那么方便。 在本地模式下， 您只需要在您本地的 PC 编辑源代码， 微服会同步源码到服务器并自动构建， 相对于云端代码编辑， 效率更高。

切换方式很简单， 以 `helloworld`​ 项目为例， 打开项目中的 `lzc-build.yml`​ 中的文件， 找到 devshell/routes 章节：

yaml
    
    
    devshell:
      routes: #此字段会合并到lzc-manifest.yml中，最终结果可以进到devshell后cat /lzcapp/pkg/manifest.yml查看
        - /=http://127.0.0.1:3000
    
    
    devshell:
      routes: #此字段会合并到lzc-manifest.yml中，最终结果可以进到devshell后cat /lzcapp/pkg/manifest.yml查看
        - /=http://127.0.0.1:3000

1  
2  
3  


将整个路由都转发到您开发机器的局域网IP，此IP需要确保可以被微服直接访问到

yaml
    
    
    devshell:
      routes:
        - /=http://${开发机的局域网IP}:3000
    
    
    devshell:
      routes:
        - /=http://${开发机的局域网IP}:3000

1  
2  
3  


修改完成后在终端中执行下面命令来重新构建容器:

bash
    
    
    cd helloworld
    lzc-cli project devshell -f
    
    
    cd helloworld
    lzc-cli project devshell -f

1  
2  


然后在本地终端（注意是本地的终端， 不是云端终端）执行：

bash
    
    
    cd helloworld
    npm install
    npm run dev
    
    
    cd helloworld
    npm install
    npm run dev

1  
2  
3  


完成以上配置后， 您只需要在本地修改一下代码， 应用镜像会在云端自动构建更新， 再重新点击应用图标， 是不是就可以看到新的效果啦？
