---
title: 声明和初始化
date: '2026-01-16T02:50:24+08:00'
weight: 4
menu:
  notes:
    name: 声明和初始化
    identifier: declare-initialize
    parent: language-mechanics
    weight: 4
---

{{< note title="声明与初始化" >}}
## 1 var

关键字`var`可以用于所有类型的变量设置为初始状态，零值。

```go
type User struct{
    Name string
    Age  uint8
}
var i8 int8
var u8 uint8
var condition bool
var user User

```

在`go`语言中字符串底层结构由两个字组成：

```go 
type stringStruct struct {
	str unsafe.Pointer
	len int
}
```

如果string被设置为nil， 那么字段`str`则是`nil`，len为0。

## 2 短变量声明操作符

短变量声明操作符`:=`

该操作符包含了声明变量，初始化变量，赋值变量三个步骤。

如果一个变量已经声明了或者定义了，就无法再次使用短变量声明操作符。

{{< /note>}}
