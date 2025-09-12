---
source: https://developer.lazycat.cloud/app-example-python-description.html
downloaded: 2025-09-02 16:56:09
---

章节导航

# Python 应用配置详解 ​

上一章我们讲了怎么构建第一个 Python 应用， 这一章我们详细的分析 Python 应用的构建细节。

## lzc-build.yml ​

[lzc-build.yml](<./spec/build.html>) 是控制应用构建的配置文件。

先介绍一下这个配置文件基本的关键字和用处：

  * `buildscript`: 构建脚本， 可以为构建脚本的路径地址， 也可以直接写 sh 的命令

根据 buildscript 定义的脚本， 把 contentdir 下面的所有文件打包成一个 lpk 压缩包， 最后安装到微服中。

  * `manifest`: 指定 lpk 包的 manifest.yml 文件路径

此处的 manifest 文件是应用的元信息， 比如应用的名称， 版本， 描述等。

  * `contentdir`: 指定打包的内容，将会打包到 lpk 中

此处的 contentdir 是需要指定为目录， 目录里面的文件将会被打包到 lpk 中。

  * `pkgout`: lpk 包的输出路径

此处的 pkgout 是 lpk 包的输出路径， 将会把打包好的 lpk 包输出到此路径。

  * `icon`: lpk 包 icon 的路径路径，如果不指定将会警告

icon 仅仅允许 png 后缀的文件

  * `devshell`: 指定开发依赖的情况

此处的 devshell 是开发依赖的情况， 比如开发依赖的依赖， 开发依赖的脚本等。


示例

shell
    
    
    # 整个文件中，可以通过 ${var} 的方式，使用 manifest 字段指定的文件定义的值
    
    # buildscript
    # - 可以为构建脚本的路径地址
    # - 如果构建命令简单，也可以直接写 sh 的命令
    buildscript: sh build.sh
    
    # manifest: 指定 lpk 包的 manifest.yml 文件路径
    manifest: ./lzc-manifest.yml
    
    # contentdir: 指定打包的内容，将会打包到 lpk 中
    contentdir: ./dist
    
    # pkgout: lpk 包的输出路径
    pkgout: ./
    
    # icon 指定 lpk 包 icon 的路径路径，如果不指定将会警告
    # icon 仅仅允许 png 后缀的文件
    icon: ./lzc-icon.png
    
    # dvshell 指定开发依赖的情况
    # 这种情况下，选用 alpine:latest 作为基础镜像，在 dependencies 中添加所需要的开发依赖即可
    # 如果 dependencies 和 build 同时存在，将会优先使用 dependencies
    devshell:
      routes:
        - /=http://127.0.0.1:5173
      dependencies:
        - nodejs
        - npm
        - python3
        - py3-pip
      setupscript: |
        export npm_config_registry=https://registry.npmmirror.com
        export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
    
    
    # 整个文件中，可以通过 ${var} 的方式，使用 manifest 字段指定的文件定义的值
    
    # buildscript
    # - 可以为构建脚本的路径地址
    # - 如果构建命令简单，也可以直接写 sh 的命令
    buildscript: sh build.sh
    
    # manifest: 指定 lpk 包的 manifest.yml 文件路径
    manifest: ./lzc-manifest.yml
    
    # contentdir: 指定打包的内容，将会打包到 lpk 中
    contentdir: ./dist
    
    # pkgout: lpk 包的输出路径
    pkgout: ./
    
    # icon 指定 lpk 包 icon 的路径路径，如果不指定将会警告
    # icon 仅仅允许 png 后缀的文件
    icon: ./lzc-icon.png
    
    # dvshell 指定开发依赖的情况
    # 这种情况下，选用 alpine:latest 作为基础镜像，在 dependencies 中添加所需要的开发依赖即可
    # 如果 dependencies 和 build 同时存在，将会优先使用 dependencies
    devshell:
      routes:
        - /=http://127.0.0.1:5173
      dependencies:
        - nodejs
        - npm
        - python3
        - py3-pip
      setupscript: |
        export npm_config_registry=https://registry.npmmirror.com
        export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

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
22  
23  
24  
25  
26  
27  
28  
29  
30  
31  
32  
33  
34  


## lzc-manifest.yml ​

[lzc-manifest.yml](<./spec/manifest.html>) 是控制应用 Meta 信息的配置文件。

