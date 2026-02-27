---
title: 'GMP基本概念'
date: '2026-02-27T21:16:55+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- GMP
- Goroutine
- 协程
- 线程
menu:
  sidebar:
    name: GMP基本概念
    identifier: gmp
    parent: go-concurrency
    weight: 10
---

---
updated: 2026-02-27 21:14:34
focused: 01:36:10

---

# GMP模型

- golang  version: Go SDK 1.20.3

- GMP在源代码中分散的位置很多，然后我是根据`ChatGPT`搜索到`sr/runtime/proc.go`这个文件中，然后找到了`m, g `的使用，然后根据`m, g`找到了其定义文件`src/runtime/runtime2.go`

  在`proc.go`文件的最开始的注释里，我们可以了解到`Goroutine Scheduler`概念，以及`GMP`具体含义是什么。

- G  - Goroutine

- M  - worker thread, or machine

- P  - processor, a resource that is required to execute Go code. M must have an associate P to execute Go code, however it can be blocked or in a syscall w/o an associated P. 



用户程序进行的系统调用都会被Runtime进行拦截，以此帮助runtime进行调度以及垃圾回收等相关工作。

{{< mermaid align="center">}}
graph TB
	subgraph GoProcess[Go可执行文件]
		program[GO Program]
		runtime[runtime]
		program <-.内存分配.->runtime
		program <-.chanel通信.->runtime
		program <-.goroutine创建.->runtime
		program <-.IO.->runtime
	end
	
	kenel[OS Kenenl]
	
	runtime -.系统调用.-> kenel
	program <-.线程创建.->runtime
{{< /mermaid >}}



## 1. GMP具体实现

​	首先要明确的一点是，`Goroutine`是执行的基本单元，但不是执行实体，一个`Goroutine`执行需要有一个空闲的`P and M`，如果只有空闲的M， 没有P， 那么`Goroutine`是不能执行，如果有空闲的P，没有空闲的M，在条件允许的情况下创建一个新的M，进行执行当前这个`Goroutine`。

{{< mermaid align="center">}}
graph TD
    subgraph "Go Runtime Scheduler"
        GlobalQueue["Global Queue (全局队列)"]
        
        subgraph P1 ["Processor (P)"]
            LRQ1["Local Run Queue (本地队列)"]
            M1["Machine (M)"]
            G1["Goroutine (G)"]
        end

        subgraph P2 ["Processor (P)"]
            LRQ2["Local Run Queue (本地队列)"]
            M2["Machine (M)"]
            G2["Goroutine (G)"]
        end
    end

    GlobalQueue -.-> LRQ1
    GlobalQueue -.-> LRQ2
    M1 --- G1
    M2 --- G2
    P1 --- M1
    P2 --- M2
{{< /mermaid >}}

### G

G就代表着一个`goroutine`。是执行function的载体。

G的状态有10中，分别是：

- `_Gidle`:表示该`goroutine`只是被创建，只是创建了一个rutime.g的结构体，还没有被初始化。然后将该g放入到`gFree`队列当中。
- `_Grunable`：表示该`goroutine`已经在运行队列当中了，此时已经给该goroutine分配了stack，但是没有访问权限。
- `_Grunning`:表示该`goroutine`可以执行用户代码，此时该goroutine有对自己的stack有访问权限，比如BP,SP已经放入到CPU的寄存器当中，此时它不在运行队列当中，它被分配了一个P和M。
- `_Gsyscall`：表示该`goroutine`正在执行一个系统调用。此时它不能继续执行用户代码，此时该`goroutine`有自己的栈空间。此时它不会被分配到运行队列当中，它被保存在当前的M中。
- `_Gwating`: 表示该`goroutine`被设置为阻塞状态。此时它不能执行任何用户代码，也不在运行队列当中。但是应该被记录在其它地方，比如：chanel wait 队列当中。此时它没有对自己的stack有访问权限。
- `_Gmoribund_unused`：目前不被使用，但是已经被硬编码到了gdb脚本中。
- `_Gdead`:表示该`goroutine`没有被运行，也许该`goroutine`退出了或者刚刚初始化。此时该`goroutine`不能执行任何代码，此时它有可能有已经分配好的stack，也有可能没有。如果一个goroutine刚被分配完stack,那么它的状态就是`_Gdead`,如果一个`goroutine`已经执行完用户代码退出了,那么此时的状态也是`_Gdead`此时`goroutine`的stack如果大于2kb那么重新创建新的stack,如果没有,那么直接使用之前的stack.但是会清理该goroutine的相关参数信息.
- `_Genqueue_unused`：该状态没有被使用.
- `_Gcopy_stack`:此时goroutine是不能被运行,表示当前goroutine的stack被调度器正在扩容中.处于这个状态的 G 既不在运行，也不在等待队列。它被“锁死”在当前的 M 上（或由 GC 线程操作中）。
- `_Gpreempted`:它标志着 Goroutine 处于 **“被异步抢占”** 的挂起态。

