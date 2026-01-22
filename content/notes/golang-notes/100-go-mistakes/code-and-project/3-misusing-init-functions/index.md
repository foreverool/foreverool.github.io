---
title: misusing-init-functions
date: '2026-01-22T19:38:48+08:00'
weight: 3
menu:
  notes:
    name: 
    identifier: 3-misusing-init-functions
    parent: code-and-project
    weight: 3
---

{{< note title="misusing-init-functions">}}
# 滥用初始化函数



## Go语言中的init函数

​	在`Go`语言中，`init`函数是一个内置的特殊函数，其主要特征如下：

- 函数签名固定： `func init(){}`无参数、无返回值
- 无法被程序**显式**调用
- 由`Go`语言运行时系统在程序启动阶段自动执行。

### init 执行规则

`init`函数的执行是在**包级全局变量初始化之后，main函数执行之前**

```go
// utils.go
package utils

import "fmt"

var Count int

func init() {
	Count = 1
	fmt.Println("我是init函数，我是否在main函数执行之前")
}

func AddCount() {
	Count++
}

func GetCount() int {
	return Count
}


// main.go
package main

import (
	"100-mistakes/code-and-project/utils"
	"fmt"
)

func main() {
	fmt.Println(utils.GetCount())
	utils.AddCount()
	fmt.Println(utils.GetCount())
}


// output:
// 我是init函数，我是否在main函数执行之前
// 1
// 2
```

从上面的程序运行结果可以看出，`init`是在`main`函数之前就执行了。

**多个`init`函数执行的顺序：**

- 同一个源文件下，`init`的执行顺序为定义顺序

```go
// init.go
package utils

import "fmt"

func init() {
	fmt.Println(1)
}

func init() {
	fmt.Println(2)
}

func init() {
	fmt.Println(3)
}

func init() {
	fmt.Println(4)
}

func init() {
	fmt.Println(5)
}

func init() {
	fmt.Println(6)
}

// 首先不用再main中单独引入该源文件，由于上面的程序中已经引入该包，而init函数的执行过程中是在包导入的时候就执行了
// output：
// 1
// 2
// 3
// 4
// 5
// 6
```

- 同一个包内多个源文件： 按照源文件名称的字字母顺序执行。

​	就按照上述`utils`包中有两个源文件`add.go`和`init.go`，这两个源文件中都定义了一个或者多个`init`函数，按照字母顺序`add.go`中的`init`函数是优先执行，然后再是`init.go`中的`init`函数。

- 不同包之间，按照导入依赖的顺序，被导入的包先执行`init`然后是当前包的`init`。

### `init`函数的常见使用场景

- 初始化全局变量

​	首先我们知道`init`函数的执行是在包全局变量初始化之后，在`main`函数之前，那么我们可以在使用全局变量之前将复杂赋值的逻辑放在`init`函数中，这样在导入包的过程中，全局变量就已经初始化完成了。

- 注册驱动/插件

​	`Go`生态中很多场景依赖`init`函数注册驱动，比如数据库驱动.

- 加载配置/初始化资源

  	比如程序启动时读取配置文件、初始化数据库连接池



## 何时应该正确使用init函数

不合理的例子：

```go
package utils

import (
	"database/sql"

	_ "github.com/go-sql-driver/mysql"
)

var DB *sql.DB

// 在init中链接数据库
func init() {
	dsn := "foreverool:010101@tcp(127.0.0.1:3306)/study_mysql?charset=utf8mb4&parseTime=True&loc=Local"
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		panic(err)
	}
	err = db.Ping()
	if err != nil {
		panic(err)
	}
	DB = db
}
```

为什么上述例子不合理呢？

- 由于`init`函数的返回错误，所以在内部我们只能通过panic来展示错误，这样做程序就中止了，如果我们想采取重试机制链接数据库，这样通过`init`函数没有办法做到。

- 如果我们在对于该文件进行测试，在测试之前，`init`函数就已经执行，这可能不是我们想要的，因为我们有可能测试的对象就是连接数据库逻辑是否正确。

- 最后一个缺点就是将数据库连接池赋值给一个全局变量，而全局变量存在一些严重的缺陷。

  - 包内任何函数都可以修改全局变量
  - 单元测试可能变得更加复杂，因为依赖于全局变量的函数将不再能独立地测试了。

  在大多数情况下下，我们应该优先将变量封装起来，而不是将其设置为全局变量。基于这些原因我们应该之前的初始化操作应该被作为一个普通函数来处理：

  ```go
  func CreateDB(dsn string) (*sql.DB, error) {
  	db, err := sql.Open("mysql", dsn)
  	if err != nil {
  		return nil, err
  	}
  	err = db.Ping()
  	if err != nil {
  		return nil, err
  	}
  	return db, nil
  }
  ```

  这样的函数，错误的处理将由调用者来处理，而不是直接panic，并且该函数可以独立的使用测试函数进行测试。

**Ad Hoc函数**

​	`Ad Hoc`函数是指为解决**特定的、临时的问题**而编写的函数，并不是为了复用性创建的函数。通常只在特定场景下使用。



阅读完本篇文章：

​	个人觉得：

​		如果`init`函数内部可能出现错误处理，那么就不要使用`init`函数实现该部分内容而是单独定义一个可以被调用者显式调用的函数。

​		如果`init`函数实现的功能需要单元测试该部分内容是否正确，那么就不要使用`init`函数，而是单独定义。

​		




{{< /note >}}