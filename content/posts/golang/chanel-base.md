---
title: "Chanel Base"
date: 2026-01-10T04:44:16+08:00
lastmod: 2026-01-10T04:44:16+08:00
hero: 
description: ""
theme: Toha
draft: false
menu:
  sidebar:
    name: 
    identifier: 
    parent: golang
    weight: 10
---

# chan的实现原理

---

# 0. 预备知识

### 0.1 Unix管道

​	在`Unix`以及类`Unix`操作系统中，管道(pipeline)是将标准输入输出链接起来的进程，其中每一个进程的输出被直接作为下一个进程的输入，也就是说管道其实是进程间的通信机制。

​	管道的典型用途是为两个不同进程（一个父进程，另一个是子进程）间进行通信的手段。首先会根据父进程`fork`（`unix`创建子进程的函数）一个子进程（也就是创建一个父进程的副本），由于创建管道会返回两个文件描述符，一个是读描述符，另一个是写描述符。在进行`fork`的时候，进程空间会进行复制，也就是说该文件描述符也会被复制，所有两个进程都有相同的读写文件描述符。

![img](images/posts/golang/chanel_base/Image00027.jpg)

​	当父进程关闭读出端，子进程关闭同一管道的写入端。这样就在父子进程间提供了一个单向数据流。

![img](images/posts/golang/chanel_base/Image00028.jpg)

​	比如在执行`linux`命令时：

```shell
ls -l | grep "chan"
```

​	首先父进程就是`shell`，它首先会创建管道(pipe)，

接着创建`ls `子进程，之后创建`grep`子进程，也就是`fork`两个子进程，这样两个子进程就会包含管道返回的两个文件描述符，之后将`ls -l`所执行的命令标准输出写入到管道之中，然后`grep "chan"`则会从管道读取数据并处理，最后就是返回结果。

#### 0.1.1 管道在linux下的具体实现

​	管道在`Linux`系统具体实现是缓冲区`buffer`而不是队列。

​	管道会为读端和写端分别分配内核缓冲区， 写进程将数据写入写端缓冲区，读进程从读端缓冲区读取数据。内核将写端缓冲区的数据进行复制到读端缓冲区，然后内核也会维护读写两端的位置指针。

​	同步机制： 

​					当写端缓冲区满的时候，写进程会被阻塞掉，直到读进程读取了部分数据腾出空间。

​					当读缓冲区为空的时候，读进程会被阻塞，直到写进程写入了新数据。

​	管道的数据采用`FIFO`的数据处理模式，也就是先写入的数据先被读取。



---

## 1. chanel

​	在`go`语言中，一个进程可能会有多个`goroutine`，多个`goroutine`之间的通信可以使用`chanel`或者对于共享内存进行加锁。

### 1.1 chan的数据结构

​	在`go SDK 1.20.3 `中的`runtime/chan.gp`文件中就定义了`chan`的底层数据结构`hchan`。  

 ```go
type hchan struct{
    qcount uint 		// 表示当前队列中的剩余元素
    dataqsiz uint		// 表示循环队列的大小，即可以存放元素的个数
	buf unsafe.Pointer	// 指向一个dataqsiz大小的数组，也就是环形队列的指针
    elemsize uint16		// 每个元素的大小
    closed uint32		// 标记关闭状态
    elemtype *_type		// 元素类型
    sendx uint			// 队列下标，指元素写入时存放到队列中的位置
    recvx uint			// 队列下标，指元素从队列的该位置读出
    recvq waitq			// 等待读消息的goroutine队列
    sendq waitq			// 等待写消息的goroutine队列
    lcok  mutex			// 互斥锁，chan不允许并发读写
}
 ```

```go
type waitq struct {
	first *sudog
	last  *sudog
}
```

​	`waitg`类型是一个队列，其包含队列的第一个元素指针和最后一个元素指针。

​	`waitq`实现了两个方法分别是: `enqueue, dequeue`。

```go
type sudog struct {
	// The following fields are protected by the hchan.lock of the
	// channel this sudog is blocking on. shrinkstack depends on
	// this for sudogs involved in channel ops.

	g *g

	next *sudog
	prev *sudog
	elem unsafe.Pointer // data element (may point to stack)

	// The following fields are never accessed concurrently.
	// For channels, waitlink is only accessed by g.
	// For semaphores, all fields (including the ones above)
	// are only accessed when holding a semaRoot lock.

	acquiretime int64
    
	releasetime int64
	ticket      uint32

	// isSelect indicates g is participating in a select, so
	// g.selectDone must be CAS'd to win the wake-up race.
	isSelect bool

	// success indicates whether communication over channel c
	// succeeded. It is true if the goroutine was awoken because a
	// value was delivered over channel c, and false if awoken
	// because c was closed.
	success bool

	parent   *sudog // semaRoot binary tree
	waitlink *sudog // g.waiting list or semaRoot
	waittail *sudog // semaRoot
	c        *hchan // channel
}
```

