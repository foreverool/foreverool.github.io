---
title: 'Redis持久化基础'
date: '2026-02-22T07:29:36+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- Redis
- AOF
- RDB

menu:
  sidebar:
    name: Redis持久化基础
    identifier: redis-persistance-base
    parent: redis-persistance
    weight: 1
---


# Redis宕机之后快速恢复数据

## RDB内存快照

内存快照就是指redis内存中的数据某一时刻的状态数据。将该状态的数据保存称RDB文件形式写入磁盘中。

{{< mermaid align="center">}}
graph LR
    %% 节点定义
    REQ((写请求))
    RDS[Redis]
    T1([T1 时刻数据快照])
    T2([T2 时刻数据快照])
    T3([T3 时刻数据快照])
    DB[(磁盘)]

    %% 连线关系
    REQ --> RDS
    RDS --> T1
    T1 --> T2
    T2 --> T3
    
    %% 指向磁盘的曲线
    T1 -.-> DB
    T2 -.-> DB
    T3 -.-> DB

    %% 样式美化
    classDef yellow fill:#fff9e6,stroke:#e6b800,stroke-width:2px;
    classDef blue fill:#e6f7ff,stroke:#006699,stroke-width:2px;
    classDef red fill:#ffe6e6,stroke:#990000,stroke-width:2px;
    
    class REQ,DB yellow;
    class RDS blue;
    class T1,T2,T3 red;

    %% 全局配置 (仅在支持的主屏渲染器有效)
    linkStyle default stroke:#5f9ea0,stroke-width:2px;
{{< /mermaid >}}

Redis通过定时执行RDB内存快照，而不是每次写数据的时候进行写入到磁盘中。

如果redis宕机了，可以直接将RDB文件读入内存中恢复。

#### 写时复制技术

写时复制技术的核心思想： 只有在任意进程尝试写入数据的时候，才将主进程的数据拷贝到子进程当中。

COW流程：

- 初始阶段：父进程和子进程的虚拟地址指向相同的物理内存页，这些页被标记为只读。
- 触发阶段： 当任意一个进程尝试写入数据时，硬件会触发一个“缺页中断”。
- 执行阶段：内核意识到这是一个COW页时，于是申请一个新的物理内存页，将原数据拷贝过去，并且修改该进程的页表指向新页。此时该页变为“可读写”。

COW的优点主要是，创建进程速度极快，减少内存开销。

COW最终要的一点是：**一开始父子进程都指向同一物理地址，但是当任意进程修改数据的时候，只复制修改的页，而不是所有页**

### 生成RDB策略

Redis提供了两个指令用于生成RDB文件：

- `save`:主线程执行，会阻塞
- `bgsave`:调用`glibc`的函数`fork`产生一个子进程用于写入RDB文件，快照持久化完全交给子进程来处理，父进程继续处理客户端请求，生成RDB文件的默认配置。

首先如果执行`save`指令的话，由于`redis`是单线程模型，所以**既不能处理读指令也不能执行写指令**。

为了确保**数据一致性**，在执行写入RDB文件的时候，会暂停写操作，这样会导致redis性能下降，所以Redis使用操作系统的**多进程写时复制技术（copy on write）**来实现快照持久化。

由于`bgsave`是创建子进程进行写入RDB文件，所以采用`CWO`技术,不影响主进程进行读取数据，并且共享主进程的数据，于是很方便的将redis主进程数据写入磁盘当中。当主进程进行写操作的时候，操作系统会将写入的数据的页单独拷贝到子进程当中。不必将所有内存数据拷贝到子进程当中，不然如果Redis主进程有1G内存数据，然后子进程把这1G数据拷贝到自己当中，会发现内存开销急剧上升。

RDB缺点：

- 如果频繁将RDB写入到磁盘当中，磁盘压力很大，上一秒的RDB文件还没有写完，又要重新写一个RDB文件。
- 执行`fork`系统调用会阻塞主线程，虽然COW不需要拷贝物理内存，但是需要拷贝页表（页表记录了虚拟地址到物理地址的映射关系），页表的大小与内存容量成正比，如果redis内存数据过多，所以创建页表的时间也就越久，所以频繁执行`bgsave`主线程的阻塞时间会很多。

{{< mermaid align="center">}}
graph LR
	write((写请求))
	main[主线程]
	child[bg子进程]
	disk[(磁盘)]

	subgraph memory[内存]
		get1[get指令]
		get2[get指令]
		set[set name:foreverool]
		copy[副本set name:forverool]
		get1 -->get2
		set -->copy
	
	end
	main -.fork.-> child
	child -.读取.->copy
	child -.写入.-> disk
	main -.执行读写指令.-> memory
	write -->set
	
    %% 样式美化
    classDef yellow fill:#fff9e6,stroke:#e6b800,stroke-width:2px;
    classDef blue fill:#e6f7ff,stroke:#006699,stroke-width:2px;
    classDef red fill:#ffe6e6,stroke:#990000,stroke-width:2px;
    classDef green fill:#78ee63,stroke:#78b463,stroke-width:2px;
    
    class main yellow
    class child red
    class disk blue
	class get1,get2 green
	linkStyle default stroke:#5f9ea0,stroke-width:2px;
{{< /mermaid >}}




