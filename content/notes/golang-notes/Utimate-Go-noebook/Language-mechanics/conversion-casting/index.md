---
title: 类型转换
date: '2026-01-16T02:50:24+08:00'
weight: 5
menu:
  notes:
    name: 类型转换
    identifier: dconversion-casting
    parent: language-mechanics
    weight: 5
---


{{< note title="转换与类型转换" >}}

`go`语言不支持隐式类型转换，并且显示类型转换不是将原有类型的转换为需要的类型，而是创建一个目标的新变量变量，对其进行赋值，然后将该变量赋值到我们指定的变量中（不是被转换的变量）。

显示转换形式：

```go
// 格式 目标类型(源变量/值)
// string([]byte)
// []byte("string value")


source := "string value"
	fmt.Println("source address: ", &source)
	target := []byte(source)
	fmt.Println("source address: ", &source)
	fmt.Println("target address: ", &target)

	//output :
	//	source address:  0xc000026300
	//	source address:  0xc000026300
	// target address:  &[115 116 114 105 110 103 32 118 97 108 117 101]
```
{{< /note >}}