`sudog`:用于表示一个在等待列表的`g(表示goroutine 的数据结构)`。

思考： 为什么需要`sudog`而不是直接使用`g`？

​	`go SDK`中作者表示：

```go
// sudog is necessary because the g ↔ synchronization object relation
// is many-to-many. A g can be on many wait lists, so there may be
// many sudogs for one g; and many gs may be waiting on the same
// synchronization object, so there may be many sudogs for one object.
```

​	总结：`sudog`的存在是必须的，因为`goroutine`和同步对象之间的关系是多对多的。一个`goroutine`可以在多个等待列表当中，因此多个`sudog`表示同一个`goroutine`，并且多个`goroutine`可能等待同一个同步对象，所以有个同步对象有多个`sudog`。

#### 1.1.1 环形队列

​	`chan`内部实现了一个环形队列的缓冲区，也就是`buf`字段，队列的长度是在创建`chan`的时候指定，也就是使用`make`函数创建的时候指定的，如果不指定长度，则没有这个环形缓冲区，也就是无缓冲`chan`。

![hchan-queue](images/posts/golang/chanel_base/hchan-queue.png)

#### 1.1.2 等待队列

​	一个`goroutine`从`chanel`读数据，如果`chanel`缓冲区为空或者没有缓冲区，当前`goroutine`会被阻塞。

​	一个`goroutine`从`chanel`写数据，如果`chanel`缓冲区满了或者没有缓冲区，当前`goroutine`会被阻塞。

​	被阻塞的`goroutine`会被存储在等待队列当中，也就是`recvq， sendq`当中。

​	`sendq`队列用于存储那些试图向`chanel`发送数据但被阻塞的`goroutine`。

​	`recvq`队列用于存储那些试图向`chanel`读取数据但被阻塞的`goroutine`。

**思考： 当多个读`goroutine`被阻塞，然后存储在`recvq`等待队列当中，此时有一个写`goroutine`写入数据，那么唤醒所有等待队列的`goroutine`还是唤醒部分？**

​	<font color="red">答: `chanel`不会唤醒所有等待队列的`goroutine`，会取出一个`goroutine`处理数据，因为`chanel`的设计是尽可能高效地完成数据的传递，如果每次读取都唤醒所有的`recvq`中的`goroutine`会导致大量无谓的上下文切换，降低性能。选择队列头部的`goroutine`来传输数据，可以保证`FIFO`的顺序，避免饥饿问题的发生。</font>

#### 1.1.3 类型信息

​	一个`chanel`只能传递一种类型的值，类型信息存储在`hchan`当中【`elemtype. elemsize`】

#### 1.1.4 锁

​	一个`chanel`同时仅允许被一个`goroutine`读写。这也是为什么`chanel`是线程安全的数据类型。

#### 1.2 向`chanel`中写数据

**code**

```go
func chansend(c *hchan, ep unsafe.Pointer, block bool, callerpc uintptr) bool {
	if c == nil {
		if !block {
			return false
		}
		gopark(nil, nil, waitReasonChanSendNilChan, traceEvGoStop, 2)
		throw("unreachable")
	}

	if debugChan {
		print("chansend: chan=", c, "\n")
	}

	if raceenabled {
		racereadpc(c.raceaddr(), callerpc, abi.FuncPCABIInternal(chansend))
	}

	// Fast path: check for failed non-blocking operation without acquiring the lock.
	//
	// After observing that the channel is not closed, we observe that the channel is
	// not ready for sending. Each of these observations is a single word-sized read
	// (first c.closed and second full()).
	// Because a closed channel cannot transition from 'ready for sending' to
	// 'not ready for sending', even if the channel is closed between the two observations,
	// they imply a moment between the two when the channel was both not yet closed
	// and not ready for sending. We behave as if we observed the channel at that moment,
	// and report that the send cannot proceed.
	//
	// It is okay if the reads are reordered here: if we observe that the channel is not
	// ready for sending and then observe that it is not closed, that implies that the
	// channel wasn't closed during the first observation. However, nothing here
	// guarantees forward progress. We rely on the side effects of lock release in
	// chanrecv() and closechan() to update this thread's view of c.closed and full().
	if !block && c.closed == 0 && full(c) {
		return false
	}

	var t0 int64
	if blockprofilerate > 0 {
		t0 = cputicks()
	}

	lock(&c.lock)

	if c.closed != 0 {
		unlock(&c.lock)
		panic(plainError("send on closed channel"))
	}

	if sg := c.recvq.dequeue(); sg != nil {
		// Found a waiting receiver. We pass the value we want to send
		// directly to the receiver, bypassing the channel buffer (if any).
		send(c, sg, ep, func() { unlock(&c.lock) }, 3)
		return true
	}

	if c.qcount < c.dataqsiz {
		// Space is available in the channel buffer. Enqueue the element to send.
		qp := chanbuf(c, c.sendx)
		if raceenabled {
			racenotify(c, c.sendx, nil)
		}
		typedmemmove(c.elemtype, qp, ep)
		c.sendx++
		if c.sendx == c.dataqsiz {
			c.sendx = 0
		}
		c.qcount++
		unlock(&c.lock)
		return true
	}

	if !block {
		unlock(&c.lock)
		return false
	}

	// Block on the channel. Some receiver will complete our operation for us.
	gp := getg()
	mysg := acquireSudog()
	mysg.releasetime = 0
	if t0 != 0 {
		mysg.releasetime = -1
	}
	// No stack splits between assigning elem and enqueuing mysg
	// on gp.waiting where copystack can find it.
	mysg.elem = ep
	mysg.waitlink = nil
	mysg.g = gp
	mysg.isSelect = false
	mysg.c = c
	gp.waiting = mysg
	gp.param = nil
	c.sendq.enqueue(mysg)
	// Signal to anyone trying to shrink our stack that we're about
	// to park on a channel. The window between when this G's status
	// changes and when we set gp.activeStackChans is not safe for
	// stack shrinking.
	gp.parkingOnChan.Store(true)
	gopark(chanparkcommit, unsafe.Pointer(&c.lock), waitReasonChanSend, traceEvGoBlockSend, 2)
	// Ensure the value being sent is kept alive until the
	// receiver copies it out. The sudog has a pointer to the
	// stack object, but sudogs aren't considered as roots of the
	// stack tracer.
	KeepAlive(ep)

	// someone woke us up.
	if mysg != gp.waiting {
		throw("G waiting list is corrupted")
	}
	gp.waiting = nil
	gp.activeStackChans = false
	closed := !mysg.success
	gp.param = nil
	if mysg.releasetime > 0 {
		blockevent(mysg.releasetime-t0, 2)
	}
	mysg.c = nil
	releaseSudog(mysg)
	if closed {
		if c.closed == 0 {
			throw("chansend: spurious wakeup")
		}
		panic(plainError("send on closed channel"))
	}
	return true
}

```

