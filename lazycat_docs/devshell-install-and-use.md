---
source: https://developer.lazycat.cloud/devshell-install-and-use.html
downloaded: 2025-09-02 16:56:11
---

章节导航

# 开发依赖安装 ​

我们开发应用中， 需要提前在微服中安装一些开发所需的软件或依赖， 比如 python, pip, unzip 等。

下面有 4 种安装方式供您选择：

## devshell 手动安装 ​

devshell 进入微服应用容器后， 可以直接执行命令来安装

bash
    
    
    apk add python3 py3-pip unzip
    
    
    apk add python3 py3-pip unzip

1  


因为微服使用的镜像是 `alpine`, 所以需要用 `alpine` 的默认包管理工具 `apk` 来安装软件。

### 定义 setupscript 安装命令自动安装 ​

  * 在 lzc-build.yml 配置`setupscript`字段,每次进入 devshell 都会帮你执行 `setupscript` 字段后的脚本



yml
    
    
    devshell:
      setupscript:
        apk add python3 py3-pip unzip
    
    
    devshell:
      setupscript:
        apk add python3 py3-pip unzip

1  
2  
3  


### 定义 dependencies 安装依赖自动安装 ​

  * 在 lzc-build.yml 配置`dependencies`字段,它会自动帮你安装指定的依赖



yml
    
    
    devshell:
      dependencies:
        - python3
        - py3-pip
        - unzip
    
    
    devshell:
      dependencies:
        - python3
        - py3-pip
        - unzip

1  
2  
3  
4  
5  


## 定义 docker 镜像 ​

  * 在 lzc-build.yml 配置`image`字段,它会自动下载 docker 镜像



例如下面指定 Go 的环境:

yml
    
    
    devshell:
      image: registry.lazycat.cloud/golang:1.21.0-alpine3.18
    
    
    devshell:
      image: registry.lazycat.cloud/golang:1.21.0-alpine3.18

1  
2  


* * *

tip: 指定`image`之后`dependencies`会失效
