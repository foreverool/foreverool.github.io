---
title: 
date: '2026-01-22T20:02:23+08:00'
weight: 4
menu:
  notes:
    name: overusing-getters-and-setters
    identifier: 4-overusing-getters-and-setters
    parent: code-and-project
    weight: 4
---

{{< note title="overusing-getters-and-setters">}}
# Overusing getters and setters

说起getters 和setters我个人感觉在`java`中十分常见，由于`java`是纯面向对象语言，所以经常会将某些字段定义为`private`然后使用getter 和setter进行操作该`priavte`字段。但是在`Go`语言中我在很多源码中并没有看到`getter`和`setter`，而是直接操作`struct`中的字段。除非该字段被设置为当前包可见。

首先说明：

​	`Go`不强制使用`getter`和`setter`，在标准库中也不强制使用。但是`getter`和`setter`具有一些优点：

- 封装了字段的设置与获取行为，允许在获取或者设置过程中添加新的行为（验证字段，返回计算值等）
- 隐藏了内部表示

在`Go`语言如何使用`getter`和`setter`呢？

​	如果我们要为`balance`字段设置`getter`和`setter`,那么我们的`getter`方法应该是`Balance()`而不是`GetBalance()`。

​	而`setter`应该命名为`SetBalance`。

如果我们的`getter`和`setter`就只是简单的取值，赋值，那么没有必要为该字段设置`getter`和`setter`。

只有当我们的`getter`和`setter`方法有有意义时才使用，遵循`go`语言的设计哲学---简单。


{{< /note >}}