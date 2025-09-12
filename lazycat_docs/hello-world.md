---
source: https://developer.lazycat.cloud/hello-world.html
downloaded: 2025-09-02 16:56:07
---

章节导航

# Hello World ​

下面请随我们下面的步骤， 一起来构建我们第一个应用吧。

首先， 使用 lzc-cli 来创建一个名为 `helloworld` 的项目：

bash
    
    
    lzc-cli project create helloworld
    
    
    lzc-cli project create helloworld

1  


按提示完成初始化后， 终端会输出如下内容：

bash
    
    
    ? 选择项目构建模板 vue3
    ? 请输入应用 ID, 如(helloworld) helloworld
    ✨ 初始化项目 helloworld
    ✨ 初始化懒猫云应用
    ✨ 懒猫微服应用已创建成功 !
    ✨ 进行下面步骤后即可进入容器开发
       cd helloworld
       lzc-cli project devshell
    ⚙️  进入应用容器后执行下面命令:
       npm install
       npm run dev
    🚀 启动应用:
       进入微服客户端启动器页面点击应用图标来测试应用
    
    
    ? 选择项目构建模板 vue3
    ? 请输入应用 ID, 如(helloworld) helloworld
    ✨ 初始化项目 helloworld
    ✨ 初始化懒猫云应用
    ✨ 懒猫微服应用已创建成功 !
    ✨ 进行下面步骤后即可进入容器开发
       cd helloworld
       lzc-cli project devshell
    ⚙️  进入应用容器后执行下面命令:
       npm install
       npm run dev
    🚀 启动应用:
       进入微服客户端启动器页面点击应用图标来测试应用

1  
2  
3  
4  
5  
6  
7  
8  
9  
10  
11  
12  
13  


然后执行以下命令进入容器开发环境：

bash
    
    
    cd helloworld
    lzc-cli project devshell
    
    
    cd helloworld
    lzc-cli project devshell

1  
2  


成功进入容器后， 终端将显示如下信息：

bash
    
    
    [info] 开始部署应用
    [info] 安装成功！
    [info] 👉 请在浏览器中访问 https://helloworld.178me.heiyu.space
    [info] 👉 使用微服的用户名和密码登录
    
    
    [info] 开始部署应用
    [info] 安装成功！
    [info] 👉 请在浏览器中访问 https://helloworld.178me.heiyu.space
    [info] 👉 使用微服的用户名和密码登录

1  
2  
3  
4  


在容器中执行以下命令启动应用：

bash
    
    
    npm install
    npm run dev
    
    
    npm install
    npm run dev

1  
2  


前端服务将运行在容器的 3000 端口：

bash
    
    
    Local:   http://localhost:3000/
    Network: http://172.31.0.36:3000/
    
    
    Local:   http://localhost:3000/
    Network: http://172.31.0.36:3000/

1  
2  


此时， 应用服务已经启动， 您可以在 PC 或者手机端点击 "helloworld" 图标， 查看应用在每个终端平台的效果。

懒猫微服的一大优势是， 您只需要编写一次 JavaScript, 我们自动解决应用在 Windows/Linux/macOS/Android/iOS/鸿蒙 6 个操作系统平台上跨平台运行的问题， 为开发者节省了大量平台适配的时间。

如果想要部署这个 Hello World 到懒猫微服中，可以参考 [构建应用](<https://developer.lazycat.cloud/app-example-python.html#%E6%9E%84%E5%BB%BA%E5%BA%94%E7%94%A8>)。
