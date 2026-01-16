---
title: unintended-variable-shadowing
date: '2026-01-17T02:24:28+08:00'
weight: 1
menu:
  notes:
    name: 
    identifier: 1-unintended-variable-shadowing
    parent: code-and-project
    weight: 1
---
{{< note title="Unintended Variable Shadowing" >}}

`Uintended Variable Shadowing`中文翻译过来是：非预期变量遮蔽

在讲解什么是非预期变量遮蔽前需要知道什么是<font color="  #FF6347"><b>变量遮蔽</b></font>。

变量遮蔽： 当内层作用域中定义了一个与外层变量同名的变量，此时在内层作用域中遮蔽了外层变量，此时该外层变量会被暂时的遮蔽了。

非预期变量遮蔽： 由于编写代码的过程中疏忽了导致了外层变量被遮蔽，从而导致程序产生了bug。简而言之就是开发者想要操作外层变量，但是是实际上操作的是内层作用域的变量。

下面展示一个由于不变量的非预期遮蔽从而产生的副作用：

```go
func TestUnintendedVariableShadowing(t *testing.T) {
	var client *http.Client
	tracing := false
	if tracing {
		client, err := createClientWithTracing() //重现定义了client变量，该变量只存在if作用域，与外层作用域的client是两个独立的变量
		if err != nil {
			fmt.Println(err)
		}
		log.Println(client)
	} else {
		client, err := createDefaultClient()
		if err != nil {
			fmt.Println(err)
		}
		log.Println(client)
	}

	useClient(client)
}

func createClientWithTracing() (*http.Client, error) {
	return &http.Client{}, nil
}

func createDefaultClient() (*http.Client, error) {
	return &http.Client{}, nil
}

func useClient(client *http.Client) {
    if client == nil{
        fmt.Println("nil client")
    }else{
        fmt.Println("正确传入client")
    }
}
```

首先根据上述代码，我们可以发现，在`if`语句块中`client`使用了短变量声明运算符，此时的client是全新的变量，我们本来想着是生成tracing client 或者默认client 然后使用该client，但是最后我们发现，`useClient`传入的参数是nil。

如何修改上述代码，让其外层变量不被遮蔽：

- 在`if`语句块中创建临时变量，然后再语句块尾部将该临时变量赋值给外层的client。

```go
func TestUnintendedVariableShadowing(t *testing.T) {
	var client *http.Client
	tracing := false
	if tracing {
		c, err := createClientWithTracing() //重现定义了client变量，该变量只存在if作用域，与外层作用域的client是两个独立的变量
		if err != nil {
			fmt.Println(err)
		}
		log.Println(c)
		client = c
	} else {
		c, err := createDefaultClient()
		if err != nil {
			fmt.Println(err)
		}
		log.Println(c)
		client = c
	}

	useClient(client)
}

func createClientWithTracing() (*http.Client, error) {
	return &http.Client{}, nil
}

func createDefaultClient() (*http.Client, error) {
	return &http.Client{}, nil
}

func useClient(client *http.Client) {
	if client == nil {
		fmt.Println("nil client")
	} else {
		fmt.Println(client)
	}
}
```

还有一种解决方案就是类似于上述情况，内部作用域变量是通过函数创建的，那么可以先声明一个error类型的变量，然后使用`=`操作符而不是`:=`短变量声明操作符。

```go
func TestUnintendedVariableShadowing(t *testing.T) {
	var client *http.Client
	tracing := false
	var err error
	if tracing {
		client, err = createClientWithTracing() //重现定义了client变量，该变量只存在if作用域，与外层作用域的client是两个独立的变量
		if err != nil {
			fmt.Println(err)
		}
		log.Println(client)
	} else {
		client, err = createDefaultClient()
		if err != nil {
			fmt.Println(err)
		}
		log.Println(client)

	}

	useClient(client)
}

```

如果使用了第二种方案，可以将没有必要在每一个条件分支进行处理error，因为条件分支判断`err`逻辑是一样的，这样可以在两个条件分支外层判断该err。

```go
func TestUnintendedVariableShadowing(t *testing.T) {
	var client *http.Client
	tracing := false
	var err error
	if tracing {
		client, err = createClientWithTracing() //重现定义了client变量，该变量只存在if作用域，与外层作用域的client是两个独立的变量

		log.Println(client)
	} else {
		client, err = createDefaultClient()

		log.Println(client)

	}
	if err != nil {
		fmt.Println(err)
	}

	useClient(client)
}
```

**如何避免非预期变量遮蔽**

- 遵循清晰的命名规范，避免同名冲突，

​	拒绝使用`count`,`data`,`num`等通用的变量名，给变量起【具有描述性】的名字，比如：`globalIrderCount`,`localNewOrderCount`,从根源减少不同作用域的同名概率。

- 利用开发工具和静态检查工具，在开发阶段即使发现遮蔽问题。
- 避免不必要的变量声明。 

{{< /note >}}