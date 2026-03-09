---
title: 'Dead Lock'
date: '2026-03-09T23:42:41+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- 死锁
- MySQL
menu:
  sidebar:
    name: MySQL死锁
    identifier: mysql-deadlock
    parent: mysql-lock
    weight: 10
---


# MySQL中的死锁

## 死锁

如果在有两个线程，分别执行两个事务，但是这两个事务中分别需要获取两个行锁，其中一个事务需要依次获取行1和2的行锁，另一个事务需要依次行2和1的行锁。

{{< mermaid align="center">}}
sequenceDiagram
    participant T1 as 事务 A (Transaction A)
    participant DB as MySQL 数据库
    participant T2 as 事务 B (Transaction B)

    Note over T1, T2: 假设表中存在 ID 为 1 和 2 的两行数据

    T1->>DB: UPDATE table SET name='A' WHERE id=1
    activate DB
    Note right of DB: 事务 A 获取 ID=1 的行级锁 (X-Lock)
    DB-->>T1: OK
    deactivate DB

    T2->>DB: UPDATE table SET name='B' WHERE id=2
    activate DB
    Note right of DB: 事务 B 获取 ID=2 的行级锁 (X-Lock)
    DB-->>T2: OK
    deactivate DB

    Note over T1, T2: --- 冲突开始 ---

    T1->>DB: UPDATE table SET name='A2' WHERE id=2
    activate DB
    Note right of DB: 事务 A 请求 ID=2 的锁 (被事务 B 持有)
    Note  over DB: 事务 A 进入等待状态 (Waiting...)

    T2->>DB: UPDATE table SET name='B2' WHERE id=1
    Note right of DB: 事务 B 请求 ID=1 的锁 (被事务 A 持有)
    
    Note  over DB: 🔴 检测到死锁 (Deadlock Detected)
    
    DB-->>T2: 报错: Deadlock found... (Error 1213)
    deactivate DB
    Note left of T2: 事务 B 被回滚 (Rollback)

    activate DB
    Note right of DB: 事务 B 释放 ID=2 的锁
    DB-->>T1: OK (解除阻塞)
    deactivate DB
    Note left of T1: 事务 A 继续执行并提交
{{< /mermaid >}}

`MySQL`有两种方式避免死锁，第一种主要是设置超时时间，当一个事务执行时间超过某种阈值，那么其会返回当前语句的错误信息，之前执行成功的语句不会主动回滚，所以需要用户手动处理，比如执行ROLLBACK 回滚整个事。这个阈值一般是50s，并且这个时间是从事务执行该语句获取锁开始计算，如果超时就返回错误。

```shell
+--------------------------+-------+
| Variable_name            | Value |
+--------------------------+-------+
| innodb_lock_wait_timeout | 50    |
+--------------------------+-------+
```



`MySQL`避免死锁的第二种方式是死锁检测。

```shell
+------------------------+-------+
| Variable_name          | Value |
+------------------------+-------+
| innodb_deadlock_detect | ON    |
+------------------------+-------+
1 row in set (0.00 sec)
```

主动死锁检测，是在发生死锁的时候，快速发现并且进行处理。它会牺牲掉其中一个事务，直接回滚报错。

```mysql
# 客户端1
mysql> BEGAIN;
mysql> update user set name="foreverool-test1" where id=1;
mysql> update user set name="foreverool-test1" where id=2; ## 这里会处于阻塞状态
```

```mysql
# 客户端2
mysql> begin;
update user set name="forverool_test2" where id=2;
mysql> update user set name="forverool_test2" where id=1; ## 执行完这条语句会直接返回错误
```

当客户端2执行最后一条语句的时候，MySQL会返回一个error，然后让你重新执行事务。

那么我们来看一下最后的数据表。

```mysql
mysql> select * from user;
+----+------------------+
| id | name             |
+----+------------------+
|  1 | foreverool-test1 |
|  2 | foreverool-test1 |
|  3 | forverool2       |
+----+------------------+
3 rows in set (0.02 sec)
```

首先可以看到客户端1的所有事务都正常执行，客户端2的事务一条语句都没有执行。由于死锁检测，发现了死锁，所以牺牲掉了客户端2执行的事务，也就是执行了回滚整个事务。此时客户端1的第二条修改指令，就不会阻塞，所以可以正常执行。

主动死锁检测如果同时访问的线程很多的情况下，其会大量的消耗CPU资源。

### 死锁检测所带来性能问题

每个新来的被堵的线程，都要判断会不会由于自己的加入导致了死锁。死锁检测的本质是DFS，通过遍历所有等待中的事务来寻找是否存在环。

#### 算法复杂度

如果有$n$个事务在等待锁，检测器需要检查每个事务与其他事务的依赖关系。最坏的情况复杂度接近$O(n^2)$。

当大量的事务（例如1000）同时争抢同一个“秒杀商品”的行锁时，每个新加入的事务都会触发依次扫描。

- 第一个等待着检测0次
- 第100个等待者可能需要扫描前面99个事务的关系
- 第1000个等待者则需要扫描极其复杂的链路

#### 严重CPU飙升

死锁检测是在Server层和存储引擎层之间进行的同步操作。

- CPU消耗：当并发事务达到一定阈值，死锁检测消耗的CPU资源会迅速超过执行SQL本身的消耗。你会发现数据库CPU占用100%，但每秒的TPS(每秒处理的事务数)却很低。
- 系统锁竞争：为了遍历等待图，检测器需要持有全局的锁资源。这意味着在检测期间，其它事务连申请锁、释放锁的操作都会被阻塞。

#### 排队带来的雪崩

没添加一个线程等待，死锁锁检测就会越来越慢，然后就导致大量的事务进入等待。又进一步加大死锁检测，形成一种恶性循环。

## 优化死锁检测思路

- 关闭死锁检测 `SET GLOBAL innodb_deadlock_detect= OFF`，适合高并发热点更新的场景。
- 调低超时时间 将`innodb_lock_wait_timeout`设置为`1-3`秒，依赖超时自动放弃打破死锁。
- 应用层限流，在进入DB前，通过redis或者消息队列限制并发数， 保证数据库不进入$O(n^2)$
- 锁的降级/拆分， 将一行库存拆分为10行，减少单行竞争。从业务逻辑上规避并发冲突。

在项目中优化死锁检测所带来的性能问题，通常的做法是在业务逻辑上减少锁的竞争。

#### 锁分片

这是解决热点更问题的经典方案。

- 场景：假设你有一个全局活动库存行，所有人都去更新它，死锁检测会瞬间爆炸。
- 做法： 将这一行数据差分成100行(slot)。
- 逻辑：用户下单时，随机选择一个slotID进行扣减。
- 效果： 所得竞争程度值降低原来的1%，死锁检测器的负担也随之降低两个数量级。

比如传统的方式存储库存数量通常在一行存储整个库存数量比如100000。

通过拆分，在这个表中产生100行库存数据，然后每行库存为100000/100=1000库存。

然后用户下单时，通过随机产生一个slotID,将该行库存进行扣减。这样锁同一行的概率就下降了99%。

#### 内存预处理+异步落库

在极高并发的情况下，直接让数据库处理事务是不明智的选择。

- 做法：利用`Redis`的`DECR`操作进行原子减库存。
- 同步：通过消息队列异步将扣减结果写入`MySQL`中。
- 优势：数据库不在面临大量的并发行锁请求，死锁检测也就不会有大量的事务等待。





