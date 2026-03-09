---
title: 'sync.Cond'
date: '2026-03-09T17:43:51+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- goroutine
- sync.Cond
menu:
  sidebar:
    name: sync.Cond
    identifier: sync-cond
    parent: golang-concurrency
    weight: 10
---


# sync.Cond 基本概念

`sync.Cond`可以称其为条件变量，主要作用是**让一组goroutine等待某个特定条件出现，并在条件满足时发送通知。**

`sync.Cond`可以通知其它`goroutine`你们可以被唤醒了。也可以主动阻塞让出CPU资源。

`sync.Cond`本质上是对`mutex`或者`RWMutex`的一种扩展。其底层必须维护着一个`Locker`接口的对象。

每当我们的业务满足某种条件时，我们可以通知其它`goroutine`你们可以开始工作了，不用阻塞了。



## `sync.Cond`底层实现

```go
type Cond struct {
	noCopy noCopy

	// L is held while observing or changing the condition
	L Locker

	notify  notifyList //通知队列
	checker copyChecker
}
```

`sync.Cond`主要包含3个方法，和Locker接口定义的两个方法（组合嵌套）。



### notifyList

`notifyList`是实现`sync.Cond`核心数据结构。其本身是一个队列，主要存储等待的`goroutine`。
	`notifyList` 的设计目标是：

- 记录哪些协程在等待。
- 保证 `Signal` 唤醒的是等待时间最长的那个（FIFO）。
- 允许 `Wait` 操作在不持有全局大锁的情况下进行一部分逻辑，减少竞争。

```go
type notifyList struct {
	// wait is the ticket number of the next waiter. It is atomically
	// incremented outside the lock.
	wait atomic.Uint32 // 下一个等待着应该持有ticket

	// notify is the ticket number of the next waiter to be notified. It can
	// be read outside the lock, but is only written to with lock held.
	//
	// Both wait & notify can wrap around, and such cases will be correctly
	// handled as long as their "unwrapped" difference is bounded by 2^31.
	// For this not to be the case, we'd need to have 2^31+ goroutines
	// blocked on the same condvar, which is currently not possible.
	notify uint32 //下一个被唤醒的goroutine的ticket

	// List of parked waiters.
	lock mutex // 保护链表的锁
	head *sudog // 链表的头部
	tail *sudog //链表的尾部
}

```

**wait (Ticket)**：每当一个协程调用 `Wait()`，它就会领到一个自增的编号。

**notify (Waiter)**：记录当前已经通知到了哪个编号。

**sudog**：这是 Go 运行时包装 Goroutine 的结构，用来把它挂在等待队列里。



#### notifyListAdd

`notifyListAdd`函数主要作用是将当前调用者(当前`goroutine`)添加到等待通知的队列当中。如果调用了`notifyListAdd`那么之后就必须调用`notifyListWait`函数等待通知。

```go
func notifyListAdd(l *notifyList) uint32 {
	// This may be called concurrently, for example, when called from
	// sync.Cond.Wait while holding a RWMutex in read mode.
	return l.wait.Add(1) - 1
}
```

可以看到`notifyListAdd`会返回一个ticket,然后使用ticket传入`notifyListWait`中。此时真正的阻塞等待通知唤醒了。



#### notifyListWait

`notifyListWait`是真正意义上等待被唤醒。其主要是获取当前`goroutine`也就是`sudog`,然后将该`sudog`放入等待通知队列当中，然后休眠，等待被唤醒。

```go
// notifyListWait waits for a notification. If one has been sent since
// notifyListAdd was called, it returns immediately. Otherwise, it blocks.
//
//go:linkname notifyListWait sync.runtime_notifyListWait
func notifyListWait(l *notifyList, t uint32) {
	lockWithRank(&l.lock, lockRankNotifyList)

	// Return right away if this ticket has already been notified.
	if less(t, l.notify) {
		unlock(&l.lock)
		return
	}

	// Enqueue itself.
	s := acquireSudog()
	s.g = getg()
	s.ticket = t
	s.releasetime = 0
	t0 := int64(0)
	if blockprofilerate > 0 {
		t0 = cputicks()
		s.releasetime = -1
	}
	if l.tail == nil {
		l.head = s
	} else {
		l.tail.next = s
	}
	l.tail = s
	goparkunlock(&l.lock, waitReasonSyncCondWait, traceBlockCondWait, 3)
	if t0 != 0 {
		blockevent(s.releasetime-t0, 2)
	}
	releaseSudog(s)
}
```



#### notifyListNotifyAll

将所有等待通知队列的`goroutine`全部唤醒。

