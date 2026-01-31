---
title: 'Docker Base Operate'
date: '2026-01-30T02:26:55+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
  - docker

menu:
  sidebar:
    name: 操作docker
    identifier: docker-base-operate
    parent: dockers
    weight: 10
---
# Docker 的基本操作



## 1. Ops视角下的Docker



### 1.1 下载Image(镜像)

镜像是包含应用程序运行所需要的一切内容的对象，其中包括操作系统文件系统、应用程序和所有依赖项。类似于代码中的类。

- 运行docker images命令

  ```shell
  docker images #如果你的docker从没有下载任何镜像，那么该指令不会输出任何镜像
  ```

- 将新的镜像复制到你的docker中，该操作成为**拉取**。

  ```shell
  $ docker pull nginx:latest
  
  $ docker images #执行该命令就会看到如下的内容
  IMAGE          ID             DISK USAGE   CONTENT SIZE   EXTRA
  nginx:latest   c881927c4077        240MB         65.7MB
  ```

  当你拉取了一个镜像，该镜像本身就包含运行该软件的运行环境（轻量级Linux OS）和运行该程序的所有依赖。

### 1.2 启动一个容器

当你拉去了一个镜像之后，就可以从该镜像中启动一个容器

```shell
docker run --name test -d -p 8080:80 nginx:latest
7fb7356ca1765a88df366d3e539fe532dc995dc114602de3b49b384b229940eb
```

如果出现了长数字，那么意味着名为test的容器已经被创建好了。

- `docker run`告诉docker启动一个新的容器。
- `--name`告诉docker将该容器命名为`test`
- `-d`告诉docker在后台启动容器。因此该容器不会接管你的终端。
- `-p`告诉docker将容器端口`80`映射到docker主机上的端口`8080`。
- 最后该命令告诉docker基于`nginx:latest`镜像启动容器。

### 1.3 查看正在运行的容器

```shell
docker ps #该命令可以查看正在运行的容器
```

执行完上述指令，可以得到类似下面的内容

```shell
CONTAINER ID   IMAGE          COMMAND                   CREATED         STATUS         PORTS                                     NAMES
7fb7356ca176   nginx:latest   "/docker-entrypoint.…"   6 minutes ago   Up 6 minutes   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   test
```

其中`CONTANINER ID`是容器的唯一标识，`IMAGE`是容器运行了什么镜像，`COMMAND`则是启动该容器执行了什么指令，`PORTS`则是我们在`docker run`的时候指定端口绑定。 `NAMES`则是该容器的名称。



### 1.4 在容器内执行命令

运行下面的命令将你的shell附加到容器内的新bash进程中：

```shell
docker exec -it test bash
```

之后你可以直接像操作Linux一样操作该容器的内容。

输入exit将终止bash进程。



### 1.5 停止和删除容器

使用`docker stop test`命令停止该容器的使用。

![image-20260129224026688](/images/posts/docker/image-20260129224026688.png)



通过`docker ps -a`查看所有容器，包括已经删除或停止的容器。

![image-20260129224318976](/images/posts/docker/image-20260129224318976.png)



### 1.5 启动一个已经停止运行的容器

`docker run`指令是新创建一个容器，如果一个容器已经创建了就不能使用该指令。

`docker start`是运行一个已经创建的容器。

![image-20260129224711006](/images/posts/docker/image-20260129224711006.png)

## 2. 开发者视角下的Docker

站在开发者的角度，我们更关心如何将我们的程序代码制作成镜像，并且可以在docker中使用。

在构建镜像之前，需要为我们的项目创建docker file文件，这部分内容我们会在后续的文章中讲解，在这里我们只是简单的说明如何创建docker file，后续介绍具体的手动编写dockerfile。

使用`docker init`生成dockerfile。

- 首先在项目的根目录中运行`docker init`
- 运行之后根据提示，一步一的完成即可，之后就可以在我们的项目根目录下发现4个文件【.dockerignore、compose.yml、Dockerfile、README.Docker.md】

当你完成之后就可以执行

```shell
docker build -t myappp .
```

根据项目大小以及依赖和网络等情况，构建时间可长可短。

![](/images/posts/docker/image-20260130012928137.png)

在创建镜像之后，我们可以使用`docker images `查看镜像是否存在。

![image-20260130022337969](/images/posts/docker/image-20260130022337969.png)

之后我们就可以直接创建这个镜像的容器了

`docker run --name <your_app_name> -d -p [宿主机端口]:[docker运行的web服务端绑定端口] myapp:latest `

之后在本地浏览器中输入：`localhost:[你绑定的端口号]`就可以查看你的服务器程序是否运行。