### P

P是一种资源， 是运行Go代码所需的所有上下文资源。

如果没有P,那么M只能通过全局运行队列去获取G，由于所有M共享这个G，所以就需要给这个全局运行队列加锁，这样做，效率大打折扣，所以才有P这个概念，每个P都维护一个属于自己的本地队列LRQ。

P都包含的资源：

- 本地运行队列（LRQ）：存储最多256个等待运行的G。
- 内存分配缓存（mcache）:为了实现高效的微小对象分配，每个P都有自己的内存缓存，这样M在分配内存的时候不需要加锁。
- 自由G列表：当一个G执行完或者被销毁时，可以复用g结构体，减少创建G的开销。
- 调度计数器：记录调度次数，用于触发抢占。

P是可以动态绑定M的，如果没有P的话，M执行G，如果G阻塞了，那么M也就阻塞了，M上的其它G都会被阻塞。引入P之后，当当前M阻塞了，P会绑定到其它空闲M上或者新创建一个M然后绑定。

### M

M是对OS线程的一种抽象，其与OS线程一一对应，但是也保存了自己的资源。M是绑定P的，如果没有绑定P是不能执行任何G的。

如果M阻塞因为G执行了系统调用而阻塞了，那么M会被挂起，G的状态从`_Grunning`变为`_Gsyscall`状态并且依然留在当前这个M中，然后P会被解绑，`sysmon`线程会将该P绑定到其它空闲线程或者新创建一个线程执行P中的其它G。

当G系统调用完成之后，G被唤醒，M会会优先去获取之前的那个P，如果该P没有被其它M绑定，直接绑定该P，然后直接执行当前的这个G，因为M中已经有了这个G，所以不需要将他放在P的本地队列当中。省区了从该本地队列获取G的时间。

如果之前的P已经被其它M所绑定，然后当前M会在全局P的队列中获取空闲的P，然后绑定，之后继续运行当前的G，然后再运行P中的其它G。

如果没有获取到任何P，那么M会将G的`_Gsyscall`状态转变为`_Grunnalbe`，放置到全局运行队列当中。

## goroutine的创建过程

首先main函数的goroutine是在程序运行开始就已经创建好了,然后如果在main所在的goroutine创建`goroutine`时:

- 当你执行`go func(){}()`的时候,`runtime`从`gFree`队列中获取一个状态为`_Gidle`或者`_Gdead`的G,并且初始化.
- G的状态变为`_Grunnable`.
- 当前M尝试将这个新的G放入与它绑定的P的`runnext`中.如果`runnext`没有G放入,如果有则将这个G放在P的本地运行队列当中.



{{< mermaid align="center">}}
graph LR
	G
	P
	M
	subgraph LRQ[本地运行队列]
	G1
	G2
	G3
	end
	P --> LRQ
	P -.获取G执行.->M
	
	subgraph gFree[gFree队列]
	G:idle
	G:dead
	end
	gFree -.G:runable.-> G
	
	G -.获取到G.-> M
	M -.尝试存入到P的runnext中.->P
{{< /mermaid >}}

## goroutine阻塞

当一个goroutine执行网络IO、锁、chanel操作时，`goroutine`的状态变为`_Gwaiting`状态，它会被存入到与操作相关的队列当中。

- 网络IO:存入到`NetPoller`管理的逻辑队列当中。该`netPoller`底层使用了操作系统的`epoll`，如果有数据到了，则会通知`netpoller`哪一个`goroutine`有数据，然后`sysmon`线程会遍历`netPoller`队列看是否有goroutine可以被唤醒了，如果有则将该goroutine的状态变为`_Grunnable`然后放入到P的`runnext`中，或者P的运行队列当中。

