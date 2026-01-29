---
title: 'Install Docker'
date: '2026-01-29T19:38:31+08:00'
draft: true
hero: 
description: ""
theme: Toha
menu:
  sidebar:
    name: 安装docker
    identifier: install-docker
    parent: docker
    weight: 2
---

# 安装docker



## 在Windows上安装docker

​	在之前的文章中我们了解到，windows内核并不像Linux在内核中支持容器相关功能，所以在Windows上安装`docker`需要安装`Docker Desktop`软件，该软件会先运行一个`Linux`虚拟机，然后再其上面安装docker。

为什么再"*Docker Deep Dive Zero to Do* "书中极力建议安装`Docker Desktop`而不是在学习过程中就将`docker`安装在`Linux`中的主要原因就是：

- 我们的主机OS可能时windows或者macOS，为了安装docker我们可能需要使用虚拟机安装Linux或者使用wsl。

- Docker Desktop 软件有一个良好的可视化操作流程，并不是简单的命令行工具。

### 获取Docker Desktop

官方网址: https://www.docker.com/products/docker-desktop/

需要注意的是在**安装了docker desktop之前需要启用wsl**。

点击Download Docker Desktop 选择适合你主机OS的版本并下载。

下载完成之后进行安装

![image-20260129182126566](/images/posts/docker/image-20260129182126566.png)



如果安装成功之后，就可以在`CMD`和`WSL`中使用docker了，这里需要注意的是命令行中的docker命令只是使用了docker的客户端，而真正的引擎是在WSL中。

由于WSL与Windows并非完全隔离，其有专属的通信方式，所以Windows与WSL共用了`docker`守护进程。

真正的docker守护进程是安装在docker desktop WSL中并不是你之前就已经安装了的wsl某个操作系统。

你可以使用`wsl --list`命令查看你主机当前的所有wsl。

![image-20260129182729608](/images/posts/docker/image-20260129182729608.png)









