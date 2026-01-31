---
title: '部署到Github'
date: '2026-01-12T06:23:32+08:00'
hero: 
description: ""
theme: Toha
draft: false
tags:
  - hugo
  - blog
  - github pages
menu:
  sidebar:
    name: 部署到Github
    identifier: deploy-to-github
    parent: deploy-hugo-blog
    weight: 3
---

# 将hugo创建的博客使用GitHub Pages发布网站




![image-20260112045208111](images/posts/deploy-hugo-blog/deploy-to-github/image-20260112045208111.png)

<font color="  #BA55D3"><b>指定Repository name为 <your_github_username>.github.io</b></font> 这是必须，不然GitHub Pages没有办法运行你的博客页面。

接下来在创建gh-pages分支：

​	首先告诉你为什么要创建gh-pages分支

- 由于我们需要将hugo创建的博客根目录发布到main分支上，但是该目录Github Pages是没办法直接将该部分内容发布到<your_github_username>.github.io网站上去的。只有该目录下的public才能让Github Pages识别到你的网站上。
- 当然也可以直接将public目录上传到main分支上，不创建gh-pages分支，但是这么做有一个缺点就是，你网站的根目录配置文件，主题文件等内容都没有托管到Github上，你只能依赖你本地的项目去发布文章，修改网页，如果你换了
- 最重要的是配置文件主题等内容与发布内容分离，main分支主要是hugo以及文章主题的内容，而gh-pages分支就是保存hugo根据你的配置数据等内容产生的静态文件。

所以这也是为什么要再创建一个gh-pages分支，让gh-pages分支存储public所有内容，这个内容是由Github Pages自动完成，每当我们提交新的内容到main分支之后，Github Pages会安装hugo，下载相关资源后然后使用hugo生成public目录到gh-pages分支，然后Github Pages会自动部署gh-pages分支的内容到<username>.github.io网页上。

创建gh-pages分支

```she
# 创建gh-pages分支
 git checkout -b gh-pages
 
 #这块最好是在项目搭建最开始，这样我们的gh-pages分支是干净的什么都没有，如果根目录已经有文件了 也没事直接add即可
 git add .
 git commit -m "添加分支"
 
#将当前根目录push到Github上面
git push -u origin gh-pages
```

创建自动化部署文件

<font color="  #BA55D3"><b>在根目录创建.github目录，在.github目录创建workflows目录，在workflows目录下创建deploy.yml文件</b></font>

![image-20260112061547254](images/posts/deploy-hugo-blog/deploy-to-github/image-20260112061547254.png)



然后将下方内容复制到你的deploy.ymml文件中

```yml
name: Deploy to Github Pages

# run when a commit is pushed to "source" branch
on:
  push:
    branches:
    - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    # checkout to the commit that has been pushed
    - uses: actions/checkout@v4

    - name: Setup Hugo
      uses: peaceiris/actions-hugo@v3
      with:
        hugo-version: 'latest'
        extended: true

    - name: Update Hugo Modules
      run: hugo mod tidy

    - name: Setup Node
      uses: actions/setup-node@v4
      with:
        node-version: 20

    - name: Install node modules
      run: |
        hugo mod npm pack
        npm install

    - name: Build
      run: hugo --minify

    # push the generated content into the `gh-pages` branch.
    - name: Deploy
      uses: peaceiris/actions-gh-pages@v4
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_branch: gh-pages
        publish_dir: ./public
```

然后将该目录上传到你的main分支下。

```shell
git add .
git commit -m "添加自动化部署文件"
git push -u origin main

```

然后配置Github Action权限

<img src="images/posts/deploy-hugo-blog/deploy-to-github/image-20260112061756301.png" alt="image-20260112061756301" style="zoom:67%;" />





![image-20260112061854342](images/posts/deploy-hugo-blog/deploy-to-github/image-20260112061854342.png)





![image-20260112061923939](images/posts/deploy-hugo-blog/deploy-to-github/image-20260112061923939.png)





![image-20260112061938715](images/posts/deploy-hugo-blog/deploy-to-github/image-20260112061938715.png)



之后直接修改任意文件，然后上传到你的main分支下，然后打开action，查看是否正在部署。

![image-20260112062036140](images/posts/deploy-hugo-blog/deploy-to-github/image-20260112062036140.png)



如果出现部署失败，不要慌，直接点击进去，看哪里出现问题了，然后直接复制到ai下面，问一下。现在ai能解决你大部分问题。

到这里就部署完成了，然后就是根据不同主题，修改相应的配置优化网站了~~~~~