向一个`chanel`写入数据的具体实现过程：

- 检查`chanel`的状态

  首先检查`chanel`的状态，包括是否已关闭、是否缓冲区满了。

- 尝试直接发送

  如果`chanel`不满且有等待接收的`goroutine`，则会直接将数据发送给等待的`goroutine`，并唤醒该`goroutine`。

  - 如何发送数据

    ```go
    	if sg := c.recvq.dequeue(); sg != nil {
    		// Found a waiting receiver. We pass the value we want to send
    		// directly to the receiver, bypassing the channel buffer (if any).
    		send(c, sg, ep, func() { unlock(&c.lock) }, 3)
    		return true
    	}
    ```

    根据源码我们可以看出如果`recvq`等待队列中有读`goroutine`（不为空的情况下），从该队列出队获取到一个`goroutine`然后发送数据。由于`recvq`不为空，也就是说`chanel`中的`buf`环形队列中没有数据，此时就直接发送数据就可以了。

    ```go
    // send processes a send operation on an empty channel c.
    // The value ep sent by the sender is copied to the receiver sg.
    // The receiver is then woken up to go on its merry way.
    // Channel c must be empty and locked.  send unlocks c with unlockf.
    // sg must already be dequeued from c.
    // ep must be non-nil and point to the heap or the caller's stack.
    func send(c *hchan, sg *sudog, ep unsafe.Pointer, unlockf func(), skip int) {
    	if raceenabled {
    		if c.dataqsiz == 0 {
    			racesync(c, sg)
    		} else {
    			// Pretend we go through the buffer, even though
    			// we copy directly. Note that we need to increment
    			// the head/tail locations only when raceenabled.
    			racenotify(c, c.recvx, nil)
    			racenotify(c, c.recvx, sg)
    			c.recvx++
    			if c.recvx == c.dataqsiz {
    				c.recvx = 0
    			}
    			c.sendx = c.recvx // c.sendx = (c.sendx+1) % c.dataqsiz
    		}
    	}
    	if sg.elem != nil {
    		sendDirect(c.elemtype, sg, ep)
    		sg.elem = nil
    	}
    	gp := sg.g
    	unlockf()
    	gp.param = unsafe.Pointer(sg)
    	sg.success = true
    	if sg.releasetime != 0 {
    		sg.releasetime = cputicks()
    	}
    	goready(gp, skip+1)
    }
    ```

    ```go
    func sendDirect(t *_type, sg *sudog, src unsafe.Pointer) {
    	// src is on our stack, dst is a slot on another stack.
    
    	// Once we read sg.elem out of sg, it will no longer
    	// be updated if the destination's stack gets copied (shrunk).
    	// So make sure that no preemption points can happen between read & use.
    	dst := sg.elem
    	typeBitsBulkBarrier(t, uintptr(dst), uintptr(src), t.size)
    	// No need for cgo write barrier checks because dst is always
    	// Go memory.
    	memmove(dst, src, t.size)
    }
    ```

    未完待续....

