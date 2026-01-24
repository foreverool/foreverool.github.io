---
title: 内置类型
date: '2026-01-16T02:50:24+08:00'
weight: 1
menu:
  notes:
    name: 内置类型
    identifier: builtin-types
    parent: language-mechanics
    weight: 1
---


{{< note title="Go语言内置类型">}}

对于类型来说，需要清楚两个问题：

- 需要分配多少内存？
- 这些内存用于存储什么类型？

## 1. 整数

对于整型类型来说：

`int` 和 `uint`:

- `int8`： 
  - 内存： 1个字节(8 bit)
  - 存储类型： 有符号整数
  - 范围： -128  -  127

- `int16`
  - 内存： 2个字节(16- bit)
  - 存储类型： 有符号整数
  - 范围： -32768  -  32767

- `int32`
  - 内存： 4个字节(32- bit)
  - 存储类型： 有符号整数
  - 范围： -2147483648  - 2147483647
- `int64`
  - 内存： 8字节个字节(64 bit)
  - 存储类型： 有符号整数
  - 范围： -9223372036854775808 -  9223372036854775807
- `uint8`
  - 内存： 1个字节(8 bit)
  - 存储类型： 无符号整数
  - 范围：0 - 255

- `uint16`
  - 内存： 2个字节(16 bit)
  - 存储类型： 无符号整数
  - 范围： 0-65535
- `uint32`
  - 内存： 4个字节(32 bit)
  - 存储类型：  无符号整数
  - 范围： 0-4294967295
- `uint64`
  - 内存： 8个字节(64 bit)
  - 存储类型： 无符号整数
  - 范围：0-18446744073709551615

​	如果我们使用非精确类型---`int`或者`uint`来声明变量时，该变量的存储大小实际上取决于用于构建程序的硬件架构。

​	32位架构： `int`用4字节存储有符号整数，`uint`用4字节存储无符号整数

​	64位架构： `int`用8字节存储有符号整数，`uint`用8字节存储无符号整数。

## 2. float

​	`Go`语言遵循`IEEE 754`二进制浮点算数标准，仅支持两种类型浮点数:

- `float32`
  - IEEE 754标准：单精度浮点数
  - 字节数：4字节
  - 指数位长度： 8bit
  - 位数为长度: 23位
  - 有效十进制精度(约): 6-7位 

​		

- `float64`
  - IEEE 754标准：双精度浮点数
  - 字节数：8字节
  - 指数位长度： 11bit
  - 尾位数为长度: 52位
  - 有效十进制精度(约): 15-16位 

未精确指定`float`的时候默认是`float64`。

浮点数存在固有**舍入误差**，无法精确表示部分十进制小数，比较时需使用容差判断，避免直接使用 `==`。

## 3. bool

```go
// true and false are the two untyped boolean values.

const (

  true  = 0 == 0 // Untyped bool.

  false = 0 != 0 // Untyped bool.

)
```

bool类型只有两个值，`true`或者`false`， 在`Go`语言中不能将整型变量直接转换成`bool`类型，也不能将bool类型转换成整型。

## 4. string

```go
// string is the set of all strings of 8-bit bytes, conventionally but not
// necessarily representing UTF-8-encoded text. A string may be empty, but
// not nil. Values of string type are immutable.
type string string
```

字符串类型在`go1.20`版本中没有在`builtin.go`中具体实现，但是在`builtin.go`文件中类型定义了`string`,在`builtin.go`文件中递归类型定义了`string`，递归类型定义只能适用于内置基本类型，普通自定义类型无法复刻。

```go
type int int
//如果类型定义类型本身，则会有错误提示
//invalid recursive type: int refers to itself
```

在`builtin.go`文件中我们可以知道 **字符串是所有8位字节的字符串的集合，通常但不一定表示UTF-8编码的文本。字符串可以是空的，但不是nil。字符串类型的值是不可变的。**

{{< /note >}}