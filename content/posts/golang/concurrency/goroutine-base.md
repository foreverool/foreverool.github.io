---
title: 'Goroutine Base'
date: '2026-02-27T21:20:43+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- Go
- goroutine
- 协程
- 线程
menu:
  sidebar:
    name: goroutine基础
    identifier: goroutine-base
    parent: go-concurrency
    weight: 10
---

# Goroutine


## Goroutine是什么

goroutine是一种轻量级线程，也称之为协程。其创建与销毁不需要经过内核而是直接在go运行时进行管理。相比线程来说其更轻量，不仅仅在创建销毁过程中速度快，而且还在上下文切换以及内存分配都优于线程。

{{< mermaid align="center">}}
graph TB
    %% 第一层：内核态（仅OS线程和内核本身）
    subgraph 内核态[内核态 - 操作系统内核管理]
        T1[OS线程1 - ~1-8MB栈/内核调度]
        T2[OS线程2 - ~1-8MB栈/内核调度]
    end
    
    %% 第二层：用户态（Go运行时+Goroutine，全部在用户态）
    subgraph 用户态[用户态 - Go程序/运行时管理]
        %% Go运行时绑定到OS线程，但仍在用户态
        subgraph R1[Go运行时M1 - 用户态调度器]
            G1[Goroutine1 - 初始2KB栈/用户态]
            G2[Goroutine2 - 动态扩容栈/用户态]
        end
        
        subgraph R2[Go运行时M2 - 用户态调度器]
            G3[Goroutine3 - 用户态执行]
            G4[Goroutine4 - 低切换成本/用户态]
        end
    end

    %% 正确的层级连线：用户态的运行时绑定到内核态的线程，但自身不进入内核
    R1 -. 绑定/映射 .-> T1
    R2 -. 绑定/映射 .-> T2
    G1 & G2 --> R1
    G3 & G4 --> R2
{{< /mermaid >}}

{{< mermaid align="center">}}
graph LR
    subgraph Goroutine[Goroutine - Go协程]
        A1[用户态 · Go运行时调度]
        A2[初始2KB栈 · 动态扩容]
        A3[创建/切换成本极低]
        A4[单进程可创建数万个]
    end
    
    subgraph OSThread[OS Thread - 操作系统线程]
        B1[内核态 · 操作系统调度]
        B2[固定1-8MB栈 · 不可扩容]
        B3[创建/切换成本极高]
        B4[数量受限 · 仅数百/数千个]
    end

    %% 可选：添加对比指向（用虚线）
    A1 -. 对比 .-> B1
    A2 -. 对比 .-> B2
    A3 -. 对比 .-> B3
    A4 -. 对比 .-> B4
{{< /mermaid >}}

## Go语言中创建goroutine

在Go语言创建goroutine很简单不需要导入其它库，go语言本身就自带了go关键字来创建goroutine。

```go
func TestGoroutine(t *testing.T) {
	createGoroutine()
}

func createGoroutine() {
	go PrintHelloWorld() #创建goroutine
}

func PrintHelloWorld() {
	fmt.Println("Hello, World!")
}

```

`go`关键字用于在新的`goroutine`中启动指定的函数。现有的`goroutine`会与新创建的`goroutine`同时运行。作为`goroutine`运行的函数可以接收参数，但不能**返回值**。`goroutine`函数的参数在`goroutine`启动前就会被求值，并且在`goroutine`开始运行后传递给函数。

## 创建goroutine所需的资源

### 栈空间

**栈初始大小**：Go1.19版本及以后的版本，运行时使用历史平均值，早期版本1.4+为2K。

**分配方式：**初始栈式连续的内存块，由`Go`运行时的内存分配器（不是系统调用）在用户态分配。

**动态特性：**栈空间可以自动扩容最大可达1GB，不像OS 线程那样是固定栈大小。扩容时会分配新的更大栈块，把旧数据拷贝过去，全程在用户态完成，无需内核介入。


### Goroutine控制块（G结构体）