先介绍一下这个配置文件基本的关键字和用处：

  * `name`: 应用名称
  * `package`: 应用的子域名， 如果不上架懒猫微服应用商店， 这个名字可以随便取
  * `version`: 版本号
  * `description`: 应用描述
  * `license`: 应用的发行许可证
  * `homepage`: 项目主页
  * `author`: 作者信息



这个文件最重要的是 [application.routes](<./advanced-route.html>)：

shell
    
    
    application:
      subdomain: todolistpy
      routes:
        - /=file:///lzcapp/pkg/content/web
        - /api/=exec://3000,./lzcapp/pkg/content/backend/run.sh
    
    
    application:
      subdomain: todolistpy
      routes:
        - /=file:///lzcapp/pkg/content/web
        - /api/=exec://3000,./lzcapp/pkg/content/backend/run.sh

1  
2  
3  
4  
5  


  * `subdomain: todolistpy`

应用子域名， 和上面的 `package` 字段的域名相关联。

  * ​`/=file:///lzcapp/pkg/content/web`

这个路由表示， 当用户访问应用时， 也就是访问路由 `/` 时， 应用程序会自动返回 `/lzcapp/pkg/content/web` 目录下的 `index.html` 文件。 `/lzcapp/pkg/content` 其实就是对应前面 `lzc-build.yml` 文件中的 `contentdir` 目录。

  * ​`/api/=exec://3000,./lzcapp/pkg/content/backend/run.sh`:

这个路由表示， 当用户访问路由 `/api/`​ 时， 应用程序会启动 `./lzcapp/pkg/content/backend/run.sh` 脚本提供后端服务， 后端服务脚本监听 3000 端口。




`application` 字段下具有以下字段:

字段| 说明| 备注  
---|---|---  
subdomain| 配置应用子域名| 仅为默认值， 后续系统版本允许管理员调整  
multi_instance| [配置多实例(同一个应用 ， 各用户数据隔离)](<./advanced-multi-instance.html>)| 仅为默认 值， 后续系统版本允许管理员调整  
routes| [配置应用规则](<./advanced-route.html>)| 所有 http 相关逻辑应该在这里声明  
public_path| [配置外网 API](<./advanced-public-api.html>)| 不建议使用  
ingress| [配置外网端口](<./advanced-public-api.html>)| 仅建议 在需要提 供非 HTTP 服务时使用  
file_handler| 声明本 app 支持操作的文件类型， [应用关联](<./advanced-mime.html>)| 工具 类应用建议配置此选项， 以便网盘里打开文件时可以选择使用本应用  
示例