## AOF写后日志

AOF(Append-Only File)Logs: 仅追加文件日志

AOF日志会记录所有修改数据集的写操作。这些日志以纯文本的格式存储。

写后日志：会先执行写指令操作，然后将数据写入内存，再记录日志。

AOF日志的特点：

- 仅追加模式：AOF日志仅追加文件，这意味着新的写操作会追加到文件末尾。
- 重放：为了恢复数据集，redis会从头到尾重放AOF日志，执行日志中的每个写操作以重建数据集。
- 持久性：AOF日志可以配置不同的持久性级别，你可以在每次写后执行`fsync`操作。写操作可以进行`fsync`最安全但是速度较慢，或者按指定间隔进行`fsync`。
- 重写：随着时间的推移，AOF日志的体积主键增大。Redis提供了通过压缩日志并删除不必要的操作来重写AOF日志的机制，同时还能保持数据的完整性。你可以在Redis配置文件中设置AOF日志相关参数，指定所需的持久化级别和重写策略。

RDB快照在存储空间方面效率较高，适用于完整备份和灾难恢复场景，它能加快redis的重启速度，但是快照之间可能会丢失数据。

AOF日志提供了细粒度的持久化控制，适用于需要确保每次写操作都被记录的系统。然而AOF日志可能消耗更多的存储空间，并且Redis重新启动速度可能会慢。

{{< mermaid align="center">}}
graph LR
	set((set name))
	redis([redis])
	memory([内存])
	disk[(磁盘)]
	set -.写指令.-> redis
	redis -.执行命令将数据写入内存.-> memory
	memory -.记录日志.-> disk
	
	classDef yellow fill:#fff9e6,stroke:#e6b800,stroke-width:2px;
    classDef blue fill:#e6f7ff,stroke:#006699,stroke-width:2px;
    classDef red fill:#ffe6e6,stroke:#990000,stroke-width:2px;
    
    class set red
    class redis yellow
    class memory blue
{{< /mermaid >}}

### AOF日志格式

当执行完指令将数据写入到内存当中，然后redis会将如下格式写入到AOF文件中：

- `*3`:表示当前指令分为三部分，每个部分都是`$+数字`开头，紧跟后面是该部分具体的`指令、键、值`。
- `数字`:表示这部分的命令、键、值占用的字节大小。

![image-20260222045343832](images/posts/redis/image-20260222045343832.png)

#### 如何在docker中查看aof日志

**version: redis 2.8.x**

- 运行`redis`

  ```shell
  docker run -d --name redis-server -p 6379:6379 redis:latest
  ```

- 启动`AOF`

  ```shell
  docker exec -it sh
  
  $cd /etc/redis
  
  $vim redis.conf #修改appendonly为yes
  ```

- 写入数据到redis当中

  ```shell
  docker exec -it redis-server redis-cli
  127.0.0.1:6379>set name foreverool
  127.0.0.1:6379>set age 1
  ```

- 查看AOF文件

  ```shell
  docker exec -it redis-server sh
  cat /data/appendonly.aof
  ```

**version redis 7.4**

- 在宿主机创建`redis.conf`文件

  ```shell
  vim redis.conf
  # 开启 AOF
  appendonly yes
  
  # 开启混合持久化 (Redis 7.4 默认是开启的，但显式写出来更稳)
  aof-use-rdb-preamble yes
  
  # 必须设置 dir，否则 AOF 文件夹可能无法创建
  dir /data
  ```

- 创建容器并映射宿主机redis.conf文件到docker 容器中，并且挂在该文件。

  ```shell
  docker run -d \
    --name redis-server7 \
    -p 6379:6379 \
    -v /home/redis/conf/redis.conf:/etc/redis/redis.conf \
    redis:7.4 \
    redis-server /etc/redis/redis.conf
  ```

- 查看/data目录就可以看到`appendonlydir`目录

为什么redis采用写后日志的形式呢？

主要因为写后日志不需要检查命令的正确，直接记录即可，并且不会阻塞当前写指令执行。

#### 写回策略

当执行写操作的时候，会先将数据写到内存当中，然后执行`write`函数，将数据存储的AOF缓冲区当中，然后根据写回策略，将缓冲区的数据写到aof文件当中。

为了提高文件的写入效率，当用户调用`write`函数时，将一些数据写入文件的时候，操作系统通常会将写入的数据暂存在内存缓冲区里面，等到缓冲区的空间被填满，或者超过了指定的时限后，才真正的将缓冲区的数据写入到磁盘当中。

