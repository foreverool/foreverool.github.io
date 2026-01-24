---
title: interface
date: '2026-01-24T22:25:35+08:00'
weight: 
menu:
  notes:
    name: 
    identifier: interface
    parent: decoupling
    weight: 2
---

{{< note title="">}}
# 接口

**面向接口编程，面向接口编程，面向接口编程**

解耦： 解耦意味着减少组件之间及其所使用数据类型之间的依赖关系。进而提升程序的正确性、质量及可维护性。

接口使我们能够根据**数据的功能**将其归类组合。重点在于数据具备何种功能，而非数据本身是什么。用户可以通过接口来获取具体的数据的方式，让代码免受变化的影响，也就是说无论我们底层的实现如何改变，调用方是不会感知到变化的，只要行为没有变化即可。

接口应描述行为而非状态，应该是动词而非名词。

在以下情况下使用接口：

- API的使用者需要提供实现细节
- API有多种实现方式，相关方需要在内部维护这些实现细节
- 已确定API中可发生变化的部分，这些部分需要进行解耦处理。

在一下情况下不要使用接口：

- 为了使用接口而使用接口。
- 对算法进行泛化处理。
- 当用户能够定义自己的接口时。
- 如果不清楚该接口时如何让代码更优化的。
- 接口毫无价值。



接口是无值类型，他只规定了一组方法，具体数据必须实现这些方法才能满足接口的要求。接口本身没有任何具体内容。

```go
type Reader interface{
    Read(b []byte)(int,error)
}

func main(){
    var r Reader
}
```

像上述的`r`变量在没有对它进行赋值实现该接口的类型实例之前，该变量没有任何意义，其为nil。

我们从不处理接口值，只处理具体值。接口具有编译器层面的表现形式（内部类型），但从我们的编程模型来看，接口本身是无价值的。

**多态性**

多态性是指代码的行为会根据其处理的具体数据而发生变化。

```go
type Mover interface {
	Move()
}

type Jumper interface {
	Jump()
}

type NormalPerson struct{}

func (n NormalPerson) Move() {
	fmt.Println("我正以每小时5公里的速度前进")
}

func (n NormalPerson) Jump() {
	fmt.Println("我每次跳跃30cm")
}

type AthlecticPerson struct{}

func (a AthlecticPerson) Move() {
	fmt.Println("我正以每小时10公里的速度前进")
}

func (a AthlecticPerson) Jump() {
	fmt.Println("我每次跳跃60cm")
}


// 定义一个多态函数
func OperatePersonMove(mover Mover) {
	mover.Move()
}

```

比如上述代码，我想操作不同的人物进行移动或者跳跃，由于不同类型的人物的行为都为走或者跳跃，但是其具体行为细节是不一样，但是我操作人物具体逻辑是一样的，所以`OperatePersonMove`函数参数为一个`Mover`接口类型，这里我需要传递的类型不是接口类型，而是实现该接口的具体类型实例。这样在调用Move函数的时候根据不同的具体类型会产生不同的移动效果。
{{< /note >}}