yml
    
    
    package: abc.example.com # app 的唯一 id,上架到商店需要保证不要冲突,尽量使用开发者自己的域名作为后缀.
    version: 2.0.2           #app 的版本
    
    name: 测试abc   #软件名称,会显示在启动器之类的地方
    description: 简单易用的英语学习软件
    
    license: https://choosealicense.com/licen ses/mit/  #软件本身的 license
    homepage: http://github.com/snyh/abc #软件的主页,会在商店等地方体现
    author: snyh@snyh.org #lpk 的作者,会在商店等地方体现
    
    unsupported_platforms: # 不支持的平 台, 不写则表示全平台支持. lpk 本身是可以被安装的,但下面列表中的平台无法打开此软件
      - linux
      - macos
      - windows
      - android
      - ios
      - tvos
    
    
     #application 作为一个特殊的 container 运行， 对应的 service 名称为固定的` app`， 其他 service 可以通过此名称与 app 进行通讯
    application:
      background_task: false #是否存在后台任务， 若存在则系统不会对此 app 进行主动休眠等操作
    
      subdomain: abc  #期望的 app 域名， 如果系统中已经有对应域名则会提示用户选择其他域名。  最终 app 分配到的域名以/lzcapp/run/app.subdomain 为准
    
      routes:
        - /api/=exec://8000,/lzcapp/pkg/content/bin/backend     #格式与/usr/bin/lzcinit -up 参数一致
        - /api/=http://service.appid.lzcapp:8000            #多实例应用会自动在 route 里加上 uid
        - /=file:///lzcapp/pkg/content/dist/
    
      public_path:
        - /api/public  #默认情况下所有路径都需要登陆后才能访问， public_path 之下的路径允许非登陆情况下访问
    
      ingress:
        - protocol: tcp     #tcp or udp
          port: 22          #需要曝露的端口号
          service: db       #为空则为此 app 容器内的端口,也可以指定为 db 等其他 service 的名称
    
      multi_instance: true # 是否启用多实例
    
      workdir: /lzcapp/pkg/content / #设置 lzcinit 以及后续子进程的 WORKDIR,若不设置或目录不存在则保持使用  container 的 WORKDIR 信息
    
      usb_accel: false # 挂在/dev/bus/usb 到容器
      gpu_accel : false # 是否允许使用硬件 加速
      kvm_accel: true  # enable 后会挂 在/dev/kvm 和/dev/network-host 到所有  service 中
    
      file_handler: # 声明本 app 支持操作的文件类型， mime 至少存在一条记录， actions 至少要支持 open
        mime:  #按照 mime 类型注册到系统
          - x-scheme-handler/http
          - x-scheme-handler/https
          - text/html
          - application/xhtml+xml
          - x-lzc-extension/km      # app 支持.km 文件 名后缀
        actions:   #打开对应文件的 url 路径,由文件管理器等 app 调用
          open: /open?file=%u   #%u 是某个 webdav 上的具体文件路径， 一定存在
          new:  /open?file=%u   #%u 是某个 webdav 上的具体文件路径， 不一定存在
          download: /download?file=%u #%u 是某个 webdav 上的具 体文件路径， 一定存在
    
       environment:
        - MYPASSWORD=123456
    
      image:  alpine:3.16  #可选 的运行环境， 为空则使用 sdk 对应版本的镜像。 若上架到商店， 则此处的镜像必须上传到商店仓库统一托管 。
    
      handlers:
        # 当 ro utes 中 https/ http/exec 类型的反代出现错误时， 则渲染对应模板。
        # 若错误类型为无法返回任何数据， 则会生成一个 502 响应， 比如上游游服务器不存在或网络不通等完全获取不到一个 http response 的情况。
        #
        # 其他情况则根据 http response status code， 选择对应的模板
        # 若命中错误处理页面, 则 http response status code 本身不会进行修改
        #
        # 页 面渲染使用此数据结构
          # struct {
          #    StatusCode int
          #    ErrorDetail string #无法获取 http response 的情况下， 此字段会显示对应错误信息， 并将 StatusCode 设置为 502
          # }
        error_page_templates:
          502: /lzcapp/pkg/content/errors/502.html.tpl
          404: /lzcapp/pkg/content/errors/404.html.tpl
    
    
    
    services: #传统 docker 镜像启动方式， 如果需要数据库等配套容器一起运行则可以在这里申明。 传统 app 如 nextcloud、 aria2c 也可以使用这种方式进行兼容运行
      backend:
        image: alpine:3.18
    
        depends_on:
          - db
    
      db: #目前只支持以下参数， network,ipc 之类的配置字段(故意)不支持
        image: bitnami/wordpress:5.8.2
        environment:
          - ALLOW_EMPTY_PASSWORD=yes
          # oauth 相关的环境变量
          - LAZYCAT_AUTH_OIDC_CLIENT_ID=xxx
          - LAZYCAT_AUTH_OIDC_CLIENT_SECRET=xxx
          - LAZYCAT_AUTH_OIDC_ISSUER_URL=xxx
    
    
        # 仅支持以下挂载点:
        # - /lzcapp/run
        # - /lzcapp/run/mnt/home
        # - /lzcapp/var
        # - /lzcapp/cache
        # - /lzcapp/pkg
        binds:
          - /lzcapp/run/mnt/home:/home  #将/lzcapp/run/mnt/home(即用户文稿)目录挂在到容器内的/home 目录
          - /lzcapp/var/db:/data
          - /lzcapp/cache/db:/cache
          - /lzcapp/pkg/content/entrypoint.sh:/entrypoint.sh # 挂载 lpk 包内的文件
    
        entrypoint: /bin/sh -c
        command: "/usr/bin/nextcloud"
    
        depends_on:
          - ui
    
        # network_mode 仅支持 host 模式， 开启后此 service 可以访问所有网卡， 但失去 lzcdns 特性
        # 非必要尽量不要使用此模式， 需要谨慎处理代码， 存在很高安全风险
        # 如果要在 network=host service 中提供内部服务， 请监听在`host.lzcapp`这个内部 IP 上， 不要直接监听 0.0.0.0
        network_mode: "host"
    
        # cpu_shares 默认值为 1024， 将此值调小可以降低容器的优先级。 只有在 CPU 周期受到限制时， 这种限制才会生效。
        # 当 CPU 周期充足时， 所有容器会使用所需的全部 CPU 资源。 cpu_shares 不会阻止容器在 Swarm 模式下被调度。
        # 它为可用的 CPU 周期优先分配容器的 CPU 资源， 但并不保证或保留任何特定的 CPU 访问权限。
        cpu_share: 2
        # cpus 用于指定容器可以使用的可用 CPU 资源量。 例如， 如果主机机器有两个 CPU， 并且您设置 --cpus="1.5"，
        # 则容器保证最多使用一个半的 CPU。
        cpu: 2
    
    
    package: abc.example.com # app 的唯一 id,上架到商店需要保证不要冲突,尽量使用开发者自己的域名作为后缀.
    version: 2.0.2           #app 的版本
    
    name: 测试abc   #软件名称,会显示在启动器之类的地方
    description: 简单易用的英语学习软件
    
    license: https://choosealicense.com/licen ses/mit/  #软件本身的 license
    homepage: http://github.com/snyh/abc #软件的主页,会在商店等地方体现
    author: snyh@snyh.org #lpk 的作者,会在商店等地方体现
    
    unsupported_platforms: # 不支持的平 台, 不写则表示全平台支持. lpk 本身是可以被安装的,但下面列表中的平台无法打开此软件
      - linux
      - macos
      - windows
      - android
      - ios
      - tvos
    
    
     #application 作为一个特殊的 container 运行， 对应的 service 名称为固定的` app`， 其他 service 可以通过此名称与 app 进行通讯
    application:
      background_task: false #是否存在后台任务， 若存在则系统不会对此 app 进行主动休眠等操作
    
      subdomain: abc  #期望的 app 域名， 如果系统中已经有对应域名则会提示用户选择其他域名。  最终 app 分配到的域名以/lzcapp/run/app.subdomain 为准
    
      routes:
        - /api/=exec://8000,/lzcapp/pkg/content/bin/backend     #格式与/usr/bin/lzcinit -up 参数一致
        - /api/=http://service.appid.lzcapp:8000            #多实例应用会自动在 route 里加上 uid
        - /=file:///lzcapp/pkg/content/dist/
    
      public_path:
        - /api/public  #默认情况下所有路径都需要登陆后才能访问， public_path 之下的路径允许非登陆情况下访问
    
      ingress:
        - protocol: tcp     #tcp or udp
          port: 22          #需要曝露的端口号
          service: db       #为空则为此 app 容器内的端口,也可以指定为 db 等其他 service 的名称
    
      multi_instance: true # 是否启用多实例
    
      workdir: /lzcapp/pkg/content / #设置 lzcinit 以及后续子进程的 WORKDIR,若不设置或目录不存在则保持使用  container 的 WORKDIR 信息
    
      usb_accel: false # 挂在/dev/bus/usb 到容器
      gpu_accel : false # 是否允许使用硬件 加速
      kvm_accel: true  # enable 后会挂 在/dev/kvm 和/dev/network-host 到所有  service 中
    
      file_handler: # 声明本 app 支持操作的文件类型， mime 至少存在一条记录， actions 至少要支持 open
        mime:  #按照 mime 类型注册到系统
          - x-scheme-handler/http
          - x-scheme-handler/https
          - text/html
          - application/xhtml+xml
          - x-lzc-extension/km      # app 支持.km 文件 名后缀
        actions:   #打开对应文件的 url 路径,由文件管理器等 app 调用
          open: /open?file=%u   #%u 是某个 webdav 上的具体文件路径， 一定存在
          new:  /open?file=%u   #%u 是某个 webdav 上的具体文件路径， 不一定存在
          download: /download?file=%u #%u 是某个 webdav 上的具 体文件路径， 一定存在
    
       environment:
        - MYPASSWORD=123456
    
      image:  alpine:3.16  #可选 的运行环境， 为空则使用 sdk 对应版本的镜像。 若上架到商店， 则此处的镜像必须上传到商店仓库统一托管 。
    
      handlers:
        # 当 ro utes 中 https/ http/exec 类型的反代出现错误时， 则渲染对应模板。
        # 若错误类型为无法返回任何数据， 则会生成一个 502 响应， 比如上游游服务器不存在或网络不通等完全获取不到一个 http response 的情况。
        #
        # 其他情况则根据 http response status code， 选择对应的模板
        # 若命中错误处理页面, 则 http response status code 本身不会进行修改
        #
        # 页 面渲染使用此数据结构
          # struct {
          #    StatusCode int
          #    ErrorDetail string #无法获取 http response 的情况下， 此字段会显示对应错误信息， 并将 StatusCode 设置为 502
          # }
        error_page_templates:
          502: /lzcapp/pkg/content/errors/502.html.tpl
          404: /lzcapp/pkg/content/errors/404.html.tpl
    
    
    
    services: #传统 docker 镜像启动方式， 如果需要数据库等配套容器一起运行则可以在这里申明。 传统 app 如 nextcloud、 aria2c 也可以使用这种方式进行兼容运行
      backend:
        image: alpine:3.18
    
        depends_on:
          - db
    
      db: #目前只支持以下参数， network,ipc 之类的配置字段(故意)不支持
        image: bitnami/wordpress:5.8.2
        environment:
          - ALLOW_EMPTY_PASSWORD=yes
          # oauth 相关的环境变量
          - LAZYCAT_AUTH_OIDC_CLIENT_ID=xxx
          - LAZYCAT_AUTH_OIDC_CLIENT_SECRET=xxx
          - LAZYCAT_AUTH_OIDC_ISSUER_URL=xxx
    
    
        # 仅支持以下挂载点:
        # - /lzcapp/run
        # - /lzcapp/run/mnt/home
        # - /lzcapp/var
        # - /lzcapp/cache
        # - /lzcapp/pkg
        binds:
          - /lzcapp/run/mnt/home:/home  #将/lzcapp/run/mnt/home(即用户文稿)目录挂在到容器内的/home 目录
          - /lzcapp/var/db:/data
          - /lzcapp/cache/db:/cache
          - /lzcapp/pkg/content/entrypoint.sh:/entrypoint.sh # 挂载 lpk 包内的文件
    
        entrypoint: /bin/sh -c
        command: "/usr/bin/nextcloud"
    
        depends_on:
          - ui
    
        # network_mode 仅支持 host 模式， 开启后此 service 可以访问所有网卡， 但失去 lzcdns 特性
        # 非必要尽量不要使用此模式， 需要谨慎处理代码， 存在很高安全风险
        # 如果要在 network=host service 中提供内部服务， 请监听在`host.lzcapp`这个内部 IP 上， 不要直接监听 0.0.0.0
        network_mode: "host"
    
        # cpu_shares 默认值为 1024， 将此值调小可以降低容器的优先级。 只有在 CPU 周期受到限制时， 这种限制才会生效。
        # 当 CPU 周期充足时， 所有容器会使用所需的全部 CPU 资源。 cpu_shares 不会阻止容器在 Swarm 模式下被调度。
        # 它为可用的 CPU 周期优先分配容器的 CPU 资源， 但并不保证或保留任何特定的 CPU 访问权限。
        cpu_share: 2
        # cpus 用于指定容器可以使用的可用 CPU 资源量。 例如， 如果主机机器有两个 CPU， 并且您设置 --cpus="1.5"，
        # 则容器保证最多使用一个半的 CPU。
        cpu: 2

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
22  
23  
24  
25  
26  
27  
28  
29  
30  
31  
32  
33  
34  
35  
36  
37  
38  
39  
40  
41  
42  
43  
44  
45  
46  
47  
48  
49  
50  
51  
52  
53  
54  
55  
56  
57  
58  
59  
60  
61  
62  
63  
64  
65  
66  
67  
68  
69  
70  
71  
72  
73  
74  
75  
76  
77  
78  
79  
80  
81  
82  
83  
84  
85  
86  
87  
88  
89  
90  
91  
92  
93  
94  
95  
96  
97  
98  
99  
100  
101  
102  
103  
104  
105  
106  
107  
108  
109  
110  
111  
112  
113  
114  
115  
116  
117  
118  
119  
120  
121  
122  
123  
124  
125  
126  
127  
128  


## 保存数据的路径 ​

当后端需要存储文件或者数据库时， 请确保文件放在 `/lzcapp/var`​ 目录下， 存在其他目录下的文件会在应用 Docker 重启后被系统清空。