- chanel阻塞： 

  - 发送阻塞： G会被封装为一个`sudog`结构，存入`channel`的内部`sendq`队列当中。
  - 接收阻塞：G封装称为`sudog`结构，然后存入到`recvq`中。

  此时G与`Channel`绑定，一旦`Channel`另一端就绪，会由另一端的`goroutine`负责唤醒该队列的第一个G。

- 锁阻塞
  当你的goroutine竞争锁失败的时候，会阻塞时：

  - 存放位置：go运行时维护了一个全局的信号量中心`senaRoot`它是一个哈希表，内部通过平衡树来管理等待的goroutine。
  - 逻辑：G进入到对应地址的信号量等待队列当中，等待锁的释放者调用`runtime_Semrelease`唤醒。

- 定时器阻塞：存放在P的`timers`堆中
  当你执行`time.Sleep`或计时器的时候：

  - 存放位置：G会被放入其当前绑定的P的本地timer堆中。
  - 逻辑： 每个P都有一个`timer`最小堆，调度器或者`sysmon`会检查堆顶的时间戳，到期后将对应的G唤醒。

## M获取G

首先要知道M运行G的前提条件是绑定P，如果没有绑定P那么M是无法执行G的。

M获取G的大致流程如下：

{{< mermaid align="center">}}
graph TD
    Start([M 开始查找任务 findrunnable]) --> Check61{schedtick%61 ==0 ?}
    
    %% 61次检查逻辑
    Check61 -- 是 --> GetGRQ_Pre[从全局队列 GRQ 获取任务]
    GetGRQ_Pre --> Found_Pre{是否获取成功?}
    Found_Pre -- 成功 --> Execute([执行任务])
    Found_Pre -- 失败 --> CheckRunNext
    
    %% 本地队列逻辑
    Check61 -- 否 --> CheckRunNext[检查 P.runnext 特权位]
    CheckRunNext --> Found_Next{是否有 G?}
    Found_Next -- 有 --> Execute
    
    Found_Next -- 无 --> CheckLRQ[检查 P.runq 本地运行队列]
    CheckLRQ --> Found_LRQ{是否有 G?}
    Found_LRQ -- 有 --> Execute
    
    %% 全局队列逻辑
    Found_LRQ -- 无 --> CheckGRQ[检查全局队列 GRQ]
    CheckGRQ --> Found_GRQ{是否有 G?}
    Found_GRQ -- 有 --> Execute
    
    %% 网络轮询逻辑
    Found_GRQ -- 无 --> CheckNetpoll[检查 Netpoll 网络轮询器 - 非阻塞]
    CheckNetpoll --> Found_Net{是否有就绪 G?}
    Found_Net -- 有 --> Execute
    
    %% 窃取逻辑
    Found_Net -- 无 --> Stealing[尝试 Work Stealing - 从其他 P 偷取]
    Stealing --> Found_Steal{是否偷到 G?}
    Found_Steal -- 有 --> Execute
    
    %% 最后尝试与休眠
    Found_Steal -- 无 --> LastCheck[最后检查: Netpoll / GC 标记任务]
    LastCheck --> Found_Last{是否有任务?}
    Found_Last -- 有 --> Execute
    
    Found_Last -- 无 --> SpinEnd[自旋结束, M 进入休眠]
{{< /mermaid >}}

当实在没有任务的时候，M会进入到休眠状态，它会被放置在全局的空闲线程队列（schedt.midle）当中。`schedt.midle`队列存储了所有休眠的`M`结构体。这是一个全局共享资源，受全局锁`sched.lock`保护。

M是如何休眠的：

- Linux： 使用futex系统调用（futex_wait）。
- 作用：这让M对应的线程从CPU上切走，然后进入到阻塞状态挂起。此时这个M不会消耗任何CPU周期，直到被内核唤醒。


​	
总结：其实为了避免锁带来的消耗，其实可以包装一层资源层将全局资源变成本地资源。合理的运用自旋锁，不要轻易的将线程或者协程挂起，可以先自旋一段时间，如果还没有获取到资源再挂起休眠等操作。

