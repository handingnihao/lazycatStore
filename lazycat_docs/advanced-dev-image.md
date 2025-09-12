---
source: https://developer.lazycat.cloud/advanced-dev-image.html
downloaded: 2025-09-02 16:56:12
---

章节导航

# 开发测试镜像 ​

`懒猫开发者工具` 支持 `docker registry v2` API， 您可以按照下面方法将本地的测试镜像推送到盒子进行测试。

  * 创建 `Dockerfile`

Dockerfile
        
        FROM busybox:latest
        
        #lzcapp中的所有service都必须一直处于运行状态,否则应用会进入错误状态
        CMD ["sleep", "1d"]
        
        FROM busybox:latest
        
        #lzcapp中的所有service都必须一直处于运行状态,否则应用会进入错误状态
        CMD ["sleep", "1d"]

1  
2  
3  
4  


  * 构建镜像

sh
        
        docker build --platform linux/amd64 -t lzc/helloworld:latest .
        
        docker build --platform linux/amd64 -t lzc/helloworld:latest .

1  


如果您当前是使用ARM64或非x86架构,需要通过`--platform`强制指定平台为`linux/amd64`.

  * 重新 `tag` 镜像成 `dev.$BOXNAME.heiyu.space` 地址, `$BOXNAME` 为目标盒子名.

sh
        
        BOXNAME=$(lzc-cli box default)
        docker tag lzc/helloworld:latest dev.$BOXNAME.heiyu.space/lzc/helloworld:latest
        
        BOXNAME=$(lzc-cli box default)
        docker tag lzc/helloworld:latest dev.$BOXNAME.heiyu.space/lzc/helloworld:latest

1  
2  


  * 推送镜像

sh
        
        docker push dev.$BOXNAME.heiyu.space/lzc/helloworld:latest
        
        docker push dev.$BOXNAME.heiyu.space/lzc/helloworld:latest

1  


  * `lzc-build.yml` 或者 `lzc-manifest.yml` 中使用

yml
        
        services:
          helloworld:
            image: dev.$BOXNAME.heiyu.space/lzc/helloworld:latest
        
        services:
          helloworld:
            image: dev.$BOXNAME.heiyu.space/lzc/helloworld:latest

1  
2  
3  


  * 拉取镜像

sh
        
        docker pull dev.$BOXNAME.heiyu.space/lzc/helloworld:latest
        
        docker pull dev.$BOXNAME.heiyu.space/lzc/helloworld:latest

1  