上述方法虽然提高了效率，但是也会带来一些问题，比如计算机突然停机了，那么缓冲区的数据都会丢失。

为了解决这个问题，操作系统提供了`fsync`和`fdatasync`两个同步函数，他们可以强制让操作系统立即将缓冲区的数据写入到硬盘里面。

redis支持三种写入策略：

- `appendonly always`: 在每次写入aof日志的时候都执行`fsync`，即写指令执行完成之后立马将缓冲区的内容写入磁盘当中。很慢，但是安全。
- `appendonly everysec`:每秒写回，写指令执行完，日志只会将写到AOF文件缓冲区当中，然后每秒把缓冲区的内容同步到磁盘文件当中。
- `appendonly no`:由操作系统控制，写执行完毕，把日志写到AOF文件内存缓冲区当中，由操作系统决定什么时候同步到磁盘文件当中。速度很快。

由于`write`和`fsync`都是系统调用，所以进程从用户态切换到内核态，非常耗时。

如果想要获得高性能选择`no`策略；如果想要保证高可靠性，选择`always`策略；如果允许数据有一点丢失并且希望性能没有太大影响可以选择`everysec`策略。

#### AOF重写机制

AOF文件会随着时间增大，会导致重放时时间会增多，并且磁盘占用也多。

为了解决AOF文件太大问题，redis设计了AOF重放机制，用于对AOF日志进行瘦身。

其原理主要是：**创建一个子进程对内存进行遍历，然后将内存数据转换成一系列Redis操作指令，序列化到新的AOF日志文件中。序列化完成之后，再将操作期间发生的新的AOF日志追加到新的AOF日志文件当中，追加完毕后立即替换旧的AOF文件。**

重写之后，会将原有的多条指令重写为一条指令。也会将一些不存在的数据不用再创建-删除操作。

再执行重写的时候，redis会创建一个新的AOF重写缓冲区，也就是在执行AOF重写的时候，这个期间执行的新的写指令会同时记录到AOF缓冲区和AOF重写缓冲区。



{{< mermaid align="center">}}
graph TD
    %% 第一部分：普通 AOF 流程
    subgraph Normal_AOF [常规 AOF 流程]
        Main1[主线程] -- "「写」指令" --> Data1[(Redis 数据)]
        Data1 -- 记录 aof 日志 --> Buf1[AOF 缓冲区]
        Buf1 -- AOF 日志落盘 --> Disk1[(磁盘)]
    end

    %% 第二部分：AOF 重写流程
    subgraph Rewrite_Process [AOF 重写流程]
        direction TB
        Main2[主线程] -- fork --> Child[子进程]
        
        subgraph Memory [内存空间]
            Data2[(Redis 数据)]
            Buf2[AOF 缓冲区]
            RWBuf[AOF 重写缓冲区]
            Copy[(Redis 数据拷贝 逻辑上拷贝，实际上采用COW与主进程共享内存数据)]
        end

        Main2 -- "「写」指令" --> Data2
        Data2 --> Buf2
        Data2 --> RWBuf
        
        Child -- 遍历内存数据生成重写记录 --> Copy
        Copy -- AOF 重写日志落盘 --> Disk2[(磁盘)]
    end

    Normal_AOF ==>|AOF 重写| Rewrite_Process

    %% 样式定义
    classDef main fill:#fff9e6,stroke:#e6b800,stroke-width:2px;
    classDef child fill:#ffe6e6,stroke:#990000,stroke-width:2px;
    classDef mem fill:#f9f9f9,stroke:#333,stroke-dasharray: 5 5;
    
    class Main1,Main2 main;
    class Child child;
    class Memory mem;
{{< /mermaid >}}

#### redis能否作为MySQL的替代

由于`always`写回策略，只要有“写”指令就将操作写到磁盘当中，这样数据“时刻”保存在磁盘当中。但是redis源码中并没有处理写磁盘失败返回错误信息给客户端，只是返回给客户端执行指令成功（此时只有内存中有数据）。

## 混合持久化

在Redis中混合使用RDB和AOF是目前官方最推荐的持久化方式。这种方式结合了RDB加载的速度和AOF数据丢失少的优点。

自 Redis 7.0.0 版本起，Redis 使用多部分 AOF 机制。也就是说，原始的单个 AOF 文件会被拆分为基础文件（最多一个）和增量文件（可能不止一个）。基础文件代表 AOF[ 重写](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/#log-rewriting)时数据的初始快照（RDB 或 AOF 格式）。增量文件包含自上次创建基础 AOF 文件以来的增量更改。所有这些文件都放在一个单独的目录中，并由清单文件进行跟踪。

## 参考网站与书籍

官网：https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/

书籍：

- 《Redis高手心法》

- 《高效使用Redis》
- *Rediscovering Redis Mastering*





