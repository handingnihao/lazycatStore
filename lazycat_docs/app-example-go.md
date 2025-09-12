---
source: https://developer.lazycat.cloud/app-example-go.html
downloaded: 2025-09-02 16:56:10
---

章节导航

# 第一个 Golang 应用 ​

刚才我们已经学会了用 Python 开发懒猫微服的应用， 其实 Golang 应用的目录结构完全和 Python 应用是一样的。

## 下载应用源码 ​

shell
    
    
    https://gitee.com/lazycatcloud/todolist-go-lzcapp-demo.git
    
    
    https://gitee.com/lazycatcloud/todolist-go-lzcapp-demo.git

1  


## 打包和安装应用 ​

警告操作

如果您在Windows进行构建操作，下面这步依赖git bash这类unix shell

也可修改build.sh的内容为powershell/cmd支持的语法

shell
    
    
    # 在本地安装应用 npm 依赖
    cd ui # 进入界面目录
    npm install # 安装前端依赖包
    cd .. # 返回项目根目录
    
    # 构建 lpk
    lzc-cli project build -o release.lpk
    
    # 安装 lpk
    lzc-cli app install release.lpk
    
    
    # 在本地安装应用 npm 依赖
    cd ui # 进入界面目录
    npm install # 安装前端依赖包
    cd .. # 返回项目根目录
    
    # 构建 lpk
    lzc-cli project build -o release.lpk
    
    # 安装 lpk
    lzc-cli app install release.lpk

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

