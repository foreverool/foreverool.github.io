---
title: 零值的概念
date: '2026-01-16T02:50:24+08:00'
weight: 3
menu:
  notes:
    name: 零值的概念
    identifier: zero-value
    parent: language-mechanics
    weight: 3
---
{{< note title="零值的概念">}}

​	我们创建的每个变量在其初始化时，其值至少被设置位零，也就是当我们声明变量时，go在编译过程中，会自动位该变量进行初始化，也就是为相应的变量的存储空间内存储相应的零值。如果我们在声明变量的时候就指定初始值，那么该变量在使用的时候，其值就是我们预先指定的值。 所谓“零值”就是指每个字节的每一位都被设置为零。

​	零值确保了数据的完整性，也就是说在我们使用一个声明的变量过程中，该变量符合我们的预期而不是在使用的时候出现一些未知的值存在我们的变量中。

​	`go`语言的内置类型的零值如下：

- `boolean`: false
- `Integer`: 0
- `Float` : 0.0
- `Complex`: `0i`
- `String`: ""(empty)
- `Pointer`: nil
- `rune`: 0
- `byte`: 0

复合类型由一个或多个基本类型组成，其零值遵循【成员各自取对应的类型零值】规则。

- 数组： 数组的每个元素都取该元素类型的零值，与数组长度无关。

- 结构体： 结构体的零值是【结构体每个字段都取该字段类型的零值】，嵌套结构体也遵循此规则，逐层递归赋零值。

- 引用类型：

  引用类型的零值都是`nil`

  - 切片 `[]int`, `nil`切片的len()、cap()均为0，可直接使用`append()`无需手动初始化。

  ```go
  	// 查看空结构体的值
  	var nilSlice []int
  	if nilSlice == nil {
  		fmt.Println("nil slice")
  	} else {
  		fmt.Printf("%+v\n", nilSlice)
  	}
  	// output : nil slice
  
  	//查看nil slice len() cap()
  	fmt.Printf("len=%d, cap=%d\n", len(nilSlice), cap(nilSlice))
  	// output:len=0, cap=0
  
  	// 对nil slice进行append
  	nilSlice = append(nilSlice, 1)
  	fmt.Printf("len=%d, cap=%d\n", len(nilSlice), cap(nilSlice))
  	fmt.Println(nilSlice)
  	// output:
  	//  		len=1, cap=1
  	//			[1]
  
  	var nilSlice1 []int
  	// 使用函数添加元素，但是传入的参数是nil
  	AppendElement(nilSlice1, 1)
  	if nilSlice1 == nil {
  		fmt.Println("nil slice")
  	} else {
  		fmt.Printf("len=%d, cap=%d\n", len(nilSlice), cap(nilSlice))
  		fmt.Println(nilSlice1)
  	}
  	// output: nil slice
  	// 由于形参是值传递，而通过函数传递给的nilSlice1最终添加了元素并没有返回给main。
  
  
  ```

  - 字典map[k]v , `nil`map无法直接添加键值对，必须通过make进行初始化，或者字面量初始化`map[int]int{}`。

    ```go
    	var nilmap map[int]int
    
    	fmt.Println(len(nilmap)) // output : 0
    	//直接添加键值对
    	nilmap[1] = 12
    	if nilmap == nil {
    		fmt.Println("nil map")
    	} else {
    		fmt.Println("len=", len(nilmap))
    		fmt.Println(nilmap)
    	}
    	// output:
    	// 			panic: assignment to entry in nil map [recovered]
    	// 		panic: assignment to entry in nil map
    
    //所以为了程序的健壮性，所以在使用map的时候尽量先对map进行nil判断，然后在进行业务处理
    ```

  - 通道 `chan T` `nil`通道无法进行发送/接受，必须通过make进行使用。

  - 函数 `nil`的直接调用会引发panic。

  - 指针 `nil`指针无法解引用，如果解引用会引发panic。

  - 接口 `nil`接口的零值要求动态类型和动态值都为`nil`，`nil`接口无法调用任何方法。

  {{< /note>}}