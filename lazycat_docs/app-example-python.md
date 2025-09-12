---
source: https://developer.lazycat.cloud/app-example-python.html
downloaded: 2025-09-02 16:56:08
---

章节导航

# 第一个 Python 应用 ​

真实的 Web 应用一般都有前后端， 前端专注界面的绘制， 后端提供服务和数据存储。 下面我们就用 Python 来开发一个真实的 Web 应用 - 待办清单， 通过对‘清单’的创建、 修改和删除来讲解 Python 后台的构建细节。

## 下载应用源码 ​

使用下面的命令先下载代办清单的源代码：

shell
    
    
    https://gitee.com/lazycatcloud/todolist-py-lzcapp-demo.git
    
    
    https://gitee.com/lazycatcloud/todolist-py-lzcapp-demo.git

1  


下载后的目录结构如下：

shell
    
    
    .
    ├── ui                // 前端代码
    ├── backend           // 后端代码
    ├── build.sh          // 项目二进制文件构建脚本
    ├── lzc-build.yml     // 懒猫应用构建脚本
    ├── lzc-manifest.yml  // 懒猫应用 Meta 信息配置
    ├── lzc-icon.png      // 懒猫应用图标
    └── README.md         // 项目简介
    
    
    .
    ├── ui                // 前端代码
    ├── backend           // 后端代码
    ├── build.sh          // 项目二进制文件构建脚本
    ├── lzc-build.yml     // 懒猫应用构建脚本
    ├── lzc-manifest.yml  // 懒猫应用 Meta 信息配置
    ├── lzc-icon.png      // 懒猫应用图标
    └── README.md         // 项目简介

1  
2  
3  
4  
5  
6  
7  
8  


## 快速测试 ​

根据我们前面学习的知识， 我们先快速启动一下这个应用:

  1. 构建前端



启动第一个终端， 启动前端服务:

shell
    
    
    # 进入远程应用容器的 shell
    lzc-cli project devshell
    
    # 进入容器 shell 后
    cd ui
    npm install
    npm run dev
    
    
    # 进入远程应用容器的 shell
    lzc-cli project devshell
    
    # 进入容器 shell 后
    cd ui
    npm install
    npm run dev

1  
2  
3  
4  
5  
6  
7  


  2. 构建后端



启动第二个终端， 启动后端服务：

shell
    
    
    lzc-cli project devshell
    
    # 进入容器 shell 后
    cd backend
    pip install -r requirements.txt --break-system-packages
    python main.py
    
    
    lzc-cli project devshell
    
    # 进入容器 shell 后
    cd backend
    pip install -r requirements.txt --break-system-packages
    python main.py

1  
2  
3  
4  
5  
6  


  3. 启动应用



前后端服务后， 点击启动器图标就可以查看代办清单应用的效果啦。

## 构建应用 ​

前面讲解的知识， 都需要开发者在本地或者微服中手动启动应用服务后， 应用才能正常运行。 但是， 每次重启微服后， 都需要执行一遍构建命令， 非常不方便。

下面， 我们教大家构建自己的第一个应用安装包， 通过安装包， 我们可以把应用安装到微服中， 每次点击启动器应用图标， 应用的前后端服务会自动启动。

警告操作

如果您在Windows进行构建操作，下面这步依赖git bash这类unix shell

也可修改build.sh的内容为powershell/cmd支持的语法

  1. 构建应用



首先,我们需要通过 lzc-cli 去构建我们的应用输出一个 lpk 文件：

shell
    
    
    # 在本地安装应用 npm 依赖
    cd ui # 进入界面目录
    npm install # 安装前端依赖包
    cd .. # 返回项目根目录
    
    # 构建 lpk
    lzc-cli project build -o release.lpk
    
    
    # 在本地安装应用 npm 依赖
    cd ui # 进入界面目录
    npm install # 安装前端依赖包
    cd .. # 返回项目根目录
    
    # 构建 lpk
    lzc-cli project build -o release.lpk

1  
2  
3  
4  
5  
6  
7  


  2. 安装应用



通过下面命令安装到懒猫微服中

shell
    
    
    lzc-cli app install release.lpk
    
    
    lzc-cli app install release.lpk

1  


INFO

如果您安装了很久，仍然没有安装完成，可能是您所在地区的网络访问 `清华` 和 `中科大` 镜像不太流畅，需要自行修改。

编辑: backend/run.sh 将里面的 `mirrors.ustc.edu.cn` 或 `tuna.tsinghua.edu.cn` 修改为您所在地区最佳的即可。

安装应用包后， 就可以通过启动器点击应用图标啦， 我们的第一个应用就这样部署完了， 是不是很有成就感？

小技巧

> lpk 软件包除了可以通过 lzc-cli 命令安装， 还可以把安装包上传懒猫网盘双击安装