```go
// notifyListNotifyAll notifies all entries in the list.
//
//go:linkname notifyListNotifyAll sync.runtime_notifyListNotifyAll
func notifyListNotifyAll(l *notifyList) {
	// Fast-path: if there are no new waiters since the last notification
	// we don't need to acquire the lock.
	if l.wait.Load() == atomic.Load(&l.notify) {
		return
	}

	// Pull the list out into a local variable, waiters will be readied
	// outside the lock.
	lockWithRank(&l.lock, lockRankNotifyList)
	s := l.head
	l.head = nil
	l.tail = nil

	// Update the next ticket to be notified. We can set it to the current
	// value of wait because any previous waiters are already in the list
	// or will notice that they have already been notified when trying to
	// add themselves to the list.
	atomic.Store(&l.notify, l.wait.Load())
	unlock(&l.lock)

	// Go through the local list and ready all waiters.
	for s != nil {
		next := s.next
		s.next = nil
		readyWithTime(s, 4)
		s = next
	}
}
```

#### notifyListNotifyOne

从等待通知队列中获取一个`goroutine`然后将其唤醒。

```go
// notifyListNotifyOne notifies one entry in the list.
//
//go:linkname notifyListNotifyOne sync.runtime_notifyListNotifyOne
func notifyListNotifyOne(l *notifyList) {
	// Fast-path: if there are no new waiters since the last notification
	// we don't need to acquire the lock at all.
	if l.wait.Load() == atomic.Load(&l.notify) {
		return
	}

	lockWithRank(&l.lock, lockRankNotifyList)

	// Re-check under the lock if we need to do anything.
	t := l.notify
	if t == l.wait.Load() {
		unlock(&l.lock)
		return
	}

	// Update the next notify ticket number.
	atomic.Store(&l.notify, t+1)

	// Try to find the g that needs to be notified.
	// If it hasn't made it to the list yet we won't find it,
	// but it won't park itself once it sees the new notify number.
	//
	// This scan looks linear but essentially always stops quickly.
	// Because g's queue separately from taking numbers,
	// there may be minor reorderings in the list, but we
	// expect the g we're looking for to be near the front.
	// The g has others in front of it on the list only to the
	// extent that it lost the race, so the iteration will not
	// be too long. This applies even when the g is missing:
	// it hasn't yet gotten to sleep and has lost the race to
	// the (few) other g's that we find on the list.
	for p, s := (*sudog)(nil), l.head; s != nil; p, s = s, s.next {
		if s.ticket == t {
			n := s.next
			if p != nil {
				p.next = n
			} else {
				l.head = n
			}
			if n == nil {
				l.tail = p
			}
			unlock(&l.lock)
			s.next = nil
			readyWithTime(s, 4)
			return
		}
	}
	unlock(&l.lock)
}

```

从链表中找到编号等于 `notify` 的那个协程。

将 `notify` 加 1。

唤醒该协程。

### Wait

`Wait`会主动阻塞当前`goroutine`。

```go
func (c *Cond) Wait() {
	c.checker.check()
	t := runtime_notifyListAdd(&c.notify) // 先加入通知列表中
	c.L.Unlock()
	runtime_notifyListWait(&c.notify, t) // 等待通知
	c.L.Lock()
}
```

根据`Wait`源码我们可以知道，调用`Wait`会**先释放锁，然后被唤醒的时候获得锁，如果在释放之后，与其它goroutine竞争锁的时候，没有获得锁的时候会被阻塞，直到拿到锁。 **

这里需要注意，wait的时候会先释放锁，所以在执行wait之前不要先释放锁，否则会引发`panic`。



### Signal

```go
// Signal wakes one goroutine waiting on c, if there is any.
//
// It is allowed but not required for the caller to hold c.L
// during the call.
//
// Signal() does not affect goroutine scheduling priority; if other goroutines
// are attempting to lock c.L, they may be awoken before a "waiting" goroutine.
func (c *Cond) Signal() {
	c.checker.check()
	runtime_notifyListNotifyOne(&c.notify)
}
```

当满足某些条件时，唤醒等待通知队列中的一个`goroutine`。



### BroadCast

```go
// Broadcast wakes all goroutines waiting on c.
//
// It is allowed but not required for the caller to hold c.L
// during the call.
func (c *Cond) Broadcast() {
	c.checker.check()
	runtime_notifyListNotifyAll(&c.notify)
}
```

唤醒所有等待通知的`goroutine`。

## 使用`sync.Cond`陷阱

- **在调用Wait之前没有加锁**：根据`Wait`方法，我们知道，其首先会释放锁，然后才等待被唤醒。如果我们在调用`Wait`之前没有加锁，那么就会产生`panic`，对没有加锁的锁进行释放锁。

- **在被唤醒的时候没有检查条件**：首先当前goroutine被唤醒的时候，条件不一定满足，如果条件不满足就执行接下来的代码就会发生逻辑错误。所以最好的选择是，被唤醒的时候使用`for`循环判断条件是否满足，如果满足则执行接下里业务逻辑。

