---
title: '解决在Typora使用zenuml异常'
date: '2026-02-12T11:43:47+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- Typora
- Zenuml
- Mermaid


menu:
  sidebar:
    name: 解决zenuml在typora中的异常
    identifier: hadnle-zenuml-exception
    parent: typora
    weight: 10
---


# 解决在Typora使用zenuml异常

本人之前使用`typora 1.4`版本是不支持`zenuml`,在`typora1.7`版本之后都是支持`zenuml`,所以今天安装了最新版本的`typora`。但是在安装完成之后发现`zenuml`虽然不会提示错误，但是显示的内容排版有问题。

所以这篇文章主要记录如何解决这个问题。

## 可能的导致排版异常的原因

- `typora`在官网上说如果出现异常，很可能是因为主题的原因。
  解决方案： 更换主题，看是否是主题的原因。
- `zenuml`版本不是最新的，与当前`mermaid`版本不匹配。–本人的问题就是这个

​	解决方案如下

## 解决`zenuml`版本不是最新的

- 打开`Typora`安装目录，然后打开`Typora/resources/`目录，找到`lib.asar`文件

- 备份`lib.asar`

  ```shell
  copy lib.asar ./lib.asar.backup
  
  ```

- 下载`asar`工具

  ```shell
  npm install -g asar
  ```

- 解压`asar`文件

  ```shell
  asar extract lib.asar  ./lib-unpack
  ```

- 下载最新版的`mermaid-zenuml.min.js`

  ```shell
  curl -L -O https://cdn.jsdelivr.net/npm/@mermaid-js/mermaid-zenuml@0.2.2/dist/mermaid-zenuml.min.js
  ```

- 然后将新下载的`mermaid-zenuml.min.js`替换`lib-unpack/diagram`目录下的`mermaid-zenuml.min.js`文件。
  ![image-20260212113311591](images/posts/software-use-tips/image-20260212113311591.png)

- 之后打包`lib-unpack`

  ```shell
  asar pack .\lib-unpack\ ./lib.asar
  ```

- 最后重启`typora`
  就会发现可以正常使用`zenuml`

{{< mermaid align="center">}}
  zenuml
      title Declare participant (optional)
      Bob
      Alice
      Alice->Bob: Hi Bob
      Bob->Alice: Hi Alice
  
{{< /mermaid>}}

  ![image-20260212113805043](images/posts/software-use-tips/image-20260212113805043.png)

