---
title: 'giscus作为hugo博客的评论系统'
date: '2026-01-12T18:50:24+08:00'
hero: 
description: ""
theme: Toha
draft: false
tags:
  - hugo
  - blog
  - giscus

menu:
  sidebar:
    name: 使用giscus作为hugo博客的评论系统
    identifier: comment
    parent: deploy-hugo-blog
    weight: 4
---


# 配置评论功能

hugo是生成静态资源的软件，所以没有后台程序去存储用户评论的数据，所以可以采用云端存储用户数据，但为了简单也可以直接使用giscus。

giscus利用Github Discussions实现评论系统的，让方可借助Github在你的网站留下评论的。也就是说你的每一个文章下面的评论都在Github上对应的文件下都有相应的平。而giscusj就是使用Github Discussions搜索API根据选定的映射方式比如url、pathname、title等方式来查找当前页面关联的discussion。

# 1. 在GitHub上安装giscus app

❗❗❗在安装giscus app之前需要确定你的仓库是公开的，否则访客是无法查看discussion的。

打开https://github.com/apps/giscus ，然后选择Install

![image-20260112164537083](images/posts/deploy-hugo-blog/deploy-comment/image-20260112164537083.png)

当然你也可以根据自己需求选择上述的选项，一般是选择 特定repository。

<font color="  #FF69B4C"><b>记得勾选严格匹配，不然会出现模糊查询过程中只要前缀相似的，都归为一篇文章了。血的教训。。。</b></font>

安装完成之后你就可以在Github Settings中Applications中查看到giscus。或者你的repository中Integrations部分可以查看Github Apps是否存在gscus。





# 2.配置giscus



## 2.1 开启discussions功能

打开你的repository settings 然后在General中下滑，找到Features

![image-20260112165238014](images/posts/deploy-hugo-blog/deploy-comment/image-20260112165238014.png)

在Fetures中找到Discussions然后勾选。

![image-20260112165313273](images/posts/deploy-hugo-blog/deploy-comment/image-20260112165313273.png)



## 2.2在giscus官网配置giscus

打开https://giscus.app/zh-CN ，然后在该网站的配置部分中配置discus。

![image-20260112170111663](images/posts/deploy-hugo-blog/deploy-comment/image-20260112170111663.png)

当你根据上面的配置信息配置完成之后，就可以将



类似于下面的代码

![image-20260112170142386](images/posts/deploy-hugo-blog/deploy-comment/image-20260112170142386.png)

放置到你的博客中你想存放的位置，当然一些主题是支持giscus的，所以直接在hugo.yml配置文件中配置即可。

我是使用的toha主题，所以接下来将我的配置信息做个参考：

![image-20260112170252848](images/posts/deploy-hugo-blog/deploy-comment/image-20260112170252848.png)

此时有关评论的评论功能就已经全部完成了，接下来运行hugo server -D 来查看是否配置成功。如果出现类似于下面的结果，那就证明配置成功了，如果没有出现，检查一下配置文件是否正确，并且在GitHub上开启了discussions，并且你的repository是否是公开的。

![image-20260112170518424](images/posts/deploy-hugo-blog/deploy-comment/image-20260112170518424.png)

# 3. 结尾

​	当我们在你的博客文章下面评论了之后，你不仅仅可以在博客页面查看到该评论，还会在你的GitHub上可以查看，而且如果有人评论了你的文章，你会收到GitHub的邮件通知，当然你不想GitHub通知你你也可以选择关闭。

![image-20260112171054697](images/posts/deploy-hugo-blog/deploy-comment/image-20260112171054697.png)

在Github上查看

![image-20260112171146907](images/posts/deploy-hugo-blog/deploy-comment/image-20260112171146907.png)

![image-20260112171204994](images/posts/deploy-hugo-blog/deploy-comment/image-20260112171204994.png)

如果你想关闭邮件通知，可以在你的repostory主页，点击watch然后选择custom，选择你想要接受到的通知。

![image-20260112171553037](images/posts/deploy-hugo-blog/deploy-comment/image-20260112171553037.png)

![image-20260112171602305](images/posts/deploy-hugo-blog/deploy-comment/image-20260112171602305.png)