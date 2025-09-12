---
source: https://developer.lazycat.cloud/lzc-cli.html
downloaded: 2025-09-02 16:56:06
---

章节导航

# 开发环境搭建 ​

懒猫微服的应用的开发环境支持 Windows, Linux, macOS， 下面是开发环境的安装步骤:

  1. 安装依赖


  * 首先需要安装 [Node.js](<https://nodejs.org/zh-cn>) 18 及以上版本和 [懒猫微服客户端](<https://lazycat.cloud/download>)


  2. 安装懒猫云开发者工具


  * 懒猫云开发者工具是构建、 安装和部署懒猫微服应用的后台工具, 通过懒猫微服客户端商店， 搜索并安装[“懒猫开发者工具”](<https://appstore.lazycat.cloud/#/shop/detail/cloud.lazycat.developer.tools>)。


  3. 安装 lzc-cli ![NPM Version](https://img.shields.io/npm/v/%40lazycatcloud%2Flzc-cli)


  * [lzc-cli](<https://www.npmjs.com/package/@lazycatcloud/lzc-cli>) 是运行在开发者终端的命令行工具，可以认为是懒猫云开发工具的前端，利用它可以进行微服应用的开发、构建、安装、调试以及发布应用到商店等。



bash
    
    
    # 安装 lzc-cli
    npm install -g @lazycatcloud/lzc-cli
    
    
    # 安装 lzc-cli
    npm install -g @lazycatcloud/lzc-cli

1  
2  


  4. 安装系统依赖



根据您的操作系统， 安装系统依赖。

  * **Ubuntu / Debian** :

bash
        
        sudo apt update
        sudo apt install openssh-client rsync
        
        sudo apt update
        sudo apt install openssh-client rsync

1  
2  


  * **macOS** :

bash
        
        brew install rsync
        brew install openssh # 如果您已经有 ssh 的话可以不安装
        
        brew install rsync
        brew install openssh # 如果您已经有 ssh 的话可以不安装

1  
2  


`macOS` 系统自带的 `rsync` 版本较老，请使用 `Homebrew` 安装的 `rsync 版本 (v3.2.0+)`

  * **Windows**

Windows 10 以上已经自带 `ssh.exe`，不再需要额外安装其他依赖。

  * **Windows (WSL)** :

> Windows WSL 更多使用指南可以参考 [lzc-cli-wsl](<./lzc-cli-wsl.html>)

bash
        
        sudo apt update
        sudo apt install openssh-client rsync
        
        sudo apt update
        sudo apt install openssh-client rsync

1  
2  




  5. 连接到微服


  * 生成公钥:

bash
        
        #请确保 ssh 已经安装，以及 ssh-keygen 生成公钥
        ssh-keygen -t ed25519
        
        #请确保 ssh 已经安装，以及 ssh-keygen 生成公钥
        ssh-keygen -t ed25519

1  
2  


  * 添加 ssh 公钥到 `懒猫开发者工具` 中

bash
        
        lzc-cli box add-public-key #执行后，按照提示点击链接，完成添加ssh公钥
        
        lzc-cli box add-public-key #执行后，按照提示点击链接，完成添加ssh公钥

1  