`g`结构体是描述`goroutine`状态核心的数据结构，创建时会分配以下资源：

- stack: 栈的起始地址、结束地址、当前栈指针。
- status： 运行状态(Gidle就绪、运行Grunning、阻塞Gwating、退出Gdead等)
- m: 绑定的M（Machine，对应OS线程）指针
- p：绑定的P(Processor 逻辑处理器)指针
- sched： 调度上下文（寄存器值、程序计数器PC等，用于Gouroutine切换时的保存状态）
- goid： Goroutine唯一ID用于标识不同的`Goroutine`。
- waitreason: 阻塞原因（如等待chanel、锁、IO等）

内存占用： `g`结构体本身大小几百字节，远小于OS线程的TCP（线程控制块）。

### 调度相关的元数据

- 就绪队列节点： 当创建一个goroutine后，比如分配完栈空间和g结构体之后，会将该goroutine加入到P的本地就绪队列（或者全局队列），仅占用队列的一个节点位置，指针大小。
- GC相关标记： Go运行时会为`goroutine`标记GC根对象（栈中的指针），无需额外分配内存，仅做状态标记。

## main函数所在goroutine终止了

在运行我们的程序时，go运行时会创建多个goroutine。具体多少根据不同版本的实现方式不同而不同。但至少会有一个用于垃圾回收的goroutine和一个主goroutine，也就是执行main函数的`goroutine`。当main函数执行完成之后，程序会立即终止，所有正在运行的goroutine都会在函数执行中途突然终止，无法执行任何清理操作。

```go
func TestGoroutine(t *testing.T) {
	mainFunc()
}

func mainFunc() {
	fmt.Println("main函数开始执行", goid.Get())
	//创建goroutine
	go longTimeRun()
	fmt.Println("main函数退出")
}

func longTimeRun() {
	fmt.Println("我正在执行", goid.Get())
	time.Sleep(time.Second) //休眠一秒
	fmt.Println("我准备退出了", goid.Get())
}
// output:
=== RUN   TestGoroutine
main函数开始执行 19
main函数退出
--- PASS: TestGoroutine (0.00s)
PASS
我正在执行 20
ok      go-concurrency-base/goroutine   1.916s
```

## Goroutine发生了panic会导致主程序退出吗

panic可以终止goroutine，如果goroutine中发生panic，它会沿着调用栈向上传播，知道找到recover函数或者gorotine返回。如果panic未被处理，将会输出panic消息，程序随之崩溃。

{{< mermaid align="center">}}
graph TB
    A[Goroutine执行代码] --> B[触发panic（如除0、空指针、主动panic）]
    B --> C{当前Goroutine是否有defer+recover？}
    C -->|否| D[panic向上传播到Go运行时]
    D --> E[运行时终止所有Goroutine]
    E --> F[整个程序崩溃，输出panic堆栈信息]
    C -->|是| G[recover捕获panic，返回错误信息]
    G --> H[Goroutine继续执行defer后续逻辑，不崩溃]
{{< /mermaid >}}

```go
func TestGoroutine(t *testing.T) {
	go riskTask()
	time.Sleep(100)
	fmt.Println("是否正确执行")
}
func riskTask() {
	var p *int

	fmt.Println(*p) // 解引用空指针
}

//程序会直接引发panic 导致整个程序崩溃
```

如果在`riskTask`中捕获`panic`然后`recover`，会发现程序不会因为一个`goroutine`panic了导致整个程序都崩溃。

```go
func TestGoroutine(t *testing.T) {
	go riskTaskWithRecover()
	time.Sleep(100)
	fmt.Println("是否正确执行")
}
func riskTaskWithRecover() {
	var p *int
	defer func() {
		if err := recover(); err != nil {
			debug.PrintStack()
		}
	}()
	fmt.Println(*p)
}

```

**重点：解决goroutine引发panic导致程序崩溃需要使用defer+recover来捕获panic然后处理，但是recover只能捕获当前goroutine不能跨goroutine。所以如果一个goroutine并没有处理panic那么整个程序都崩溃了。**