## 让goroutine顺序执行

比如我们有三个`goroutine`，这三个`goroutine`分别打印100次`cat ,dog, pig`。我们需要这三个`goroutine`按照`cat dog pig`的顺序交互打印。

根据上述需求，我们可以使用`sync.Cond`或者`chanel`实现。

### 使用`sync.Cond`实现

思路： 我们需要定义一个类型，然后判断这个类型是否是否和我们需要的类型，如果是我才能打印数据，如果不是当前`goroutine`阻塞，直到满足条件时，我们在打印。

```go
type Display struct {
	condition *sync.Cond
	ttype     int // 0 cat 1 dog 2 pig
	times     int
}

func TestSequenceDispaly(t *testing.T) {

	display := Display{}
	var mutex sync.Mutex
	display.condition = sync.NewCond(&mutex)
	display.times = 100
	var wg sync.WaitGroup
	wg.Add(3)
	go display.Cat(&wg)
	go display.Dog(&wg)
	go display.Pig(&wg)
	wg.Wait()
}

func (d *Display) Cat(wg *sync.WaitGroup) {
	defer wg.Done()

	for i := 0; i < d.times; {
		d.condition.L.Lock() //加互斥锁

		// 这里使用for循环判断条件是否满足，如果不满足就阻塞，不会执行for语句块下方的代码，让出了CPU资源
		// 因为我们的逻辑是，唤醒所有等待的goroutine，唤醒的时候并不一定满足条件
		// 如果当前goroutine被唤醒，但是不满足条件，我继续阻塞，直到满足条件的时候，才执行接下来的指令
		for d.ttype != 0 {
			d.condition.Wait()
		}

		// 如果满足条件
		fmt.Println("cat")
		d.ttype = 1 // 将条件变为1 等待Dog协程打印
		i++

		d.condition.L.Unlock()  // 释放锁
		d.condition.Broadcast() //通知其它goroutine 可以唤醒了，不需要阻塞了
	}
}

func (d *Display) Dog(wg *sync.WaitGroup) {
	defer wg.Done()

	for i := 0; i < d.times; {
		d.condition.L.Lock()

		for d.ttype != 1 {
			d.condition.Wait()
		}

		fmt.Println("dog")
		d.ttype = 2
		i++

		d.condition.L.Unlock()
		d.condition.Broadcast()
	}

}

func (d *Display) Pig(wg *sync.WaitGroup) {
	defer wg.Done()
	for i := 0; i < d.times; {
		d.condition.L.Lock()

		for d.ttype != 2 {
			d.condition.Wait()
		}

		fmt.Println("pig")
		d.ttype = 0
		i++

		d.condition.L.Unlock()
		d.condition.Broadcast()
	}

}

```

### 使用`chanel`实现

可以使用无缓冲`chanel`，主要思想就是在一个goroutine中唤醒特定的goroutine，而不是将所有阻塞的goroutine都被唤醒。

```go
func TestSequenceDisplayByChanel(t *testing.T) {

	c := make(chan struct{})
	d := make(chan struct{})
	p := make(chan struct{})
	end := make(chan struct{})

	go cat(c, d)
	go dog(d, p)
	go pig(p, c, end)

	c <- struct{}{}
	<-end

}

func cat(start, next chan struct{}) {
	for i := 0; i < 100; i++ {
		<-start // 如果start没有数据则会被阻塞
		fmt.Println("cat")
		next <- struct{}{}
	}
}

func dog(start, next chan struct{}) {
	for i := 0; i < 100; i++ {
		<-start 
		fmt.Println("dog")
		next <- struct{}{}
	}
}

func pig(start, next, end chan struct{}) {
	for i := 0; i < 100; i++ {
		<-start 

		if i == 99 {
			fmt.Println("pig")
			end <- struct{}{}
		} else {
			next <- struct{}{}

		}
	}
}
```

## `sync.Cond`使用模板

```go
cond.L.Lock()
for !condition{
    cond.Wait()
}

// 业务逻辑
cond.L.Unlock()
```

## `sync.Cond`使用场景

- 一呼百应：当某种状态改变了，然后需要通知其它所有等待协程时。比如当一个协程改变了全局配置，那么就需要通知其它协程，刷新自己的配置。
- 频繁的状态切换:如果状态一直在满足和不满足之间切换，那么就可以使用`sync.Cond`。
- 高性能缓存/队列:在使用自建的缓冲队列或者对象池时，可以使用`sync.Cond`

**使用sync.Cond基本上可以使用chanel来实现，所以很多大型开源项目和标准库基本上是不使用sync.Cond，如果非要使用需要权衡sync.Cond和chanel实现的性能。**

