---
title: '下载安装hugo'
date: '2026-01-11T19:02:01+08:00'
hero: images/posts/deploy-hugo-blog/images.png
description: ""
theme: Toha
menu:
  sidebar:
    name: 
    identifier: install-hugo
    parent: deploy-hugo-blog
    weight: 1
---

# hugo个人博客搭建

在使用hugo搭建个人博客之前，我们需要明确知道hugo是一种生成静态文件的博客软件。它没有与数据库这种存储用户数据的软件进行搭配，而是将我们的文章转换成静态网页的形式发布的。

**该篇文章所有的安装过程都是在windows上**

## 1. 下载与安装hugo

### 1.1 下载

如果你使用了其它系统，可以参考`hugo`官网[https://gohugo.io/installation](https://gohugo.io/installation)

在windows下安装hugo个人建议直接在https://github.com/gohugoio/hugo/releases/tag/v0.154.4下载安装包，这里要注意官方提供了很多不同的压缩包，**建议安装扩展版也就是安装包中包含extended**，这里主要是方便你后续选择不同的hugo主题的时候可以正常使用这些主题。extended就是hugo的扩展，包含了更多的内容。

### 1.2 安装

这个安装步骤其实准确来说是将下载好的压缩包解压，解压完成后，你会得到`hugo.exe`软件，然后将该软件所在的目录添加到用户的环境变量中，这样就可以直接在命令行中使用`hugo`。

对于不知道如何设置环境变量的同学，请看接下来的操作，如果知道的同学直接看第二部分。

**设置环境变量**

windows 11

打开设置，找到系统


![image.png](images/posts/deploy-hugo-blog/install/image.png)

然后**点击系统**，拉到最下面，**找到系统信息**，并且点击

然后找到**高级系统设置**

![image.png](images/posts/deploy-hugo-blog/install/image%201.png)

之后点击环境变量

![image.png](images/posts/deploy-hugo-blog/install/image%202.png)

在用户那里找到path

![image.png](images/posts/deploy-hugo-blog/install/image%203.png)

双击path，然后将hugo所在的目录复制到path那里就可以了

之后打开cmd看是否可以执行hugo，如果不能执行直接重启，然后就可以了。

这也是有时候我们设置完环境变量不能立马直接某些程序的解决方法之一。

## 2. 创建网站（博客）

如果在命令行可以正常使用`hugo` ，那么执行下面的命令:

```bash
hugo new site your-website-name
```

这个命令主要是创建你的网站的骨架，此时还没有任何网站主题和相关内容。

在创建完网站骨架之后，你可以在命令行切换到your-website-name目录下，然后执行：

```bash
# 切换到刚才使用hugo创建的项目根目录下
Z:\blog>cd demo-website

#然后执行
hugo server -D
```

如果出现下面这样的内容，就证明你的网站骨架创建成功了，接下来就是选择主题了

![image.png](images/posts/deploy-hugo-blog/install/image%204.png)

之后想要查看你的网站内容的话，按住ctrl 并且点击上面的localhost地址就可以直接访问

![image.png](images/posts/deploy-hugo-blog/install/image%205.png)

此时下载与安装基本已经完成了，接下来就是配置主题了。请看下一篇文章~

