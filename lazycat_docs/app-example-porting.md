---
source: https://developer.lazycat.cloud/app-example-porting.html
downloaded: 2025-09-02 16:56:35
---

章节导航

# 移植一个应用 ​

有时候我们只想部署一个已经存在的docker，或者说开发的应用依赖别人的docker，需要先运行一个数据库、消息通信等组件，接下来我们将以 gitlab 为例带您一步步把docker镜像移植到懒猫微服上运行。

在此之前，您需要简单了解一下`lzc-build.yml`和`lzc-manifest.yml`的各个配置项的含义。这个在[应用配置详解](<./app-example-python-description.html#lzc-build-yml>)中有讲解，已经有的内容这里不再赘述。这里简单介绍一下`services`这个配置项，在`services`中，我们可以指定多个服务，每个服务有一个名字，每一个服务底下可以指定一个docker镜像，针对这个镜像，可以配置环境变量，存储位置、启动命令等。一个应用的services配好大致长这样：

yaml
    
    
    services:
      servicename1:
        image: xxx/yyy:123
        environment:
          - ENV1=123
        binds:
          - /lzcapp/run/mnt/home:/home
    
    
    services:
      servicename1:
        image: xxx/yyy:123
        environment:
          - ENV1=123
        binds:
          - /lzcapp/run/mnt/home:/home

1  
2  
3  
4  
5  
6  
7  


## 从Docker镜像转换成懒猫微服应用 ​

### 找到应用启动的docker命令 ​

举个简单的例子，假设我们需要将Gitlab移植到懒猫微服，可以先去gitlab官网，通过查看[Docker Engine安装](<https://docs.gitlab.com/ee/install/docker/installation.html#install-gitlab-by-using-docker-engine>) 能看到底下有一个docker命令

bash
    
    
     sudo docker run --detach \
       --hostname gitlab.example.com \
       --env GITLAB_OMNIBUS_CONFIG="external_url 'http://gitlab.example.com'" \
       --publish 443:443 --publish 80:80 --publish 22:22 \
       --name gitlab \
       --restart always \
       --volume $GITLAB_HOME/config:/etc/gitlab \
       --volume $GITLAB_HOME/logs:/var/log/gitlab \
       --volume $GITLAB_HOME/data:/var/opt/gitlab \
       --shm-size 256m \
       gitlab/gitlab-ee:<version>-ee.0
    
    
     sudo docker run --detach \
       --hostname gitlab.example.com \
       --env GITLAB_OMNIBUS_CONFIG="external_url 'http://gitlab.example.com'" \
       --publish 443:443 --publish 80:80 --publish 22:22 \
       --name gitlab \
       --restart always \
       --volume $GITLAB_HOME/config:/etc/gitlab \
       --volume $GITLAB_HOME/logs:/var/log/gitlab \
       --volume $GITLAB_HOME/data:/var/opt/gitlab \
       --shm-size 256m \
       gitlab/gitlab-ee:<version>-ee.0

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


### 将docker命令转换成微服的manifest ​

这里面有很多参数，我们主要关注`--env`、`--publish`、`--volume`，以及最后的镜像名称（这里镜像名称是`gitlab/gitlab-ee:<version>-ee.0`）。

其中

  * `--env`是环境变量，对应到`lzc-manifest.yml`的`environment`
  * `--publish`指明了`docker`通过什么端口来提供服务。微服不推荐直接将端口暴露出去，如果是`http(s)`服务建议通过`application`下的`routes`来配置。如果**不是**`http(s)`服务，想要暴露出去，比如这里的22端口，应该是ssh协议的服务，那么可以通过配置`application -> ingress`来完成，详细配置参考 [外网API服务](<./advanced-public-api.html>)。
  * `--volume`配置的通常是docker中用来存储持久化数据的地方。可以通过配置`service -> binds`参数来实现。`volume`后面的值，冒号右边对应到docker中的实际位置，微服配置的`binds`接收的值和`volume`相似，只是我们的冒号左边，一定需要`/lzcapp`开头的文件路径，通常是`/lzcapp/var`或者`/lzcapp/cache`开头, 更为详细的目录可以参考 [文件访问](<./advanced-file.html>)。比如这里的`$GITLAB_HOME/config:/etc/gitlab`，转成`binds`配置，可以写成`/lzcapp/var/config:/etc/gitlab`
  * 镜像名称。这个填到`service`的`image`参数后面就行



因此, 这个docker命令就能转换成`services`配置：

yaml
    
    
    services:
      gitlab:
        image: gitlab/gitlab-ee:17.2.8-patch7
        binds:
          - /lzcapp/var/config:/etc/gitlab
          - /lzcapp/var/logs:/var/log/gitlab
          - /lzcapp/var/data:/var/opt/gitlab
        environment:
          - GITLAB_OMNIBUS_CONFIG=external_url 'http://gitlab.example.com'
    
    
    services:
      gitlab:
        image: gitlab/gitlab-ee:17.2.8-patch7
        binds:
          - /lzcapp/var/config:/etc/gitlab
          - /lzcapp/var/logs:/var/log/gitlab
          - /lzcapp/var/data:/var/opt/gitlab
        environment:
          - GITLAB_OMNIBUS_CONFIG=external_url 'http://gitlab.example.com'

1  
2  
3  
4  
5  
6  
7  
8  
9  


结合[应用配置详解](<./app-example-python-description.html#lzc-build-yml>)中的那些必填字段，把routes或者ingress配置到docker提供的端口（在这个例子中，routes需要填写80端口，ingress需要配置一下22端口，就形成了完整的`lzc-manifest.yml`：

yaml
    
    
    lzc-sdk-version: '0.1'
    name: GitLab
    package: cloud.lazycat.app.gitlab
    version: 17.2.8-patch1
    application:
      routes:
        - /=http://gitlab.cloud.lazycat.app.gitlab.lzcapp:80 # gitlab是services中的名字，.lzcapp是固定后缀，中间的是上面的package字段
      subdomain: gitlab
      ingress:
        - protocol: tcp
          port: 22
          service: gitlab
    services:
      gitlab: # 应用名字可以自定义，但是不能使用app 
        image: gitlab/gitlab-ee:17.2.8
        binds:
          - /lzcapp/var/config:/etc/gitlab
          - /lzcapp/var/logs:/var/log/gitlab
          - /lzcapp/var/data:/var/opt/gitlab
        environment:
          - GITLAB_OMNIBUS_CONFIG=external_url 'http://gitlab.${LAZYCAT_BOX_DOMAIN}'; gitlab_rails['lfs_enabled'] = true;
    
    
    lzc-sdk-version: '0.1'
    name: GitLab
    package: cloud.lazycat.app.gitlab
    version: 17.2.8-patch1
    application:
      routes:
        - /=http://gitlab.cloud.lazycat.app.gitlab.lzcapp:80 # gitlab是services中的名字，.lzcapp是固定后缀，中间的是上面的package字段
      subdomain: gitlab
      ingress:
        - protocol: tcp
          port: 22
          service: gitlab
    services:
      gitlab: # 应用名字可以自定义，但是不能使用app 
        image: gitlab/gitlab-ee:17.2.8
        binds:
          - /lzcapp/var/config:/etc/gitlab
          - /lzcapp/var/logs:/var/log/gitlab
          - /lzcapp/var/data:/var/opt/gitlab
        environment:
          - GITLAB_OMNIBUS_CONFIG=external_url 'http://gitlab.${LAZYCAT_BOX_DOMAIN}'; gitlab_rails['lfs_enabled'] = true;

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
14  
15  
16  
17  
18  
19  
20  
21  


### 补全需要的文件并安装 ​

`lzc-manifest.yml`有了, 我们在下载一个[Gitlab的png格式](<https://images.ctfassets.net/xz1dnu24egyd/1IRkfXmxo8VP2RAE5jiS1Q/ea2086675d87911b0ce2d34c354b3711/gitlab-logo-500.png>)作为图标，最后再填一个`lzc-build.yml`:

yaml
    
    
    pkgout: ./ # 输出的lpk包的位置
    icon: ./icon.png   # 图标文件的位置
    
    
    pkgout: ./ # 输出的lpk包的位置
    icon: ./icon.png   # 图标文件的位置

1  
2  


所需要的文件就准备完了，将这些文件放到一个文件夹中，文件目录看起来长这样：
    
    
    .
    ├── lzc-build.yml     // 懒猫应用构建脚本
    ├── lzc-manifest.yml  // 懒猫应用 Meta 信息配置
    └── icon.png          // 懒猫应用图标
    
    
    .
    ├── lzc-build.yml     // 懒猫应用构建脚本
    ├── lzc-manifest.yml  // 懒猫应用 Meta 信息配置
    └── icon.png          // 懒猫应用图标

1  
2  
3  
4  


在命令行中，进入这个目录，执行`lzc-cli project build`，执行完成后，目录下会多一个文件： `cloud.lazycat.app.gitlab-v17.2.8-patch1.lpk`, 最后执行`lzc-cli app install ./cloud.lazycat.app.gitlab-v17.2.8-patch1.lpk`来安装刚刚的lpk包，即可完成安装。

## 从docker-compose转换成懒猫微服应用 ​

还是刚才的Gitlab，我们可以先去Gitlab官网，找到如何通过[Docker Compose安装](<https://docs.gitlab.com/ee/install/docker/installation.html#install-gitlab-by-using-docker-compose>)

能看到底下有一个**docker-compose.yml** 文件例子

yaml
    
    
    version: '3.6'
    services:
      gitlab:
        image: gitlab/gitlab-ee:<version>-ee.0
        container_name: gitlab
        restart: always
        hostname: 'gitlab.example.com'
        environment:
          GITLAB_OMNIBUS_CONFIG: |
            # Add any other gitlab.rb configuration here, each on its own line
            external_url 'https://gitlab.example.com'
        ports:
          - '80:80'
          - '443:443'
          - '22:22'
        volumes:
          - '$GITLAB_HOME/config:/etc/gitlab'
          - '$GITLAB_HOME/logs:/var/log/gitlab'
          - '$GITLAB_HOME/data:/var/opt/gitlab'
        shm_size: '256m'
    
    
    version: '3.6'
    services:
      gitlab:
        image: gitlab/gitlab-ee:<version>-ee.0
        container_name: gitlab
        restart: always
        hostname: 'gitlab.example.com'
        environment:
          GITLAB_OMNIBUS_CONFIG: |
            # Add any other gitlab.rb configuration here, each on its own line
            external_url 'https://gitlab.example.com'
        ports:
          - '80:80'
          - '443:443'
          - '22:22'
        volumes:
          - '$GITLAB_HOME/config:/etc/gitlab'
          - '$GITLAB_HOME/logs:/var/log/gitlab'
          - '$GITLAB_HOME/data:/var/opt/gitlab'
        shm_size: '256m'

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
14  
15  
16  
17  
18  
19  
20  


这里面有很多配置，这里的services的层次结构和lzc-manifest中的services其实是类似的，不过我们主要关注`environment`、`ports`、`volumes`和`image`，这里几个参数分别等同于上面docker命令中提到的`--env`、`--publish`、`--volume`和镜像名。遵循相同的转换规则，即可将`docker-compose.yml`转换成`lzc-manifest.yml`。剩余的步骤也和 补全需要的文件并安装 章节一样。

## 常见问题 ​

### image拉不下来怎么办 ​

由于一些原因，可能docker image不能成功拉下来。如果只是自己用，可以考虑参考[开发测试镜像](<./advanced-dev-image.html>)中的**重新tag镜像** 步骤和**推送镜像** 步骤。如果考虑公用，则需要自行建立registry。

## 社区移植工具 ​

如果你觉得步骤繁琐，想一键把docker-compose转换成懒猫应用，不妨试试社区大佬的转换工具： [docker2lzc](<https://www.npmjs.com/package/docker2lzc>)

## 官方移植开源仓库 ​

官方的移植开源是个很好学习的仓库，欢迎参考: <https://gitee.com/lazycatcloud/appdb>
